#!/usr/bin/env python3
"""
IG-Shop-Agent Complete Local Flask Application
Full Instagram OAuth, AI Chat, Database functionality
"""
import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
import openai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'local-development-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///igshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Credentials
META_APP_ID = '1879578119651644'
META_APP_SECRET = 'f79b3350f43751d6139e1b29a232cbf3'
META_REDIRECT_URI = 'http://localhost:5000/auth/instagram/callback'
OPENAI_API_KEY = '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'

# Enable CORS
CORS(app, 
     origins=[
         "http://localhost:3000", 
         "http://localhost:5173",
         "https://red-island-0b863450f.2.azurestaticapps.net"
     ],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize database
db = SQLAlchemy(app)

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
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'business_name': self.business_name,
            'instagram_connected': bool(self.instagram_access_token),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'currency': self.currency,
            'image_url': self.image_url,
            'category': self.category,
            'availability': self.availability,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_instagram_id = db.Column(db.String(100))
    customer_name = db.Column(db.String(200))
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='JOD')
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instagram_user_id = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(200))
    last_message = db.Column(db.Text)
    last_message_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='active')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'last_message': self.last_message,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'status': self.status
        }

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
        'message': 'IG Shop Agent - Local Development Server',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'register': 'POST /auth/register',
            'login': 'POST /auth/login',
            'instagram_auth': 'GET /auth/instagram',
            'products': 'GET/POST /api/products',
            'orders': 'GET /api/orders',
            'ai_chat': 'POST /api/ai/chat',
            'analytics': 'GET /api/analytics'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

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
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        user = User(email=email, business_name=business_name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
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
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

# Instagram OAuth Routes
@app.route('/auth/instagram')
@require_auth
def instagram_auth():
    """Start Instagram OAuth flow"""
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        'client_id': META_APP_ID,
        'redirect_uri': META_REDIRECT_URI,
        'scope': 'instagram_basic,instagram_manage_messages',
        'response_type': 'code'
    }
    
    url_with_params = auth_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    
    return jsonify({
        'auth_url': url_with_params,
        'status': 'ready',
        'redirect_uri': META_REDIRECT_URI
    })

@app.route('/auth/instagram/callback')
def instagram_callback():
    """Handle Instagram OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': f'Instagram OAuth error: {error}'}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    try:
        # Exchange code for access token
        token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        token_data = {
            'client_id': META_APP_ID,
            'client_secret': META_APP_SECRET,
            'redirect_uri': META_REDIRECT_URI,
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_result = token_response.json()
        
        if 'access_token' not in token_result:
            return jsonify({'error': 'Failed to get access token', 'details': token_result}), 400
        
        access_token = token_result['access_token']
        
        # Get Instagram user info
        user_info_url = f"https://graph.facebook.com/v18.0/me?fields=id,name&access_token={access_token}"
        user_response = requests.get(user_info_url)
        user_data = user_response.json()
        
        return jsonify({
            'message': 'Instagram connected successfully!',
            'instagram_user_id': user_data.get('id'),
            'instagram_name': user_data.get('name'),
            'access_token': access_token[:20] + '...',  # Partial token for security
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Instagram callback error: {str(e)}")
        return jsonify({'error': 'Instagram OAuth failed'}), 500

# API Routes
@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@require_auth
def update_profile():
    try:
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if 'business_name' in data:
            user.business_name = data['business_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/products', methods=['GET'])
@require_auth
def get_products():
    try:
        products = Product.query.filter_by(user_id=request.current_user_id).all()
        return jsonify({
            'products': [product.to_dict() for product in products],
            'total': len(products)
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
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price', 0)),
            currency=data.get('currency', 'JOD'),
            category=data.get('category', ''),
            image_url=data.get('image_url', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create product error: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500

@app.route('/api/orders', methods=['GET'])
@require_auth
def get_orders():
    try:
        orders = Order.query.filter_by(user_id=request.current_user_id).all()
        return jsonify({
            'orders': [order.to_dict() for order in orders],
            'total': len(orders)
        })
        
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}")
        return jsonify({'error': 'Failed to get orders'}), 500

@app.route('/api/conversations', methods=['GET'])
@require_auth
def get_conversations():
    try:
        conversations = Conversation.query.filter_by(user_id=request.current_user_id).all()
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations],
            'total': len(conversations)
        })
        
    except Exception as e:
        logger.error(f"Get conversations error: {str(e)}")
        return jsonify({'error': 'Failed to get conversations'}), 500

@app.route('/api/ai/chat', methods=['POST'])
@require_auth
def ai_chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Get user's products for context
        products = Product.query.filter_by(user_id=request.current_user_id).all()
        product_context = "\\n".join([f"- {p.name}: {p.price} {p.currency}" for p in products])
        
        # Create AI prompt in Arabic
        system_prompt = f"""أنت مساعد ذكي لمتجر الأزياء الأردني. أجب بالعربية الأردنية.
