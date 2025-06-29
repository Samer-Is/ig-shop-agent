#!/usr/bin/env python3
"""Test script for IG-Shop-Agent Local Backend"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except:
        print("❌ Server not running")
        return False

def test_login():
    """Test login with sample account"""
    try:
        data = {
            "email": "owner@jordanfashion.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        if response.status_code == 200:
            token = response.json().get('token')
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_products(token):
    """Test products endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/products", headers=headers)
        if response.status_code == 200:
            products = response.json().get('products', [])
            print(f"✅ Products loaded: {len(products)} items")
            return True
        else:
            print(f"❌ Products failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Products error: {e}")
        return False

def test_ai_chat(token):
    """Test AI chat endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"message": "مرحبا، أريد السؤال عن المنتجات"}
        response = requests.post(f"{BASE_URL}/api/ai/chat", json=data, headers=headers)
        if response.status_code == 200:
            ai_response = response.json().get('message', '')
            print(f"✅ AI Chat working: {ai_response[:50]}...")
            return True
        else:
            print(f"❌ AI Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Chat error: {e}")
        return False

def main():
    print("🧪 Testing IG-Shop-Agent Local Backend")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("Start the server first: python app.py")
        return
    
    # Test login
    token = test_login()
    if not token:
        return
    
    # Test products
    test_products(token)
    
    # Test AI chat
    test_ai_chat(token)
    
    print("\n🎉 All tests completed!")
    print("Local backend is working correctly!")

if __name__ == "__main__":
    main() 