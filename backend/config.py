"""
IG-Shop-Agent Configuration Module
Environment variables and settings management
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database Configuration
    database_url: str = Field(default='postgresql://localhost:5432/igshop', env='DATABASE_URL')
    
    # OpenAI Configuration
    openai_api_key: str = Field(default='', env='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4o', env='OPENAI_MODEL')
    openai_embedding_model: str = Field(default='text-embedding-3-small', env='OPENAI_EMBEDDING_MODEL')
    
    # Meta/Instagram Configuration
    meta_app_id: str = Field(default='', env='META_APP_ID')
    meta_app_secret: str = Field(default='', env='META_APP_SECRET')
    meta_webhook_verify_token: str = Field(default='', env='META_WEBHOOK_VERIFY_TOKEN')
    meta_graph_api_version: str = Field(default='v18.0', env='META_GRAPH_API_VERSION')
    
    # Azure Configuration
    azure_storage_connection_string: Optional[str] = Field(None, env='AZURE_STORAGE_CONNECTION_STRING')
    azure_key_vault_url: Optional[str] = Field(None, env='AZURE_KEY_VAULT_URL')
    
    # Application Configuration
    app_name: str = Field(default='IG-Shop-Agent', env='APP_NAME')
    environment: str = Field(default='development', env='ENVIRONMENT')
    debug: bool = Field(default=False, env='DEBUG')
    
    # Security Configuration
    jwt_secret_key: str = Field(default='dev-secret-key-change-in-production', env='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', env='JWT_ALGORITHM')
    jwt_expiration_hours: int = Field(default=24, env='JWT_EXPIRATION_HOURS')
    
    # Licensing Configuration
    license_public_key_path: Optional[str] = Field(None, env='LICENSE_PUBLIC_KEY_PATH')
    license_private_key_path: Optional[str] = Field(None, env='LICENSE_PRIVATE_KEY_PATH')
    
    # Performance Configuration
    max_conversation_history: int = Field(default=20, env='MAX_CONVERSATION_HISTORY')
    ai_response_timeout_seconds: int = Field(default=30, env='AI_RESPONSE_TIMEOUT_SECONDS')
    
    # Rate Limiting
    api_rate_limit_per_minute: int = Field(default=60, env='API_RATE_LIMIT_PER_MINUTE')
    instagram_api_rate_limit_per_hour: int = Field(default=200, env='INSTAGRAM_API_RATE_LIMIT_PER_HOUR')
    
    class Config:
        env_file = '.env'
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_database_url() -> str:
    """Get database URL with fallback for different environments"""
    if settings.database_url:
        return settings.database_url
    
    # Fallback for local development
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'igshop')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'password')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_instagram_oauth_config() -> dict:
    """Get Instagram OAuth configuration"""
    return {
        'app_id': settings.meta_app_id,
        'app_secret': settings.meta_app_secret,
        'redirect_uri': os.getenv('META_OAUTH_REDIRECT_URI', 'https://localhost:3000/auth/callback'),
        'scope': 'instagram_basic,instagram_manage_messages,pages_messaging',
        'webhook_verify_token': settings.meta_webhook_verify_token
    }

def get_openai_config() -> dict:
    """Get OpenAI configuration"""
    return {
        'api_key': settings.openai_api_key,
        'model': settings.openai_model,
        'embedding_model': settings.openai_embedding_model,
        'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
        'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    }

def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() in ['production', 'prod']

def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() in ['development', 'dev', 'local']

def get_cors_origins() -> list:
    """Get CORS origins based on environment"""
    if is_production():
        return [
            "https://igshop-prod-app.azurestaticapps.net",
            "https://igshop-staging-app.azurestaticapps.net"
        ]
    else:
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]

# Environment validation on import
def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = [
        'DATABASE_URL',
        'OPENAI_API_KEY', 
        'META_APP_ID',
        'META_APP_SECRET',
        'META_WEBHOOK_VERIFY_TOKEN',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate environment on module import for production
if is_production():
    validate_environment() 