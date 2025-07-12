#!/usr/bin/env python3
"""
Test script for Order Entity Recognition via API
Tests the deployed backend with order processing capabilities
"""

import requests
import json
import time

# API base URL
API_BASE = "https://igshop-api.azurewebsites.net"

def test_ai_conversation_endpoint():
    """Test the AI conversation endpoint with order scenarios"""
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Complete Order Information",
            "message": "بدي أطلب فستان صيفي أزرق مقاس M، اسمي أحمد محمد، رقم تلفوني 0791234567، وعنواني شارع الملك حسين، عمان",
            "expected_intent": "order_placement"
        },
        {
            "name": "Partial Order Information", 
            "message": "بدي أطلب الفستان الأزرق",
            "expected_intent": "order_placement"
        },
        {
            "name": "Product Inquiry",
            "message": "شو سعر الفستان الأزرق؟",
            "expected_intent": "price_check"
        },
        {
            "name": "Order with Missing Address",
            "message": "بدي أطلب حذاء رياضي أبيض مقاس 42، اسمي سارة أحمد، رقمي 0791234567",
            "expected_intent": "order_placement"
        }
    ]
    
    print("🧪 Testing AI Order Entity Recognition via API\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Test {i}: {scenario['name']}")
        print(f"Message: {scenario['message']}")
        
        try:
            # Call the AI test endpoint
            response = requests.post(
                f"{API_BASE}/api/conversations/ai/test-response",
                json={
                    "message": scenario['message']
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('ai_response', 'No response')
                
                print(f"✅ API Response: {ai_response}")
                
                # Check for order creation indicators
                if "[ORDER_CREATED]" in ai_response:
                    print("🎯 Order was created successfully!")
                elif "[ORDER_CREATION_FAILED]" in ai_response:
                    print("⚠️ Order creation failed")
                elif "missing" in ai_response.lower() or "ناقص" in ai_response:
                    print("📝 AI is asking for missing information")
                else:
                    print("ℹ️ Standard response")
                    
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
            
        print("-" * 50)
        time.sleep(1)  # Rate limiting
    
    print("🏁 Order Entity Recognition API Test Complete")

def test_health_check():
    """Test if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Order Entity Recognition System")
    print("=" * 50)
    
    # First check if API is healthy
    if test_health_check():
        print()
        test_ai_conversation_endpoint()
    else:
        print("❌ Cannot test - API is not accessible") 