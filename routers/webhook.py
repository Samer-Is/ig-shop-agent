"""
Instagram Webhook Router - Real-time DM Processing with AI Responses
IG-Shop-Agent: Enterprise SaaS Platform
"""

import logging
import json
import hmac
import hashlib
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
import httpx

from database import get_database, DatabaseService
from azure_openai_service import AzureOpenAIService
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Initialize AI service
ai_service = AzureOpenAIService()

# Meta Webhook verification token (should be in environment)
WEBHOOK_VERIFY_TOKEN = "igshop_webhook_verify_2024"

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
    """Process a messaging event and generate AI response"""
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
        
        # Skip if no sender ID or message text
        if not sender_id:
            logger.warning("No sender ID in message event")
            return
            
        message_text = message.get("text", "")
        if not message_text:
            logger.info("No text in message, skipping")
            return
            
        logger.info(f"Processing message from {sender_id}: {message_text}")
        
        # Get merchant data by page_id
        merchant = await get_merchant_by_page_id(page_id, db)
        if not merchant:
            logger.warning(f"No merchant found for page_id: {page_id}")
            return
            
        # Get catalog items for context
        catalog_items = await db.fetch_all(
            "SELECT name, description, price_jod, stock_quantity FROM catalog_items WHERE user_id = $1",
            merchant["id"]
        )
        
        # Get conversation history
        conversation_history = await db.fetch_all(
            "SELECT message, is_ai_response, created_at FROM conversations WHERE user_id = $1 AND customer = $2 ORDER BY created_at DESC LIMIT 10",
            merchant["id"],
            sender_id
        )
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message=message_text,
            catalog_items=catalog_items,
            conversation_history=conversation_history
        )
        
        if ai_response:
            # Save customer message to database
            await db.execute_query(
                "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES (gen_random_uuid(), $1, $2, $3, $4)",
                merchant["id"],
                sender_id,
                message_text,
                False
            )
            
            # Save AI response to database
            await db.execute_query(
                "INSERT INTO conversations (id, user_id, customer, message, is_ai_response) VALUES (gen_random_uuid(), $1, $2, $3, $4)",
                merchant["id"],
                sender_id,
                ai_response,
                True
            )
            
            # Send AI response back to Instagram
            await send_instagram_message(
                recipient_id=sender_id,
                message_text=ai_response,
                access_token=merchant.get("instagram_access_token")
            )
            
            logger.info(f"✅ Processed message and sent AI response to {sender_id}")
        else:
            logger.warning("Failed to generate AI response")
            
    except Exception as e:
        logger.error(f"❌ Error processing messaging event: {e}", exc_info=True)

async def get_merchant_by_page_id(page_id: str, db: DatabaseService) -> Optional[Dict[str, Any]]:
    """Get merchant data by Instagram page ID"""
    try:
        # For now, use the default user. In production, store page_id mapping
        merchant = await db.fetch_one(
            "SELECT * FROM users WHERE instagram_connected = true LIMIT 1"
        )
        return merchant
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