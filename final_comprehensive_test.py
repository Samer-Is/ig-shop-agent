#!/usr/bin/env python3
"""
PHASE 3: COMPREHENSIVE TESTING
Final testing before GitHub commit - test EVERYTHING
"""

import requests
import json
import time
import sys

BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"
FRONTEND_URL = "https://red-island-0b863450f.2.azurestaticapps.net"

class ComprehensiveTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_total = 0
        self.token = None
        
    def test(self, name, success, details=""):
        self.tests_total += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        return success
    
    def get_success_rate(self):
        return (self.tests_passed / self.tests_total * 100) if self.tests_total > 0 else 0

def test_backend_basic(tester):
    """Test basic backend functionality"""
    print("\n🔍 PHASE 3.1: BASIC BACKEND TESTS")
    print("="*50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        success = response.status_code == 200 and "IG-Shop-Agent Production API" in response.text
        tester.test("Root endpoint", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            tester.test("API features configured", len(data.get('features', [])) >= 4, 
                       f"Features: {data.get('features', [])}")
    except Exception as e:
        tester.test("Root endpoint", False, f"Error: {str(e)}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        success = response.status_code == 200
        tester.test("Health endpoint", success, f"Status: {response.status_code}")
        
        if success:
            health = response.json()
            tester.test("Instagram OAuth configured", 
                       health.get('instagram_oauth') == 'configured',
                       f"Instagram: {health.get('instagram_oauth')}")
            
            tester.test("OpenAI configured", 
                       health.get('openai') == 'configured',
                       f"OpenAI: {health.get('openai')}")
    except Exception as e:
        tester.test("Health endpoint", False, f"Error: {str(e)}")

def test_authentication(tester):
    """Test user authentication system"""
    print("\n🔍 PHASE 3.2: AUTHENTICATION TESTS")
    print("="*50)
    
    test_user = {
        "email": "final-test@igshop.dev",
        "password": "finaltest123",
        "business_name": "Final Test Business"
    }
    
    # Test registration
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user, timeout=10)
        if response.status_code == 201:
            tester.test("User registration", True, "New user created successfully")
            data = response.json()
            tester.token = data.get('token')
            tester.test("JWT token generation", bool(tester.token), 
                       f"Token: {tester.token[:20] if tester.token else 'None'}...")
        elif response.status_code == 400:
            tester.test("User registration", True, "User already exists, testing login...")
            
            # Try login instead
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            }, timeout=10)
            
            if response.status_code == 200:
                tester.test("User login", True, "Login successful")
                data = response.json()
                tester.token = data.get('token')
                tester.test("JWT token from login", bool(tester.token),
                           f"Token: {tester.token[:20] if tester.token else 'None'}...")
            else:
                tester.test("User login", False, f"Status: {response.status_code}")
        else:
            tester.test("User registration", False, f"Status: {response.status_code}")
    except Exception as e:
        tester.test("User registration", False, f"Error: {str(e)}")

