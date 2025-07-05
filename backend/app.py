"""
FastAPI Backend Application for IG-Shop-Agent
Multi-tenant Instagram DM management system
"""
# Updated to trigger deployment with fixed workflow (no nuclear option)
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import os
import logging
from contextlib import asynccontextmanager
import sys

# Import configuration and database
from config import settings
from database import get_database, init_database

# Import routers
from routers import auth, conversations, orders, catalog, kb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting IG-Shop-Agent Backend...")
    
    # Initialize database
    try:
        await init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Don't fail startup - let the app run and handle DB errors gracefully
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down IG-Shop-Agent Backend...")

# Create FastAPI application
app = FastAPI(
    title="IG-Shop-Agent API",
    description="Multi-tenant Instagram DM management system with AI-powered conversations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to import settings
        try:
            from config import settings
            environment = settings.ENVIRONMENT
        except Exception as e:
            environment = "unknown"
            logger.warning(f"Could not import settings: {e}")
        
        # Try to check Instagram OAuth status
        oauth_status = "unknown"
        oauth_message = "Could not check OAuth status"
        try:
            from instagram_oauth import instagram_oauth
            oauth_status = "configured" if hasattr(instagram_oauth, 'is_configured') and instagram_oauth.is_configured else "not_configured"
            oauth_message = "Instagram OAuth not configured - please set META_APP_ID and META_APP_SECRET" if oauth_status == "not_configured" else "All services operational"
        except Exception as e:
            logger.warning(f"Could not check Instagram OAuth status: {e}")
            oauth_message = f"OAuth check failed: {str(e)}"
        
        return {
            "status": "healthy",
            "service": "ig-shop-agent-backend",
            "version": "1.0.0",
            "environment": environment,
            "instagram_oauth": oauth_status,
            "message": oauth_message
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "service": "ig-shop-agent-backend",
            "version": "1.0.0",
            "error": str(e),
            "message": "Health check encountered errors but service may still be functional"
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    try:
        return {
            "message": "IG-Shop-Agent Backend API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "debug": "/debug/filesystem",
                "auth": "/auth/instagram/login"
            }
        }
    except Exception as e:
        return {
            "message": "IG-Shop-Agent Backend API",
            "status": "error",
            "error": str(e)
        }

# Debug endpoint to check file system
@app.get("/debug/filesystem")
async def debug_filesystem():
    """Debug endpoint to check file system structure"""
    try:
        import os
        from pathlib import Path
        
        current_dir = Path.cwd()
        parent_dir = current_dir.parent
        
        # Safely get directory contents
        try:
            current_dir_contents = [str(item) for item in current_dir.iterdir()]
        except Exception as e:
            current_dir_contents = [f"Error reading directory: {e}"]
        
        try:
            parent_dir_contents = [str(item) for item in parent_dir.iterdir()] if parent_dir.exists() else []
        except Exception as e:
            parent_dir_contents = [f"Error reading parent directory: {e}"]
        
        return {
            "current_working_directory": str(current_dir),
            "parent_directory": str(parent_dir),
            "current_dir_contents": current_dir_contents,
            "parent_dir_contents": parent_dir_contents,
            "python_path": os.environ.get("PYTHONPATH", ""),
            "environment_vars": {
                "PORT": os.environ.get("PORT", ""),
                "ENVIRONMENT": os.environ.get("ENVIRONMENT", ""),
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                "META_APP_ID": "***" if os.environ.get("META_APP_ID") else "not_set",
                "META_APP_SECRET": "***" if os.environ.get("META_APP_SECRET") else "not_set"
            }
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint failed: {e}")
        return {
            "error": str(e),
            "message": "Debug endpoint encountered an error",
            "basic_info": {
                "working_directory": str(Path.cwd()) if Path else "unknown",
                "python_executable": sys.executable if sys else "unknown"
            }
        }

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(catalog.router, prefix="/catalog", tags=["Catalog"])
app.include_router(kb.router, prefix="/kb", tags=["Knowledge Base"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    ) 