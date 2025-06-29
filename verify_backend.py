#!/usr/bin/env python3
"""
Backend Verification Script
Tests the production Flask backend endpoints
"""

import requests
import json
import time
import os

# Backend URL
BACKEND_URL = "https://igshop-dev-yjhtoi-api.azurewebsites.net"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a specific endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n🔍 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Response: {json.dumps(result, indent=2)[:200]}...")
                return True
            except:
                print(f"   ✅ Response: {response.text[:100]}...")
                return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {str(e)}")
        return False

def main():
    print("🚀 IG-Shop-Agent Backend Verification")
    print("="*50)
    
    # Test basic endpoints
    tests = [
        ("/", "GET"),
        ("/health", "GET"),
    ]
    
    # Test authentication endpoints
    auth_tests = [
        ("/auth/register", "POST", {
            "email": "test@example.com",
            "password": "testpass123",
            "business_name": "Test Business"
        }),
        ("/auth/login", "POST", {
            "email": "test@example.com", 
            "password": "testpass123"
        })
    ]
    
    results = []
    
    # Run basic tests
    for endpoint, method in tests:
        result = test_endpoint(endpoint, method)
        results.append((endpoint, result))
    
    # Test authentication
    token = None
    for endpoint, method, data in auth_tests:
        result = test_endpoint(endpoint, method, data)
        results.append((endpoint, result))
        
        # Try to extract token from login
        if endpoint == "/auth/login" and result:
            try:
                response = requests.post(f"{BACKEND_URL}{endpoint}", json=data)
                if response.status_code == 200:
                    token = response.json().get('token')
                    print(f"   🔑 Got auth token: {token[:20]}...")
            except:
                pass
    
    # Test protected endpoints if we have a token
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        protected_tests = [
            ("/api/catalog", "GET"),
            ("/api/orders", "GET"),  
            ("/api/analytics", "GET"),
            ("/auth/instagram", "GET")
        ]
        
        for endpoint, method in protected_tests:
            result = test_endpoint(endpoint, method, headers=headers)
            results.append((endpoint, result))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    elif passed > total * 0.7:
        print("\n⚠️  Most tests passed. Backend is mostly functional.")
    else:
        print("\n❌ Multiple test failures. Backend needs attention.")
    
    # Final connectivity test
    print("\n🔗 Testing Production Frontend Integration:")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible from frontend")
            print("🌐 Frontend URL: https://red-island-0b863450f.2.azurestaticapps.net")
        else:
            print("❌ Backend connectivity issues")
    except:
        print("❌ Backend is not accessible")

if __name__ == "__main__":
    main() 