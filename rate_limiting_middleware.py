"""
Rate Limiting Middleware for IG-Shop-Agent
Provides in-memory rate limiting for development and database-backed for production
"""
import logging
import time
import hashlib
from typing import Dict, Optional, Tuple, DefaultDict
from datetime import datetime, timezone, timedelta
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from config import settings

logger = logging.getLogger(__name__)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with development and production modes"""
    
    def __init__(self, app, default_limits: Optional[Dict[str, int]] = None):
        super().__init__(app)
        
        # Default rate limits per endpoint type
        self.default_limits = default_limits or {
            'auth': 10,          # Authentication endpoints: 10 requests/hour
            'ai': 100,           # AI endpoints: 100 requests/hour
            'api': 1000,         # General API: 1000 requests/hour
            'webhook': 10000,    # Webhooks: 10000 requests/hour
            'upload': 50,        # File uploads: 50 requests/hour
            'admin': 500,        # Admin endpoints: 500 requests/hour
        }
        
        # In-memory storage for development
        self.memory_store: DefaultDict[str, Dict] = defaultdict(dict)
        
        # IP-based rate limiting for unauthenticated requests
        self.ip_limits = {
            'default': 100,      # 100 requests per IP per hour
            'auth': 20,          # 20 auth attempts per IP per hour
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limiting(request.url.path):
            return await call_next(request)
        
        # Get user context
        user_id = getattr(request.state, 'user_id', None)
        ip_address = self._get_client_ip(request)
        endpoint_type = self._classify_endpoint(request.url.path)
        
        # Check rate limits
        try:
            # Check user-based rate limiting
            if user_id:
                allowed, remaining, reset_time = await self._check_user_rate_limit(
                    user_id, endpoint_type, request
                )
                
                if not allowed:
                    return self._rate_limit_response(remaining, reset_time, 'user')
            
            # Check IP-based rate limiting
            allowed, remaining, reset_time = await self._check_ip_rate_limit(
                ip_address, endpoint_type, request
            )
            
            if not allowed:
                return self._rate_limit_response(remaining, reset_time, 'ip')
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers['X-RateLimit-Limit'] = str(self._get_limit(endpoint_type, user_id))
            response.headers['X-RateLimit-Remaining'] = str(remaining)
            response.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request on error to prevent service disruption
            return await call_next(request)
    
    def _should_skip_rate_limiting(self, path: str) -> bool:
        """Check if rate limiting should be skipped for this path"""
        skip_paths = [
            '/health',
            '/metrics',
            '/docs',
            '/openapi.json',
            '/static/',
            '/favicon.ico'
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _classify_endpoint(self, path: str) -> str:
        """Classify endpoint type for rate limiting"""
        if '/auth' in path or '/login' in path or '/oauth' in path:
            return 'auth'
        elif '/ai' in path or '/chat' in path or '/test-response' in path:
            return 'ai'
        elif '/webhook' in path:
            return 'webhook'
        elif '/upload' in path or '/kb' in path:
            return 'upload'
        elif '/admin' in path:
            return 'admin'
        else:
            return 'api'
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded headers (Azure, Cloudflare, etc.)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else '127.0.0.1'
    
    async def _check_user_rate_limit(self, user_id: str, endpoint_type: str, 
                                   request: Request) -> Tuple[bool, int, datetime]:
        """Check user-based rate limiting"""
        try:
            if settings.ENVIRONMENT == "production":
                # Use enterprise database for production
                return await self._check_database_rate_limit(user_id, endpoint_type, request)
            else:
                # Use in-memory storage for development
                return await self._check_memory_rate_limit(user_id, endpoint_type, request)
                
        except Exception as e:
            logger.error(f"User rate limit check failed: {e}")
            return True, 1000, datetime.now(timezone.utc) + timedelta(hours=1)
    
    async def _check_ip_rate_limit(self, ip_address: str, endpoint_type: str, 
                                 request: Request) -> Tuple[bool, int, datetime]:
        """Check IP-based rate limiting"""
        try:
            # Use IP address as user_id for rate limiting
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
            
            # Get IP-based limit
            limit = self.ip_limits.get(endpoint_type, self.ip_limits['default'])
            
            if settings.ENVIRONMENT == "production":
                # Use enterprise database for production
                return await self._check_database_rate_limit(f"ip_{ip_hash}", f"ip_{endpoint_type}", request, limit)
            else:
                # Use in-memory storage for development
                return await self._check_memory_rate_limit(f"ip_{ip_hash}", f"ip_{endpoint_type}", request, limit)
                
        except Exception as e:
            logger.error(f"IP rate limit check failed: {e}")
            return True, 1000, datetime.now(timezone.utc) + timedelta(hours=1)
    
    async def _check_memory_rate_limit(self, user_id: str, endpoint_type: str, 
                                     request: Request, custom_limit: Optional[int] = None) -> Tuple[bool, int, datetime]:
        """Check rate limit using in-memory storage (development mode)"""
        now = datetime.now(timezone.utc)
        window_start = now.replace(minute=0, second=0, microsecond=0)
        reset_time = window_start + timedelta(hours=1)
        
        # Get limit
        limit = custom_limit or self._get_limit(endpoint_type, user_id)
        
        # Get or create user record
        key = f"{user_id}_{endpoint_type}_{window_start.isoformat()}"
        
        if key not in self.memory_store:
            self.memory_store[key] = {
                'count': 0,
                'window_start': window_start,
                'reset_time': reset_time
            }
        
        # Clean old entries
        self._cleanup_memory_store()
        
        # Check current count
        current_count = self.memory_store[key]['count']
        
        if current_count >= limit:
            remaining = 0
            allowed = False
        else:
            # Increment count
            self.memory_store[key]['count'] += 1
            remaining = limit - self.memory_store[key]['count']
            allowed = True
        
        logger.debug(f"Memory rate limit check: {user_id} {endpoint_type} {current_count}/{limit} allowed={allowed}")
        
        return allowed, remaining, reset_time
    
    async def _check_database_rate_limit(self, user_id: str, endpoint_type: str, 
                                       request: Request, custom_limit: Optional[int] = None) -> Tuple[bool, int, datetime]:
        """Check rate limit using enterprise database (production mode)"""
        try:
            from database_service_rls import get_enterprise_database
            
            db = await get_enterprise_database()
            
            # Get limit
            limit = custom_limit or self._get_limit(endpoint_type, user_id)
            
            # Check current usage
            allowed = await db.check_rate_limit(user_id, endpoint_type, limit)
            
            # Calculate remaining and reset time
            window_start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            reset_time = window_start + timedelta(hours=1)
            
            # Get current count for remaining calculation
            current_count = await self._get_current_count(user_id, endpoint_type, window_start)
            remaining = max(0, limit - current_count)
            
            return allowed, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Database rate limit check failed: {e}")
            return True, 1000, datetime.now(timezone.utc) + timedelta(hours=1)
    
    def _cleanup_memory_store(self):
        """Clean up old entries from memory store"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=2)  # Keep 2 hours of data
        
        keys_to_remove = []
        for key, data in self.memory_store.items():
            if data['window_start'] < cutoff:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_store[key]
    
    def _get_limit(self, endpoint_type: str, user_id: Optional[str] = None) -> int:
        """Get rate limit for endpoint type"""
        base_limit = self.default_limits.get(endpoint_type, self.default_limits['api'])
        
        # In development, use base limits
        if settings.ENVIRONMENT != "production":
            return base_limit
        
        # In production, could apply tier multipliers
        return base_limit
    
    async def _get_current_count(self, user_id: str, endpoint: str, 
                               window_start: datetime) -> int:
        """Get current count for user/endpoint in time window"""
        try:
            from database_service_rls import get_enterprise_database
            
            db = await get_enterprise_database()
            
            result = await db.fetch_one("""
                SELECT COALESCE(requests_count, 0) as count FROM rate_limits
                WHERE user_id = $1 AND endpoint = $2 AND window_start = $3
            """, user_id, endpoint, window_start)
            
            return result['count'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get current count: {e}")
            return 0
    
    def _rate_limit_response(self, remaining: int, reset_time: datetime, 
                           limit_type: str) -> Response:
        """Create rate limit exceeded response"""
        return Response(
            content=f"Rate limit exceeded for {limit_type}. Try again at {reset_time.isoformat()}",
            status_code=429,
            headers={
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(int(reset_time.timestamp())),
                'Retry-After': str(int((reset_time - datetime.now(timezone.utc)).total_seconds()))
            }
        ) 