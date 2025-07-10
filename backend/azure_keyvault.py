"""
IG-Shop-Agent Azure Key Vault Integration
Secure secrets management for production environments
"""
import os
import logging
from typing import Optional, Dict, Any
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)

class KeyVaultManager:
    """Azure Key Vault secrets manager"""
    
    def __init__(self):
        self.client: Optional[SecretClient] = None
        self.vault_url = os.getenv('AZURE_KEY_VAULT_URL')
        self._secrets_cache: Dict[str, str] = {}
        
    def initialize(self) -> bool:
        """Initialize Key Vault client"""
        if not self.vault_url:
            logger.info("Azure Key Vault URL not configured, using environment variables")
            return False
            
        try:
            # Try multiple authentication methods
            credential = None
            
            # Method 1: Managed Identity (preferred for Azure)
            try:
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for Key Vault authentication")
            except Exception as e:
                logger.warning(f"DefaultAzureCredential failed: {e}")
            
            # Method 2: Service Principal (for local development)
            if not credential:
                client_id = os.getenv('AZURE_CLIENT_ID')
                client_secret = os.getenv('AZURE_CLIENT_SECRET')
                tenant_id = os.getenv('AZURE_TENANT_ID')
                
                if client_id and client_secret and tenant_id:
                    credential = ClientSecretCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret
                    )
                    logger.info("Using ClientSecretCredential for Key Vault authentication")
                else:
                    logger.warning("Azure service principal credentials not found")
                    return False
            
            self.client = SecretClient(vault_url=self.vault_url, credential=credential)
            
            # Test connection
            try:
                # Try to access a dummy secret to verify connection
                self.client.get_secret("connection-test")
            except Exception:
                pass  # It's OK if the secret doesn't exist
                
            logger.info("Azure Key Vault client initialized successfully")
            return True
            
        except AzureError as e:
            logger.error(f"Failed to initialize Azure Key Vault: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error initializing Key Vault: {e}")
            return False
    
    def get_secret(self, secret_name: str, default_value: Optional[str] = None) -> Optional[str]:
        """Get secret from Key Vault with fallback to environment variables"""
        
        # Check cache first
        if secret_name in self._secrets_cache:
            return self._secrets_cache[secret_name]
        
        # Try Key Vault if available
        if self.client:
            try:
                secret = self.client.get_secret(secret_name)
                value = secret.value
                self._secrets_cache[secret_name] = value
                logger.debug(f"Retrieved secret '{secret_name}' from Key Vault")
                return value
            except Exception as e:
                logger.warning(f"Failed to get secret '{secret_name}' from Key Vault: {e}")
        
        # Fallback to environment variables
        env_value = os.getenv(secret_name.upper().replace('-', '_'))
        if env_value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment variables")
            return env_value
        
        # Return default if provided
        if default_value is not None:
            logger.debug(f"Using default value for secret '{secret_name}'")
            return default_value
        
        logger.warning(f"Secret '{secret_name}' not found in Key Vault or environment")
        return None
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Key Vault"""
        if not self.client:
            logger.error("Key Vault client not initialized")
            return False
        
        try:
            self.client.set_secret(secret_name, secret_value)
            # Update cache
            self._secrets_cache[secret_name] = secret_value
            logger.info(f"Secret '{secret_name}' set in Key Vault")
            return True
        except Exception as e:
            logger.error(f"Failed to set secret '{secret_name}' in Key Vault: {e}")
            return False
    
    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Key Vault"""
        if not self.client:
            logger.error("Key Vault client not initialized")
            return False
        
        try:
            self.client.begin_delete_secret(secret_name)
            # Remove from cache
            self._secrets_cache.pop(secret_name, None)
            logger.info(f"Secret '{secret_name}' deleted from Key Vault")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_name}' from Key Vault: {e}")
            return False
    
    def list_secrets(self) -> list:
        """List all secrets in Key Vault"""
        if not self.client:
            logger.error("Key Vault client not initialized")
            return []
        
        try:
            secrets = []
            for secret_properties in self.client.list_properties_of_secrets():
                secrets.append({
                    'name': secret_properties.name,
                    'enabled': secret_properties.enabled,
                    'created_on': secret_properties.created_on,
                    'updated_on': secret_properties.updated_on
                })
            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets in Key Vault: {e}")
            return []

# Global Key Vault manager instance
keyvault = KeyVaultManager()

def init_keyvault() -> bool:
    """Initialize Key Vault - call this on startup"""
    return keyvault.initialize()

def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret with Key Vault fallback to environment variables"""
    return keyvault.get_secret(secret_name, default)

def get_database_url() -> str:
    """Get database URL from Key Vault or environment"""
    return get_secret('database-url') or get_secret('DATABASE_URL') or ''

def get_openai_api_key() -> str:
    """Get OpenAI API key from Key Vault or environment"""
    return get_secret('openai-api-key') or get_secret('OPENAI_API_KEY') or ''

def get_meta_app_secret() -> str:
    """Get Meta app secret from Key Vault or environment"""
    return get_secret('meta-app-secret') or get_secret('META_APP_SECRET') or ''

def get_jwt_secret() -> str:
    """Get JWT secret from Key Vault or environment"""
    return get_secret('jwt-secret-key') or get_secret('JWT_SECRET_KEY') or ''

def get_instagram_config() -> Dict[str, str]:
    """Get Instagram configuration from Key Vault or environment"""
    return {
        'app_id': get_secret('meta-app-id') or get_secret('META_APP_ID') or '',
        'app_secret': get_meta_app_secret(),
        'webhook_verify_token': get_secret('meta-webhook-verify-token') or get_secret('META_WEBHOOK_VERIFY_TOKEN') or '',
        'graph_api_version': get_secret('meta-graph-api-version') or get_secret('META_GRAPH_API_VERSION') or 'v18.0'
    }

def setup_production_secrets():
    """Set up secrets in Key Vault for production deployment"""
    if not keyvault.client:
        logger.error("Key Vault not initialized - cannot set up production secrets")
        return False
    
    # List of secrets that should be in Key Vault for production
    production_secrets = [
        'database-url',
        'openai-api-key',
        'meta-app-id',
        'meta-app-secret',
        'meta-webhook-verify-token',
        'jwt-secret-key'
    ]
    
    missing_secrets = []
    for secret_name in production_secrets:
        value = keyvault.get_secret(secret_name)
        if not value:
            missing_secrets.append(secret_name)
    
    if missing_secrets:
        logger.warning(f"Missing production secrets in Key Vault: {missing_secrets}")
        return False
    
    logger.info("All production secrets are configured in Key Vault")
    return True 