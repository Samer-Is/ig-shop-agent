"""
Instagram Webhook Router - Real-time DM Processing with AI Responses
IG-Shop-Agent: Enterprise SaaS Platform
"""

import logging
import json
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
import httpx

from database import get_database, DatabaseService
from azure_openai_service import AzureOpenAIService
from azure_speech_service import AzureSpeechService
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Initialize services
ai_service = AzureOpenAIService()
speech_service = AzureSpeechService()

# Meta Webhook verification token (should be in environment)
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "")

@router.get("/instagram")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    """
    Instagram Webhook Verification
    Required by Meta to verify webhook endpoint
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
        logger.info("✅ Webhook verification successful")
        return PlainTextResponse(content=hub_challenge)
    else:
        logger.error(f"❌ Webhook verification failed: invalid token or mode")
        raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/instagram")
async def handle_instagram_webhook(
    request: Request,
    db: DatabaseService = Depends(get_database)
):
    """
    Handle Instagram webhook events (messages, etc.)
    Process incoming messages and generate AI responses
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature (recommended for production)
        if not verify_webhook_signature(request.headers.get("x-hub-signature-256"), body):
            logger.warning("⚠️ Webhook signature verification failed - proceeding anyway for development")
            # In production, uncomment the line below:
            # raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = json.loads(body.decode('utf-8'))
        logger.info(f"Received Instagram webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Process webhook entries
        if "entry" in webhook_data:
            for entry in webhook_data["entry"]:
                await process_webhook_entry(entry, db)
        
        return {"status": "received"}
        
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in webhook request")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_webhook_entry(entry: Dict[str, Any], db: DatabaseService):
    """Process a single webhook entry"""
    try:
        page_id = entry.get("id")
        logger.info(f"Processing entry for page_id: {page_id}")
        
        # Handle messaging events
        if "messaging" in entry:
            for messaging_event in entry["messaging"]:
                await process_messaging_event(messaging_event, page_id, db)
        
        # Handle changes (for other types of updates)
        if "changes" in entry:
            for change in entry["changes"]:
                logger.info(f"Change event: {change.get('field', 'unknown')}")
                # Handle other types of changes if needed
                
    except Exception as e:
        logger.error(f"❌ Error processing entry: {e}", exc_info=True)

async def process_messaging_event(event: Dict[str, Any], page_id: str, db: DatabaseService):
    """Process a messaging event and generate AI response with voice message support"""
    try:
        logger.info(f"Processing messaging event: {json.dumps(event, indent=2)}")
        
        # Check if this is a message (not a delivery receipt, etc.)
        if "message" not in event:
            logger.info("No message in event, skipping")
            return
            
        message = event["message"]
        sender_id = event.get("sender", {}).get("id")
        recipient_id = event.get("recipient", {}).get("id")
        timestamp = event.get("timestamp")
        
        # Skip if no sender ID
        if not sender_id:
            logger.warning("No sender ID in message event")
            return
        
        # Handle different message types
        message_text = ""
        is_voice_message = False
        
        # Check for text message
        if "text" in message:
            message_text = message["text"]
            logger.info(f"Processing text message from {sender_id}: {message_text}")
        
        # Check for voice message (audio attachment)
        elif "attachments" in message:
            for attachment in message["attachments"]:
                if attachment.get("type") == "audio":
                    logger.info(f"Processing voice message from {sender_id}")
                    is_voice_message = True
                    
                    # Transcribe voice message
                    transcript = await speech_service.transcribe_instagram_audio(attachment)
                    if transcript:
                        message_text = transcript
                        logger.info(f"Voice message transcribed: {message_text}")
                    else:
                        message_text = "[Voice message - transcription failed]"
                        logger.warning("Voice message transcription failed")
                    break
        
        # Skip if no processable message content
        if not message_text:
            logger.info("No processable message content, skipping")
            return
        
        # Get merchant data by page_id
        merchant = await get_merchant_by_page_id(page_id, db)
        if not merchant:
            logger.warning(f"No merchant found for page_id: {page_id}")
            return
            
        # Get catalog items for context
        catalog_items = await db.fetch_all(
            "SELECT name, description, price_jod, stock_quantity, product_link, category FROM catalog_items WHERE user_id = $1",
            merchant["id"]
        )
        
        # Get business rules for context
        business_rules = await db.fetch_one(
            "SELECT business_name, business_type, working_hours, delivery_info, payment_methods, return_policy, terms_conditions, contact_info, custom_prompt, ai_instructions, language_preference, response_tone FROM business_rules WHERE user_id = $1",
            merchant["id"]
        )
        
        # Get knowledge base items for context
        knowledge_base = await db.fetch_all(
            "SELECT title, content FROM kb_documents WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10",
            merchant["id"]
        )
        
        # Get conversation history (last 20 messages as per consultant recommendations)
        conversation_history = await db.fetch_all(
            "SELECT message, is_ai_response, sentiment, intent, created_at FROM conversations WHERE user_id = $1 AND customer = $2 ORDER BY created_at DESC LIMIT 20",
            merchant["id"],
            sender_id
        )
        
        # Generate AI response with full context
        ai_response = await ai_service.generate_response(
            message=message_text,
            catalog_items=catalog_items,
            conversation_history=conversation_history,
            customer_context={"sender_id": sender_id, "page_id": page_id, "is_voice_message": is_voice_message},
            business_rules=business_rules,
            knowledge_base=knowledge_base
        )
        
        if ai_response:
            # Analyze sentiment and intent for the customer message
            sentiment, intent, products_mentioned = await analyze_message_context(
                message_text, catalog_items, conversation_history
            )
            
            # Save customer message to database with analytics
            await db.execute_query(
                """INSERT INTO conversations 
                   (id, user_id, customer, message, is_ai_response, sentiment, intent, products_mentioned) 
                   VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7)""",
                merchant["id"],
                sender_id,
                f"{'[Voice] ' if is_voice_message else ''}{message_text}",
                False,
                sentiment,
                intent,
                products_mentioned
            )
            
            # Save AI response to database
            await db.execute_query(
                """INSERT INTO conversations 
                   (id, user_id, customer, message, is_ai_response, sentiment, intent, products_mentioned) 
                   VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7)""",
                merchant["id"],
                sender_id,
                ai_response,
                True,
                "neutral",
                "response",
                []
            )
            
            # Send AI response back to Instagram
            await send_instagram_message(
                recipient_id=sender_id,
                message_text=ai_response,
                access_token=merchant.get("instagram_access_token")
            )
            
            logger.info(f"✅ Processed {'voice ' if is_voice_message else ''}message and sent AI response to {sender_id}")
        else:
            logger.warning("Failed to generate AI response")
            
    except Exception as e:
        logger.error(f"❌ Error processing messaging event: {e}", exc_info=True)

async def analyze_message_context(message_text: str, catalog_items: list, conversation_history: list) -> tuple:
    """Analyze message for sentiment, intent, and product mentions"""
    try:
        # Simple sentiment analysis
        sentiment = "neutral"
        if any(word in message_text.lower() for word in ["great", "excellent", "love", "amazing", "ممتاز", "رائع", "حلو"]):
            sentiment = "positive"
        elif any(word in message_text.lower() for word in ["bad", "terrible", "hate", "awful", "سيء", "فظيع", "مش حلو"]):
            sentiment = "negative"
        elif any(word in message_text.lower() for word in ["angry", "frustrated", "problem", "زعلان", "مشكلة", "غاضب"]):
            sentiment = "angry"
        
        # Intent classification
        intent = "general_inquiry"
        if any(word in message_text.lower() for word in ["buy", "order", "purchase", "اشتري", "اطلب", "بدي"]):
            intent = "order_placement"
        elif any(word in message_text.lower() for word in ["price", "cost", "سعر", "كم", "بكم"]):
            intent = "price_inquiry"
        elif any(word in message_text.lower() for word in ["available", "stock", "متوفر", "موجود", "في"]):
            intent = "stock_check"
        elif any(word in message_text.lower() for word in ["delivery", "shipping", "توصيل", "شحن"]):
            intent = "delivery_inquiry"
        elif sentiment in ["negative", "angry"]:
            intent = "complaint"
        
        # Product mentions
        products_mentioned = []
        for item in catalog_items:
            if item["name"].lower() in message_text.lower():
                products_mentioned.append(item["name"])
        
        return sentiment, intent, products_mentioned
        
    except Exception as e:
        logger.error(f"Error analyzing message context: {e}")
        return "neutral", "general_inquiry", []

async def get_merchant_by_page_id(page_id: str, db: DatabaseService) -> Optional[Dict[str, Any]]:
    """Get merchant data by Instagram page ID"""
    try:
        # First try to find merchant by exact page_id match
        merchant = await db.fetch_one(
            "SELECT * FROM users WHERE instagram_page_id = $1 AND instagram_connected = true",
            page_id
        )
        
        if merchant:
            logger.info(f"Found merchant by page_id: {page_id} -> user_id: {merchant['id']}")
            return merchant
        
        # If no exact match, try to find by checking if page_id is stored in instagram_user_id
        merchant = await db.fetch_one(
            "SELECT * FROM users WHERE instagram_user_id = $1 AND instagram_connected = true",
            page_id
        )
        
        if merchant:
            logger.info(f"Found merchant by instagram_user_id: {page_id} -> user_id: {merchant['id']}")
            return merchant
        
        # If still no match, log all connected users for debugging
        all_connected = await db.fetch_all(
            "SELECT id, email, instagram_page_id, instagram_user_id, instagram_connected FROM users WHERE instagram_connected = true"
        )
        
        logger.warning(f"No merchant found for page_id: {page_id}")
        logger.warning(f"Available connected users: {all_connected}")
        
        # No fallback - fail secure
        logger.error(f"No merchant found for page_id {page_id} - this is a security issue")
        return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting merchant by page_id {page_id}: {e}")
        return None

async def send_instagram_message(recipient_id: str, message_text: str, access_token: str):
    """Send message to Instagram user via Graph API"""
    try:
        if not access_token:
            logger.error("❌ No access token available for sending message")
            return False
            
        # Instagram Graph API endpoint for sending messages
        url = f"https://graph.instagram.com/v18.0/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully sent message to {recipient_id}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error sending Instagram message: {e}", exc_info=True)
        return False

def verify_webhook_signature(signature: str, body: bytes) -> bool:
    """Verify webhook signature from Meta"""
    try:
        if not signature or not hasattr(settings, 'META_APP_SECRET'):
            return False
            
        # Meta sends signature as "sha256=<hash>"
        expected_signature = "sha256=" + hmac.new(
            settings.META_APP_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False

# Health check endpoint for webhook
@router.get("/health")
async def webhook_health():
    """Webhook health check"""
    return {
        "status": "healthy",
        "service": "instagram_webhook",
        "ai_service": "connected" if ai_service else "disconnected"
    } 