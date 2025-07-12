"""
IG-Shop-Agent Backend - FastAPI Application
Multi-tenant SaaS platform for Instagram DM management
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from routers import webhook, auth, catalog, conversations, orders, analytics, kb, business

# Import services
from database import init_database, close_database, get_database
from auth_middleware import AuthMiddleware
from rate_limiting_middleware import RateLimitingMiddleware
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting IG-Shop-Agent Backend...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Initialize enterprise database with RLS (if enabled)
        if getattr(settings, 'ENVIRONMENT', 'development') != 'development':
            try:
                from database_service_rls import init_enterprise_database
                await init_enterprise_database()
                logger.info("✅ Enterprise database with RLS initialized successfully")
            except Exception as e:
                logger.error(f"❌ Enterprise database initialization failed: {e}")
        else:
            logger.info("ℹ️ Enterprise database with RLS disabled in development mode")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down IG-Shop-Agent Backend...")
    await close_database()

# Create FastAPI application
app = FastAPI(
    title="IG-Shop-Agent API",
    description="Multi-tenant SaaS platform for Instagram DM management with AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (if not in development)
if getattr(settings, 'ENVIRONMENT', 'development') != 'development':
    app.add_middleware(RateLimitingMiddleware)
    logger.info("✅ Rate limiting middleware enabled")
else:
    logger.info("ℹ️ Enterprise rate limiting middleware disabled in development mode")

# Add authentication middleware (if not in development)
if getattr(settings, 'ENVIRONMENT', 'development') != 'development':
    app.add_middleware(AuthMiddleware, secret_key=settings.SECRET_KEY)
    logger.info("✅ Authentication middleware enabled")
else:
    logger.info("ℹ️ Authentication middleware disabled in development mode")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = await get_database()
        health_status = await db.health_check()
        return {
            "status": "healthy",
            "service": "ig-shop-agent-backend",
            "database": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "ig-shop-agent-backend",
                "error": str(e)
            }
        )

# Include routers
app.include_router(webhook.router, tags=["webhooks"])
logger.info("✅ Webhook router included successfully")

app.include_router(auth.router, tags=["authentication"])
app.include_router(catalog.router, tags=["catalog"])
app.include_router(conversations.router, tags=["conversations"])
app.include_router(orders.router, tags=["orders"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(kb.router, tags=["knowledge-base"])
app.include_router(business.router, tags=["business"])
logger.info("✅ Original API routers included successfully")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    ) 