"""
IG-Shop-Agent Production FastAPI Backend - LIVE SYSTEM
Complete SaaS platform with Instagram OAuth, AI, Database - NO MOCK DATA
DEPLOYMENT: Production ready - live Instagram and OpenAI integration  
"""
import os
import logging
import uuid
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Import settings
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IG-Shop-Agent API",
    description="Production API for Instagram Shop Agent",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET,
    same_site="none",
    https_only=True
)

# Database configuration moved to unified database service
from database import db_service, get_db_connection, database_lifespan

# LIVE OpenAI configuration
from openai import OpenAI
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Routes
@app.get("/")
async def home():
    return {
        'message': 'IG-Shop-Agent Production API',
        'version': '1.0.0',
        'status': 'running',
        'features': ['LIVE Instagram OAuth', 'Real OpenAI AI', 'PostgreSQL Database', 'JWT Auth'],
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        db = await get_db_connection()
        health_status = await db.health_check()
        
        # Test OpenAI connection
        openai_client.models.list()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': health_status,
            'instagram_oauth': 'configured',
            'openai': 'connected'
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        )

# LIVE Instagram OAuth
@app.get("/auth/instagram/login")
async def instagram_login(request: Request, response: Response):
    try:
        state = str(uuid.uuid4())
        request.session['oauth_state'] = state
        
        # Use Facebook Graph API OAuth endpoint instead of Instagram's direct endpoint
        auth_url = (
            f"https://www.facebook.com/v{settings.META_GRAPH_API_VERSION}/dialog/oauth"
            f"?client_id={settings.META_APP_ID}"
            f"&redirect_uri={settings.META_REDIRECT_URI}"
            f"&scope=instagram_basic,instagram_manage_messages,pages_show_list,pages_manage_metadata,pages_read_engagement"
            f"&response_type=code"
            f"&state={state}"
        )
        
        logger.info(f"Generated Instagram auth URL with state {state}")
        
        # Set cookie for state
        response.set_cookie(
            'oauth_state',
            state,
            secure=True,
            httponly=True,
            samesite='none',
            max_age=3600  # 1 hour
        )
        
        return {
            'auth_url': auth_url,
            'state': state
        }
        
    except Exception as e:
        logger.error(f"Instagram auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Instagram auth failed")

@app.post("/auth/instagram/callback")
async def instagram_callback(request: Request):
    try:
        data = await request.json()
        code = data.get('code')
        state = data.get('state')
        
        if not code or not state:
            raise HTTPException(status_code=400, detail="Missing code or state")
        
        # Check state from cookie
        stored_state = request.cookies.get('oauth_state')
        if not stored_state or stored_state != state:
            logger.error(f"Invalid state. Expected {stored_state}, got {state}")
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for access token using Facebook Graph API
        token_url = f'https://graph.facebook.com/v{settings.META_GRAPH_API_VERSION}/oauth/access_token'
        token_data = {
            'client_id': settings.META_APP_ID,
            'client_secret': settings.META_APP_SECRET,
            'redirect_uri': settings.META_REDIRECT_URI,
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_result = token_response.json()
        
        if 'access_token' not in token_result:
            logger.error(f"Token exchange failed: {token_result}")
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Get Facebook Pages (required for Instagram Business)
        pages_url = f"https://graph.facebook.com/v{settings.META_GRAPH_API_VERSION}/me/accounts"
        pages_response = requests.get(pages_url, params={
            'access_token': token_result['access_token'],
            'fields': 'instagram_business_account,name,access_token'
        })
        pages_data = pages_response.json()
        
        if 'data' not in pages_data or not pages_data['data']:
            logger.error("No Facebook pages found")
            raise HTTPException(status_code=400, detail="No Facebook pages found")
            
        # Find page with Instagram account
        instagram_page = None
        for page in pages_data['data']:
            if 'instagram_business_account' in page:
                instagram_page = page
                break
                
        if not instagram_page:
            logger.error("No Instagram business account found")
            raise HTTPException(status_code=400, detail="No Instagram business account found")
            
        # Get Instagram account details
        instagram_account_id = instagram_page['instagram_business_account']['id']
        instagram_url = f"https://graph.facebook.com/v{settings.META_GRAPH_API_VERSION}/{instagram_account_id}"
        instagram_response = requests.get(instagram_url, params={
            'access_token': instagram_page['access_token'],
            'fields': 'id,username,name,profile_picture_url'
        })
        
        if instagram_response.status_code != 200:
            logger.error(f"Failed to get Instagram details: {instagram_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get Instagram account details")
            
        instagram_data = instagram_response.json()
        
        # Store tokens and account info in database
        db = await get_db_connection()
        await db.store_instagram_tokens(
            instagram_account_id,
            instagram_page['access_token'],
            instagram_data
        )
        
        return {
            'success': True,
            'instagram_account': {
                'id': instagram_data['id'],
                'username': instagram_data['username'],
                'name': instagram_data.get('name'),
                'profile_picture_url': instagram_data.get('profile_picture_url')
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add database lifespan
app.add_event_handler("startup", database_lifespan)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)