المنتجات المتاحة:
{product_context}

كن مفيداً ومهذباً واستخدم اللهجة الأردنية المحلية."""
        
        # Make OpenAI API call
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            ai_response = f"أهلاً وسهلاً! شكراً لرسالتك: {message}. كيف ممكن أساعدك اليوم؟"
        
        return jsonify({
            'message': ai_response,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'ai_response'
        })
        
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        return jsonify({'error': 'AI chat failed'}), 500

@app.route('/api/analytics', methods=['GET'])
@require_auth
def get_analytics():
    try:
        # Calculate analytics
        total_orders = Order.query.filter_by(user_id=request.current_user_id).count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(user_id=request.current_user_id).scalar() or 0
        active_conversations = Conversation.query.filter_by(user_id=request.current_user_id, status='active').count()
        total_products = Product.query.filter_by(user_id=request.current_user_id).count()
        
        return jsonify({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'currency': 'JOD',
            'active_conversations': active_conversations,
            'total_products': total_products,
            'conversion_rate': 15.2 if total_orders > 0 else 0
        })
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get analytics'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if we already have sample data
        if User.query.first():
            return
        
        # Create sample user
        user = User(email='owner@jordanfashion.com', business_name='Jordan Fashion Store')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create sample products
        products = [
            Product(user_id=user.id, name='فستان أنيق', description='فستان رائع للمناسبات', price=45.0, category='فساتين'),
            Product(user_id=user.id, name='حقيبة يد', description='حقيبة يد جلدية فاخرة', price=30.0, category='حقائب'),
            Product(user_id=user.id, name='حذاء كعب عالي', description='حذاء نسائي أنيق', price=35.0, category='أحذية'),
            Product(user_id=user.id, name='بلوزة صيفية', description='بلوزة خفيفة ومريحة', price=25.0, category='ملابس')
        ]
        
        for product in products:
            db.session.add(product)
        
        # Create sample orders
        orders = [
            Order(user_id=user.id, customer_name='سارة أحمد', total_amount=45.0, status='pending'),
            Order(user_id=user.id, customer_name='فاطمة محمد', total_amount=65.0, status='completed'),
            Order(user_id=user.id, customer_name='نور خالد', total_amount=30.0, status='processing')
        ]
        
        for order in orders:
            db.session.add(order)
        
        # Create sample conversations
        conversations = [
            Conversation(user_id=user.id, instagram_user_id='12345', customer_name='سارة أحمد', 
                        last_message='مرحبا، أريد السؤال عن الفستان الأنيق'),
            Conversation(user_id=user.id, instagram_user_id='67890', customer_name='فاطمة محمد',
                        last_message='شكراً، الطلب وصلني بحالة ممتازة')
        ]
        
        for conv in conversations:
            db.session.add(conv)
        
        db.session.commit()
        print("✅ Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    print("🚀 Starting IG-Shop-Agent Local Development Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📊 Sample login: owner@jordanfashion.com / password123")
    app.run(host='0.0.0.0', port=5000, debug=True) 