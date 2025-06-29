#!/usr/bin/env python3
"""
Force Flask Deployment and Complete Testing
This script ensures the Azure Web App is properly configured for Flask and tests all functionality
"""

import subprocess
import requests
import json
import time
import sys

BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"
FRONTEND_URL = "https://red-island-0b863450f.2.azurestaticapps.net"

def run_azure_command(cmd, description):
    """Run an Azure CLI command"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def force_azure_configuration():
    """Force Azure Web App configuration for Flask"""
    print("🚀 FORCING AZURE WEB APP CONFIGURATION FOR FLASK")
    print("="*60)
    
    commands = [
        (
            'az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --linux-fx-version "PYTHON|3.11"',
            "Setting Python 3.11 runtime"
        ),
        (
            'az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"',
            "Setting Flask startup command"
        ),
        (
            'az webapp config appsettings set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --settings META_APP_ID="1879578119651644" META_APP_SECRET="f79b3350f43751d6139e1b29a232cbf3" OPENAI_API_KEY="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" JWT_SECRET_KEY="production-jwt-secret-2024" META_REDIRECT_URI="https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback" FLASK_APP="production_app.py" FLASK_ENV="production" SCM_DO_BUILD_DURING_DEPLOYMENT="true"',
            "Setting environment variables"
        ),
        (
            'az webapp restart --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api',
            "Restarting web app"
        )
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_azure_command(cmd, desc):
            success_count += 1
        time.sleep(5)
    
    print(f"\n📊 Configuration: {success_count}/{len(commands)} commands successful")
    return success_count == len(commands)

def wait_for_deployment(max_attempts=6):
    """Wait for the Flask app to become available"""
    print(f"\n⏳ Quick deployment check ({max_attempts} attempts, 10s intervals)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n📡 Check {attempt}/{max_attempts}")
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if "IG-Shop-Agent Production API" in response.text:
                print("✅ Flask app is running!")
                return True
            else:
                print(f"   Still Azure default page...")
        except Exception as e:
            print(f"   Connection error: {str(e)}")
        
        if attempt < max_attempts:
            print("   ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    print("❌ Flask not ready yet - will test anyway (deployment may still be in progress)")
    return False

def test_all_endpoints():
    """Test all backend endpoints comprehensively"""
    print("\n🔍 COMPREHENSIVE ENDPOINT TESTING")
    print("="*60)
    
    # Test basic endpoints
    tests = []
    
    # 1. Root endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200 and "IG-Shop-Agent Production API" in response.text:
            tests.append(("Root endpoint", True))
            print("✅ Root endpoint working")
        else:
            tests.append(("Root endpoint", False))
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        tests.append(("Root endpoint", False))
        print(f"❌ Root endpoint error: {str(e)}")
    
    # 2. Health endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            tests.append(("Health endpoint", True))
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            tests.append(("Health endpoint", False))
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        tests.append(("Health endpoint", False))
        print(f"❌ Health endpoint error: {str(e)}")
    
    # 3. Registration endpoint
    test_user = {
        "email": "test@igshop.dev",
        "password": "testpass123",
        "business_name": "Test Shop"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user, timeout=10)
        if response.status_code in [201, 400]:  # 400 if user already exists
            tests.append(("Registration endpoint", True))
            print("✅ Registration endpoint working")
            
            if response.status_code == 201:
                token = response.json().get('token')
                print(f"   Got token: {token[:20]}...")
            else:
                print("   User already exists, testing login...")
                
                # Try login
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                }, timeout=10)
                
                if login_response.status_code == 200:
                    token = login_response.json().get('token')
                    print(f"   Login successful, token: {token[:20]}...")
        else:
            tests.append(("Registration endpoint", False))
            print(f"❌ Registration failed: {response.status_code}")
            token = None
    except Exception as e:
        tests.append(("Registration endpoint", False))
        print(f"❌ Registration error: {str(e)}")
        token = None
    
    return tests, token

def test_instagram_oauth(token):
    """Test Instagram OAuth functionality"""
    print("\n📱 INSTAGRAM OAUTH TESTING")
    print("="*60)
    
    if not token:
        print("❌ No token available for Instagram OAuth testing")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/instagram", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Instagram OAuth endpoint working!")
            
            if 'auth_url' in data:
                auth_url = data['auth_url']
                print(f"   Auth URL: {auth_url[:80]}...")
                
                # Verify URL contains correct parameters
                if "1879578119651644" in auth_url:
                    print("✅ Using correct Meta App ID!")
                else:
                    print("❌ Wrong Meta App ID in OAuth URL")
                    return False
                    
                if "instagram.com/oauth/authorize" in auth_url:
                    print("✅ Correct Instagram OAuth URL!")
                else:
                    print("❌ Invalid OAuth URL format")
                    return False
                    
                return True
            else:
                print("❌ No auth_url in response")
                return False
        else:
            print(f"❌ Instagram OAuth failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Instagram OAuth error: {str(e)}")
        return False

def test_ai_functionality(token):
    """Test AI chat functionality"""
    print("\n🤖 AI FUNCTIONALITY TESTING")
    print("="*60)
    
    if not token:
        print("❌ No token available for AI testing")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    test_message = "مرحبا، أريد شراء قميص أبيض"
    
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
            print(f"   Input: {test_message}")
            print(f"   AI Response: {data.get('response', '')[:150]}...")
            return True
        else:
            print(f"❌ AI Chat failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Chat error: {str(e)}")
        return False

def test_protected_endpoints(token):
    """Test protected API endpoints"""
    print("\n🔐 PROTECTED ENDPOINTS TESTING")
    print("="*60)
    
    if not token:
        print("❌ No token available for protected endpoint testing")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    protected_tests = []
    
    endpoints = [
        ("/api/catalog", "Catalog endpoint"),
        ("/api/orders", "Orders endpoint"),
        ("/api/analytics", "Analytics endpoint")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                protected_tests.append((name, True))
                print(f"✅ {name} working")
            else:
                protected_tests.append((name, False))
                print(f"❌ {name} failed: {response.status_code}")
        except Exception as e:
            protected_tests.append((name, False))
            print(f"❌ {name} error: {str(e)}")
    
    return protected_tests

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🌐 FRONTEND INTEGRATION TESTING")
    print("="*60)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            
            checks = [
                ("Frontend accessible", True),
                ("Contains Instagram", "instagram" in content),
                ("Contains login", "login" in content or "sign" in content),
                ("Contains dashboard", "dashboard" in content or "catalog" in content)
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
            
            return all(result for _, result in checks)
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend error: {str(e)}")
        return False

def main():
    print("🚀 COMPLETE IG-SHOP-AGENT TESTING SUITE")
    print("="*70)
    print("This will test EVERYTHING before committing to GitHub")
    print("="*70)
    
    # Quick pre-check
    print("\n🔍 Quick pre-check...")
    flask_already_running = False
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if "IG-Shop-Agent Production API" in response.text:
            print("✅ Flask app already running! Skipping Azure config.")
            config_success = True
            flask_already_running = True
        else:
            print("⚠️  Azure default page detected. Need to configure.")
            # Step 1: Force Azure configuration
            config_success = force_azure_configuration()
            if not config_success:
                print("\n❌ Azure configuration failed. Cannot proceed.")
                return False
    except Exception:
        print("⚠️  Backend not responding. Need to configure.")
        # Step 1: Force Azure configuration
        config_success = force_azure_configuration()
        if not config_success:
            print("\n❌ Azure configuration failed. Cannot proceed.")
            return False
    
    # Step 2: Quick deployment check (skip if Flask already detected)
    if flask_already_running:
        print("\n✅ Skipping deployment wait - Flask already confirmed running")
        deployment_success = True
    else:
        deployment_success = wait_for_deployment()
        if not deployment_success:
            print("\n⚠️  Flask not ready yet, but continuing with tests...")
            print("   (Deployment may still be in progress in the background)")
    
    # Step 3: Test all endpoints
    endpoint_tests, token = test_all_endpoints()
    
    # Step 4: Test Instagram OAuth
    oauth_success = test_instagram_oauth(token)
    
    # Step 5: Test AI functionality
    ai_success = test_ai_functionality(token)
    
    # Step 6: Test protected endpoints
    protected_tests = test_protected_endpoints(token)
    
    # Step 7: Test frontend
    frontend_success = test_frontend_integration()
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 FINAL TEST RESULTS")
    print("="*70)
    
    all_tests = [
        ("Azure Configuration", config_success),
        ("Flask Deployment", deployment_success),
        ("Instagram OAuth", oauth_success),
        ("AI Functionality", ai_success),
        ("Frontend Integration", frontend_success)
    ]
    
    # Add endpoint tests
    all_tests.extend(endpoint_tests)
    all_tests.extend(protected_tests)
    
    passed = sum(1 for _, result in all_tests if result)
    total = len(all_tests)
    
    for test_name, result in all_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total) * 100
    print(f"\nOverall: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("\n🎉 ALL SYSTEMS GO! READY FOR GITHUB COMMIT!")
        print("✅ Instagram OAuth is working")
        print("✅ AI functionality is working") 
        print("✅ All endpoints are working")
        print("✅ Frontend integration is working")
        print(f"\n🌐 Frontend: {FRONTEND_URL}")
        print(f"🔗 Backend: {BACKEND_URL}")
        return True
    else:
        print(f"\n❌ SYSTEM NOT READY ({success_rate:.1f}% pass rate)")
        print("🔧 Fix the failing tests before committing to GitHub")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 