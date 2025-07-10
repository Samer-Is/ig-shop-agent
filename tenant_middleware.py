"""
IG-Shop-Agent Multi-Tenant Middleware
Simplified tenant identification
"""
import logging
from typing import Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    """Simplified multi-tenant middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with basic tenant identification"""
        
        # Try to identify tenant from various sources
        tenant_id = self._identify_tenant(request)
        
        # Set tenant in request state
        request.state.tenant_id = tenant_id
        
        if tenant_id:
            logger.debug(f"Request processed for tenant: {tenant_id}")
        else:
            logger.debug("Request processed without tenant identification")
        
        response = await call_next(request)
        return response
    
    def _identify_tenant(self, request: Request) -> Optional[str]:
        """Identify tenant from request"""
        
        # Method 1: Check X-Tenant-ID header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            logger.debug(f"Tenant identified from header: {tenant_id}")
            return tenant_id
        
        # Method 2: Check Authorization header for JWT
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from .instagram_oauth import verify_session_token
                token = auth_header[7:]
                payload = verify_session_token(token)
                if payload and 'tenant_id' in payload:
                    tenant_id = payload['tenant_id']
                    logger.debug(f"Tenant identified from JWT: {tenant_id}")
                    return tenant_id
            except Exception as e:
                logger.warning(f"Failed to extract tenant from JWT: {e}")
        
        # Method 3: Check URL path for tenant ID
        path = request.url.path
        if '/tenant/' in path:
            parts = path.split('/tenant/')
            if len(parts) > 1:
                tenant_part = parts[1].split('/')[0]
                logger.debug(f"Tenant identified from path: {tenant_part}")
                return tenant_part
        
        # Method 4: Check subdomain
        host = request.headers.get('Host', '')
        if host:
            parts = host.split('.')
            if len(parts) >= 3:
                subdomain = parts[0]
                if subdomain != 'www' and subdomain != 'api':
                    tenant_handle = f"@{subdomain}"
                    logger.debug(f"Tenant identified from subdomain: {tenant_handle}")
                    return tenant_handle
        
        # Default tenant for development
        return "default-user"

def get_current_tenant_id(request: Request) -> Optional[str]:
    """Get current tenant ID from request"""
    return getattr(request.state, 'tenant_id', None) 