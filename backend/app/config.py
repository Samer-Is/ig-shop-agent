"""
Configuration management for IG-Shop-Agent FastAPI backend.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class Settings(BaseSettings):
    """Application settings with Azure Key Vault integration."""
    
    # Basic app settings
    app_name: str = "IG Shop Agent API"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: Optional[str] = None
    
    # Azure Services
    azure_key_vault_url: Optional[str] = None
    azure_storage_connection_string: Optional[str] = None
    azure_servicebus_connection_string: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_search_endpoint: Optional[str] = None
    azure_search_api_key: Optional[str] = None
    applicationinsights_connection_string: Optional[str] = None
    
    # Instagram/Meta API
    meta_app_id: Optional[str] = None
    meta_app_secret: Optional[str] = None
    meta_webhook_verify_token: Optional[str] = None
    
    # AI Configuration
    gpt_model_name: str = "gpt-4o"
    embedding_model_name: str = "text-embedding-3-small"
    max_conversation_memory: int = 20
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Licensing
    ed25519_public_key: Optional[str] = None
    license_file_path: str = "whitelist.sig"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets_from_keyvault()
    
    def _load_secrets_from_keyvault(self):
        """Load secrets from Azure Key Vault if available."""
        if not self.azure_key_vault_url:
            return
            
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=self.azure_key_vault_url, credential=credential)
            
            # Map of secret names to settings attributes
            secret_mappings = {
                "postgres-connection-string": "database_url",
                "servicebus-connection-string": "azure_servicebus_connection_string",
                "storage-connection-string": "azure_storage_connection_string",
                "openai-endpoint": "azure_openai_endpoint",
                "openai-api-key": "azure_openai_api_key",
                "search-endpoint": "azure_search_endpoint",
                "search-api-key": "azure_search_api_key",
                "appinsights-connection-string": "applicationinsights_connection_string",
                "meta-app-id": "meta_app_id",
                "meta-app-secret": "meta_app_secret",
                "meta-webhook-verify-token": "meta_webhook_verify_token",
                "secret-key": "secret_key",
                "ed25519-public-key": "ed25519_public_key",
            }
            
            for secret_name, attr_name in secret_mappings.items():
                try:
                    secret = client.get_secret(secret_name)
                    setattr(self, attr_name, secret.value)
                except Exception as e:
                    print(f"Warning: Could not load secret {secret_name}: {e}")
                    
        except Exception as e:
            print(f"Warning: Could not connect to Key Vault: {e}")


# Global settings instance
settings = Settings()
