"""
Authentication Middleware for Multi-Tenant Support
Extracts user information from JWT tokens and makes it available to all API endpoints
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from database import get_database

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication and user context"""
    
    def __init__(self, app, secret_key: str = "your-secret-key"):
        super().__init__(app)
        self.secret_key = secret_key
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and inject user context"""
        
        # Skip auth for certain endpoints
        if self._should_skip_auth(request.url.path):
            return await call_next(request)
        
        # Extract user from token
        user_info = await self._extract_user_from_request(request)
        
        # Inject user info into request state
        request.state.user = user_info
        request.state.user_id = user_info.get('id') if user_info else None
        request.state.is_authenticated = user_info is not None
        
        # Continue with request
        response = await call_next(request)
        return response
    
    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        skip_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/webhooks",
            "/auth/instagram",
            "/auth/callback",
            "/backend-api/ai/test-detailed",  # For testing
            "/backend-api/ai/test",  # For testing
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _extract_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract user information from request"""
        
        # Method 1: Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                user_info = await self._verify_jwt_token(token)
                if user_info:
                    logger.debug(f"User authenticated via JWT: {user_info.get('id')}")
                    return user_info
            except Exception as e:
                logger.warning(f"Failed to verify JWT token: {e}")
        
        # Method 2: Check X-User-ID header (for development/testing)
        user_id = request.headers.get('X-User-ID')
        if user_id:
            try:
                user_info = await self._get_user_by_id(user_id)
                if user_info:
                    logger.debug(f"User authenticated via header: {user_id}")
                    return user_info
            except Exception as e:
                logger.warning(f"Failed to get user by ID: {e}")
        
        # Method 3: Check for session in localStorage (for frontend compatibility)
        # This would be handled by the frontend sending proper tokens
        
        # Method 4: Default to first authenticated user (for development)
        try:
            db = await get_database()
            user_info = await db.fetch_one(
                "SELECT id, instagram_username, instagram_page_name, instagram_connected FROM users WHERE instagram_connected = true LIMIT 1"
            )
            if user_info:
                logger.debug(f"Using default authenticated user: {user_info.get('id')}")
                return dict(user_info)
        except Exception as e:
            logger.warning(f"Failed to get default user: {e}")
        
        return None
    
    async def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and extract user information"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Extract user ID from payload
            user_id = payload.get('user_id') or payload.get('sub')
            if not user_id:
                return None
            
            # Get user from database
            return await self._get_user_by_id(user_id)
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from database"""
        try:
            db = await get_database()
            user = await db.fetch_one(
                "SELECT id, instagram_username, instagram_page_name, instagram_connected, created_at FROM users WHERE id = $1",
                user_id
            )
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

# Helper function to get current user from request
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from request state"""
    return getattr(request.state, 'user', None)

def get_current_user_id(request: Request) -> Optional[str]:
    """Get current user ID from request state"""
    return getattr(request.state, 'user_id', None)

def require_auth(request: Request) -> Dict[str, Any]:
    """Require authentication and return user info"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user 