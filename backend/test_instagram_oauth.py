"""
IG-Shop-Agent Instagram OAuth Test Script
Test Instagram OAuth integration and authentication flow
"""
import os
import sys
import json
from typing import Dict

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from instagram_oauth import (
    instagram_oauth, 
    get_instagram_auth_url, 
    handle_oauth_callback,
    validate_instagram_token,
    generate_session_token,
    verify_session_token
)

def test_oauth_url_generation():
    """Test Instagram OAuth URL generation"""
    print("🔗 Testing Instagram OAuth URL Generation...")
    
    try:
        # Test with mock data
        redirect_uri = "http://localhost:3000/auth/callback"
        business_name = "Test Fashion Store"
        
        auth_url, state = get_instagram_auth_url(redirect_uri, business_name)
        
        # Basic validation
        if auth_url and state:
            print("✅ OAuth URL generated successfully")
            print(f"   State length: {len(state)}")
            print(f"   URL contains client_id: {'client_id=' in auth_url}")
            print(f"   URL contains redirect_uri: {redirect_uri.replace(':', '%3A') in auth_url}")
            print(f"   URL contains scope: {'scope=' in auth_url}")
            
            # Check state storage
            if state in instagram_oauth._oauth_states:
                print("✅ OAuth state stored correctly")
                state_data = instagram_oauth._oauth_states[state]
                print(f"   Business name: {state_data.get('business_name')}")
                print(f"   Redirect URI: {state_data.get('redirect_uri')}")
            else:
                print("❌ OAuth state not stored")
                return False
            
            return True
        else:
            print("❌ Failed to generate OAuth URL")
            return False
            
    except Exception as e:
        print(f"❌ OAuth URL generation failed: {e}")
        return False

def test_jwt_token_functionality():
    """Test JWT token generation and verification"""
    print("\n🔐 Testing JWT Token Functionality...")
    
    try:
        # Mock user data
        user_data = {
            'id': '12345',
            'username': 'testuser',
            'name': 'Test User'
        }
        tenant_id = 'tenant-123'
        
        # Generate JWT token
        jwt_token = generate_session_token(user_data, tenant_id)
        
        if jwt_token:
            print("✅ JWT token generated successfully")
            print(f"   Token length: {len(jwt_token)}")
            
            # Verify JWT token
            payload = verify_session_token(jwt_token)
            
            if payload:
                print("✅ JWT token verified successfully")
                print(f"   User ID: {payload.get('user_id')}")
                print(f"   Username: {payload.get('username')}")
                print(f"   Tenant ID: {payload.get('tenant_id')}")
                print(f"   Issuer: {payload.get('iss')}")
                
                # Validate payload data
                if (payload.get('user_id') == user_data['id'] and 
                    payload.get('username') == user_data['username'] and
                    payload.get('tenant_id') == tenant_id):
                    print("✅ JWT payload validation successful")
                    return True
                else:
                    print("❌ JWT payload validation failed")
                    return False
            else:
                print("❌ JWT token verification failed")
                return False
        else:
            print("❌ JWT token generation failed")
            return False
            
    except Exception as e:
        print(f"❌ JWT token functionality test failed: {e}")
        return False

def test_token_encryption():
    """Test token encryption/decryption functionality"""
    print("\n🔒 Testing Token Encryption...")
    
    try:
        test_token = "fake_access_token_12345"
        
        # Encrypt token
        encrypted_token = instagram_oauth.encrypt_token(test_token)
        
        if encrypted_token and encrypted_token != test_token:
            print("✅ Token encryption successful")
            print(f"   Original length: {len(test_token)}")
            print(f"   Encrypted length: {len(encrypted_token)}")
            
            # Decrypt token
            decrypted_token = instagram_oauth.decrypt_token(encrypted_token)
            
            if decrypted_token == test_token:
                print("✅ Token decryption successful")
                print(f"   Decrypted matches original: {decrypted_token == test_token}")
                return True
            else:
                print(f"❌ Token decryption failed: '{decrypted_token}' != '{test_token}'")
                return False
        else:
            print("❌ Token encryption failed or returned same token")
            return False
            
    except Exception as e:
        print(f"❌ Token encryption test failed: {e}")
        return False

