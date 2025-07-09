"""
IG-Shop-Agent Instagram OAuth Integration
Real Instagram authentication to replace mock login
"""
import os
import logging
import time
import hashlib
import secrets
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException
import jwt
from cryptography.fernet import Fernet

from config import settings

# Import Azure Key Vault functions
try:
    from azure_keyvault import get_secret
except ImportError:
    def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Fallback function if Azure Key Vault is not available"""
        return os.getenv(secret_name.upper().replace('-', '_'), default)

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class InstagramOAuth:
    """Instagram OAuth 2.0 implementation"""
    
    def __init__(self):
        """Initialize Instagram OAuth handler"""
        try:
            logger.info("Initializing Instagram OAuth...")
            
            # OAuth configuration
            self.base_url = "https://graph.facebook.com"
            self.graph_api_version = "v21.0"
            
            # Get credentials from environment or Azure Key Vault
            self.app_id = get_secret("META_APP_ID") or os.getenv("META_APP_ID")
            self.app_secret = get_secret("META_APP_SECRET") or os.getenv("META_APP_SECRET")
            self.redirect_uri = settings.META_REDIRECT_URI
            
            # JWT settings
            self.jwt_secret_key = settings.JWT_SECRET
            self.jwt_algorithm = settings.JWT_ALGORITHM
            self.jwt_expiration_hours = 24  # Default 24 hours
            
            # Handle missing credentials gracefully
            if not self.app_id or not self.app_secret:
                logger.warning("⚠️ META_APP_ID and META_APP_SECRET not configured - Instagram OAuth will be disabled")
                logger.warning("⚠️ Please configure Instagram OAuth credentials in Azure Key Vault or environment variables")
                self.is_configured = False
                # Set dummy values to prevent crashes
                self.app_id = "not_configured"
                self.app_secret = "not_configured"
            else:
                self.is_configured = True
                logger.info("✅ Instagram OAuth credentials loaded successfully")
            
            if not self.redirect_uri:
                logger.warning("⚠️ META_REDIRECT_URI not configured - using default")
                self.redirect_uri = "https://igshop-api.azurewebsites.net/auth/instagram/callback"
            
            # Encryption for token storage
            self.encryption_key = self._get_encryption_key()
            self.cipher_suite = Fernet(self.encryption_key)
            
            # OAuth state management
            self._oauth_states: Dict[str, dict] = {}
            
            if self.is_configured:
                logger.info("✅ Instagram OAuth initialized successfully")
            else:
                logger.info("⚠️ Instagram OAuth initialized in disabled mode")
                
        except Exception as e:
            logger.error("❌ Failed to initialize Instagram OAuth: %s", str(e), exc_info=True)
            # Don't crash the application - set disabled mode
            self.is_configured = False
            self.app_id = "not_configured"
            self.app_secret = "not_configured"
            self.redirect_uri = "https://igshop-api.azurewebsites.net/auth/instagram/callback"
            logger.warning("⚠️ Instagram OAuth disabled due to initialization error")
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for token storage"""
        try:
            logger.debug("Getting encryption key...")
            key = os.getenv('TOKEN_ENCRYPTION_KEY')
            if not key:
                key = Fernet.generate_key()
                logger.warning("⚠️ Generated new encryption key - store this securely in production")
            return key if isinstance(key, bytes) else key.encode()
        except Exception as e:
            logger.error("❌ Failed to get/generate encryption key: %s", str(e), exc_info=True)
            raise
    
    def get_authorization_url(self, redirect_uri: str = None, business_name: str = "") -> Tuple[str, str]:
        """Generate Instagram authorization URL"""
        try:
            # Check if OAuth is properly configured
            if not self.is_configured:
                logger.error("❌ Instagram OAuth not configured - cannot generate authorization URL")
                raise ValueError("Instagram OAuth is not configured. Please set META_APP_ID and META_APP_SECRET.")
            
            logger.info("Generating Instagram authorization URL for business: %s", business_name)
            
            # Generate state parameter for CSRF protection
            state = secrets.token_urlsafe(32)
            logger.debug("Generated state token: %s", state)
            
            # Store state with metadata
            self._oauth_states[state] = {
                'created_at': datetime.utcnow(),
                'redirect_uri': redirect_uri or self.redirect_uri,
                'business_name': business_name
            }
            
            # Required Instagram Business Login scopes (from Meta's embed URL)
            scopes = [
                'instagram_business_basic',
                'instagram_business_manage_messages', 
                'instagram_business_manage_comments',
                'instagram_business_content_publish',
                'instagram_business_manage_insights'
            ]
            logger.debug("Using Instagram Business Login scopes: %s", scopes)
            
            # Build authorization URL with proper encoding (Meta's format)
            auth_params = {
                'force_reauth': 'true',
                'client_id': self.app_id,
                'redirect_uri': redirect_uri or self.redirect_uri,
                'response_type': 'code',
                'scope': ','.join(scopes),
                'state': state
            }
            
            # Use Instagram Business Login endpoint (Meta's domain)
            auth_url = f"https://www.instagram.com/oauth/authorize?" + "&".join([
                f"{key}={requests.utils.quote(str(value))}" 
                for key, value in auth_params.items()
            ])
            
            logger.info("✅ Generated Instagram Business Login URL: %s", auth_url)
            logger.debug("Auth parameters: %s", auth_params)
            
            return auth_url, state
            
        except Exception as e:
            logger.error("❌ Failed to generate authorization URL: %s", str(e), exc_info=True)
            raise ValueError(f"Failed to generate authorization URL: {str(e)}")
    
    def exchange_code_for_token(self, code: str, state: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            logger.info("Exchanging authorization code for token with state: %s", state)
            
            # Verify state parameter
            if state not in self._oauth_states:
                logger.error("❌ Invalid OAuth state: %s", state)
                logger.debug("Current states: %s", list(self._oauth_states.keys()))
                raise ValueError("Invalid state parameter")
            
            state_data = self._oauth_states[state]
            logger.debug("State data: %s", state_data)
            
            # Check state expiration (15 minutes)
            state_age = datetime.utcnow() - state_data['created_at']
            if state_age > timedelta(minutes=15):
                logger.error("❌ Expired OAuth state: %s (age: %s)", state, state_age)
                del self._oauth_states[state]
                raise ValueError("OAuth state has expired")
            
            # Exchange code for token using Instagram API
            token_url = "https://api.instagram.com/oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': state_data['redirect_uri'],
                'grant_type': 'authorization_code',
                'code': code
            }
            
            logger.debug("Making token exchange request to: %s", token_url)
            logger.debug("Token request data: %s", {**token_data, 'client_secret': '***'})
            
            response = requests.post(token_url, data=token_data, timeout=10)
            logger.debug("Token exchange response status: %d", response.status_code)
            logger.debug("Token exchange response headers: %s", dict(response.headers))
            
            try:
                response.raise_for_status()
                token_info = response.json()
                logger.debug("Instagram token exchange response: %s", {
                    **token_info,
                    'access_token': '***' if 'access_token' in token_info else None
                })
            except Exception as e:
                logger.error("❌ Instagram token exchange request failed: %s", str(e))
                logger.error("Response content: %s", response.text)
                raise

            if 'access_token' not in token_info:
                logger.error("❌ No access token in response: %s", token_info)
                raise ValueError("Failed to get access token from Instagram")

            # For Instagram Business Login, we get Instagram User access token directly
            # The response includes: access_token, user_id, permissions
            instagram_access_token = token_info['access_token']
            instagram_user_id = token_info.get('user_id')

            logger.info("✅ Received Instagram User access token for user ID: %s", instagram_user_id)

            # Exchange for long-lived Instagram token
            logger.info("Getting long-lived Instagram token...")
            long_lived_token = self._get_long_lived_instagram_token(instagram_access_token)
            if not long_lived_token:
                # If long-lived token exchange fails, use the short-lived token
                logger.warning("⚠️ Failed to get long-lived token, using short-lived token")
                long_lived_token = {
                    'access_token': instagram_access_token,
                    'token_type': 'bearer',
                    'expires_in': 3600  # 1 hour for short-lived tokens
                }

            # Get Instagram user profile information
            logger.info("Getting Instagram user profile...")
            user_profile = self._get_instagram_user_profile(long_lived_token['access_token'])
            if not user_profile:
                raise ValueError("Failed to get Instagram user profile")

            # Cleanup state
            del self._oauth_states[state]

            # Return Instagram authentication data
            auth_data = {
                'access_token': long_lived_token['access_token'],
                'expires_in': long_lived_token.get('expires_in', 3600),
                'token_type': long_lived_token.get('token_type', 'bearer'),
                'user_id': instagram_user_id,
                'username': user_profile.get('username'),
                'name': user_profile.get('name'),
                'account_type': user_profile.get('account_type'),
                'business_name': state_data.get('business_name', ''),
                'authenticated_at': datetime.utcnow().isoformat()
            }

            logger.info("✅ Instagram Business Login successful for user: %s", user_profile.get('username'))
            logger.debug("Auth data: %s", {
                **auth_data,
                'access_token': '***'
            })

            return auth_data
            
        except RequestException as e:
            logger.error("❌ Network error during token exchange: %s", str(e), exc_info=True)
            raise ValueError(f"Network error during authentication: {str(e)}")
        except Exception as e:
            logger.error("❌ Unexpected error during token exchange: %s", str(e), exc_info=True)
            raise ValueError(f"Authentication failed: {str(e)}")
    
    def _get_long_lived_instagram_token(self, short_lived_token: str) -> Optional[Dict]:
        """Exchange short-lived Instagram token for long-lived token"""
        try:
            logger.info("Exchanging short-lived Instagram token for long-lived token")
            url = "https://graph.instagram.com/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.app_secret,
                'access_token': short_lived_token
            }
            
            logger.debug("Making long-lived Instagram token request to: %s", url)
            logger.debug("Request params: %s", {**params, 'client_secret': '***', 'access_token': '***'})
            
            response = requests.get(url, params=params, timeout=10)
            logger.debug("Long-lived Instagram token response status: %d", response.status_code)
            
            try:
                response.raise_for_status()
                token_info = response.json()
                logger.debug("Long-lived Instagram token response: %s", {
                    **token_info,
                    'access_token': '***' if 'access_token' in token_info else None
                })
                return token_info
            except Exception as e:
                logger.error("❌ Long-lived Instagram token request failed: %s", str(e))
                logger.error("Response content: %s", response.text)
                return None
            
        except Exception as e:
            logger.error("❌ Failed to get long-lived Instagram token: %s", str(e), exc_info=True)
            return None
    
    def _get_instagram_user_profile(self, access_token: str) -> Optional[Dict]:
        """Get Instagram user profile information"""
        try:
            logger.info("Getting Instagram user profile")
            
            url = "https://graph.instagram.com/me"
            params = {
                'access_token': access_token,
                'fields': 'user_id,username,name,account_type,profile_picture_url,followers_count,follows_count,media_count'
            }
            
            logger.debug("Making Instagram profile request to: %s", url)
            logger.debug("Request params: %s", {**params, 'access_token': '***'})
            
            response = requests.get(url, params=params, timeout=10)
            logger.debug("Instagram profile response status: %d", response.status_code)
            
            try:
                response.raise_for_status()
                profile_data = response.json()
                logger.debug("Instagram profile response: %s", profile_data)
                return profile_data
            except Exception as e:
                logger.error("❌ Instagram profile request failed: %s", str(e))
                logger.error("Response content: %s", response.text)
                return None
            
        except Exception as e:
            logger.error("❌ Failed to get Instagram user profile: %s", str(e), exc_info=True)
            return None
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt access token for secure storage"""
        try:
            encrypted_token = self.cipher_suite.encrypt(token.encode())
            return encrypted_token.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt token: {e}")
            return token  # Return unencrypted as fallback
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt access token from storage"""
        try:
            decrypted_token = self.cipher_suite.decrypt(encrypted_token.encode())
            return decrypted_token.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            return encrypted_token  # Return as-is if decryption fails
    
    def validate_token(self, access_token: str) -> bool:
        """Validate if access token is still valid"""
        try:
            url = f"{self.base_url}/me"
            params = {'access_token': access_token}
            
            response = requests.get(url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to validate token: {e}")
            return False
    
    def refresh_token_if_needed(self, token_data: Dict) -> Optional[Dict]:
        """Refresh token if it's close to expiring"""
        try:
            authenticated_at = datetime.fromisoformat(token_data['authenticated_at'])
            expires_in = token_data.get('expires_in', 3600)
            
            # If token expires in less than 1 hour, try to refresh
            expiry_time = authenticated_at + timedelta(seconds=expires_in)
            if datetime.utcnow() + timedelta(hours=1) > expiry_time:
                
                # For Instagram tokens, we typically need to re-authenticate
                # as refresh tokens are not always available
                logger.info("Token is close to expiring - user will need to re-authenticate")
                return None
            
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return None
    
    def generate_jwt_token(self, user_data: Dict, tenant_id: str) -> str:
        """Generate JWT token for session management"""
        payload = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'tenant_id': tenant_id,
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            'iat': datetime.utcnow(),
            'iss': 'ig-shop-agent'
        }
        
        secret_key = get_secret('jwt-secret-key') or self.jwt_secret_key
        return jwt.encode(payload, secret_key, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            secret_key = get_secret('jwt-secret-key') or self.jwt_secret_key
            payload = jwt.decode(token, secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

# Global Instagram OAuth instance
instagram_oauth = InstagramOAuth()

def get_instagram_auth_url(redirect_uri: str = None, business_name: str = "") -> Tuple[str, str]:
    """Get Instagram authorization URL"""
    return instagram_oauth.get_authorization_url(redirect_uri, business_name)

def handle_oauth_callback(code: str, state: str) -> Optional[Dict]:
    """Handle OAuth callback"""
    return instagram_oauth.exchange_code_for_token(code, state)

def validate_instagram_token(access_token: str) -> bool:
    """Validate Instagram access token"""
    return instagram_oauth.validate_token(access_token)

def generate_session_token(user_data: Dict, tenant_id: str) -> str:
    """Generate session token"""
    return instagram_oauth.generate_jwt_token(user_data, tenant_id)

def verify_session_token(token: str) -> Optional[Dict]:
    """Verify session token"""
    return instagram_oauth.verify_jwt_token(token)

# Export for convenience
__all__ = [
    "InstagramOAuth",
    "instagram_oauth", 
    "get_instagram_auth_url",
    "handle_oauth_callback",
    "validate_instagram_token",
    "generate_session_token",
    "verify_session_token"
] 