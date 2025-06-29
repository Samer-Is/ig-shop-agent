import aiohttp
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from datetime import datetime, timedelta
from ..config import settings

class InstagramService:
    """Service for Instagram OAuth and API interactions"""
    
    def __init__(self):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.graph_api_url = settings.META_GRAPH_API_URL
        self.oauth_url = settings.INSTAGRAM_OAUTH_URL
        self.token_url = settings.INSTAGRAM_TOKEN_URL
    
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Instagram OAuth authorization URL"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }
        
        return f"{self.oauth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
                'code': code
            }
            
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Token exchange failed: {error_text}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Instagram API"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.graph_api_url}/me"
            params = {
                'fields': 'id,username,account_type',
                'access_token': access_token
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    user_data = await response.json()
                    # Add display name if not present
                    if 'name' not in user_data:
                        user_data['name'] = user_data.get('username', 'Unknown')
                    return user_data
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get user info: {error_text}")
    
    async def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived token"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.graph_api_url}/oauth/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.app_secret,
                'access_token': short_lived_token
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get long-lived token: {error_text}")
    
    async def create_or_update_tenant(
        self, 
        db, 
        instagram_id: str, 
        username: str, 
        display_name: str,
        access_token: str,
        expires_in: int = 3600
    ) -> str:
        """Create or update tenant in database"""
        
        # Check if tenant already exists
        existing_tenant = await db.fetchrow(
            "SELECT id FROM tenants WHERE instagram_handle = $1",
            username
        )
        
        if existing_tenant:
            tenant_id = existing_tenant['id']
            
            # Update tenant info
            await db.execute(
                "UPDATE tenants SET display_name = $1 WHERE id = $2",
                display_name, tenant_id
            )
        else:
            # Create new tenant
            tenant_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO tenants (id, instagram_handle, display_name, plan, status) 
                VALUES ($1, $2, $3, $4, $5)
                """,
                tenant_id, username, display_name, 'starter', 'trial'
            )
            
            # Create default user
            user_id = str(uuid.uuid4())
            await db.execute(
                """
                INSERT INTO users (id, tenant_id, email, role) 
                VALUES ($1, $2, $3, $4)
                """,
                user_id, tenant_id, f"{username}@instagram.com", 'admin'
            )
        
        # Store/update access token
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        await db.execute(
            """
            INSERT INTO meta_tokens (tenant_id, access_token, expires_at) 
            VALUES ($1, $2, $3)
            ON CONFLICT (tenant_id) 
            DO UPDATE SET 
                access_token = EXCLUDED.access_token,
                expires_at = EXCLUDED.expires_at
            """,
            tenant_id, access_token, expires_at
        )
        
        return tenant_id
    
    async def get_user_media(self, access_token: str, limit: int = 25) -> Dict[str, Any]:
        """Get user's media from Instagram"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.graph_api_url}/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,timestamp',
                'limit': limit,
                'access_token': access_token
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get user media: {error_text}")
    
    async def validate_webhook(self, verify_token: str, challenge: str) -> Optional[str]:
        """Validate Instagram webhook verification"""
        # For now, we'll use a simple verification
        # In production, you should use a secure verification token
        expected_token = "instagram_webhook_verify_token"
        
        if verify_token == expected_token:
            return challenge
        return None
    
    async def handle_webhook_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming Instagram webhook message"""
        # This is a placeholder for webhook message handling
        # In production, this would process incoming Instagram messages
        # and trigger AI responses
        
        return {
            "status": "received",
            "message": "Webhook processed successfully"
        }

# Export for convenience
__all__ = ["InstagramService"] 