from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from ..instagram_oauth import get_instagram_auth_url, instagram_oauth
from ..config import Settings
import secrets
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/instagram/login")
async def instagram_login(request: Request, settings: Settings = Depends(Settings)):
    """
    Start Instagram OAuth flow by generating authorization URL
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session
        request.session["oauth_state"] = state
        
        # Get Instagram auth URL
        auth_url, _ = get_instagram_auth_url()
        
        logger.info(f"Generated Instagram auth URL with state: {state}")
        
        return JSONResponse({
            "auth_url": auth_url,
            "state": state
        })
    except Exception as e:
        logger.error(f"Failed to generate Instagram auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram/callback")
async def instagram_callback(request: Request, code: str, state: str):
    """
    Handle Instagram OAuth callback
    """
    try:
        # Verify state
        stored_state = request.session.get("oauth_state")
        if not stored_state or stored_state != state:
            logger.error(f"Invalid state. Expected {stored_state}, got {state}")
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for access token
        auth_data = instagram_oauth.exchange_code_for_token(code, state)
        
        if not auth_data:
            logger.error("Failed to exchange code for token")
            raise HTTPException(status_code=400, detail="Failed to complete Instagram authentication")
        
        # Clear state from session
        del request.session["oauth_state"]
        
        # Return success response with Instagram account data
        return JSONResponse({
            "success": True,
            "instagram_handle": auth_data["instagram_accounts"][0]["username"],
            "token": auth_data["access_token"],
            "user": {
                "id": auth_data["instagram_accounts"][0]["id"],
                "instagram_handle": auth_data["instagram_accounts"][0]["username"],
                "instagram_connected": True
            }
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user():
    return {"message": "Auth endpoint working"} 