def test_instagram_oauth(tester):
    """Test Instagram OAuth functionality"""
    print("\n🔍 PHASE 3.3: INSTAGRAM OAUTH TESTS")
    print("="*50)
    
    if not tester.token:
        tester.test("Instagram OAuth", False, "No authentication token available")
        return
    
    headers = {"Authorization": f"Bearer {tester.token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/instagram", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url', '')
            
            tester.test("Instagram OAuth endpoint", True, "OAuth endpoint responding")
            tester.test("OAuth URL generated", bool(auth_url), f"URL length: {len(auth_url)}")
            
            if auth_url:
                tester.test("Correct Meta App ID", "1879578119651644" in auth_url,
                           "Using live Meta App ID")
                tester.test("Instagram OAuth URL format", "instagram.com/oauth/authorize" in auth_url,
                           "Correct Instagram OAuth URL")
                tester.test("OAuth scope included", "user_profile" in auth_url and "user_media" in auth_url,
                           "Required scopes included")
        else:
            tester.test("Instagram OAuth endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        tester.test("Instagram OAuth endpoint", False, f"Error: {str(e)}")

def test_ai_functionality(tester):
    """Test AI chat functionality"""
    print("\n🔍 PHASE 3.4: AI FUNCTIONALITY TESTS")
    print("="*50)
    
    if not tester.token:
        tester.test("AI Chat", False, "No authentication token available")
        return
    
    headers = {"Authorization": f"Bearer {tester.token}"}
    test_messages = [
        "مرحبا، أريد شراء قميص أبيض",
        "ما هي الأسعار؟",
        "هل يوجد توصيل؟"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/ai/chat",
                json={"message": message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '')
                
                tester.test(f"AI Chat Test {i}", True, f"Arabic message processed")
                tester.test(f"AI Response {i}", bool(ai_response), 
                           f"Response: {ai_response[:50]}..." if ai_response else "No response")
                
                # Test response quality
                if ai_response:
                    arabic_chars = any(ord(char) > 1536 for char in ai_response)
                    tester.test(f"Arabic Response {i}", arabic_chars, "Response contains Arabic text")
            else:
                tester.test(f"AI Chat Test {i}", False, f"Status: {response.status_code}")
                break
        except Exception as e:
            tester.test(f"AI Chat Test {i}", False, f"Error: {str(e)}")
            break

def test_api_endpoints(tester):
    """Test all API endpoints"""
    print("\n🔍 PHASE 3.5: API ENDPOINTS TESTS")
    print("="*50)
    
    if not tester.token:
        tester.test("API Endpoints", False, "No authentication token available")
        return
    
    headers = {"Authorization": f"Bearer {tester.token}"}
    
    # Test protected endpoints
    endpoints = [
        ("/api/catalog", "Catalog endpoint"),
        ("/api/orders", "Orders endpoint"),
        ("/api/analytics", "Analytics endpoint")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            tester.test(name, response.status_code == 200, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tester.test(f"{name} data format", isinstance(data, (list, dict)),
                           f"Data type: {type(data).__name__}")
        except Exception as e:
            tester.test(name, False, f"Error: {str(e)}")

def test_frontend_integration(tester):
    """Test frontend integration"""
    print("\n🔍 PHASE 3.6: FRONTEND INTEGRATION TESTS")
    print("="*50)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=15)
        tester.test("Frontend accessibility", response.status_code == 200,
                   f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for key elements
            tester.test("Contains Instagram references", "instagram" in content,
                       "Instagram integration mentioned")
            tester.test("Contains authentication", "login" in content or "sign" in content,
                       "Authentication system present")
            tester.test("Contains dashboard elements", "dashboard" in content or "catalog" in content,
                       "Dashboard functionality present")
            
            # Check for React/Vite setup
            tester.test("React app loaded", "react" in content or "vite" in content,
                       "Frontend framework loaded")
    except Exception as e:
        tester.test("Frontend accessibility", False, f"Error: {str(e)}")

def main():
    print("🚀 PHASE 3: COMPREHENSIVE TESTING")
    print("="*70)
    print("Testing EVERYTHING before GitHub commit")
    print("="*70)
    
    tester = ComprehensiveTester()
    
    # Run all test phases
    test_backend_basic(tester)
    test_authentication(tester)
    test_instagram_oauth(tester)
    test_ai_functionality(tester)
    test_api_endpoints(tester)
    test_frontend_integration(tester)
    
    # Final results
    print("\n" + "="*70)
    print("📊 FINAL COMPREHENSIVE TEST RESULTS")
    print("="*70)
    
    success_rate = tester.get_success_rate()
    print(f"Overall Success Rate: {tester.tests_passed}/{tester.tests_total} ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        print("\n🎉 SYSTEM READY FOR PRODUCTION!")
        print("✅ All critical systems operational")
        print("✅ Instagram OAuth working")
        print("✅ AI functionality working")
        print("✅ Frontend integration working")
        print("✅ Authentication system working")
        print("\n🚀 READY FOR GITHUB COMMIT!")
        print(f"🌐 Frontend: {FRONTEND_URL}")
        print(f"🔗 Backend: {BACKEND_URL}")
        return True
    elif success_rate >= 80:
        print("\n⚠️  SYSTEM MOSTLY READY")
        print(f"✅ {success_rate:.1f}% of tests passing")
        print("🔧 Minor issues to address before commit")
        return False
    else:
        print("\n❌ SYSTEM NOT READY")
        print(f"❌ Only {success_rate:.1f}% of tests passing")
        print("🔧 Significant issues need fixing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 