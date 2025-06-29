"""
IG-Shop-Agent Flask Web Application
Azure Web App compatible backend with all API endpoints
"""
import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests

# Import our modules
from config import settings
from database import init_database, close_database, db
from instagram_oauth import (
    get_instagram_auth_url, 
    handle_oauth_callback,
    generate_session_token,
    verify_session_token
)
from tenant_middleware import (
    tenant_context,
    tenant_middleware,
    process_tenant_request,
    get_current_tenant_id
)
from azure_keyvault import get_secret

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = get_secret('flask-secret-key') or settings.jwt_secret_key

# Enable CORS for frontend
CORS(app, 
     origins=["http://localhost:3000", "https://*.azurewebsites.net"],
     supports_credentials=True)

# Global variables for async operations
loop = None

def get_event_loop():
    """Get or create event loop for async operations"""
    global loop
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

def run_async(coro):
    """Run async function in Flask context"""
    loop = get_event_loop()
    return loop.run_until_complete(coro)

@app.before_request
async def before_request():
    """Process tenant context before each request"""
    try:
        # Skip tenant processing for public endpoints
        public_endpoints = ['/health', '/auth/instagram', '/auth/callback']
        if request.endpoint in public_endpoints or request.path in public_endpoints:
            return
        
        # Prepare request data for tenant middleware
        request_data = {
            'headers': dict(request.headers),
            'url': request.path,
            'method': request.method
        }
        
        # Process tenant context
        tenant_result = await process_tenant_request(request_data)
        
        # Store tenant info in request context
        request.tenant_info = tenant_result
        
    except Exception as e:
        logger.error(f"Error in before_request: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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
            'database_connected': True  # Will be updated based on actual connection
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
        
        # Create or get tenant
        instagram_accounts = auth_data['instagram_accounts']
        if not instagram_accounts:
            return jsonify({'error': 'No Instagram business accounts found'}), 400
        
        # Use first Instagram account
        ig_account = instagram_accounts[0]
        tenant_handle = f"@{ig_account['username']}"
        
        # Create tenant if doesn't exist
        tenant_id = run_async(db.create_tenant(
            tenant_handle,
            auth_data.get('business_name') or ig_account['name'],
            'professional'  # Default plan
        ))
        
        # Generate session token
        user_data = {
            'id': ig_account['id'],
            'username': ig_account['username'],
            'name': ig_account['name']
        }
        
        session_token = generate_session_token(user_data, tenant_id)
        
        # Store auth data securely
        run_async(db.store_instagram_token(tenant_id, auth_data))
        
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
# CATALOG MANAGEMENT ENDPOINTS
# =============================================================================

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    """Get catalog items for current tenant"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Get catalog items
        items = run_async(db.get_catalog_items(
            tenant_id=tenant_info['tenant_id'],
            limit=limit,
            offset=offset,
            category=category,
            search=search
        ))
        
        return jsonify({
            'items': items,
            'total': len(items),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Get catalog error: {e}")
        return jsonify({'error': 'Failed to fetch catalog'}), 500

@app.route('/api/catalog', methods=['POST'])
def create_catalog_item():
    """Create new catalog item"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'name', 'price_jod']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create catalog item
        item_id = run_async(db.create_catalog_item(
            tenant_id=tenant_info['tenant_id'],
            item_data=data
        ))
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'message': 'Catalog item created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create catalog item error: {e}")
        return jsonify({'error': 'Failed to create catalog item'}), 500

@app.route('/api/catalog/<item_id>', methods=['PUT'])
def update_catalog_item(item_id):
    """Update catalog item"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Update catalog item
        updated = run_async(db.update_catalog_item(
            tenant_id=tenant_info['tenant_id'],
            item_id=item_id,
            item_data=data
        ))
        
        if not updated:
            return jsonify({'error': 'Item not found or access denied'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Catalog item updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Update catalog item error: {e}")
        return jsonify({'error': 'Failed to update catalog item'}), 500

@app.route('/api/catalog/<item_id>', methods=['DELETE'])
def delete_catalog_item(item_id):
    """Delete catalog item"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Delete catalog item
        deleted = run_async(db.delete_catalog_item(
            tenant_id=tenant_info['tenant_id'],
            item_id=item_id
        ))
        
        if not deleted:
            return jsonify({'error': 'Item not found or access denied'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Catalog item deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete catalog item error: {e}")
        return jsonify({'error': 'Failed to delete catalog item'}), 500

# =============================================================================
# ORDER MANAGEMENT ENDPOINTS
# =============================================================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders for current tenant"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        
        # Get orders
        orders = run_async(db.get_orders(
            tenant_id=tenant_info['tenant_id'],
            limit=limit,
            offset=offset,
            status=status
        ))
        
        return jsonify({
            'orders': orders,
            'total': len(orders),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        required_fields = ['sku', 'qty', 'customer', 'phone', 'total_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create order
        order_id = run_async(db.create_order(
            tenant_id=tenant_info['tenant_id'],
            order_data=data
        ))
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify({'error': 'Failed to create order'}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing status field'}), 400
        
        # Update order status
        updated = run_async(db.update_order_status(
            tenant_id=tenant_info['tenant_id'],
            order_id=order_id,
            status=data['status']
        ))
        
        if not updated:
            return jsonify({'error': 'Order not found or access denied'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Update order status error: {e}")
        return jsonify({'error': 'Failed to update order status'}), 500

# =============================================================================
# AI AGENT ENDPOINTS
# =============================================================================

@app.route('/api/ai/test-response', methods=['POST'])
def test_ai_response():
    """Test AI agent response"""
    try:
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        # Get customer message
        customer_message = data['message']
        
        # Get tenant's catalog for context
        catalog = run_async(db.get_catalog_items(
            tenant_id=tenant_info['tenant_id'],
            limit=50
        ))
        
        # Generate AI response (simplified for now)
        ai_response = generate_ai_response(customer_message, catalog, tenant_info)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'processed_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI test response error: {e}")
        return jsonify({'error': 'Failed to generate AI response'}), 500

def generate_ai_response(message: str, catalog: List[Dict], tenant_info: Dict) -> str:
    """Generate AI response using OpenAI (simplified implementation)"""
    try:
        import openai
        
        # Set OpenAI API key
        openai.api_key = settings.openai_api_key
        
        # Create context from catalog
        catalog_context = ""
        if catalog:
            catalog_context = "Available products:\n"
            for item in catalog[:10]:  # Limit to first 10 items
                catalog_context += f"- {item['name']}: {item['price_jod']} JOD\n"
        
        # Create prompt
        prompt = f"""You are a helpful sales assistant for {tenant_info.get('tenant_info', {}).get('display_name', 'an online store')} in Jordan. 
        
Respond in Jordanian Arabic dialect. Be friendly and helpful.

{catalog_context}

Customer message: {message}

Provide a helpful response in Jordanian Arabic:"""
        
        # Make OpenAI API call
        response = openai.ChatCompletion.create(
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
        # Check tenant authentication
        tenant_info = getattr(request, 'tenant_info', {})
        if not tenant_info.get('success'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get analytics data
        analytics = run_async(db.get_dashboard_analytics(tenant_info['tenant_id']))
        
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

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

@app.before_first_request
def initialize_app():
    """Initialize the application"""
    try:
        logger.info("Initializing IG-Shop-Agent backend...")
        
        # Initialize database
        run_async(init_database())
        
        logger.info("Backend initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        raise

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    # For local development
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=settings.debug
    ) 