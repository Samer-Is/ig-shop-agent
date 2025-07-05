from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db_connection, DatabaseService
from ..azure_openai_service import get_openai_client
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
    return await get_db_connection()

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(db: DatabaseService = Depends(get_db)):
    """Get all conversations"""
    try:
        conversations = await db.fetch_all(
            "SELECT id, message as text, is_ai_response as ai_generated, created_at FROM conversations ORDER BY created_at DESC LIMIT 100"
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
async def test_ai_response(request: AITestRequest, db: DatabaseService = Depends(get_db)):
    """Test AI response generation"""
    try:
        # Get catalog items for context
        catalog_items = await db.fetch_all(
            "SELECT name, description, price_jod, stock_quantity FROM catalog_items"
        )
        
        # Build catalog context
        catalog_context = "\n".join([
            f"- {item['name']}: {item['description']} - {item['price_jod']} JOD (Stock: {item['stock_quantity']})"
            for item in catalog_items
        ])
        
        # Create system prompt
        system_prompt = f"""You are a helpful shopping assistant for an Instagram store. 
        You speak both English and Jordanian Arabic fluently.
        
        Available products:
        {catalog_context}
        
        Instructions:
        1. Respond in the same language as the customer
        2. Be helpful and friendly
        3. Provide product recommendations when appropriate
        4. If asked about products not in the catalog, politely say they're not available
        5. For orders, collect: product name, quantity, customer name, phone, address
        
        Always analyze the customer's intent and respond appropriately."""
        
        # Get AI response
        openai_client = get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
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
        
        # Save conversation
        user_conv_id = str(uuid.uuid4())
        ai_conv_id = str(uuid.uuid4())
        
        await db.execute_query(
            "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES ($1, $2, $3, $4, $5)",
            user_conv_id,
            "default-user",  # TODO: Get from auth context
            "test-customer",
            request.message,
            False
        )
        
        await db.execute_query(
            "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES ($1, $2, $3, $4, $5)",
            ai_conv_id,
            "default-user",  # TODO: Get from auth context
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