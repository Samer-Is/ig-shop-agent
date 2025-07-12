#!/usr/bin/env python3
"""
Test script for AI Order Entity Recognition
Tests the enhanced AI service with order processing capabilities
"""

import asyncio
import json
import logging
from azure_openai_service import AzureOpenAIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_order_entity_recognition():
    """Test AI order entity recognition with different scenarios"""
    
    # Initialize AI service
    ai_service = AzureOpenAIService()
    
    # Test data - sample catalog and business rules
    catalog_items = [
        {
            "id": "1",
            "name": "فستان صيفي أزرق",
            "description": "فستان صيفي جميل باللون الأزرق",
            "price_jod": 35.0,
            "stock_quantity": 10,
            "category": "فساتين",
            "product_link": "https://example.com/dress1",
            "media_link": "https://example.com/dress1.jpg"
        },
        {
            "id": "2", 
            "name": "حذاء رياضي أبيض",
            "description": "حذاء رياضي مريح باللون الأبيض",
            "price_jod": 45.0,
            "stock_quantity": 5,
            "category": "أحذية",
            "product_link": "https://example.com/shoes1",
            "media_link": "https://example.com/shoes1.jpg"
        }
    ]
    
    business_rules = {
        "business_name": "متجر الأزياء",
        "business_type": "متجر ملابس",
        "language_preference": "arabic",
        "response_tone": "friendly",
        "custom_prompt": "كن مساعد ودود ومفيد",
        "working_hours": "9 صباحاً - 9 مساءً",
        "delivery_info": "التوصيل خلال 24 ساعة في عمان",
        "payment_methods": "كاش عند الاستلام أو تحويل بنكي",
        "contact_info": "واتساب: 0791234567"
    }
    
    customer_context = {
        "page_id": "test_page_123",
        "sender_id": "test_customer_456"
    }
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Complete Order Information",
            "message": "بدي أطلب فستان صيفي أزرق مقاس M، اسمي أحمد محمد، رقم تلفوني 0791234567، وعنواني شارع الملك حسين، عمان",
            "expected_intent": "order_placement",
            "expected_ready": True
        },
        {
            "name": "Partial Order Information",
            "message": "بدي أطلب الفستان الأزرق",
            "expected_intent": "order_placement", 
            "expected_ready": False
        },
        {
            "name": "Product Inquiry",
            "message": "شو سعر الفستان الأزرق؟",
            "expected_intent": "price_check",
            "expected_ready": False
        },
        {
            "name": "Order with Missing Address",
            "message": "بدي أطلب حذاء رياضي أبيض مقاس 42، اسمي سارة أحمد، رقمي 0791234567",
            "expected_intent": "order_placement",
            "expected_ready": False
        }
    ]
    
    print("🧪 Testing AI Order Entity Recognition\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Test {i}: {scenario['name']}")
        print(f"Message: {scenario['message']}")
        
        try:
            # Generate AI response
            response = await ai_service.generate_response(
                message=scenario['message'],
                catalog_items=catalog_items,
                conversation_history=[],
                customer_context=customer_context,
                business_rules=business_rules,
                knowledge_base=[]
            )
            
            print(f"AI Response: {response}")
            
            # Check for order creation flags
            if "[ORDER_CREATED]" in response:
                print("✅ Order was created successfully")
            elif "[ORDER_CREATION_FAILED]" in response:
                print("❌ Order creation failed")
            else:
                print("ℹ️ No order creation attempted")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            print("-" * 50)
    
    print("🏁 Order Entity Recognition Test Complete")

if __name__ == "__main__":
    asyncio.run(test_order_entity_recognition()) 