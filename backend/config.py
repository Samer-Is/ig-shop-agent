"""
IG-Shop-Agent Configuration Module
Environment variables and settings management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Frontend URL (for CORS and redirects)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://red-island-0b863450f.2.azurestaticapps.net")
    
    # Database Configuration (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/igshop"
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "igshop-postgres.postgres.database.azure.com")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "igshop_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "igshop_admin")
    DATABASE_PASSWORD: Optional[str] = os.getenv("DATABASE_PASSWORD")
    
    # JWT Configuration
    JWT_SECRET: str = "your-secret-key-here"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Meta/Instagram OAuth Settings
    META_APP_ID: str = "1879578119651644"
    META_APP_SECRET: str = "f79b3350f43751d6139e1b29a232cbf3"
    META_GRAPH_API_VERSION: str = "v18.0"
    META_REDIRECT_URI: str = "https://red-island-0b863450f.2.azurestaticapps.net/auth/callback"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = "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"
    OPENAI_API_VERSION: str = "2023-05-15"
    OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-ada-002"
    
    # Azure OpenAI Configuration (for production)
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Azure Key Vault Configuration
    AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    
    # Redis Configuration (for caching and sessions)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # File Storage Configuration
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, azure_blob
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "igshop-files")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "./storage")
    
    # Application Configuration
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES: list = ["pdf", "txt", "md", "doc", "docx", "csv", "yaml", "yml"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]  # Update with actual frontend domain in production
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

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