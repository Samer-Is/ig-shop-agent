"""
Conversations API Router - Enhanced with Sentiment Analysis and Intent Tracking
IG-Shop-Agent: Enterprise SaaS Platform
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_database, DatabaseService
from auth_middleware import get_current_user
from azure_openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Pydantic models for API requests/responses
class AITestRequest(BaseModel):
    message: str

class AITestResponse(BaseModel):
    response: str
    analysis: Dict[str, Any]
    context_used: Dict[str, Any]

class ConversationAnalytics(BaseModel):
    total_conversations: int
    intents_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]
    top_products_mentioned: List[Dict[str, Any]]
    recent_conversations: List[Dict[str, Any]]

class ConversationMessage(BaseModel):
    id: str
    customer: str
    message: str
    is_ai_response: bool
    sentiment: Optional[str] = None
    intent: Optional[str] = None
    products_mentioned: Optional[List[str]] = None
    created_at: datetime

def get_openai_client():
    """Get OpenAI client instance"""
    return AzureOpenAIService()

@router.get("/", response_model=List[ConversationMessage])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_database)
):
    """Get all conversations for the current user with analytics data"""
    try:
        conversations = await db.fetch_all(
            """SELECT id, customer, message, is_ai_response, sentiment, intent, 
                      products_mentioned, created_at 
               FROM conversations 
               WHERE user_id = $1 
               ORDER BY created_at DESC 
               LIMIT 100""",
            current_user["id"]
        )
        
        return [
            ConversationMessage(
                id=conv["id"],
                customer=conv["customer"],
                message=conv["message"],
                is_ai_response=conv["is_ai_response"],
                sentiment=conv.get("sentiment"),
                intent=conv.get("intent"),
                products_mentioned=conv.get("products_mentioned", []),
                created_at=conv["created_at"]
            )
            for conv in conversations
        ]
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@router.get("/analytics", response_model=ConversationAnalytics)
async def get_conversation_analytics(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_database)
):
    """Get conversation analytics including sentiment and intent breakdown"""
    try:
        # Get total conversations
        total_result = await db.fetch_one(
            "SELECT COUNT(*) as total FROM conversations WHERE user_id = $1",
            current_user["id"]
        )
        total_conversations = total_result["total"] if total_result else 0
        
        # Get intent breakdown
        intent_results = await db.fetch_all(
            """SELECT intent, COUNT(*) as count 
               FROM conversations 
               WHERE user_id = $1 AND intent IS NOT NULL 
               GROUP BY intent 
               ORDER BY count DESC""",
            current_user["id"]
        )
        intents_breakdown = {row["intent"]: row["count"] for row in intent_results}
        
        # Get sentiment breakdown
        sentiment_results = await db.fetch_all(
            """SELECT sentiment, COUNT(*) as count 
               FROM conversations 
               WHERE user_id = $1 AND sentiment IS NOT NULL 
               GROUP BY sentiment 
               ORDER BY count DESC""",
            current_user["id"]
        )
        sentiment_breakdown = {row["sentiment"]: row["count"] for row in sentiment_results}
        
        # Get top products mentioned
        product_results = await db.fetch_all(
            """SELECT unnest(products_mentioned) as product, COUNT(*) as mentions
               FROM conversations 
               WHERE user_id = $1 AND products_mentioned IS NOT NULL 
               GROUP BY product 
               ORDER BY mentions DESC 
               LIMIT 10""",
            current_user["id"]
        )
        top_products_mentioned = [
            {"product": row["product"], "mentions": row["mentions"]}
            for row in product_results
        ]
        
        # Get recent conversations
        recent_conversations = await db.fetch_all(
            """SELECT customer, message, is_ai_response, sentiment, intent, created_at
               FROM conversations 
               WHERE user_id = $1 
               ORDER BY created_at DESC 
               LIMIT 20""",
            current_user["id"]
        )
        
        return ConversationAnalytics(
            total_conversations=total_conversations,
            intents_breakdown=intents_breakdown,
            sentiment_breakdown=sentiment_breakdown,
            top_products_mentioned=top_products_mentioned,
            recent_conversations=[
                {
                    "customer": conv["customer"],
                    "message": conv["message"][:100] + "..." if len(conv["message"]) > 100 else conv["message"],
                    "is_ai_response": conv["is_ai_response"],
                    "sentiment": conv.get("sentiment"),
                    "intent": conv.get("intent"),
                    "created_at": conv["created_at"].isoformat()
                }
                for conv in recent_conversations
            ]
        )
    except Exception as e:
        logger.error(f"Error fetching conversation analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@router.post("/ai/test-response", response_model=AITestResponse)
async def test_ai_response(
    request: AITestRequest, 
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_database)
):
    """Test AI response generation with enhanced analytics and sentiment analysis"""
    try:
        # Get catalog items for CURRENT USER ONLY
        catalog_items = await db.fetch_all(
            "SELECT name, description, price_jod, stock_quantity, product_link, category FROM catalog_items WHERE user_id = $1",
            current_user["id"]
        )
        
        # Get business rules for CURRENT USER ONLY
        business_rules = await db.fetch_one(
            "SELECT business_name, business_type, working_hours, delivery_info, payment_methods, return_policy, terms_conditions, contact_info, custom_prompt, ai_instructions, language_preference, response_tone FROM business_rules WHERE user_id = $1",
            current_user["id"]
        )
        
        # Get knowledge base items for CURRENT USER ONLY
        knowledge_base = await db.fetch_all(
            "SELECT title, content FROM kb_documents WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10",
            current_user["id"]
        )
        
        # Get conversation history for CURRENT USER ONLY (test customer)
        conversation_history = await db.fetch_all(
            "SELECT message, is_ai_response, created_at FROM conversations WHERE user_id = $1 AND customer = $2 ORDER BY created_at DESC LIMIT 20",
            current_user["id"],
            "test-customer"
        )
        
        # Generate AI response with enhanced structured analysis
        openai_client = get_openai_client()
        ai_response = await openai_client.generate_response(
            message=request.message,
            catalog_items=catalog_items,
            conversation_history=conversation_history,
            customer_context={"sender_id": "test-customer", "page_id": current_user.get("instagram_page_id")},
            business_rules=business_rules,
            knowledge_base=knowledge_base
        )
        
        # The structured AI service now returns analysis data - we need to modify it to return both response and analysis
        # For now, let's create a simple analysis based on the message
        analysis = {
            "detected_language": "english" if any(word in request.message.lower() for word in ["hello", "hi", "what", "how", "the", "is", "are"]) else "arabic",
            "customer_intent": "general_inquiry",
            "sentiment": "neutral",
            "products_mentioned": [],
            "requires_escalation": False
        }
        
        # Check for product mentions
        for item in catalog_items:
            if item["name"].lower() in request.message.lower():
                analysis["products_mentioned"].append(item["name"])
        
        # Determine intent based on keywords
        if any(word in request.message.lower() for word in ["buy", "order", "purchase", "اشتري", "اطلب"]):
            analysis["customer_intent"] = "order_placement"
        elif any(word in request.message.lower() for word in ["price", "cost", "سعر", "كم"]):
            analysis["customer_intent"] = "price_inquiry"
        elif any(word in request.message.lower() for word in ["available", "stock", "متوفر", "موجود"]):
            analysis["customer_intent"] = "stock_check"
        elif any(word in request.message.lower() for word in ["angry", "frustrated", "problem", "زعلان", "مشكلة"]):
            analysis["customer_intent"] = "complaint"
            analysis["sentiment"] = "negative"
        
        # Determine sentiment
        if any(word in request.message.lower() for word in ["great", "excellent", "love", "amazing", "ممتاز", "رائع"]):
            analysis["sentiment"] = "positive"
        elif any(word in request.message.lower() for word in ["bad", "terrible", "hate", "awful", "سيء", "فظيع"]):
            analysis["sentiment"] = "negative"
        
        # Save conversation with analytics data
        user_conv_id = str(uuid.uuid4())
        ai_conv_id = str(uuid.uuid4())
        
        await db.execute_query(
            """INSERT INTO conversations 
               (id, user_id, customer, message, is_ai_response, sentiment, intent, products_mentioned) 
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            user_conv_id,
            current_user["id"],
            "test-customer",
            request.message,
            False,
            analysis["sentiment"],
            analysis["customer_intent"],
            analysis["products_mentioned"]
        )
        
        await db.execute_query(
            """INSERT INTO conversations 
               (id, user_id, customer, message, is_ai_response, sentiment, intent, products_mentioned) 
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            ai_conv_id,
            current_user["id"],
            "test-customer",
            ai_response,
            True,
            "neutral",  # AI responses are neutral
            "response",
            []
        )
        
        # Context used for transparency
        context_used = {
            "catalog_items_count": len(catalog_items),
            "business_rules_configured": business_rules is not None,
            "knowledge_base_items": len(knowledge_base),
            "conversation_history_length": len(conversation_history),
            "merchant_business_name": business_rules.get("business_name") if business_rules else None
        }
        
        return AITestResponse(
            response=ai_response,
            analysis=analysis,
            context_used=context_used
        )
        
    except Exception as e:
        logger.error(f"Error generating AI test response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI response") 