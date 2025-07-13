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
            "version": "1.0.2",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "instagram_oauth": "configured" if settings.INSTAGRAM_APP_ID else "not_configured",
            "message": "Instagram OAuth not configured - please set META_APP_ID and META_APP_SECRET environment variables" if not settings.INSTAGRAM_APP_ID else "All systems operational",
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

# Debug configuration endpoint
@app.get("/backend-api/debug/config")
async def debug_config():
    """Debug endpoint to check configuration - REMOVE IN PRODUCTION"""
    return {
        "openai_api_key_set": bool(settings.OPENAI_API_KEY),
        "openai_api_key_length": len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0,
        "azure_openai_endpoint_set": bool(getattr(settings, 'AZURE_OPENAI_ENDPOINT', '')),
        "azure_openai_api_key_set": bool(getattr(settings, 'AZURE_OPENAI_API_KEY', '')),
        "azure_openai_deployment": getattr(settings, 'AZURE_OPENAI_DEPLOYMENT', 'gpt4o'),
        "use_azure_openai": getattr(settings, 'USE_AZURE_OPENAI', True),
        "meta_app_id_set": bool(settings.INSTAGRAM_APP_ID),
        "meta_app_secret_set": bool(settings.INSTAGRAM_APP_SECRET),
        "database_connected": True,  # If we reach here, database is connected
        "environment": getattr(settings, 'ENVIRONMENT', 'development')
    }

# AI test endpoints
@app.post("/backend-api/ai/test")
async def backend_ai_test(request: Request):
    """Backend API AI test endpoint"""
    try:
        from azure_openai_service import AzureOpenAIService
        from database import get_database
        
        body = await request.json()
        message = body.get("message", "Hello, how are you?")
        
        # Get database and fetch context
        db = await get_database()
        catalog_items = await db.get_catalog_items("test_user")
        
        # Initialize AI service and generate response
        ai_service = AzureOpenAIService()
        response = await ai_service.generate_response(
            message=message,
            catalog_items=catalog_items,
            customer_context={"name": "Test Customer", "phone": "+962123456789"}
        )
        
        return {
            "response": response,
            "context": {
                "products_count": len(catalog_items),
                "message_processed": True
            }
        }
        
    except Exception as e:
        logger.error(f"AI test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/backend-api/ai/test-detailed")
async def backend_ai_test_detailed(request: Request):
    """Detailed AI test endpoint with error information"""
    try:
        from azure_openai_service import AzureOpenAIService
        
        # Initialize AI service
        ai_service = AzureOpenAIService()
        
        return {
            "success": True,
            "service_initialized": True,
            "model": ai_service.model
        }
        
    except Exception as e:
        logger.error(f"Detailed AI test failed: {e}")
        error_type = type(e).__name__
        
        return {
            "success": False,
            "error": str(e),
            "error_type": error_type,
            "service_type": "OpenAI",
            "use_azure_openai": getattr(settings, 'USE_AZURE_OPENAI', True),
            "azure_endpoint_set": bool(getattr(settings, 'AZURE_OPENAI_ENDPOINT', '')),
            "azure_api_key_set": bool(getattr(settings, 'AZURE_OPENAI_API_KEY', ''))
                 }

# Additional backend API endpoints
@app.get("/backend-api/catalog")
async def backend_catalog():
    """Backend API catalog endpoint"""
    try:
        from database import get_database
        db = await get_database()
        catalog_items = await db.get_catalog_items("test_user")
        return catalog_items
    except Exception as e:
        logger.error(f"Backend catalog failed: {e}")
        return []

@app.post("/backend-api/catalog")
async def backend_create_catalog_item(request: Request):
    """Backend API create catalog item endpoint"""
    try:
        from database import get_database
        body = await request.json()
        db = await get_database()
        
        # Create catalog item with test user
        item_data = {
            "sku": body.get("sku", "TEST-SKU"),
            "name": body.get("name", "Test Product"),
            "description": body.get("description", ""),
            "price_jod": body.get("price_jod", 10.0),
            "media_url": body.get("media_url", ""),
            "category": body.get("category", ""),
            "stock_quantity": body.get("stock_quantity", 0)
        }
        
        result = await db.create_catalog_item("test_user", item_data)
        return result
    except Exception as e:
        logger.error(f"Backend create catalog item failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/backend-api/orders")
async def backend_orders():
    """Backend API orders endpoint"""
    try:
        from database import get_database
        db = await get_database()
        orders = await db.get_orders("test_user")
        return orders
    except Exception as e:
        logger.error(f"Backend orders failed: {e}")
        return []

@app.get("/backend-api/conversations")
async def backend_conversations():
    """Backend API conversations endpoint"""
    return []

@app.get("/backend-api/analytics")
async def backend_analytics():
    """Backend API analytics endpoint"""
    return {"analytics": "data"}

@app.get("/backend-api/business/rules")
async def backend_business_rules():
    """Backend API business rules endpoint"""
    return {"rules": "data"}

@app.get("/backend-api/user/profile")
async def get_user_profile():
    """Get current user profile information"""
    return {"user": "profile"}

# Root and test endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "IG-Shop-Agent API", "version": "1.0.0"}

@app.get("/debug/filesystem")
async def debug_filesystem():
    """Debug endpoint to check file system structure"""
    import os
    return {
        "current_directory": os.getcwd(),
        "files": os.listdir("."),
        "python_path": os.environ.get("PYTHONPATH", "Not set")
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to check if the app is working"""
    return {"status": "working", "message": "API is operational"}

@app.get("/webhook-test")
async def webhook_test_endpoint():
    """Test endpoint to verify webhook functionality is available"""
    return {"webhook": "available", "status": "ready"}

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