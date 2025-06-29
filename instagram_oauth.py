"""
IG-Shop-Agent Instagram OAuth Integration
Real Instagram authentication to replace mock login
"""
import os
import logging
import time
import hashlib
import secrets
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
import jwt
from cryptography.fernet import Fernet

from config import settings
from azure_keyvault import get_secret

logger = logging.getLogger(__name__)

class InstagramOAuth:
    """Instagram OAuth 2.0 implementation"""
    
    def __init__(self):
        self.app_id = get_secret('meta-app-id') or settings.meta_app_id
        self.app_secret = get_secret('meta-app-secret') or settings.meta_app_secret
        self.graph_api_version = settings.meta_graph_api_version
        self.base_url = f"https://graph.facebook.com/{self.graph_api_version}"
        
        # Encryption for token storage
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # OAuth state management (in production, use Redis/database)
        self._oauth_states: Dict[str, dict] = {}
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for token storage"""
        key = get_secret('token-encryption-key')
        if not key:
            # Generate a new key (in production, store this securely)
            key = Fernet.generate_key().decode()
            logger.warning("Generated new encryption key - store this securely in production")
        else:
            key = key.encode() if isinstance(key, str) else key
        return key
    
    def get_authorization_url(self, redirect_uri: str, business_name: str = "") -> Tuple[str, str]:
        """Generate Instagram authorization URL"""
        
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state with metadata
        self._oauth_states[state] = {
            'created_at': datetime.utcnow(),
            'redirect_uri': redirect_uri,
            'business_name': business_name
        }
        
        # Instagram OAuth scopes
        scopes = [
            'instagram_basic',
            'instagram_manage_messages',
            'pages_messaging',
            'pages_show_list'
        ]
        
        # Build authorization URL
        auth_params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
            'state': state
        }
        
        auth_url = "https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([
            f"{key}={requests.utils.quote(str(value))}" 
            for key, value in auth_params.items()
        ])
        
        logger.info(f"Generated Instagram OAuth URL for business: {business_name}")
        return auth_url, state
    
    def exchange_code_for_token(self, code: str, state: str, redirect_uri: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        
        # Verify state parameter
        if state not in self._oauth_states:
            logger.error(f"Invalid OAuth state: {state}")
            return None
        
        state_data = self._oauth_states[state]
        
        # Check state expiration (15 minutes)
        if datetime.utcnow() - state_data['created_at'] > timedelta(minutes=15):
            logger.error(f"Expired OAuth state: {state}")
            del self._oauth_states[state]
            return None
        
        # Exchange code for token
        try:
            token_url = f"{self.base_url}/oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': redirect_uri,
                'code': code
            }
            
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            
            if 'access_token' not in token_info:
                logger.error(f"No access token in response: {token_info}")
                return None
            
            # Get long-lived token
            long_lived_token = self._get_long_lived_token(token_info['access_token'])
            if not long_lived_token:
                logger.error("Failed to get long-lived token")
                return None
            
            # Get user Instagram accounts
            instagram_accounts = self._get_instagram_accounts(long_lived_token['access_token'])
            if not instagram_accounts:
                logger.error("No Instagram accounts found")
                return None
            
            # Cleanup state
            del self._oauth_states[state]
            
            # Return complete authentication data
            auth_data = {
                'access_token': long_lived_token['access_token'],
                'expires_in': long_lived_token.get('expires_in', 3600),
                'token_type': long_lived_token.get('token_type', 'bearer'),
                'instagram_accounts': instagram_accounts,
                'business_name': state_data.get('business_name', ''),
                'authenticated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Instagram OAuth successful for {len(instagram_accounts)} accounts")
            return auth_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code for token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            return None
    
    def _get_long_lived_token(self, short_lived_token: str) -> Optional[Dict]:
        """Exchange short-lived token for long-lived token"""
        try:
            url = f"{self.base_url}/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_lived_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get long-lived token: {e}")
            return None
    
    def _get_instagram_accounts(self, access_token: str) -> Optional[list]:
        """Get Instagram accounts associated with the user"""
        try:
            # First get Facebook pages
            pages_url = f"{self.base_url}/me/accounts"
            params = {
                'access_token': access_token,
                'fields': 'id,name,access_token,instagram_business_account'
            }
            
            response = requests.get(pages_url, params=params)
            response.raise_for_status()
            
            pages_data = response.json()
            instagram_accounts = []
            
            for page in pages_data.get('data', []):
                if 'instagram_business_account' in page:
                    ig_account_id = page['instagram_business_account']['id']
                    
                    # Get Instagram account details
                    ig_url = f"{self.base_url}/{ig_account_id}"
                    ig_params = {
                        'access_token': page['access_token'],
                        'fields': 'id,username,name,profile_picture_url,followers_count,media_count'
                    }
                    
                    ig_response = requests.get(ig_url, params=ig_params)
                    if ig_response.status_code == 200:
                        ig_data = ig_response.json()
                        
                        instagram_accounts.append({
                            'id': ig_data['id'],
                            'username': ig_data.get('username'),
                            'name': ig_data.get('name'),
                            'profile_picture_url': ig_data.get('profile_picture_url'),
                            'followers_count': ig_data.get('followers_count'),
                            'media_count': ig_data.get('media_count'),
                            'page_id': page['id'],
                            'page_name': page['name'],
                            'page_access_token': page['access_token']
                        })
            
            return instagram_accounts
            
        except Exception as e:
            logger.error(f"Failed to get Instagram accounts: {e}")
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
            'exp': datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
            'iat': datetime.utcnow(),
            'iss': 'ig-shop-agent'
        }
        
        secret_key = get_secret('jwt-secret-key') or settings.jwt_secret_key
        return jwt.encode(payload, secret_key, algorithm=settings.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            secret_key = get_secret('jwt-secret-key') or settings.jwt_secret_key
            payload = jwt.decode(token, secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

# Global Instagram OAuth instance
instagram_oauth = InstagramOAuth()

def get_instagram_auth_url(redirect_uri: str, business_name: str = "") -> Tuple[str, str]:
    """Get Instagram authorization URL"""
    return instagram_oauth.get_authorization_url(redirect_uri, business_name)

def handle_oauth_callback(code: str, state: str, redirect_uri: str) -> Optional[Dict]:
    """Handle OAuth callback and return authentication data"""
    return instagram_oauth.exchange_code_for_token(code, state, redirect_uri)

def validate_instagram_token(access_token: str) -> bool:
    """Validate Instagram access token"""
    return instagram_oauth.validate_token(access_token)

def generate_session_token(user_data: Dict, tenant_id: str) -> str:
    """Generate session JWT token"""
    return instagram_oauth.generate_jwt_token(user_data, tenant_id)

def verify_session_token(token: str) -> Optional[Dict]:
    """Verify session JWT token"""
    return instagram_oauth.verify_jwt_token(token) 