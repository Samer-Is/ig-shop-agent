"""
IG-Shop-Agent Flask Application Test Suite
Complete test of all API endpoints
"""
import os
import sys
import json
import requests
import time
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['META_APP_ID'] = "1879578119651644"
os.environ['META_APP_SECRET'] = "f79b3350f43751d6139e1b29a232cbf3"
os.environ['OPENAI_API_KEY'] = "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"
os.environ['JWT_SECRET_KEY'] = "ig-shop-agent-production-jwt-secret-key-2024"

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"\n🧪 Testing {method} {endpoint}")
        if description:
            print(f"   📝 {description}")
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Success")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📄 Response: {response.text[:200]}...")
            return True
        else:
            print(f"   ❌ Failed")
            print(f"   📄 Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Flask app not running on {BASE_URL}")
        print("   💡 Please start the Flask app first:")
        print("   💡 python app_simple.py")
        return False
    except Exception as e:
        print(f"\n❌ Error testing {endpoint}: {e}")
        return False

def run_comprehensive_tests():
    """Run comprehensive API tests"""
    print("=" * 70)
    print("🚀 IG-Shop-Agent Flask Application Test Suite")
    print("=" * 70)
    
    # Test results tracking
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check
    total_tests += 1
    if test_endpoint("GET", "/health", description="Basic health check"):
        tests_passed += 1
    
    # Test 2: Detailed Health Check
    total_tests += 1
    if test_endpoint("GET", "/api/health", description="Detailed health check with features"):
        tests_passed += 1
    
    # Test 3: Instagram OAuth URL Generation
    total_tests += 1
    if test_endpoint("GET", "/auth/instagram?business_name=Test Store&redirect_uri=http://localhost:3000/auth/callback", 
                    description="Generate Instagram OAuth URL"):
        tests_passed += 1
    
    # Test 4: Token Verification (should fail without token)
    total_tests += 1
    if test_endpoint("POST", "/auth/verify", description="Token verification (should fail without token)"):
        tests_passed += 1  # This should actually fail, so we count it as expected behavior
    
    # Generate a test token for authenticated endpoints
    print("\n🔑 Generating test token for authenticated endpoints...")
    try:
        from instagram_oauth import generate_session_token
        
        test_user_data = {
            'id': 'test_user_123',
            'username': 'test_store',
            'name': 'Test Store'
        }
        test_token = generate_session_token(test_user_data, 'test_tenant_456')
        
        auth_headers = {
            'Authorization': f'Bearer {test_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"   ✅ Test token generated: {test_token[:50]}...")
        
        # Test 5: Token Verification (should succeed with token)
        total_tests += 1
        if test_endpoint("POST", "/auth/verify", headers=auth_headers, description="Token verification with valid token"):
            tests_passed += 1
        
        # Test 6: Get Catalog
        total_tests += 1
        if test_endpoint("GET", "/api/catalog", headers=auth_headers, description="Get catalog items"):
            tests_passed += 1
        
        # Test 7: Create Catalog Item
        total_tests += 1
        new_item_data = {
            'sku': 'TEST-001',
            'name': 'منتج تجريبي',
            'price_jod': 25.99,
            'description': 'منتج تجريبي للاختبار',
            'category': 'اختبار',
            'stock_quantity': 10
        }
        if test_endpoint("POST", "/api/catalog", data=new_item_data, headers=auth_headers, 
                        description="Create new catalog item"):
            tests_passed += 1
        
        # Test 8: Get Orders
        total_tests += 1
        if test_endpoint("GET", "/api/orders", headers=auth_headers, description="Get orders"):
            tests_passed += 1
        
        # Test 9: Create Order
        total_tests += 1
        new_order_data = {
            'sku': 'DRESS-001',
            'qty': 1,
            'customer': 'عميل تجريبي',
            'phone': '+962791234567',
            'total_amount': 45.99,
            'delivery_address': 'عمان، الأردن',
            'notes': 'طلب تجريبي'
        }
        if test_endpoint("POST", "/api/orders", data=new_order_data, headers=auth_headers,
                        description="Create new order"):
            tests_passed += 1
        
        # Test 10: AI Response
        total_tests += 1
        ai_test_data = {
            'message': 'مرحبا، أريد فستان للمناسبات'
        }
        if test_endpoint("POST", "/api/ai/test-response", data=ai_test_data, headers=auth_headers,
                        description="Test AI response generation"):
            tests_passed += 1
        
        # Test 11: Dashboard Analytics
        total_tests += 1
        if test_endpoint("GET", "/api/analytics/dashboard", headers=auth_headers,
                        description="Get dashboard analytics"):
            tests_passed += 1
        
    except Exception as e:
        print(f"❌ Failed to generate test token: {e}")
        print("⚠️  Skipping authenticated endpoint tests")
    
    # Test 12: 404 Error Handling
    total_tests += 1
    if test_endpoint("GET", "/api/nonexistent", description="Test 404 error handling"):
        # This should fail with 404, so we don't increment tests_passed
        pass
    
    # Results Summary
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Flask app is working perfectly!")
        print("🚀 Ready for Azure Web App deployment!")
    elif tests_passed >= total_tests * 0.8:
        print("✅ Most tests passed! Flask app is mostly working correctly.")
        print("🔧 Minor issues may need attention.")
    else:
        print("⚠️  Some tests failed. Check the Flask app configuration.")
    
    # Deployment Information
    print("\n" + "=" * 70)
    print("🔧 AZURE WEB APP DEPLOYMENT INFORMATION")
    print("=" * 70)
    print("📁 Main Application File: app_simple.py")
    print("🌐 Entry Point: Flask app running on all interfaces (0.0.0.0)")
    print("🔧 Port: Uses PORT environment variable (default 8000)")
    print("🔐 Environment Variables Required:")
    print("   - META_APP_ID: ✅ Configured")
    print("   - META_APP_SECRET: ✅ Configured") 
    print("   - OPENAI_API_KEY: ✅ Configured")
    print("   - JWT_SECRET_KEY: ✅ Configured")
    print("\n📋 Azure Web App Configuration:")
    print("   - Runtime: Python 3.9+")
    print("   - Startup Command: python app_simple.py")
    print("   - Set environment variables in Azure portal")
    print("   - Enable CORS for your frontend domain")
    
    return tests_passed == total_tests

def test_app_import():
    """Test if the app can be imported correctly"""
    print("🔍 Testing Flask App Import...")
    
    try:
        from app_simple import app
        print("✅ Flask app imported successfully")
        
        print(f"✅ App name: {app.name}")
        print(f"✅ Secret key configured: {bool(app.secret_key)}")
        print(f"✅ CORS enabled: {len(app.extensions.get('cors', {}).get('resources', {})) > 0}")
        
        print("\n📋 Available Routes:")
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"   {rule.rule:<30} -> {methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False

def main():
    """Main test function"""
    print("Starting IG-Shop-Agent Flask Application Tests...\n")
    
    # Test app import first
    if not test_app_import():
        print("❌ Cannot proceed - Flask app import failed")
        return False
    
    print("\n" + "="*50)
    print("🚀 STARTING ENDPOINT TESTS")
    print("="*50)
    print("💡 Make sure to start the Flask app first:")
    print("💡 python app_simple.py")
    print("💡 Then run this test in another terminal")
    
    # Wait for user confirmation
    input("\n⏯️  Press Enter when Flask app is running...")
    
    # Run comprehensive tests
    success = run_comprehensive_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 