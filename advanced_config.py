"""
Advanced Configuration for 100% Production Readiness
IG-Shop-Agent: Complete Enterprise SaaS Platform
"""

import os
import logging
from typing import Dict, Any
from datetime import timedelta

class ProductionConfig:
    """100% Production-ready configuration"""
    
    # Azure OpenAI Configuration (Upgrade from basic OpenAI)
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_API_VERSION = "2023-12-01-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"
    
    # Enhanced Security Settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SESSION_TIMEOUT = timedelta(hours=2)
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    
    # Rate Limiting
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL', '')
    DEFAULT_RATE_LIMIT = "100 per hour"
    API_RATE_LIMIT = "1000 per hour"
    AUTH_RATE_LIMIT = "5 per minute"
    
    # Monitoring & Logging
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ENABLE_STRUCTURED_LOGGING = True
    LOG_TO_AZURE_MONITOR = True
    
    # Performance Settings
    ENABLE_CACHING = True
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_LONG_TIMEOUT = 3600   # 1 hour
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 10
    
    # Instagram API Enhancements
    INSTAGRAM_WEBHOOK_VERIFY_TOKEN = os.environ.get('INSTAGRAM_WEBHOOK_VERIFY_TOKEN', 'your-verify-token')
    INSTAGRAM_WEBHOOK_SECRET = os.environ.get('INSTAGRAM_WEBHOOK_SECRET', '')
    WEBHOOK_TIMEOUT = 10  # seconds
    
    # AI Response Configuration
    AI_RESPONSE_MAX_TOKENS = 150
    AI_TEMPERATURE = 0.7
    AI_CONTEXT_WINDOW = 10  # Number of previous messages to include
    AI_FALLBACK_RESPONSES = [
        "أعتذر، أواجه مشكلة تقنية مؤقتة. يرجى المحاولة مرة أخرى.",
        "Sorry, I'm experiencing a temporary issue. Please try again.",
    ]
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
    UPLOAD_FOLDER = 'uploads'
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    
    # Business Settings
    DEFAULT_CURRENCY = "JOD"
    SUPPORTED_LANGUAGES = ["ar", "en"]
    DEFAULT_LANGUAGE = "ar"
    TIMEZONE = "Asia/Amman"
    
    @classmethod
    def get_azure_openai_config(cls) -> Dict[str, Any]:
        """Get Azure OpenAI configuration"""
        return {
            'api_type': 'azure',
            'api_base': cls.AZURE_OPENAI_ENDPOINT,
            'api_key': cls.AZURE_OPENAI_API_KEY,
            'api_version': cls.AZURE_OPENAI_API_VERSION,
            'deployment_name': cls.AZURE_OPENAI_DEPLOYMENT_NAME
        }
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get production CORS configuration"""
        return {
            'origins': [
                'https://*.azurewebsites.net',
                'https://*.azurestaticapps.net',
                'https://igshop-agent.com',  # Custom domain
                'https://www.igshop-agent.com'
            ],
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
            'expose_headers': ['X-Total-Count'],
            'supports_credentials': True,
            'max_age': 600
        }
    
    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get security headers for production"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }

class HealthCheckConfig:
    """Health check endpoints configuration"""
    
    HEALTH_CHECKS = {
        'database': {
            'timeout': 5,
            'critical': True
        },
        'openai': {
            'timeout': 10,
            'critical': False
        },
        'instagram': {
            'timeout': 5,
            'critical': False
        },
        'storage': {
            'timeout': 3,
            'critical': False
        }
    }

class MonitoringConfig:
    """Monitoring and alerts configuration"""
    
    # Azure Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING', '')
    
    # Custom metrics
    TRACK_CUSTOM_EVENTS = True
    TRACK_DEPENDENCIES = True
    TRACK_REQUESTS = True
    TRACK_EXCEPTIONS = True
    
    # Performance thresholds
    RESPONSE_TIME_THRESHOLD = 2.0  # seconds
    ERROR_RATE_THRESHOLD = 0.05    # 5%
    CPU_THRESHOLD = 80             # percent
    MEMORY_THRESHOLD = 85          # percent

# Environment-specific configurations
ENVIRONMENTS = {
    'production': ProductionConfig,
    'staging': ProductionConfig,  # Same as production for now
    'development': ProductionConfig  # Simplified for development
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('ENVIRONMENT', 'production')
    return ENVIRONMENTS.get(env, ProductionConfig) 