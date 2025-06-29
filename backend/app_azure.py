"""
Simplified IG-Shop-Agent Flask Application for Azure Web Apps
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'fallback-secret-key')

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

# Environment variables check
@app.route('/')
def home():
    return jsonify({
        'message': 'IG Shop Agent API - Azure Compatible',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': {
            'meta_app_id': os.environ.get('META_APP_ID', 'not_set'),
            'openai_configured': 'yes' if os.environ.get('OPENAI_API_KEY') else 'no',
            'jwt_configured': 'yes' if os.environ.get('JWT_SECRET_KEY') else 'no'
        },
        'endpoints': {
            'health': '/health',
            'auth': '/auth/*',
            'api': '/api/*'
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Instagram OAuth endpoints
@app.route('/auth/instagram')
def instagram_auth():
    meta_app_id = os.environ.get('META_APP_ID')
    if not meta_app_id:
        return jsonify({'error': 'META_APP_ID not configured'}), 500
    
    redirect_uri = os.environ.get('META_REDIRECT_URI', 
                                 'https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback')
    
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={meta_app_id}&redirect_uri={redirect_uri}&scope=instagram_basic,instagram_manage_messages&response_type=code"
    
    return jsonify({
        'auth_url': auth_url,
        'status': 'ready'
    })

@app.route('/auth/instagram/callback')
def instagram_callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': error}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    return jsonify({
        'message': 'Instagram OAuth callback received',
        'code': code[:20] + '...',  # Partial code for security
        'status': 'success'
    })

# AI Chat endpoint
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    data = request.get_json()
    message = data.get('message', '')
    
    # Simple response for now
    response = {
        'message': f"أهلاً وسهلاً! شكراً لرسالتك: {message}",
        'timestamp': datetime.utcnow().isoformat(),
        'type': 'ai_response'
    }
    
    return jsonify(response)

# Basic API endpoints
@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    return jsonify({
        'business_name': 'Jordan Fashion Store',
        'email': 'owner@jordanfashion.com',
        'instagram_connected': True,
        'status': 'active'
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({
        'products': [
            {
                'id': 1,
                'name': 'فستان أنيق',
                'price': 45.0,
                'currency': 'JOD',
                'availability': 'available'
            },
            {
                'id': 2,
                'name': 'حقيبة يد',
                'price': 30.0,
                'currency': 'JOD',
                'availability': 'available'
            }
        ],
        'total': 2
    })

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify({
        'orders': [
            {
                'id': 1,
                'customer_name': 'سارة أحمد',
                'total_amount': 45.0,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
        ],
        'total': 1
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    return jsonify({
        'total_orders': 5,
        'total_revenue': 225.0,
        'currency': 'JOD',
        'active_conversations': 3,
        'conversion_rate': 15.2
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Azure Web App entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 