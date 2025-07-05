from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from instagram_oauth import get_instagram_auth_url, instagram_oauth
from config import settings
from database import get_database
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

class CallbackRequest(BaseModel):
    code: str
    state: str

class TokenResponse(BaseModel):
    success: bool
    token: str
    user: dict
    instagram_handle: str

@router.get("/instagram/login")
async def instagram_login(request: Request) -> Dict:
    """
    Start Instagram OAuth flow by generating authorization URL
    """
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
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

@router.post("/instagram/callback")
async def instagram_callback_post(callback_data: CallbackRequest) -> TokenResponse:
    """
    Handle Instagram OAuth callback (POST version for frontend)
    """
    try:
        logger.info("Handling Instagram OAuth callback (POST)")
        logger.debug("Callback data: %s", {
            'code': '***' if callback_data.code else None,
            'state': callback_data.state
        })
        
        # Validate required parameters
        if not callback_data.code or not callback_data.state:
            logger.error("❌ Missing required parameters: code=%s, state=%s", 
                        bool(callback_data.code), bool(callback_data.state))
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: code and state are required"
            )
        
        try:
            # Exchange code for token
            logger.info("Exchanging authorization code for token")
            token_data = instagram_oauth.exchange_code_for_token(callback_data.code, callback_data.state)
            
            if not token_data:
                logger.error("❌ Failed to exchange code for token - no data returned")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to exchange authorization code for token"
                )
            
            logger.info("✅ Successfully exchanged code for token")
            
            # Get database connection
            db = await get_database()
            
            # Store tokens in database
            if token_data.get('instagram_accounts'):
                account = token_data['instagram_accounts'][0]  # Use first account
                await db.store_instagram_tokens(
                    account['id'],
                    account['access_token'],
                    account
                )
            
            # Create response
            response = TokenResponse(
                success=True,
                token=token_data.get('access_token', ''),
                user={
                    'id': token_data.get('instagram_accounts', [{}])[0].get('id', ''),
                    'instagram_handle': token_data.get('instagram_accounts', [{}])[0].get('username', ''),
                    'instagram_connected': True
                },
                instagram_handle=token_data.get('instagram_accounts', [{}])[0].get('username', '')
            )
            
            return response
            
        except ValueError as e:
            logger.error("❌ Token exchange failed: %s", str(e), exc_info=True)
            raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Unexpected error in instagram_callback_post: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/instagram/callback")
async def instagram_oauth_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    error_reason: Optional[str] = None,
    error_description: Optional[str] = None
):
    """Handle Instagram OAuth callback (GET version for direct redirects)"""
    try:
        logger.info("Handling Instagram OAuth callback (GET)")
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
        
        # Use the same logic as POST version
        callback_data = CallbackRequest(code=code, state=state)
        return await instagram_callback_post(callback_data)
            
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