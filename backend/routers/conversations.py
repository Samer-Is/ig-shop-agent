from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from database import get_database, DatabaseService
from azure_openai_service import get_openai_client
from auth_middleware import get_current_user
import logging
import json
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class ConversationResponse(BaseModel):
    id: str
    text: str
    ai_generated: bool
    created_at: str

class AITestRequest(BaseModel):
    message: str

class AITestResponse(BaseModel):
    response: str
    intent_analysis: dict
    catalog_items_used: int

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_database()

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db)
):
    """Get all conversations for the current user"""
    try:
        conversations = await db.fetch_all(
            "SELECT id, message as text, is_ai_response as ai_generated, created_at FROM conversations WHERE user_id = $1 ORDER BY created_at DESC LIMIT 100",
            current_user["id"]
        )
        return [ConversationResponse(
            id=conv["id"],
            text=conv["text"],
            ai_generated=conv["ai_generated"],
            created_at=conv["created_at"].isoformat() if conv["created_at"] else ""
        ) for conv in conversations]
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@router.post("/ai/test-response", response_model=AITestResponse)
async def test_ai_response(
    request: AITestRequest, 
    current_user: dict = Depends(get_current_user),
    db: DatabaseService = Depends(get_db)
):
    """Test AI response generation with proper multi-tenant isolation"""
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
        
        # Generate AI response with full context using the enhanced system
        openai_client = get_openai_client()
        ai_response = await openai_client.generate_response(
            message=request.message,
            catalog_items=catalog_items,
            conversation_history=conversation_history,
            customer_context={"sender_id": "test-customer", "page_id": current_user.get("instagram_page_id")},
            business_rules=business_rules,
            knowledge_base=knowledge_base
        )
        
        # Analyze intent
        intent_analysis = {
            "intent": "general_inquiry",
            "products_mentioned": [],
            "urgency": "normal",
            "language": "english" if any(word in request.message.lower() for word in ["hello", "hi", "what", "how"]) else "arabic"
        }
        
        # Check for product mentions
        for item in catalog_items:
            if item["name"].lower() in request.message.lower():
                intent_analysis["products_mentioned"].append(item["name"])
        
        # Determine intent
        if any(word in request.message.lower() for word in ["buy", "order", "purchase", "اشتري", "اطلب"]):
            intent_analysis["intent"] = "order_placement"
        elif any(word in request.message.lower() for word in ["price", "cost", "سعر", "كم"]):
            intent_analysis["intent"] = "price_inquiry"
        elif any(word in request.message.lower() for word in ["available", "stock", "متوفر", "موجود"]):
            intent_analysis["intent"] = "stock_check"
        
        # Save conversation with CURRENT USER ID
        user_conv_id = str(uuid.uuid4())
        ai_conv_id = str(uuid.uuid4())
        
        await db.execute_query(
            "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES ($1, $2, $3, $4, $5)",
            user_conv_id,
            current_user["id"],  # Use actual user ID
            "test-customer",
            request.message,
            False
        )
        
        await db.execute_query(
            "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES ($1, $2, $3, $4, $5)",
            ai_conv_id,
            current_user["id"],  # Use actual user ID
            "test-customer",
            ai_response,
            True
        )
        
        return AITestResponse(
            response=ai_response,
            intent_analysis=intent_analysis,
            catalog_items_used=len(catalog_items)
        )
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI response") 