def test_oauth_state_management():
    """Test OAuth state management"""
    print("\n📝 Testing OAuth State Management...")
    
    try:
        # Generate multiple states
        redirect_uri = "http://localhost:3000/auth/callback"
        
        auth_url1, state1 = get_instagram_auth_url(redirect_uri, "Store 1")
        auth_url2, state2 = get_instagram_auth_url(redirect_uri, "Store 2")
        
        if state1 != state2:
            print("✅ Unique states generated")
            print(f"   State 1: {state1[:10]}...")
            print(f"   State 2: {state2[:10]}...")
        else:
            print("❌ States are not unique")
            return False
        
        # Check state data
        state1_data = instagram_oauth._oauth_states.get(state1)
        state2_data = instagram_oauth._oauth_states.get(state2)
        
        if state1_data and state2_data:
            print("✅ State data stored correctly")
            print(f"   Store 1 business name: {state1_data.get('business_name')}")
            print(f"   Store 2 business name: {state2_data.get('business_name')}")
            
            if (state1_data.get('business_name') == "Store 1" and 
                state2_data.get('business_name') == "Store 2"):
                print("✅ State data validation successful")
                return True
            else:
                print("❌ State data validation failed")
                return False
        else:
            print("❌ State data not stored properly")
            return False
            
    except Exception as e:
        print(f"❌ OAuth state management test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration Loading...")
    
    try:
        # Check if Instagram OAuth is properly configured
        app_id = instagram_oauth.app_id
        app_secret = instagram_oauth.app_secret
        graph_version = instagram_oauth.graph_api_version
        base_url = instagram_oauth.base_url
        
        print(f"✅ App ID configured: {bool(app_id)}")
        print(f"✅ App Secret configured: {bool(app_secret)}")
        print(f"✅ Graph API version: {graph_version}")
        print(f"✅ Base URL: {base_url}")
        
        # Check encryption key
        encryption_key = instagram_oauth.encryption_key
        if encryption_key:
            print("✅ Encryption key generated/loaded")
            print(f"   Key length: {len(encryption_key)}")
        else:
            print("❌ Encryption key not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_production_readiness():
    """Test production readiness"""
    print("\n🚀 Testing Production Readiness...")
    
    # Check required environment variables
    required_vars = [
        'META_APP_ID',
        'META_APP_SECRET',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    configured_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value.strip():
            configured_vars.append(var)
        else:
            missing_vars.append(var)
    
    print(f"✅ Configured variables: {len(configured_vars)}/{len(required_vars)}")
    for var in configured_vars:
        print(f"   ✅ {var}")
    
    if missing_vars:
        print(f"ℹ️  Missing variables (for production): {len(missing_vars)}")
        for var in missing_vars:
            print(f"   ⚠️  {var}")
        print("\n💡 To make production-ready:")
        print("   1. Set up Meta Developer App")
        print("   2. Configure environment variables")
        print("   3. Test with real Instagram credentials")
        print("   4. Set up proper redirect URIs")
    else:
        print("🎉 All required variables are configured!")
        print("✅ Instagram OAuth is production-ready")
    
    return len(missing_vars) == 0

def main():
    """Main test function"""
    print("=" * 60)
    print("🔐 IG-Shop-Agent Instagram OAuth Test Suite")
    print("=" * 60)
    
    tests = [
        ("OAuth URL Generation", test_oauth_url_generation),
        ("JWT Token Functionality", test_jwt_token_functionality),
        ("Token Encryption", test_token_encryption),
        ("OAuth State Management", test_oauth_state_management),
        ("Configuration Loading", test_configuration_loading),
        ("Production Readiness", test_production_readiness)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL INSTAGRAM OAUTH TESTS PASSED!")
            print("✅ Instagram OAuth integration is working correctly")
        else:
            print(f"⚠️  {total - passed} tests failed")
            print("🔧 Some functionality needs attention")
        
        print("=" * 60)
        return passed == total
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 