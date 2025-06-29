"""
IG-Shop-Agent Production Flask Backend - LIVE SYSTEM
Complete SaaS platform with Instagram OAuth, AI, Database - NO MOCK DATA
DEPLOYMENT: Production ready - live Instagram and OpenAI integration  
"""
import os
import logging
import uuid
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import asyncio
from asgiref.wsgi import WsgiToAsgi
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# PRODUCTION Configuration - LIVE CREDENTIALS
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for cross-origin cookies

# Enable CORS for frontend
CORS(app, 
     origins=[
         "http://localhost:3000", 
         "http://localhost:5173",
         "https://red-island-0b863450f.2.azurestaticapps.net",
         "https://*.azurestaticapps.net"
     ],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Set-Cookie'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Database configuration moved to unified database service
from database import db_service, get_db_connection, database_lifespan

# LIVE Instagram/Meta configuration
app.config['META_APP_ID'] = os.environ.get('META_APP_ID', '1879578119651644')
app.config['META_APP_SECRET'] = os.environ.get('META_APP_SECRET', 'f79b3350f43751d6139e1b29a232cbf3')
app.config['META_REDIRECT_URI'] = os.environ.get('META_REDIRECT_URI', 'https://red-island-0b863450f.2.azurestaticapps.net/auth/callback')

# LIVE OpenAI configuration
from openai import OpenAI
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', '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'))

# Routes
@app.route('/')
async def home():
    return jsonify({
        'message': 'IG-Shop-Agent Production API',
        'version': '1.0.0',
        'status': 'running',
        'features': ['LIVE Instagram OAuth', 'Real OpenAI AI', 'PostgreSQL Database', 'JWT Auth'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
async def health_check():
    try:
        # Test database connection
        db = await get_db_connection()
        health_status = await db.health_check()
        
        # Test OpenAI connection
        openai_client.models.list()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': health_status,
            'instagram_oauth': 'configured',
            'openai': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

# LIVE Instagram OAuth
@app.route('/auth/instagram/login')
async def instagram_login():
    try:
        state = str(uuid.uuid4())
        session['oauth_state'] = state
        
        # Use Facebook Graph API OAuth endpoint instead of Instagram's direct endpoint
        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth"
            f"?client_id={app.config['META_APP_ID']}"
            f"&redirect_uri={app.config['META_REDIRECT_URI']}"
            f"&scope=instagram_basic,instagram_manage_messages,pages_show_list,pages_manage_metadata,pages_read_engagement"
            f"&response_type=code"
            f"&state={state}"
        )
        
        logger.info(f"Generated Instagram auth URL with state {state}")
        response = jsonify({
            'auth_url': auth_url,
            'state': state
        })
        
        # Set cookie for state
        response.set_cookie(
            'oauth_state',
            state,
            secure=True,
            httponly=True,
            samesite='None',
            max_age=3600  # 1 hour
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Instagram auth error: {str(e)}")
        return jsonify({'error': 'Instagram auth failed'}), 500

@app.route('/auth/instagram/callback', methods=['POST'])
async def instagram_callback():
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')
        
        if not code or not state:
            return jsonify({'error': 'Missing code or state'}), 400
        
        # Check state from cookie instead of session
        stored_state = request.cookies.get('oauth_state')
        if not stored_state or stored_state != state:
            logger.error(f"Invalid state. Expected {stored_state}, got {state}")
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Exchange code for access token using Facebook Graph API
        token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        token_data = {
            'client_id': app.config['META_APP_ID'],
            'client_secret': app.config['META_APP_SECRET'],
            'redirect_uri': app.config['META_REDIRECT_URI'],
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_result = token_response.json()
        
        if 'access_token' not in token_result:
            logger.error(f"Token exchange failed: {token_result}")
            return jsonify({'error': 'Failed to get access token'}), 400
        
        # Get Facebook Pages (required for Instagram Business)
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts"
        pages_response = requests.get(pages_url, params={
            'access_token': token_result['access_token'],
            'fields': 'instagram_business_account,name,access_token'
        })
        pages_data = pages_response.json()
        
        if 'data' not in pages_data or not pages_data['data']:
            logger.error("No Facebook pages found")
            return jsonify({'error': 'No Facebook pages found'}), 400
            
        # Find page with Instagram account
        instagram_page = None
        for page in pages_data['data']:
            if 'instagram_business_account' in page:
                instagram_page = page
                break
                
        if not instagram_page:
            logger.error("No Instagram business account found")
            return jsonify({'error': 'No Instagram business account found'}), 400
            
        # Get Instagram account details
        instagram_account_id = instagram_page['instagram_business_account']['id']
        instagram_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}"
        instagram_response = requests.get(instagram_url, params={
            'access_token': instagram_page['access_token'],
            'fields': 'id,username,name,profile_picture_url'
        })
        instagram_data = instagram_response.json()
        
        # Store user data in database
        db = await get_db_connection()
        user_data = {
            'instagram_handle': instagram_data['username'],
            'instagram_user_id': instagram_data['id'],
            'instagram_access_token': instagram_page['access_token'],
            'instagram_connected': True
        }
        
        # Check if user exists
        existing_user = await db.fetch_one(
            "SELECT id FROM users WHERE instagram_handle = $1",
            instagram_data['username']
        )
        
        if existing_user:
            # Update existing user
            await db.execute_query(
                """
                UPDATE users 
                SET instagram_user_id = $1, 
                    instagram_access_token = $2, 
                    instagram_connected = $3,
                    updated_at = NOW()
                WHERE instagram_handle = $4
                """,
                instagram_data['id'],
                instagram_page['access_token'],
                True,
                instagram_data['username']
            )
            user_id = existing_user['id']
        else:
            # Create new user
            user_id = await db.fetch_val(
                """
                INSERT INTO users (instagram_handle, instagram_user_id, instagram_access_token, instagram_connected)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                instagram_data['username'],
                instagram_data['id'],
                instagram_page['access_token'],
                True
            )
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user_id,
                'instagram_handle': instagram_data['username'],
                'exp': datetime.utcnow() + timedelta(days=30)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'instagram_handle': instagram_data['username'],
                'name': instagram_data.get('name'),
                'profile_picture_url': instagram_data.get('profile_picture_url')
            }
        })
        
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Convert Flask app to ASGI
asgi_app = WsgiToAsgi(app)

# Run the app with uvicorn
if __name__ == '__main__':
    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        lifespan="on"
    )