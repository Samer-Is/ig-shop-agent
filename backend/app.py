# IG-Shop-Agent Backend API
# Multi-tenant Instagram DM automation platform
# 🚀 FORCE DEPLOYMENT - Backend API routing fix

import logging
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager
import sys

# Import configuration and database
from config import settings
from database import get_database, init_database

# Import routers
try:
    from routers import auth, conversations, orders, catalog, kb, webhook, analytics, business
    routers_imported = True
    import_error = None
except Exception as e:
    routers_imported = False
    import_error = str(e)
    logger.error(f"Failed to import routers: {e}")

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

# Remove duplicate router inclusions and add direct backend-api routes
if routers_imported:
    try:
        # Original /api/ routes for backward compatibility
        app.include_router(analytics.router, prefix="/api/analytics")
        app.include_router(auth.router, prefix="/api")
        app.include_router(conversations.router, prefix="/api/conversations")
        app.include_router(orders.router, prefix="/api/orders")
        app.include_router(catalog.router, prefix="/api/catalog")
        app.include_router(kb.router, prefix="/api/kb")
        app.include_router(business.router, prefix="/api")
        app.include_router(webhook.router)
        logger.info("✅ Webhook router included successfully")
        
        logger.info("✅ Original API routers included successfully")
    except Exception as e:
        logger.error(f"❌ Failed to include routers: {e}")
else:
    logger.error(f"❌ Routers not imported due to error: {import_error}")

# Direct backend-api routes to avoid Azure SWA conflicts
@app.get("/backend-api/analytics")
async def backend_analytics():
    """Backend API analytics endpoint"""
    try:
        from routers.analytics import get_analytics
        from database import get_database
        db = await get_database()
        return await get_analytics(db)
    except Exception as e:
        logger.error(f"Backend analytics error: {e}")
        return {
            "orders": {"total": 0, "revenue": 0.0, "average_value": 0.0, "pending": 0, "completed": 0},
            "catalog": {"total_products": 0, "active_products": 0, "out_of_stock": 0},
            "conversations": {"total_messages": 0, "ai_responses": 0, "customer_messages": 0},
            "recent_orders": []
        }

@app.get("/backend-api/catalog")
async def backend_catalog():
    """Backend API catalog endpoint"""
    try:
        from routers.catalog import get_catalog
        from database import get_database
        db = await get_database()
        return await get_catalog(db)
    except Exception as e:
        logger.error(f"Backend catalog error: {e}")
        return []

@app.get("/backend-api/orders")
async def backend_orders():
    """Backend API orders endpoint"""
    try:
        from routers.orders import get_orders
        from database import get_database
        db = await get_database()
        return await get_orders(db)
    except Exception as e:
        logger.error(f"Backend orders error: {e}")
        return []

@app.get("/backend-api/conversations")
async def backend_conversations():
    """Backend API conversations endpoint"""
    try:
        from routers.conversations import get_conversations
        from database import get_database
        db = await get_database()
        return await get_conversations(db)
    except Exception as e:
        logger.error(f"Backend conversations error: {e}")
        return []

@app.get("/backend-api/business/rules")
async def backend_business_rules():
    """Backend API business rules endpoint"""
    try:
        from routers.business import get_business_rules
        from database import get_database
        db = await get_database()
        return await get_business_rules(db)
    except Exception as e:
        logger.error(f"Backend business rules error: {e}")
        return {
            "business_name": None,
            "business_type": None,
            "working_hours": None,
            "delivery_info": None,
            "payment_methods": None,
            "return_policy": None,
            "terms_conditions": None,
            "contact_info": None,
            "custom_prompt": None,
            "ai_instructions": None,
            "language_preference": "en,ar",
            "response_tone": "professional"
        }

