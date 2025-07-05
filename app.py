#!/usr/bin/env python3
"""
IG-Shop-Agent - Minimal FastAPI Application
Standalone version that works regardless of directory structure
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="IG-Shop-Agent API",
    description="Multi-tenant Instagram DM management system with AI-powered conversations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IG-Shop-Agent Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "debug": "/debug/filesystem"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if Instagram OAuth is configured
    meta_app_id = os.environ.get("META_APP_ID")
    meta_app_secret = os.environ.get("META_APP_SECRET")
    
    if meta_app_id and meta_app_secret:
        instagram_oauth_status = "configured"
        oauth_message = f"Instagram OAuth configured with App ID: {meta_app_id[:8]}..."
    else:
        instagram_oauth_status = "not_configured"
        oauth_message = "Instagram OAuth not configured - please set META_APP_ID and META_APP_SECRET"
    
    return {
        "status": "healthy",
        "service": "ig-shop-agent-backend",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "instagram_oauth": instagram_oauth_status,
        "message": f"Basic service operational. {oauth_message}"
    }

# Debug endpoint
@app.get("/debug/filesystem")
async def debug_filesystem():
    """Debug endpoint to check file system structure"""
    try:
        current_dir = Path.cwd()
        parent_dir = current_dir.parent
        
        # Safely get directory contents
        try:
            current_dir_contents = [str(item) for item in current_dir.iterdir()][:20]  # Limit to first 20 items
        except Exception as e:
            current_dir_contents = [f"Error reading directory: {e}"]
        
        try:
            parent_dir_contents = [str(item) for item in parent_dir.iterdir()][:20] if parent_dir.exists() else []
        except Exception as e:
            parent_dir_contents = [f"Error reading parent directory: {e}"]
        
        return {
            "current_working_directory": str(current_dir),
            "parent_directory": str(parent_dir),
            "current_dir_contents": current_dir_contents,
            "parent_dir_contents": parent_dir_contents,
            "python_path": os.environ.get("PYTHONPATH", ""),
            "python_executable": sys.executable,
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
                "working_directory": str(Path.cwd()),
                "python_executable": sys.executable
            }
        }

# Instagram OAuth endpoints
@app.get("/auth/instagram/login")
async def instagram_login():
    """Instagram OAuth login endpoint"""
    meta_app_id = os.environ.get("META_APP_ID")
    meta_app_secret = os.environ.get("META_APP_SECRET")
    
    if not meta_app_id or not meta_app_secret:
        return {
            "error": "Instagram OAuth not configured",
            "message": "Please configure META_APP_ID and META_APP_SECRET environment variables",
            "status": "service_unavailable"
        }
    
    # Generate OAuth URL with state for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)
    
    redirect_uri = "https://igshop-api.azurewebsites.net/auth/instagram/callback"
    scope = "user_profile,user_media,instagram_basic"
    
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={meta_app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&response_type=code"
        f"&state={state}"
    )
    
    return {
        "auth_url": auth_url,
        "state": state,
        "redirect_uri": redirect_uri,
        "app_id": meta_app_id,
        "status": "ready"
    }

@app.get("/auth/instagram/callback")
async def instagram_callback(code: str = None, state: str = None, error: str = None):
    """Instagram OAuth callback endpoint"""
    if error:
        return {
            "error": error,
            "message": "Instagram OAuth authorization failed",
            "status": "failed"
        }
    
    if not code:
        return {
            "error": "missing_code",
            "message": "Authorization code not provided",
            "status": "failed"
        }
    
    if not state:
        return {
            "error": "missing_state",
            "message": "State parameter not provided",
            "status": "failed"
        }
    
    return {
        "code": code,
        "state": state,
        "message": "Authorization code received successfully",
        "status": "success",
        "next_step": "Exchange code for access token"
    }

@app.post("/auth/instagram/callback")
async def instagram_callback_post(request_data: dict):
    """Instagram OAuth callback endpoint (POST)"""
    code = request_data.get("code")
    state = request_data.get("state")
    error = request_data.get("error")
    
    if error:
        return {
            "error": error,
            "message": "Instagram OAuth authorization failed",
            "status": "failed"
        }
    
    if not code:
        return {
            "error": "missing_code",
            "message": "Authorization code not provided",
            "status": "failed"
        }
    
    if not state:
        return {
            "error": "missing_state",
            "message": "State parameter not provided",
            "status": "failed"
        }
    
    # TODO: Validate state parameter against stored value
    # TODO: Exchange code for access token
    # TODO: Get user profile from Instagram
    # TODO: Store user data in database
    
    return {
        "token": "placeholder_token",
        "user": {
            "id": 1,
            "instagram_handle": "placeholder_handle",
            "instagram_connected": True
        },
        "message": "Instagram authentication successful",
        "status": "success"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": "application_error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting FastAPI server on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    ) 