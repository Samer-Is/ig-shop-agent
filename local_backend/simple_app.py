#!/usr/bin/env python3
"""Simple test Flask app to verify local setup works"""

from flask import Flask, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'IG-Shop-Agent Local Backend - WORKING!',
        'status': 'running',
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': [
            'GET / - This message',
            'GET /health - Health check',
            'POST /test-login - Test login',
            'GET /test-products - Test products'
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Local backend is working perfectly!',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/test-login', methods=['POST'])
def test_login():
    return jsonify({
        'message': 'Login test successful',
        'token': 'test-token-12345',
        'user': {
            'email': 'owner@jordanfashion.com',
            'business_name': 'Jordan Fashion Store'
        }
    })

@app.route('/test-products')
def test_products():
    return jsonify({
        'products': [
            {'id': 1, 'name': 'فستان أنيق', 'price': 45.0, 'currency': 'JOD'},
            {'id': 2, 'name': 'حقيبة يد', 'price': 30.0, 'currency': 'JOD'},
            {'id': 3, 'name': 'حذاء كعب عالي', 'price': 35.0, 'currency': 'JOD'}
        ],
        'total': 3,
        'message': 'Test products loaded successfully!'
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Test Server...")
    print("📍 URL: http://localhost:8000")
    print("🧪 This is a test version to verify everything works")
    app.run(host='0.0.0.0', port=8000, debug=True) 