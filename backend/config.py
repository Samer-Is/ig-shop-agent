"""
IG-Shop-Agent Configuration Module
Environment variables and settings management - Simplified without pydantic-settings
"""
# Configuration settings for the Instagram AI Agent SaaS platform
# Updated to trigger deployment after fixing root requirements.txt FastAPI issue

import os
from typing import Optional

class Settings:
    """Simple settings class using environment variables"""
    
    def __init__(self):
        # Environment
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        # API Configuration
        self.API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT: int = int(os.getenv("API_PORT", "8000"))
        
        # Frontend URL (for CORS and redirects)
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://red-island-0b863450f.2.azurestaticapps.net")
        
        # Database Configuration (PostgreSQL)
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/igshop")
        self.DATABASE_HOST: str = os.getenv("DATABASE_HOST", "igshop-postgres.postgres.database.azure.com")
        self.DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
        self.DATABASE_NAME: str = os.getenv("DATABASE_NAME", "igshop_db")
        self.DATABASE_USER: str = os.getenv("DATABASE_USER", "igshop_admin")
        self.DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
        
        # JWT Configuration
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("JWT_SECRET_KEY", ""))
        self.JWT_ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
        
        # Meta/Instagram OAuth Settings
        self.META_APP_ID: str = os.getenv("META_APP_ID", "")
        self.META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
        self.META_GRAPH_API_VERSION: str = "v18.0"
        self.META_REDIRECT_URI: str = os.getenv("META_REDIRECT_URI", "https://red-island-0b863450f.2.azurestaticapps.net/login")
        
        # OpenAI Configuration
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_API_VERSION: str = "2023-05-15"
        self.OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
        self.OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-ada-002"
        
        # Azure OpenAI Configuration (for production)
        self.AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt4o")
        self.AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Azure Key Vault Configuration
        self.AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")
        self.AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
        self.AZURE_CLIENT_SECRET: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")
        self.AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
        
        # Redis Configuration (for caching and sessions)
        self.REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
        self.REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
        
        # File Storage Configuration
        self.STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, azure_blob
        self.AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "igshop-files")
        self.LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./storage")
        
        # Application Configuration
        self.MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
        self.ALLOWED_FILE_TYPES: list = ["pdf", "txt", "md", "doc", "docx", "csv", "yaml", "yml"]
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # CORS Configuration
        self.CORS_ORIGINS: list = [
            "https://red-island-0b863450f.2.azurestaticapps.net",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @property
    def database_url_async(self) -> str:
        """Get the async database URL for asyncpg"""
        if self.DATABASE_URL:
            # Replace postgresql:// with postgresql+asyncpg://
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        # Build from components
        password_part = f":{self.DATABASE_PASSWORD}" if self.DATABASE_PASSWORD else ""
        return f"postgresql+asyncpg://{self.DATABASE_USER}{password_part}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def database_url_sync(self) -> str:
        """Get the sync database URL for psycopg2"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Build from components
        password_part = f":{self.DATABASE_PASSWORD}" if self.DATABASE_PASSWORD else ""
        return f"postgresql://{self.DATABASE_USER}{password_part}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def use_azure_openai(self) -> bool:
        """Check if Azure OpenAI should be used"""
        return bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_API_KEY)

# Create global settings instance
settings = Settings()

# Export for convenience
__all__ = ["settings", "Settings"] 