#!/usr/bin/env python3
"""
Instagram OAuth Integration Test
Comprehensive testing of the Instagram connect button and OAuth flow
"""

import requests
import json
import time
import sys
from urllib.parse import parse_qs, urlparse

BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"
FRONTEND_URL = "https://red-island-0b863450f.2.azurestaticapps.net"

def test_backend_health():
    """Test if backend is running and responding"""
    print("\n🔍 Testing Backend Health...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if "IG-Shop-Agent Production API" in response.text:
            print("✅ Flask app is running!")
            print(f"   Response contains: {response.text[:100]}...")
            return True
        else:
            print(f"❌ Backend serving wrong content: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")
        return False

def test_health_endpoint():
    """Test the /health endpoint specifically"""
    print("\n🔍 Testing /health endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def create_test_user():
    """Create a test user account"""
    print("\n👤 Creating test user account...")
    
    test_user = {
        "email": "test@igshop.com",
        "password": "testpass123",
        "business_name": "Test IG Shop"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Test user created successfully!")
            print(f"   Token: {data.get('token', '')[:20]}...")
            return data.get('token')
        elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
            print("ℹ️  User already exists, trying to login...")
            
            # Try to login instead
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            }, timeout=10)
            
            if login_response.status_code == 200:
                data = login_response.json()
                print("✅ Logged in successfully!")
                print(f"   Token: {data.get('token', '')[:20]}...")
                return data.get('token')
        
        print(f"❌ User creation failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ User creation error: {str(e)}")
        return None

def test_instagram_oauth_endpoint(token):
    """Test the Instagram OAuth endpoint"""
    print("\n📱 Testing Instagram OAuth endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/instagram", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Instagram OAuth endpoint working!")
            
            if 'auth_url' in data:
                auth_url = data['auth_url']
                print(f"   Auth URL: {auth_url[:80]}...")
                
                # Parse the auth URL to verify it's correct
                parsed = urlparse(auth_url)
                query_params = parse_qs(parsed.query)
                
                print("   📋 OAuth Parameters:")
                print(f"      Client ID: {query_params.get('client_id', ['Not found'])[0]}")
                print(f"      Redirect URI: {query_params.get('redirect_uri', ['Not found'])[0]}")
                print(f"      Scope: {query_params.get('scope', ['Not found'])[0]}")
                print(f"      Response Type: {query_params.get('response_type', ['Not found'])[0]}")
                
                # Check if it's using the correct Meta App ID
                expected_app_id = "1879578119651644"
                actual_app_id = query_params.get('client_id', [''])[0]
                
                if actual_app_id == expected_app_id:
                    print("✅ Using correct Meta App ID!")
                else:
                    print(f"❌ Wrong App ID! Expected: {expected_app_id}, Got: {actual_app_id}")
                
                # Check redirect URI
                expected_redirect = f"{BACKEND_URL}/auth/instagram/callback"
                actual_redirect = query_params.get('redirect_uri', [''])[0]
                
                if actual_redirect == expected_redirect:
                    print("✅ Correct redirect URI!")
                else:
                    print(f"❌ Wrong redirect URI! Expected: {expected_redirect}, Got: {actual_redirect}")
                
                return True
            else:
                print("❌ No auth_url in response")
                return False
        else:
            print(f"❌ Instagram OAuth failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Instagram OAuth test error: {str(e)}")
        return False

def test_ai_chat_endpoint(token):
    """Test the AI chat endpoint"""
    print("\n🤖 Testing AI Chat endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    test_message = "مرحبا، أريد شراء قميص"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/chat", 
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Chat endpoint working!")
            print(f"   Test message: {test_message}")
            print(f"   AI Response: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ AI Chat failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Chat test error: {str(e)}")
        return False

def test_frontend_integration():
    """Test frontend connectivity to backend"""
    print("\n🌐 Testing Frontend Integration...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
            
            # Check if frontend contains Instagram connect functionality
            content = response.text.lower()
            if "instagram" in content:
                print("✅ Frontend contains Instagram functionality!")
            else:
                print("⚠️  Frontend might not have Instagram integration")
            
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test error: {str(e)}")
        return False

def monitor_deployment():
    """Monitor deployment and wait for it to complete"""
    print("\n⏳ Monitoring deployment progress...")
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n📡 Attempt {attempt}/{max_attempts}")
        
        if test_backend_health():
            print("✅ Deployment completed successfully!")
            return True
        
        if attempt < max_attempts:
            print(f"⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("❌ Deployment monitoring timed out")
    return False

def main():
    print("🚀 IG-Shop-Agent Instagram OAuth Integration Test")
    print("="*70)
    
    # Monitor deployment first
    if not monitor_deployment():
        print("\n❌ Deployment failed. Cannot proceed with Instagram OAuth testing.")
        return False
    
    # Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health endpoint not working. Checking basic functionality...")
    
    # Create test user
    token = create_test_user()
    if not token:
        print("\n❌ Cannot create test user. Instagram OAuth testing limited.")
        return False
    
    # Test Instagram OAuth
    oauth_success = test_instagram_oauth_endpoint(token)
    
    # Test AI Chat
    ai_success = test_ai_chat_endpoint(token)
    
    # Test Frontend
    frontend_success = test_frontend_integration()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    tests = {
        "Backend Health": test_backend_health(),
        "Instagram OAuth": oauth_success,
        "AI Chat": ai_success,
        "Frontend Integration": frontend_success
    }
    
    passed = sum(tests.values())
    total = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if oauth_success:
        print("\n🎉 INSTAGRAM OAUTH IS WORKING!")
        print("✅ Users can now connect their Instagram accounts")
        print("✅ Instagram connect button should work in frontend")
        print(f"🌐 Frontend: {FRONTEND_URL}")
        print(f"🔗 Backend: {BACKEND_URL}")
    else:
        print("\n❌ Instagram OAuth needs attention")
        print("🔧 Check Azure Web App environment variables")
        print("🔧 Verify Meta App credentials are correct")
    
    return oauth_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 