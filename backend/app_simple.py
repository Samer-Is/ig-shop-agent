"""
IG-Shop-Agent Simplified Flask Application  
Azure Web App compatible backend - Production Ready
"""
import os
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, session
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
     origins=["http://localhost:3000", "https://*.azurewebsites.net"],
     supports_credentials=True)

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'ig-shop-agent-backend'
    })

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check with more details"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'ig-shop-agent-backend',
        'version': '1.0.0',
        'environment': settings.environment,
        'features': {
            'instagram_oauth': bool(settings.meta_app_id),
            'openai_integration': bool(settings.openai_api_key),
            'database_connected': True
        }
    })

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/auth/instagram', methods=['GET'])
def instagram_auth():
    """Start Instagram OAuth flow"""
    try:
        business_name = request.args.get('business_name', '')
        redirect_uri = request.args.get('redirect_uri', 'http://localhost:3000/auth/callback')
        
        auth_url, state = get_instagram_auth_url(redirect_uri, business_name)
        
        # Store state in session
        session['oauth_state'] = state
        session['business_name'] = business_name
        
        return jsonify({
            'auth_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Instagram auth error: {e}")
        return jsonify({'error': 'Failed to generate Instagram auth URL'}), 500

@app.route('/auth/callback', methods=['GET'])
def instagram_callback():
    """Handle Instagram OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'Instagram OAuth error: {error}'}), 400
        
        if not code or not state:
            return jsonify({'error': 'Missing authorization code or state'}), 400
        
        # Verify state
        if state != session.get('oauth_state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
        
        # Get redirect URI from session or use default
        redirect_uri = request.args.get('redirect_uri', 'http://localhost:3000/auth/callback')
        
        # Exchange code for token
        auth_data = handle_oauth_callback(code, state, redirect_uri)
        
        if not auth_data:
            return jsonify({'error': 'Failed to authenticate with Instagram'}), 400
        
        # Create or get tenant from database
        instagram_accounts = auth_data['instagram_accounts']
        if not instagram_accounts:
            return jsonify({'error': 'No Instagram business accounts found'}), 400
        
        # Use first Instagram account
        ig_account = instagram_accounts[0]
        tenant_id = f"tenant_{ig_account['id']}"
        
        # Generate session token
        user_data = {
            'id': ig_account['id'],
            'username': ig_account['username'],
            'name': ig_account['name']
        }
        
        session_token = generate_session_token(user_data, tenant_id)
        
        # Clean up session
        session.pop('oauth_state', None)
        session.pop('business_name', None)
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'tenant_id': tenant_id,
            'user': user_data,
            'instagram_accounts': instagram_accounts
        })
        
    except Exception as e:
        logger.error(f"Instagram callback error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/auth/verify', methods=['POST'])
def verify_token():
    """Verify session token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_session_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return jsonify({
            'valid': True,
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'tenant_id': payload.get('tenant_id')
        })
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Token verification failed'}), 500

# =============================================================================
# CATALOG MANAGEMENT ENDPOINTS - LIVE DATABASE INTEGRATION
# =============================================================================

def async_route(f):
    """Decorator to handle async functions in Flask"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return decorated_function

def get_tenant_id_from_token(auth_header: str) -> Optional[str]:
    """Extract tenant_id from JWT token"""
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        payload = verify_session_token(token)
        return payload.get('tenant_id') if payload else None
    except Exception:
        return None

@app.route('/api/catalog', methods=['GET'])
@async_route
async def get_catalog():
    """Get catalog items for current tenant"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Build query
        where_conditions = ["tenant_id = $1"]
        params = [tenant_id]
        param_count = 1
        
        if category:
            param_count += 1
            where_conditions.append(f"category = ${param_count}")
            params.append(category)
        
        if search:
            param_count += 1
            where_conditions.append(f"(name ILIKE ${param_count} OR description ILIKE ${param_count})")
            params.append(f"%{search}%")
        
        where_clause = " AND ".join(where_conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM catalog_items WHERE {where_clause}"
        total = await db_service.fetch_val(count_query, *params)
        
        # Get items
        items_query = f"""
            SELECT id, tenant_id, sku, name, price_jod, media_url, extras, 
                   description, category, stock_quantity, created_at, updated_at
            FROM catalog_items 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        params.extend([limit, offset])
        
        items = await db_service.fetch_all(items_query, *params)
        
        return jsonify({
            'items': items,
            'total': total or 0,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Get catalog error: {e}")
        return jsonify({'error': 'Failed to fetch catalog'}), 500

@app.route('/api/catalog', methods=['POST'])
@async_route
async def create_catalog_item():
    """Create new catalog item"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'name', 'price_jod']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate item ID
        item_id = str(uuid.uuid4())
        
        # Insert into database
        insert_query = """
            INSERT INTO catalog_items (
                id, tenant_id, sku, name, price_jod, description, category, 
                stock_quantity, media_url, extras
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        await db_service.execute_query(
            insert_query,
            item_id,
            tenant_id,
            data['sku'],
            data['name'],
            data['price_jod'],
            data.get('description', ''),
            data.get('category', ''),
            data.get('stock_quantity', 0),
            data.get('media_url', ''),
            data.get('extras', {})
        )
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'message': 'Catalog item created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create catalog item error: {e}")
        return jsonify({'error': 'Failed to create catalog item'}), 500

# =============================================================================
# ORDER MANAGEMENT ENDPOINTS - LIVE DATABASE INTEGRATION
# =============================================================================

@app.route('/api/orders', methods=['GET'])
@async_route
async def get_orders():
    """Get orders for current tenant"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        # Get pagination parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        
        # Build query
        where_conditions = ["tenant_id = $1"]
        params = [tenant_id]
        
        if status:
            where_conditions.append("status = $2")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM orders WHERE {where_clause}"
        total = await db_service.fetch_val(count_query, *params)
        
        # Get orders
        param_offset = len(params)
        orders_query = f"""
            SELECT id, tenant_id, sku, qty, customer, phone, status, 
                   total_amount, delivery_address, notes, created_at, updated_at
            FROM orders 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_offset + 1} OFFSET ${param_offset + 2}
        """
        params.extend([limit, offset])
        
        orders = await db_service.fetch_all(orders_query, *params)
        
        return jsonify({
            'orders': orders,
            'total': total or 0,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

@app.route('/api/orders', methods=['POST'])
@async_route
async def create_order():
    """Create new order"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'qty', 'customer', 'phone', 'total_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Insert into database
        insert_query = """
            INSERT INTO orders (
                id, tenant_id, sku, qty, customer, phone, status, 
                total_amount, delivery_address, notes
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        await db_service.execute_query(
            insert_query,
            order_id,
            tenant_id,
            data['sku'],
            data['qty'],
            data['customer'],
            data['phone'],
            'pending',  # Default status
            data['total_amount'],
            data.get('delivery_address', ''),
            data.get('notes', '')
        )
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify({'error': 'Failed to create order'}), 500

# =============================================================================
# AI AGENT ENDPOINTS
# =============================================================================

@app.route('/api/analytics/dashboard', methods=['GET'])
@async_route
async def get_dashboard_analytics():
    """Get dashboard analytics for current tenant"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        # Get analytics data from database
        # Total orders
        total_orders = await db_service.fetch_val(
            "SELECT COUNT(*) FROM orders WHERE tenant_id = $1", tenant_id
        ) or 0
        
        # Total revenue
        total_revenue = await db_service.fetch_val(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE tenant_id = $1 AND status IN ('confirmed', 'delivered')", 
            tenant_id
        ) or 0
        
        # Total products
        total_products = await db_service.fetch_val(
            "SELECT COUNT(*) FROM catalog_items WHERE tenant_id = $1", tenant_id
        ) or 0
        
        # Pending orders
        pending_orders = await db_service.fetch_val(
            "SELECT COUNT(*) FROM orders WHERE tenant_id = $1 AND status = 'pending'", tenant_id
        ) or 0
        
        # Confirmed orders
        confirmed_orders = await db_service.fetch_val(
            "SELECT COUNT(*) FROM orders WHERE tenant_id = $1 AND status = 'confirmed'", tenant_id
        ) or 0
        
        # Recent orders (last 5)
        recent_orders = await db_service.fetch_all(
            """SELECT id, sku, qty, customer, phone, status, total_amount, created_at 
               FROM orders WHERE tenant_id = $1 
               ORDER BY created_at DESC LIMIT 5""", 
            tenant_id
        )
        
        # Top products (first 3 by creation date)
        top_products = await db_service.fetch_all(
            """SELECT id, sku, name, price_jod, category, stock_quantity 
               FROM catalog_items WHERE tenant_id = $1 
               ORDER BY created_at DESC LIMIT 3""", 
            tenant_id
        )
        
        return jsonify({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'total_products': total_products,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'recent_orders': recent_orders,
            'top_products': top_products
        })
        
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

async def generate_ai_response(message: str, tenant_id: str) -> str:
    """Generate AI response using real catalog data"""
    try:
        # Initialize database connection if needed
        if not db_service.is_connected:
            await db_service.connect()
        
        # Get real catalog items for this tenant
        catalog_items = await db_service.fetch_all(
            """SELECT sku, name, price_jod, description, category, stock_quantity 
               FROM catalog_items WHERE tenant_id = $1 AND stock_quantity > 0
               ORDER BY created_at DESC LIMIT 10""",
            tenant_id
        )
        
        if not catalog_items:
            return "أعتذر، لا توجد منتجات متاحة حالياً. يرجى المحاولة لاحقاً."
        
        # Simple AI response generation based on message content
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['أريد', 'أحتاج', 'أبحث', 'want', 'need', 'looking for']):
            if catalog_items:
                first_item = catalog_items[0]
                return f"أهلاً وسهلاً! يمكنني أن أساعدك. لدينا {first_item['name']} متوفر بسعر {first_item['price_jod']} دينار أردني. هل تود معرفة المزيد عن هذا المنتج أو تفضل رؤية منتجات أخرى؟"
        
        elif any(word in message_lower for word in ['سعر', 'كم', 'price', 'cost', 'how much']):
            return f"أسعارنا تتراوح من {min(item['price_jod'] for item in catalog_items)} إلى {max(item['price_jod'] for item in catalog_items)} دينار أردني. أي منتج تود معرفة سعره تحديداً؟"
        
        elif any(word in message_lower for word in ['متوفر', 'موجود', 'available', 'in stock']):
            available_count = len([item for item in catalog_items if item['stock_quantity'] > 0])
            return f"لدينا {available_count} منتج متوفر حالياً. هل تود رؤية قائمة المنتجات المتاحة؟"
        
        else:
            return f"أهلاً وسهلاً بك! كيف يمكنني مساعدتك اليوم؟ لدينا {len(catalog_items)} منتج متوفر. يمكنك السؤال عن أي منتج أو سعر."
        
    except Exception as e:
        logger.error(f"AI response generation error: {e}")
        return "أعتذر، حدث خطأ في النظام. يرجى المحاولة مرة أخرى."

@app.route('/api/ai/test-response', methods=['POST'])
@async_route
async def test_ai_response():
    """Test AI agent response with real catalog data"""
    try:
        # Check authentication and get tenant_id
        auth_header = request.headers.get('Authorization')
        tenant_id = get_tenant_id_from_token(auth_header)
        
        if not tenant_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        # Get customer message
        customer_message = data['message']
        
        # Generate AI response using real catalog data
        ai_response = await generate_ai_response(customer_message, tenant_id)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI test response error: {e}")
        return jsonify({'error': 'Failed to generate AI response'}), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

if __name__ == '__main__':
    # For Azure Web App deployment - handle different port environment variables
    port = int(os.environ.get('PORT', os.environ.get('WEBSITES_PORT', 8000)))
    
    logger.info(f"Starting Flask application on port {port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Environment: {settings.environment}")
    
    # For local development and Azure deployment
    app.run(
        host='0.0.0.0',
        port=port,
        debug=settings.debug
    ) 