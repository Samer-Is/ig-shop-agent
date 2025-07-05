from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from instagram_oauth import get_instagram_auth_url, instagram_oauth
from config import settings
import secrets
import logging
from typing import Dict, Optional
from pydantic import BaseModel

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthResponse(BaseModel):
    auth_url: str
    state: str

class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    instagram_accounts: list
    business_name: str
    authenticated_at: str

@router.get("/instagram/login")
async def instagram_login(request: Request) -> Dict:
    """
    Start Instagram OAuth flow by generating authorization URL
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session
        request.session["oauth_state"] = state
        
        # Get Instagram auth URL
        auth_url, _ = get_instagram_auth_url(
            redirect_uri=settings.META_REDIRECT_URI,
            business_name=request.headers.get("X-Business-Name", "")
        )
        
        logger.info(f"Generated Instagram auth URL with state: {state}")
        
        # Create response with auth URL and state
        response = {
            "auth_url": auth_url,
            "state": state
        }
        
        return response
        
    except ValueError as e:
        logger.error(f"Configuration error in Instagram auth: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Instagram OAuth configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to generate Instagram auth URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate Instagram authorization URL. Please try again later."
        )

@router.post("/instagram/url", response_model=AuthResponse)
async def get_instagram_oauth_url(request: Request):
    """Get Instagram OAuth URL for authorization"""
    try:
        logger.info("Generating Instagram OAuth URL")
        logger.debug("Request headers: %s", dict(request.headers))
        
        # Get origin for dynamic redirect URI
        origin = request.headers.get('origin')
        if not origin:
            logger.error("❌ No origin header in request")
            raise HTTPException(status_code=400, detail="Missing origin header")
        
        logger.debug("Request origin: %s", origin)
        
        # Get business name from query params
        business_name = request.query_params.get('business_name', '')
        logger.debug("Business name from query: %s", business_name)
        
        # Build redirect URI
        redirect_uri = f"{origin}/auth/instagram/callback"
        logger.debug("Constructed redirect URI: %s", redirect_uri)
        
        # Get authorization URL
        try:
            auth_url, state = get_instagram_auth_url(redirect_uri, business_name)
            logger.info("✅ Successfully generated Instagram OAuth URL")
            logger.debug("Auth URL: %s", auth_url)
            logger.debug("State token: %s", state)
            
            return AuthResponse(auth_url=auth_url, state=state)
        except Exception as e:
            logger.error("❌ Failed to get Instagram authorization URL: %s", str(e), exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get Instagram authorization URL: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Unexpected error in get_instagram_oauth_url: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/instagram/callback", response_model=TokenResponse)
async def instagram_oauth_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    error_reason: Optional[str] = None,
    error_description: Optional[str] = None
):
    """Handle Instagram OAuth callback"""
    try:
        logger.info("Handling Instagram OAuth callback")
        logger.debug("Callback parameters: %s", {
            'code': '***' if code else None,
            'state': state,
            'error': error,
            'error_reason': error_reason,
            'error_description': error_description
        })
        
        # Check for OAuth errors
        if error:
            error_msg = f"Instagram OAuth error: {error}"
            if error_reason:
                error_msg += f" - Reason: {error_reason}"
            if error_description:
                error_msg += f" - Description: {error_description}"
                
            logger.error("❌ %s", error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate required parameters
        if not code or not state:
            logger.error("❌ Missing required parameters: code=%s, state=%s", bool(code), bool(state))
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: code and state are required"
            )
        
        try:
            # Exchange code for token
            logger.info("Exchanging authorization code for token")
            token_data = instagram_oauth.exchange_code_for_token(code, state)
            
            if not token_data:
                logger.error("❌ Failed to exchange code for token - no data returned")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to exchange authorization code for token"
                )
            
            logger.info("✅ Successfully exchanged code for token")
            logger.debug("Token data: %s", {
                **token_data,
                'access_token': '***',
                'instagram_accounts': [
                    {**acc, 'access_token': '***'} for acc in token_data.get('instagram_accounts', [])
                ]
            })
            
            return TokenResponse(**token_data)
            
        except ValueError as e:
            logger.error("❌ Token exchange failed: %s", str(e), exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Unexpected error in instagram_oauth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/me")
async def get_current_user():
    return {"message": "Auth endpoint working"} 