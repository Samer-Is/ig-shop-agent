from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from ..config import settings

# Security scheme
security = HTTPBearer()

class AuthService:
    """Authentication service for handling JWT tokens and tenant context"""
    
    @staticmethod
    def create_token(user_id: str, username: str, tenant_id: str) -> str:
        """Create JWT token for user"""
        from datetime import datetime, timedelta
        
        payload = {
            "user_id": user_id,
            "username": username,
            "tenant_id": tenant_id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def get_token_from_request(request: Request) -> Optional[str]:
        """Extract token from request headers"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]
    
    @staticmethod
    def get_user_from_token(token: str) -> dict:
        """Get user information from token"""
        payload = AuthService.verify_token(token)
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "tenant_id": payload.get("tenant_id")
        }

# FastAPI Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency to get current authenticated user"""
    try:
        payload = AuthService.verify_token(credentials.credentials)
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "tenant_id": payload.get("tenant_id")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_tenant(current_user: dict = Depends(get_current_user)) -> str:
    """FastAPI dependency to get current tenant ID"""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="No tenant context found")
    return tenant_id

async def get_optional_user(request: Request) -> Optional[dict]:
    """FastAPI dependency to get current user (optional, no exception if not authenticated)"""
    try:
        token = AuthService.get_token_from_request(request)
        if not token:
            return None
        
        payload = AuthService.verify_token(token)
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "tenant_id": payload.get("tenant_id")
        }
    except:
        return None

# Export for convenience
__all__ = ["AuthService", "get_current_user", "get_current_tenant", "get_optional_user"] 