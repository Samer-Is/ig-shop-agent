"""
IG-Shop-Agent Simplified Flask Application  
Azure Web App compatible backend - Production Ready
"""
import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import asyncio
import asyncpg
from functools import wraps
import jwt
import hashlib
import time
import requests
import openai
import csv
import io
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import our modules
from config import settings
from database import db_service
from instagram_oauth import (
    get_instagram_auth_url, 
    handle_oauth_callback,
    generate_session_token,
    verify_session_token
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = settings.jwt_secret_key
app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Azure-compatible configuration
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Database configuration for Azure
if os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING'):
    # Parse Azure connection string
    conn_str = os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING')
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
elif all([
    os.environ.get('AZURE_POSTGRESQL_HOST'),
    os.environ.get('AZURE_POSTGRESQL_USER'), 
    os.environ.get('AZURE_POSTGRESQL_PASSWORD'),
    os.environ.get('AZURE_POSTGRESQL_NAME')
]):
    # Use individual environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('AZURE_POSTGRESQL_USER')}:{os.environ.get('AZURE_POSTGRESQL_PASSWORD')}@{os.environ.get('AZURE_POSTGRESQL_HOST')}/{os.environ.get('AZURE_POSTGRESQL_NAME')}"
else:
    # Local development fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_dev.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Instagram/Meta configuration
app.config['META_APP_ID'] = os.environ.get('META_APP_ID', '1879578119651644')
app.config['META_APP_SECRET'] = os.environ.get('META_APP_SECRET', 'f79b3350f43751d6139e1b29a232cbf3')
app.config['META_REDIRECT_URI'] = os.environ.get('META_REDIRECT_URI', 'https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback')

# OpenAI configuration
openai.api_key = os.environ.get('OPENAI_API_KEY', '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')

# File upload configuration
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    business_name = db.Column(db.String(200))
    instagram_user_id = db.Column(db.String(100))
    instagram_access_token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='JOD')
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    availability = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_instagram_id = db.Column(db.String(100))
    customer_name = db.Column(db.String(200))
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='JOD')
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instagram_user_id = db.Column(db.String(100), nullable=False)
    last_message = db.Column(db.Text)
    last_message_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='active')

# JWT Token handling
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
            user_id = verify_token(token)
            if user_id:
                request.current_user_id = user_id
                return f(*args, **kwargs)
        return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'IG Shop Agent API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/auth/*',
            'api': '/api/*',
            'health': '/health'
        }
    })

@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

# Authentication Routes
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        business_name = data.get('business_name', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400
        
        user = User(email=email, business_name=business_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'business_name': user.business_name
            }
        })
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'business_name': user.business_name,
                'has_instagram': bool(user.instagram_access_token)
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/instagram', methods=['GET'])
@require_auth
def instagram_auth():
    try:
        user_id = request.current_user_id
        
        # Instagram OAuth URL
        auth_url = f"https://api.instagram.com/oauth/authorize?client_id={app.config['META_APP_ID']}&redirect_uri={app.config['META_REDIRECT_URI']}&scope=user_profile,user_media&response_type=code&state={user_id}"
        
        return jsonify({
            'auth_url': auth_url,
            'message': 'Redirect to Instagram authorization'
        })
    except Exception as e:
        logger.error(f"Instagram auth error: {str(e)}")
        return jsonify({'error': 'Instagram auth failed'}), 500

@app.route('/auth/instagram/callback', methods=['GET'])
def instagram_callback():
    try:
        code = request.args.get('code')
        state = request.args.get('state')  # user_id
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'Instagram auth error: {error}'}), 400
        
        if not code or not state:
            return jsonify({'error': 'Missing authorization code or state'}), 400
        
        # Exchange code for access token
        token_url = "https://api.instagram.com/oauth/access_token"
        token_data = {
            'client_id': app.config['META_APP_ID'],
            'client_secret': app.config['META_APP_SECRET'],
            'grant_type': 'authorization_code',
            'redirect_uri': app.config['META_REDIRECT_URI'],
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_result = token_response.json()
        
        if 'access_token' not in token_result:
            return jsonify({'error': 'Failed to get access token'}), 400
        
        # Update user with Instagram info
        user = User.query.get(state)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.instagram_access_token = token_result['access_token']
        user.instagram_user_id = token_result.get('user_id')
        db.session.commit()
        
        # Redirect to frontend success page
        frontend_url = "https://red-island-0b863450f.2.azurestaticapps.net"
        return redirect(f"{frontend_url}/?instagram_connected=true")
        
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        return jsonify({'error': 'Instagram callback failed'}), 500

# API Routes
@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'business_name': user.business_name,
            'has_instagram': bool(user.instagram_access_token),
            'created_at': user.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@require_auth
def update_profile():
    try:
        data = request.get_json()
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'business_name' in data:
            user.business_name = data['business_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'business_name': user.business_name
            }
        })
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

