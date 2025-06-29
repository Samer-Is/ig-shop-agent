from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import secrets
import urllib.parse
from datetime import datetime, timedelta
import jwt
from ..config import settings
from ..database import get_db
from ..services.instagram import InstagramService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models
class InstagramAuthRequest(BaseModel):
    business_name: Optional[str] = None
    redirect_uri: Optional[str] = None

class InstagramCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: Optional[str] = None

class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: str
    username: str
    tenant_id: str

class InstagramAuthResponse(BaseModel):
    auth_url: str
    state: str

class InstagramCallbackResponse(BaseModel):
    success: bool
    session_token: str
    tenant_id: str
    user: dict
    instagram_accounts: list

# Instagram OAuth routes
@router.post("/instagram/auth", response_model=InstagramAuthResponse)
async def get_instagram_auth_url(
    request: InstagramAuthRequest,
    db = Depends(get_db)
):
    """Generate Instagram OAuth URL for user authentication"""
    try:
        instagram_service = InstagramService()
        
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        
        # Build redirect URI
        redirect_uri = request.redirect_uri or settings.FRONTEND_URL
        
        # Generate Instagram OAuth URL
        auth_url = instagram_service.get_auth_url(
            redirect_uri=redirect_uri,
            state=state
        )
        
        # Store state in session/cache for validation
        # TODO: Implement state storage (Redis/database)
        
        return InstagramAuthResponse(
            auth_url=auth_url,
            state=state
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/instagram/callback", response_model=InstagramCallbackResponse)
async def handle_instagram_callback(
    callback_request: InstagramCallbackRequest,
    db = Depends(get_db)
):
    """Handle Instagram OAuth callback and create user session"""
    try:
        instagram_service = InstagramService()
        
        # Verify state parameter
        # TODO: Implement state validation
        
        # Exchange code for access token
        token_data = await instagram_service.exchange_code_for_token(
            code=callback_request.code,
            redirect_uri=callback_request.redirect_uri or settings.FRONTEND_URL
        )
        
        # Get user info from Instagram
        user_info = await instagram_service.get_user_info(token_data["access_token"])
        
        # Create or update tenant
        tenant_id = await instagram_service.create_or_update_tenant(
            db=db,
            instagram_id=user_info["id"],
            username=user_info["username"],
            display_name=user_info.get("name", user_info["username"]),
            access_token=token_data["access_token"],
            expires_in=token_data.get("expires_in", 3600)
        )
        
        # Generate session token
        session_token = jwt.encode(
            {
                "user_id": user_info["id"],
                "username": user_info["username"],
                "tenant_id": tenant_id,
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            settings.JWT_SECRET,
            algorithm="HS256"
        )
        
        return InstagramCallbackResponse(
            success=True,
            session_token=session_token,
            tenant_id=tenant_id,
            user={
                "id": user_info["id"],
                "username": user_info["username"],
                "name": user_info.get("name", user_info["username"])
            },
            instagram_accounts=[{
                "id": user_info["id"],
                "username": user_info["username"],
                "name": user_info.get("name", user_info["username"])
            }]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    request: Request,
    db = Depends(get_db)
):
    """Verify user session token"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Decode and verify JWT
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        
        return TokenVerifyResponse(
            valid=True,
            user_id=payload["user_id"],
            username=payload["username"],
            tenant_id=payload["tenant_id"]
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token verification failed: {str(e)}")

@router.post("/logout")
async def logout(
    request: Request,
    db = Depends(get_db)
):
    """Logout user (invalidate session)"""
    try:
        # For now, just return success
        # In production, you might want to blacklist the token
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}") 