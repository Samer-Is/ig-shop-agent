from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from ..instagram_oauth import get_instagram_auth_url
from ..config import Settings
import secrets

router = APIRouter()

@router.get("/instagram/login")
async def instagram_login(request: Request, settings: Settings = Depends(Settings)):
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session
        request.session["oauth_state"] = state
        
        # Get Instagram auth URL
        auth_url, _ = get_instagram_auth_url(
            redirect_uri=settings.META_REDIRECT_URI,
            business_name=""  # Optional business name
        )
        
        return JSONResponse({
            "auth_url": auth_url,
            "state": state
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram/callback")
async def instagram_callback(request: Request, code: str, state: str):
    try:
        # Verify state
        stored_state = request.session.get("oauth_state")
        if not stored_state or stored_state != state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for access token
        # This is where you'd implement the token exchange with Instagram
        # For now, we'll return a mock success response
        return JSONResponse({
            "success": True,
            "instagram_handle": "test_user",
            "token": "mock_token"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user():
    return {"message": "Auth endpoint working"} 