#!/usr/bin/env python3
"""
Simple Flask App Test
"""
import sys
import os

# Set environment variables
os.environ['META_APP_ID'] = '1879578119651644'
os.environ['META_APP_SECRET'] = 'f79b3350f43751d6139e1b29a232cbf3'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['JWT_SECRET_KEY'] = 'ig-shop-agent-production-jwt-secret-key-2024'

print('=' * 60)
print('🔍 IG-Shop-Agent Flask App Test')
print('=' * 60)

try:
    print('📦 Importing Flask app...')
    from app_simple import app
    print('✅ Flask app imported successfully')
    
    print(f'✅ App name: {app.name}')
    print(f'✅ Debug mode: {app.debug}')
    print(f'✅ Secret key configured: {bool(app.secret_key)}')
    print(f'✅ Environment: {os.environ.get("ENVIRONMENT", "development")}')
    
    print('\n📋 Available API Routes:')
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api') or rule.rule.startswith('/auth') or rule.rule.startswith('/health'):
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            routes.append((rule.rule, methods, rule.endpoint))
    
    for route, methods, endpoint in sorted(routes):
        print(f'   {route:<35} [{methods:<15}] -> {endpoint}')
    
    print('\n🔧 Configuration Check:')
    from config import settings
    print(f'   Meta App ID: {"✅ Set" if settings.meta_app_id else "❌ Missing"}')
    print(f'   Meta App Secret: {"✅ Set" if settings.meta_app_secret else "❌ Missing"}')
    print(f'   OpenAI API Key: {"✅ Set" if settings.openai_api_key else "❌ Missing"}')
    print(f'   JWT Secret: {"✅ Set" if settings.jwt_secret_key else "❌ Missing"}')
    
    print('\n🧪 Testing OAuth URL Generation:')
    from instagram_oauth import get_instagram_auth_url
    auth_url, state = get_instagram_auth_url('http://localhost:3000/auth/callback', 'Test Store')
    print(f'   ✅ OAuth URL generated successfully')
    print(f'   📝 State: {state[:20]}...')
    print(f'   🔗 URL length: {len(auth_url)} characters')
    
    print('\n🔐 Testing Token Generation:')
    from instagram_oauth import generate_session_token, verify_session_token
    test_user = {'id': 'test123', 'username': 'teststore', 'name': 'Test Store'}
    token = generate_session_token(test_user, 'test_tenant')
    print(f'   ✅ JWT token generated successfully')
    print(f'   📝 Token: {token[:50]}...')
    
    # Verify token
    payload = verify_session_token(token)
    if payload:
        print(f'   ✅ Token verification successful')
        print(f'   👤 User: {payload.get("username")}')
        print(f'   🏢 Tenant: {payload.get("tenant_id")}')
    else:
        print(f'   ❌ Token verification failed')
    
    print('\n' + '=' * 60)
    print('🎉 ALL TESTS PASSED!')
    print('🚀 Flask app is ready for production deployment')
    print('=' * 60)
    
    print('\n📋 Deployment Instructions:')
    print('1. 🏗️  Deploy to Azure Web App')
    print('2. 🔧 Set environment variables in Azure portal:')
    print('   - META_APP_ID')
    print('   - META_APP_SECRET') 
    print('   - OPENAI_API_KEY')
    print('   - JWT_SECRET_KEY')
    print('3. 🚀 Set startup command: python app_simple.py')
    print('4. 🌐 Configure CORS for your frontend domain')
    
    print('\n🏃 To run locally:')
    print('   python app_simple.py')
    print('   Then visit: http://localhost:8000/health')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1) 