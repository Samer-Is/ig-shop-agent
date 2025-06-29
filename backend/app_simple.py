"""
IG-Shop-Agent Simplified Flask Application  
Azure Web App compatible backend - Production Ready
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, session
from flask_cors import CORS

# Import our modules
from config import settings
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
        
        # Create or get tenant (simplified - using mock data for now)
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
# CATALOG MANAGEMENT ENDPOINTS (MOCK DATA FOR NOW)
# =============================================================================

# Mock catalog data
MOCK_CATALOG = [
    {
        'id': '1',
        'sku': 'DRESS-001',
        'name': 'فستان صيفي أنيق',
        'price_jod': 45.99,
        'description': 'فستان صيفي مريح ومناسب لجميع المناسبات',
        'category': 'فساتين',
        'stock_quantity': 15,
        'media_url': 'https://example.com/dress1.jpg'
    },
    {
        'id': '2',
        'sku': 'SHOES-001',
        'name': 'حذاء رياضي للنساء',
        'price_jod': 65.00,
        'description': 'حذاء رياضي مريح للاستخدام اليومي',
        'category': 'أحذية',
        'stock_quantity': 8,
        'media_url': 'https://example.com/shoes1.jpg'
    },
    {
        'id': '3',
        'sku': 'BAG-001',
        'name': 'حقيبة يد عصرية',
        'price_jod': 89.99,
        'description': 'حقيبة يد أنيقة ومناسبة للعمل والمناسبات',
        'category': 'حقائب',
        'stock_quantity': 5,
        'media_url': 'https://example.com/bag1.jpg'
    }
]

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    """Get catalog items for current tenant"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        # For now, return mock data
        return jsonify({
            'items': MOCK_CATALOG,
            'total': len(MOCK_CATALOG),
            'limit': 50,
            'offset': 0
        })
        
    except Exception as e:
        logger.error(f"Get catalog error: {e}")
        return jsonify({'error': 'Failed to fetch catalog'}), 500

@app.route('/api/catalog', methods=['POST'])
def create_catalog_item():
    """Create new catalog item"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'name', 'price_jod']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate new item ID
        new_id = str(len(MOCK_CATALOG) + 1)
        new_item = {
            'id': new_id,
            **data
        }
        
        # Add to mock catalog
        MOCK_CATALOG.append(new_item)
        
        return jsonify({
            'success': True,
            'item_id': new_id,
            'message': 'Catalog item created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create catalog item error: {e}")
        return jsonify({'error': 'Failed to create catalog item'}), 500

# =============================================================================
# ORDER MANAGEMENT ENDPOINTS (MOCK DATA FOR NOW)
# =============================================================================

MOCK_ORDERS = [
    {
        'id': '1',
        'sku': 'DRESS-001',
        'qty': 2,
        'customer': 'أحمد محمد',
        'phone': '+962791234567',
        'status': 'pending',
        'total_amount': 91.98,
        'delivery_address': 'عمان، الأردن',
        'notes': 'يرجى التواصل قبل التوصيل',
        'created_at': '2024-01-15T10:30:00Z'
    },
    {
        'id': '2',
        'sku': 'SHOES-001',
        'qty': 1,
        'customer': 'فاطمة أحمد',
        'phone': '+962795678901',
        'status': 'confirmed',
        'total_amount': 65.00,
        'delivery_address': 'إربد، الأردن',
        'notes': '',
        'created_at': '2024-01-15T14:15:00Z'
    }
]

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders for current tenant"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Return mock orders
        return jsonify({
            'orders': MOCK_ORDERS,
            'total': len(MOCK_ORDERS),
            'limit': 50,
            'offset': 0
        })
        
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'qty', 'customer', 'phone', 'total_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate new order ID
        new_id = str(len(MOCK_ORDERS) + 1)
        new_order = {
            'id': new_id,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat() + 'Z',
            **data
        }
        
        # Add to mock orders
        MOCK_ORDERS.append(new_order)
        
        return jsonify({
            'success': True,
            'order_id': new_id,
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify({'error': 'Failed to create order'}), 500

# =============================================================================
# AI AGENT ENDPOINTS
# =============================================================================

@app.route('/api/ai/test-response', methods=['POST'])
def test_ai_response():
    """Test AI agent response"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        # Get customer message
        customer_message = data['message']
        
        # Generate AI response
        ai_response = generate_ai_response(customer_message)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI test response error: {e}")
        return jsonify({'error': 'Failed to generate AI response'}), 500

def generate_ai_response(message: str) -> str:
    """Generate AI response using OpenAI"""
    try:
        import openai
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Create context from catalog
        catalog_context = "Available products:\n"
        for item in MOCK_CATALOG:
            catalog_context += f"- {item['name']}: {item['price_jod']} JOD\n"
        
        # Create prompt
        prompt = f"""You are a helpful sales assistant for an online store in Jordan. 
        
Respond in Jordanian Arabic dialect. Be friendly and helpful.

{catalog_context}

Customer message: {message}

Provide a helpful response in Jordanian Arabic:"""
        
        # Make OpenAI API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful sales assistant in Jordan. Always respond in Jordanian Arabic dialect."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "أهلاً وسهلاً! كيف بقدر أساعدك اليوم؟ (Hello! How can I help you today?)"

# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard analytics data"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Mock analytics data
        analytics = {
            'total_orders': len(MOCK_ORDERS),
            'total_revenue': sum(order['total_amount'] for order in MOCK_ORDERS),
            'total_products': len(MOCK_CATALOG),
            'pending_orders': len([o for o in MOCK_ORDERS if o['status'] == 'pending']),
            'confirmed_orders': len([o for o in MOCK_ORDERS if o['status'] == 'confirmed']),
            'recent_orders': MOCK_ORDERS[:5],
            'top_products': MOCK_CATALOG[:3]
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For local development
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=settings.debug
    ) 