# Product Management
@app.route('/api/products', methods=['GET'])
@require_auth
def get_products():
    try:
        products = Product.query.filter_by(user_id=request.current_user_id).all()
        return jsonify({
            'products': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'currency': p.currency,
                'image_url': p.image_url,
                'category': p.category,
                'availability': p.availability,
                'created_at': p.created_at.isoformat()
            } for p in products]
        })
    except Exception as e:
        logger.error(f"Get products error: {str(e)}")
        return jsonify({'error': 'Failed to get products'}), 500

@app.route('/api/products', methods=['POST'])
@require_auth
def create_product():
    try:
        data = request.get_json()
        
        product = Product(
            user_id=request.current_user_id,
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            currency=data.get('currency', 'JOD'),
            image_url=data.get('image_url', ''),
            category=data.get('category', ''),
            availability=data.get('availability', 'available')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'currency': product.currency
            }
        })
    except Exception as e:
        logger.error(f"Create product error: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500

# Order Management
@app.route('/api/orders', methods=['GET'])
@require_auth
def get_orders():
    try:
        orders = Order.query.filter_by(user_id=request.current_user_id).all()
        return jsonify({
            'orders': [{
                'id': o.id,
                'customer_name': o.customer_name,
                'total_amount': o.total_amount,
                'currency': o.currency,
                'status': o.status,
                'created_at': o.created_at.isoformat()
            } for o in orders]
        })
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}")
        return jsonify({'error': 'Failed to get orders'}), 500

# AI Chat Integration
@app.route('/api/ai/chat', methods=['POST'])
@require_auth
def ai_chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user's products for context
        products = Product.query.filter_by(user_id=request.current_user_id).all()
        user = User.query.get(request.current_user_id)
        
        # Create context for AI
        context = f"""
        أنت مساعد ذكي لمتجر {user.business_name or 'المتجر'} في الأردن.
        المنتجات المتوفرة:
        """
        
        for product in products[:10]:  # Limit context
            context += f"- {product.name}: {product.price} {product.currency}\n"
        
        context += """
        يرجى الرد باللغة العربية الأردنية المحلية والتفاعل مع العملاء بطريقة ودودة ومهنية.
        ساعد العملاء في العثور على المنتجات وقدم المعلومات حول الأسعار والتوفر.
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        return jsonify({'error': 'AI chat failed', 'details': str(e)}), 500

# Analytics
@app.route('/api/analytics', methods=['GET'])
@require_auth
def get_analytics():
    try:
        user_id = request.current_user_id
        
        # Calculate basic analytics
        total_products = Product.query.filter_by(user_id=user_id).count()
        total_orders = Order.query.filter_by(user_id=user_id).count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(user_id=user_id).scalar() or 0
        
        # Recent orders
        recent_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).limit(5).all()
        
        return jsonify({
            'analytics': {
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'currency': 'JOD'
            },
            'recent_orders': [{
                'id': o.id,
                'customer_name': o.customer_name,
                'total_amount': o.total_amount,
                'status': o.status,
                'created_at': o.created_at.isoformat()
            } for o in recent_orders]
        })
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get analytics'}), 500

# File Upload
@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # In production, upload to Azure Blob Storage
            file_url = f"/api/files/{filename}"
            
            return jsonify({
                'message': 'File uploaded successfully',
                'url': file_url,
                'filename': filename
            })
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/files/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
@app.before_first_request
def create_tables():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")

if __name__ == '__main__':
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    ) 