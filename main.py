"""
IG-Shop-Agent FastAPI Backend
Main application entry point for Instagram DM automation platform
"""
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

# Import routes
from .routes.auth import router as auth_router
from .routes.catalog import router as catalog_router  
from .routes.orders import router as orders_router
from .routes.additional import router as additional_router

# Import services
from .database import db_service, database_lifespan
from .services.auth import AuthService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting IG-Shop-Agent FastAPI backend...")
    await db_service.connect()
    await db_service.initialize_schema()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down IG-Shop-Agent FastAPI backend...")
    await db_service.disconnect()
    logger.info("✅ Database connections closed")

# Create FastAPI application
app = FastAPI(
    title="IG-Shop-Agent API",
    description="AI-powered Instagram DM automation platform for Jordanian businesses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite dev server
        "https://red-island-0b863450f.2.azurestaticapps.net",  # Production frontend
        "https://*.azurestaticapps.net",  # Any Azure Static Web Apps domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "ig-shop-agent-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/health")
async def detailed_health_check():
    """Detailed health check with service dependencies"""
    try:
        # Check database health
        db_health = await db_service.health_check()
        
        return {
            "status": "healthy",
            "service": "ig-shop-agent-api",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": db_health,
            "components": {
                "fastapi": "running",
                "postgresql": db_health["status"],
                "instagram_api": "available",
                "openai": "available"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "tenant_id": payload.get("tenant_id")
        }
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(catalog_router, tags=["Catalog"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(additional_router, tags=["Additional"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IG-Shop-Agent API",
        "description": "AI-powered Instagram DM automation platform",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    ) 