@app.get("/backend-api/debug/config")
async def debug_config():
    """Debug endpoint to check configuration - REMOVE IN PRODUCTION"""
    try:
        return {
            "openai_api_key_set": bool(settings.OPENAI_API_KEY),
            "openai_api_key_length": len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0,
            "azure_openai_endpoint_set": bool(settings.AZURE_OPENAI_ENDPOINT),
            "azure_openai_api_key_set": bool(settings.AZURE_OPENAI_API_KEY),
            "azure_openai_deployment": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            "use_azure_openai": settings.use_azure_openai,
            "meta_app_id_set": bool(settings.META_APP_ID),
            "database_url_set": bool(settings.DATABASE_URL),
            "environment": settings.ENVIRONMENT,
            "cors_origins": settings.CORS_ORIGINS[:2]  # Show only first 2 for brevity
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/backend-api/ai/test-detailed")
async def backend_ai_test_detailed(request: Request):
    """Detailed AI test endpoint with error information"""
    try:
        from azure_openai_service import AzureOpenAIService
        
        # Parse request data
        data = await request.json()
        message = data.get('message', 'Hello')
        
        logger.info(f"Testing AI with message: {message}")
        
        # Test Azure OpenAI or regular OpenAI based on configuration
        try:
            if settings.use_azure_openai:
                logger.info("Testing with Azure OpenAI")
                from openai import AzureOpenAI
                client = AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
                model = settings.AZURE_OPENAI_DEPLOYMENT_NAME
                service_type = "Azure OpenAI"
            else:
                logger.info("Testing with regular OpenAI")
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                model = "gpt-4o"
                service_type = "OpenAI"
            
            logger.info(f"Client created successfully for {service_type}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"{service_type} response received: {ai_response[:50]}...")
            
            return {
                "success": True,
                "response": ai_response,
                "service_type": service_type,
                "model_used": model,
                "use_azure_openai": settings.use_azure_openai
            }
            
        except Exception as openai_error:
            logger.error(f"AI API error: {openai_error}")
            return {
                "success": False,
                "error": str(openai_error),
                "error_type": type(openai_error).__name__,
                "service_type": "Azure OpenAI" if settings.use_azure_openai else "OpenAI",
                "use_azure_openai": settings.use_azure_openai,
                "azure_endpoint_set": bool(settings.AZURE_OPENAI_ENDPOINT),
                "azure_api_key_set": bool(settings.AZURE_OPENAI_API_KEY)
            }
        
    except Exception as e:
        logger.error(f"General error in AI test: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.post("/backend-api/ai/test")
async def backend_ai_test(request: Request):
    """Backend API AI test endpoint"""
    try:
        from azure_openai_service import AzureOpenAIService
        
        # Parse request data
        data = await request.json()
        message = data.get('message', '')
        business_rules = data.get('business_rules', {})
        products = data.get('products', [])
        knowledge_base = data.get('knowledge_base', [])
        
        if not message:
            return {"error": "Message is required"}
        
        # Initialize AI service
        ai_service = AzureOpenAIService()
        
        # Build enhanced context with knowledge base
        enhanced_context = {
            'products': products,
            'business_rules': business_rules,
            'knowledge_base': knowledge_base
        }
        
        # Generate AI response with enhanced context
        ai_response = await ai_service.generate_response(
            message=message,
            catalog_items=products,
            conversation_history=[],
            business_rules=business_rules,
            knowledge_base=knowledge_base
        )
        
        return {
            "response": ai_response,
            "context": {
                "products_count": len(products),
                "knowledge_items_count": len(knowledge_base),
                "business_rules_provided": bool(business_rules),
                "message_length": len(message)
            }
        }
        
    except Exception as e:
        logger.error(f"Backend AI test error: {e}")
        return {
            "error": str(e),
            "message": "AI test failed - check logs for details"
        }

# Instagram Webhook endpoints are now handled by the webhook router

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
            "version": "1.0.1",
            "environment": environment,
            "instagram_oauth": oauth_status,
            "message": oauth_message,
            "webhook_endpoints_available": True,
            "deployment_timestamp": str(datetime.now())
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
                "auth": "/auth/instagram/login",
                "api": {
                    "analytics": "/api/analytics",
                    "conversations": "/api/conversations",
                    "orders": "/api/orders",
                    "catalog": "/api/catalog",
                    "knowledge_base": "/api/kb",
                    "authentication": "/api/auth"
                },
                "backend_api": {
                    "analytics": "/backend-api/analytics",
                    "conversations": "/backend-api/conversations",
                    "orders": "/backend-api/orders",
                    "catalog": "/backend-api/catalog",
                    "knowledge_base": "/backend-api/kb",
                    "authentication": "/backend-api/auth"
                }
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

# Test endpoint
@app.get("/test")
async def test_endpoint():
    """Test endpoint to check if the app is working"""
    return {
        "message": "Test endpoint working",
        "routers_imported": routers_imported,
        "import_error": import_error
    }

@app.get("/webhook-test")
async def webhook_test_endpoint():
    """Test endpoint to verify webhook functionality is available"""
    logger.info("🔍 Webhook test endpoint called")
    return {
        "message": "Webhook routes are working",
        "webhook_endpoints": ["/webhooks/instagram", "/webhooks/health"],
        "timestamp": str(datetime.now()),
        "status": "ok"
    }

# Instagram OAuth endpoint (workaround)
@app.get("/auth/instagram/login")
async def instagram_login_direct():
    """Instagram OAuth login endpoint - direct implementation"""
    try:
        # Import Instagram OAuth
        from instagram_oauth import get_instagram_auth_url, instagram_oauth
        from config import settings
        import secrets
        
        # Check if Instagram OAuth is configured
        if not hasattr(instagram_oauth, 'is_configured') or not instagram_oauth.is_configured:
            logger.error("❌ Instagram OAuth not configured")
            return {
                "error": "Instagram OAuth not configured",
                "message": "Please contact the administrator to set up META_APP_ID and META_APP_SECRET."
            }
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Get Instagram auth URL
        auth_url, _ = get_instagram_auth_url(
            redirect_uri=settings.META_REDIRECT_URI,
            business_name=""
        )
        
        logger.info(f"Generated Instagram auth URL with state: {state}")
        
        # Create response with auth URL and state
        response = {
            "auth_url": auth_url,
            "state": state,
            "status": "ready"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate Instagram auth URL: {str(e)}")
        return {
            "error": "Failed to generate Instagram authorization URL",
            "message": str(e),
            "status": "error"
        }

# Instagram OAuth callback endpoint (workaround)
@app.post("/auth/instagram/callback")
async def instagram_callback_direct(request: dict):
    """Instagram OAuth callback endpoint - direct implementation"""
    try:
        # Import Instagram OAuth
        from instagram_oauth import instagram_oauth
        from database import get_database
        
        code = request.get("code")
        state = request.get("state")
        
        if not code or not state:
            logger.error("❌ Missing required parameters: code=%s, state=%s", bool(code), bool(state))
            return {
                "error": "Missing required parameters",
                "message": "Code and state are required",
                "status": "error"
            }
        
        try:
            # Exchange code for token
            logger.info("Exchanging authorization code for token")
            token_data = instagram_oauth.exchange_code_for_token(code, state)
            
            if not token_data:
                logger.error("❌ Failed to exchange code for token - no data returned")
                return {
                    "error": "Failed to exchange authorization code for token",
                    "status": "error"
                }
            
            logger.info("✅ Successfully exchanged code for token")
            
            # Get database connection
            db = await get_database()
            
            # Store tokens in database
            if token_data.get('instagram_accounts'):
                account = token_data['instagram_accounts'][0]  # Use first account
                await db.store_instagram_tokens(
                    account['id'],
                    account['access_token'],
                    account
                )
            
            # Create response
            response = {
                "success": True,
                "token": token_data.get('access_token', ''),
                "user": {
                    "id": token_data.get('instagram_accounts', [{}])[0].get('id', ''),
                    "instagram_handle": token_data.get('instagram_accounts', [{}])[0].get('username', ''),
                    "instagram_connected": True
                },
                "instagram_handle": token_data.get('instagram_accounts', [{}])[0].get('username', ''),
                "status": "success"
            }
            
            return response
            
        except ValueError as e:
            logger.error("❌ Token exchange failed: %s", str(e))
            return {
                "error": "Token exchange failed",
                "message": str(e),
                "status": "error"
            }
            
    except Exception as e:
        logger.error("❌ Unexpected error in instagram_callback_direct: %s", str(e))
        return {
            "error": "Internal server error",
            "message": str(e),
            "status": "error"
        }

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