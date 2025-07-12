"""
Enterprise Rate Limiting Middleware
Provides database-backed rate limiting with advanced features for SaaS applications
"""
import logging
import time
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone, timedelta
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from database_service_rls import get_enterprise_database

logger = logging.getLogger(__name__)

class EnterpriseRateLimitingMiddleware(BaseHTTPMiddleware):
    """Enterprise-grade rate limiting middleware with database persistence"""
    
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
        
        # Premium tier multipliers
        self.tier_multipliers = {
            'basic': 1.0,
            'premium': 5.0,
            'enterprise': 10.0,
            'admin': 100.0
        }
        
        # Burst allowance (short-term higher limits)
        self.burst_limits = {
            'auth': 20,          # Allow 20 auth attempts in 5 minutes
            'ai': 200,           # Allow 200 AI requests in 5 minutes
            'api': 2000,         # Allow 2000 API calls in 5 minutes
        }
        
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
            db = await get_enterprise_database()
            
            # Get user tier for limit calculation
            user_tier = await self._get_user_tier(user_id)
            limit = self._get_limit(endpoint_type, user_id, user_tier)
            
            # Check current usage
            allowed = await db.check_rate_limit(user_id, endpoint_type, limit)
            
            # Calculate remaining and reset time
            window_start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            reset_time = window_start + timedelta(hours=1)
            
            # Get current count for remaining calculation
            current_count = await self._get_current_count(user_id, endpoint_type, window_start)
            remaining = max(0, limit - current_count)
            
            # Log rate limit check
            await db.log_audit_event(
                user_id=user_id,
                action='RATE_LIMIT_CHECK',
                table_name='rate_limits',
                new_values={
                    'endpoint': endpoint_type,
                    'allowed': allowed,
                    'limit': limit,
                    'remaining': remaining
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get('User-Agent', '')
            )
            
            return allowed, remaining, reset_time
            
        except Exception as e:
            logger.error(f"User rate limit check failed: {e}")
            return True, 1000, datetime.now(timezone.utc) + timedelta(hours=1)
    
    async def _check_ip_rate_limit(self, ip_address: str, endpoint_type: str, 
                                 request: Request) -> Tuple[bool, int, datetime]:
        """Check IP-based rate limiting"""
        try:
            # Use IP address as user_id for rate limiting
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
            
            db = await get_enterprise_database()
            
            # Get IP-based limit
            limit = self.ip_limits.get(endpoint_type, self.ip_limits['default'])
            
            # Check current usage
            allowed = await db.check_rate_limit(f"ip_{ip_hash}", f"ip_{endpoint_type}", limit)
            
            # Calculate remaining and reset time
            window_start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            reset_time = window_start + timedelta(hours=1)
            
            # Get current count
            current_count = await self._get_current_count(f"ip_{ip_hash}", f"ip_{endpoint_type}", window_start)
            remaining = max(0, limit - current_count)
            
            return allowed, remaining, reset_time
            
        except Exception as e:
            logger.error(f"IP rate limit check failed: {e}")
            return True, 100, datetime.now(timezone.utc) + timedelta(hours=1)
    
    async def _get_user_tier(self, user_id: str) -> str:
        """Get user subscription tier"""
        try:
            db = await get_enterprise_database()
            
            # Get user tier from database
            user_data = await db.fetch_one(
                "SELECT subscription_tier FROM users WHERE id = $1",
                user_id, user_id=user_id
            )
            
            if user_data and user_data.get('subscription_tier'):
                return user_data['subscription_tier']
            
            return 'basic'  # Default tier
            
        except Exception as e:
            logger.error(f"Failed to get user tier: {e}")
            return 'basic'
    
    def _get_limit(self, endpoint_type: str, user_id: Optional[str] = None, 
                  user_tier: str = 'basic') -> int:
        """Calculate rate limit based on endpoint type and user tier"""
        base_limit = self.default_limits.get(endpoint_type, self.default_limits['api'])
        multiplier = self.tier_multipliers.get(user_tier, 1.0)
        
        return int(base_limit * multiplier)
    
    async def _get_current_count(self, user_id: str, endpoint: str, 
                               window_start: datetime) -> int:
        """Get current request count for user/endpoint/window"""
        try:
            db = await get_enterprise_database()
            
            count = await db.fetch_one("""
                SELECT requests_count FROM rate_limits
                WHERE user_id = $1 AND endpoint = $2 AND window_start = $3
            """, user_id, endpoint, window_start, user_id=user_id)
            
            return count['requests_count'] if count else 0
            
        except Exception as e:
            logger.error(f"Failed to get current count: {e}")
            return 0
    
    def _rate_limit_response(self, remaining: int, reset_time: datetime, 
                           limit_type: str) -> Response:
        """Create rate limit exceeded response"""
        
        retry_after = int((reset_time - datetime.now(timezone.utc)).total_seconds())
        
        response = Response(
            content=f"Rate limit exceeded. Limit type: {limit_type}. Try again in {retry_after} seconds.",
            status_code=429,
            headers={
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(int(reset_time.timestamp())),
                'Retry-After': str(retry_after),
                'Content-Type': 'text/plain'
            }
        )
        
        logger.warning(f"Rate limit exceeded - Type: {limit_type}, Retry after: {retry_after}s")
        
        return response

class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system load"""
    
    def __init__(self):
        self.base_limits = {
            'auth': 10,
            'ai': 100,
            'api': 1000,
        }
        
        self.load_factors = {
            'low': 1.5,      # 50% higher limits when load is low
            'normal': 1.0,   # Normal limits
            'high': 0.7,     # 30% lower limits when load is high
            'critical': 0.5  # 50% lower limits when load is critical
        }
    
    async def get_adaptive_limit(self, endpoint_type: str, user_tier: str) -> int:
        """Get adaptive rate limit based on current system load"""
        try:
            # Get current system load
            load_level = await self._assess_system_load()
            
            # Calculate base limit
            base_limit = self.base_limits.get(endpoint_type, 1000)
            
            # Apply tier multiplier
            tier_multiplier = {
                'basic': 1.0,
                'premium': 3.0,
                'enterprise': 5.0
            }.get(user_tier, 1.0)
            
            # Apply load factor
            load_factor = self.load_factors.get(load_level, 1.0)
            
            # Calculate final limit
            final_limit = int(base_limit * tier_multiplier * load_factor)
            
            logger.debug(f"Adaptive limit: {endpoint_type} {user_tier} {load_level} = {final_limit}")
            
            return final_limit
            
        except Exception as e:
            logger.error(f"Failed to calculate adaptive limit: {e}")
            return self.base_limits.get(endpoint_type, 1000)
    
    async def _assess_system_load(self) -> str:
        """Assess current system load"""
        try:
            db = await get_enterprise_database()
            
            # Check database connection pool utilization
            health = await db.health_check()
            pool_info = health.get('pool_info', {})
            
            # Calculate pool utilization
            pool_utilization = pool_info.get('size', 0) / pool_info.get('max_size', 1)
            
            # Determine load level
            if pool_utilization < 0.5:
                return 'low'
            elif pool_utilization < 0.7:
                return 'normal'
            elif pool_utilization < 0.9:
                return 'high'
            else:
                return 'critical'
                
        except Exception as e:
            logger.error(f"Failed to assess system load: {e}")
            return 'normal'

# Usage tracking for billing
class UsageTracker:
    """Track API usage for billing purposes"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': 1,       # 1 credit per API call
            'ai_requests': 10,    # 10 credits per AI request
            'storage_mb': 1,      # 1 credit per MB stored
            'bandwidth_mb': 1,    # 1 credit per MB transferred
        }
    
    async def track_usage(self, user_id: str, usage_type: str, 
                         amount: int = 1) -> None:
        """Track usage for billing"""
        try:
            db = await get_enterprise_database()
            
            # Calculate credits
            credits = self.metrics.get(usage_type, 1) * amount
            
            # Track usage
            now = datetime.now(timezone.utc)
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
            
            await db.track_usage(
                user_id=user_id,
                metric_type=usage_type,
                metric_value=credits,
                period_start=period_start,
                period_end=period_end
            )
            
            logger.debug(f"Usage tracked: {user_id} {usage_type} {amount} = {credits} credits")
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")

# Global instances
usage_tracker = UsageTracker()
adaptive_limiter = AdaptiveRateLimiter()

async def track_api_usage(user_id: str, usage_type: str, amount: int = 1) -> None:
    """Convenience function to track API usage"""
    await usage_tracker.track_usage(user_id, usage_type, amount) 