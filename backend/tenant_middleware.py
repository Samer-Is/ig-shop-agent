"""
IG-Shop-Agent Multi-Tenant Middleware
Request-level tenant identification and data isolation
"""
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
import asyncio
from contextvars import ContextVar

from database import db
from instagram_oauth import verify_session_token

logger = logging.getLogger(__name__)

# Context variable to store current tenant ID for the request
current_tenant_id: ContextVar[Optional[str]] = ContextVar('current_tenant_id', default=None)

class TenantContext:
    """Thread-safe tenant context manager"""
    
    def __init__(self):
        self._tenant_cache: Dict[str, Dict[str, Any]] = {}
    
    def set_tenant(self, tenant_id: str) -> None:
        """Set current tenant ID in context"""
        current_tenant_id.set(tenant_id)
        logger.debug(f"Tenant context set to: {tenant_id}")
    
    def get_tenant_id(self) -> Optional[str]:
        """Get current tenant ID from context"""
        return current_tenant_id.get()
    
    def clear_tenant(self) -> None:
        """Clear tenant context"""
        current_tenant_id.set(None)
        logger.debug("Tenant context cleared")
    
    async def get_tenant_info(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant information with caching"""
        if tenant_id in self._tenant_cache:
            return self._tenant_cache[tenant_id]
        
        try:
            # Get tenant from database
            tenant_info = await db.get_tenant_by_handle(tenant_id)
            if tenant_info:
                self._tenant_cache[tenant_id] = tenant_info
                return tenant_info
            
            # Try by actual tenant ID
            async with db.get_connection() as conn:
                row = await conn.fetchrow("""
                    SELECT id, instagram_handle, display_name, plan, status, created_at
                    FROM tenants 
                    WHERE id = $1
                """, tenant_id)
                
                if row:
                    tenant_info = dict(row)
                    self._tenant_cache[tenant_id] = tenant_info
                    return tenant_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tenant info for {tenant_id}: {e}")
            return None
    
    def invalidate_cache(self, tenant_id: str = None) -> None:
        """Invalidate tenant cache"""
        if tenant_id:
            self._tenant_cache.pop(tenant_id, None)
        else:
            self._tenant_cache.clear()

# Global tenant context
tenant_context = TenantContext()

class TenantIdentificationStrategy:
    """Base class for tenant identification strategies"""
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Identify tenant from request data"""
        raise NotImplementedError

class HeaderBasedTenantStrategy(TenantIdentificationStrategy):
    """Identify tenant from HTTP headers"""
    
    def __init__(self, header_name: str = 'X-Tenant-ID'):
        self.header_name = header_name
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract tenant ID from headers"""
        headers = request_data.get('headers', {})
        tenant_id = headers.get(self.header_name) or headers.get(self.header_name.lower())
        
        if tenant_id:
            logger.debug(f"Tenant identified from header {self.header_name}: {tenant_id}")
            return tenant_id
        
        return None

class JWTBasedTenantStrategy(TenantIdentificationStrategy):
    """Identify tenant from JWT token"""
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract tenant ID from JWT token"""
        # Get authorization header
        headers = request_data.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            return None
        
        # Extract token
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
        
        try:
            # Verify and decode JWT
            payload = verify_session_token(token)
            if payload:
                tenant_id = payload.get('tenant_id')
                if tenant_id:
                    logger.debug(f"Tenant identified from JWT: {tenant_id}")
                    return tenant_id
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract tenant from JWT: {e}")
            return None

class SubdomainBasedTenantStrategy(TenantIdentificationStrategy):
    """Identify tenant from subdomain"""
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract tenant ID from subdomain"""
        headers = request_data.get('headers', {})
        host = headers.get('Host') or headers.get('host')
        
        if not host:
            return None
        
        # Extract subdomain (assuming format: tenant.domain.com)
        parts = host.split('.')
        if len(parts) >= 3:
            subdomain = parts[0]
            # Convert subdomain to tenant handle format
            tenant_handle = f"@{subdomain}"
            logger.debug(f"Tenant identified from subdomain: {tenant_handle}")
            return tenant_handle
        
        return None

class PathBasedTenantStrategy(TenantIdentificationStrategy):
    """Identify tenant from URL path"""
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Extract tenant ID from URL path"""
        url = request_data.get('url', '')
        
        # Assuming format: /api/v1/tenant/{tenant_id}/...
        if '/tenant/' in url:
            parts = url.split('/tenant/')
            if len(parts) > 1:
                tenant_part = parts[1].split('/')[0]
                logger.debug(f"Tenant identified from path: {tenant_part}")
                return tenant_part
        
        return None

class TenantMiddleware:
    """Multi-tenant middleware for request processing"""
    
    def __init__(self):
        self.strategies = [
            JWTBasedTenantStrategy(),          # Primary: JWT token
            HeaderBasedTenantStrategy(),       # Secondary: Headers
            PathBasedTenantStrategy(),         # Tertiary: URL path
            SubdomainBasedTenantStrategy()     # Fallback: Subdomain
        ]
    
    async def identify_tenant(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Identify tenant using multiple strategies"""
        for strategy in self.strategies:
            tenant_id = await strategy.identify_tenant(request_data)
            if tenant_id:
                return tenant_id
        
        logger.warning("No tenant identified from request")
        return None
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with tenant context"""
        # Clear any existing tenant context
        tenant_context.clear_tenant()
        
        # Identify tenant
        tenant_id = await self.identify_tenant(request_data)
        
        if tenant_id:
            # Validate tenant exists and is active
            tenant_info = await tenant_context.get_tenant_info(tenant_id)
            
            if tenant_info and tenant_info.get('status') == 'active':
                # Set tenant context
                tenant_context.set_tenant(str(tenant_info['id']))
                
                # Add tenant info to request
                request_data['tenant'] = tenant_info
                request_data['tenant_id'] = str(tenant_info['id'])
                
                logger.info(f"Request processed for tenant: {tenant_info['display_name']} ({tenant_info['id']})")
                
                return {
                    'success': True,
                    'tenant_id': str(tenant_info['id']),
                    'tenant_info': tenant_info,
                    'request_data': request_data
                }
            else:
                logger.warning(f"Tenant not found or inactive: {tenant_id}")
                return {
                    'success': False,
                    'error': 'Tenant not found or inactive',
                    'tenant_id': tenant_id
                }
        else:
            # Allow requests without tenant for public endpoints
            logger.debug("Processing request without tenant context")
            return {
                'success': True,
                'tenant_id': None,
                'tenant_info': None,
                'request_data': request_data
            }

# Global middleware instance
tenant_middleware = TenantMiddleware()

def require_tenant(func: Callable) -> Callable:
    """Decorator to require tenant context for function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tenant_id = tenant_context.get_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant context required but not set")
        
        return await func(*args, **kwargs)
    
    return wrapper

def with_tenant(tenant_id: str):
    """Decorator to execute function with specific tenant context"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            original_tenant = tenant_context.get_tenant_id()
            try:
                tenant_context.set_tenant(tenant_id)
                return await func(*args, **kwargs)
            finally:
                if original_tenant:
                    tenant_context.set_tenant(original_tenant)
                else:
                    tenant_context.clear_tenant()
        
        return wrapper
    return decorator

class TenantAwareDatabase:
    """Database operations with automatic tenant isolation"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def get_connection(self):
        """Get database connection with tenant context"""
        tenant_id = tenant_context.get_tenant_id()
        return self.db.get_connection(tenant_id)
    
    @require_tenant
    async def create_catalog_item(self, item_data: Dict[str, Any]) -> str:
        """Create catalog item for current tenant"""
        tenant_id = tenant_context.get_tenant_id()
        
        async with self.get_connection() as conn:
            item_id = await conn.fetchval("""
                INSERT INTO catalog_items (
                    tenant_id, sku, name, price_jod, description, 
                    category, stock_quantity, media_url, extras
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """, 
                tenant_id,
                item_data['sku'],
                item_data['name'],
                item_data['price_jod'],
                item_data.get('description'),
                item_data.get('category'),
                item_data.get('stock_quantity', 0),
                item_data.get('media_url'),
                item_data.get('extras', {})
            )
            
            logger.info(f"Created catalog item {item_id} for tenant {tenant_id}")
            return str(item_id)
    
    @require_tenant
    async def get_catalog_items(self, limit: int = 100, offset: int = 0) -> list:
        """Get catalog items for current tenant"""
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM catalog_items 
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            return [dict(row) for row in rows]
    
    @require_tenant
    async def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create order for current tenant"""
        tenant_id = tenant_context.get_tenant_id()
        
        async with self.get_connection() as conn:
            order_id = await conn.fetchval("""
                INSERT INTO orders (
                    tenant_id, sku, qty, customer, phone, 
                    status, total_amount, delivery_address, notes
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """,
                tenant_id,
                order_data['sku'],
                order_data['qty'],
                order_data['customer'],
                order_data['phone'],
                order_data.get('status', 'pending'),
                order_data['total_amount'],
                order_data.get('delivery_address'),
                order_data.get('notes')
            )
            
            logger.info(f"Created order {order_id} for tenant {tenant_id}")
            return str(order_id)
    
    @require_tenant
    async def get_orders(self, limit: int = 100, offset: int = 0) -> list:
        """Get orders for current tenant"""
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM orders 
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            return [dict(row) for row in rows]

# Global tenant-aware database instance
tenant_db = TenantAwareDatabase(db)

# Utility functions
def get_current_tenant_id() -> Optional[str]:
    """Get current tenant ID from context"""
    return tenant_context.get_tenant_id()

async def get_current_tenant_info() -> Optional[Dict[str, Any]]:
    """Get current tenant information"""
    tenant_id = get_current_tenant_id()
    if tenant_id:
        return await tenant_context.get_tenant_info(tenant_id)
    return None

async def process_tenant_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process request with tenant middleware"""
    return await tenant_middleware.process_request(request_data) 