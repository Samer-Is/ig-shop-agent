"""
Webhook Router - Instagram Meta Webhooks
"""

import logging
from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.get("/instagram")
async def verify_webhook(request: Request):
    """Verify Instagram webhook subscription"""
    try:
        # Get verification parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        # Verify the webhook
        if mode == "subscribe" and token == "ig_shop_verify_token":
            logger.info("Instagram webhook verified successfully")
            return int(challenge)
        else:
            logger.warning("Instagram webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        raise HTTPException(status_code=400, detail="Verification error")

@router.post("/instagram")
async def receive_webhook(request: Request):
    """Receive Instagram webhook events"""
    try:
        data = await request.json()
        logger.info(f"Received Instagram webhook: {data}")
        
        # Process webhook data here
        # This is where the AI order processing would happen
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Processing error") 