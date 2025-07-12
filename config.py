"""
Configuration module for IG-Shop-Agent
Loads environment variables and provides application settings
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (with override for Azure)
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Database Configuration
        self.DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
        self.DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
        self.DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "igshop_db")
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # Instagram OAuth
        self.INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
        self.INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
        self.INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", "")
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
        
        # Azure Services
        self.AZURE_KEY_VAULT_URL = os.getenv("AZURE_KEY_VAULT_URL", "")
        self.AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
        self.AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
        self.AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
        
        # Azure Speech Service
        self.AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
        self.AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "")
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate critical settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical configuration settings"""
        if self.ENVIRONMENT == "production":
            required_settings = [
                ("DATABASE_HOST", self.DATABASE_HOST),
                ("DATABASE_PASSWORD", self.DATABASE_PASSWORD),
                ("SECRET_KEY", self.SECRET_KEY),
                ("OPENAI_API_KEY", self.OPENAI_API_KEY),
            ]
            
            missing_settings = [name for name, value in required_settings if not value]
            
            if missing_settings:
                logger.error(f"Missing required production settings: {missing_settings}")
                raise ValueError(f"Missing required production settings: {missing_settings}")
        
        logger.info(f"✅ Configuration loaded for environment: {self.ENVIRONMENT}")
    
    def get_database_url(self) -> str:
        """Get the database connection URL"""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

# Global settings instance
settings = Settings()

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 