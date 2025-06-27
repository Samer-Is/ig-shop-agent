"""
Azure Functions application for IG-Shop-Agent API Backend.
Uses consumption plan for ultra-low cost deployment.
"""
import azure.functions as func
import logging
from datetime import datetime
import json
import asyncio
import os

# Import the FastAPI app
from backend.main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Azure Functions app
app = func.FunctionApp()


@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for the API."""
    try:
        return func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "platform": "Azure Functions"
            }),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="api/{*path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def api_proxy(req: func.HttpRequest) -> func.HttpResponse:
    """
    Proxy all API requests to FastAPI app.
    This allows FastAPI to run on Azure Functions.
    """
    try:
        # Import FastAPI test client for processing requests
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(fastapi_app)
        
        # Get path from route
        path = req.route_params.get("path", "")
        full_path = f"/{path}" if path else "/"
        
        # Add query string if present
        if req.url.query:
            full_path += f"?{req.url.query}"
        
        # Get request body
        try:
            body = req.get_body().decode('utf-8') if req.get_body() else None
        except:
            body = None
        
        # Convert headers
        headers = dict(req.headers)
        
        # Make request to FastAPI app
        if req.method == "GET":
            response = client.get(full_path, headers=headers)
        elif req.method == "POST":
            response = client.post(full_path, data=body, headers=headers)
        elif req.method == "PUT":
            response = client.put(full_path, data=body, headers=headers)
        elif req.method == "DELETE":
            response = client.delete(full_path, headers=headers)
        elif req.method == "PATCH":
            response = client.patch(full_path, data=body, headers=headers)
        elif req.method == "OPTIONS":
            response = client.options(full_path, headers=headers)
        else:
            return func.HttpResponse(
                "Method not allowed",
                status_code=405
            )
        
        # Return response
        return func.HttpResponse(
            response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"API proxy error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="webhook/instagram", methods=["GET", "POST"])
async def instagram_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """
    Instagram webhook handler for real-time message processing.
    Optimized for Azure Functions consumption plan.
    """
    try:
        if req.method == "GET":
            # Webhook verification
            hub_mode = req.params.get("hub.mode")
            hub_challenge = req.params.get("hub.challenge")
            hub_verify_token = req.params.get("hub.verify_token")
            
            # Verify token (get from environment variables)
            verify_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN")
            
            if hub_mode == "subscribe" and hub_verify_token == verify_token:
                logger.info("Instagram webhook verified successfully")
                return func.HttpResponse(hub_challenge, status_code=200)
            else:
                logger.warning("Instagram webhook verification failed")
                return func.HttpResponse("Forbidden", status_code=403)
        
        elif req.method == "POST":
            # Process incoming webhook
            try:
                body = req.get_json()
                logger.info(f"Received Instagram webhook: {body}")
                
                # Process webhook data
                if body.get("object") == "instagram":
                    for entry in body.get("entry", []):
                        for messaging in entry.get("messaging", []):
                            # Process message asynchronously
                            await process_instagram_message_async(messaging)
                
                return func.HttpResponse("OK", status_code=200)
                
            except Exception as e:
                logger.error(f"Error processing Instagram webhook: {e}")
                return func.HttpResponse("Error", status_code=500)
        
    except Exception as e:
        logger.error(f"Instagram webhook error: {e}")
        return func.HttpResponse("Internal Server Error", status_code=500)


async def process_instagram_message_async(messaging_data: dict):
    """
    Process Instagram message asynchronously.
    This function handles the AI response generation and sending.
    """
    try:
        # Extract message data
        sender_id = messaging_data.get("sender", {}).get("id")
        message_text = messaging_data.get("message", {}).get("text")
        
        if not sender_id or not message_text:
            logger.warning("Invalid message data received")
            return
        
        logger.info(f"Processing message from {sender_id}: {message_text}")
        
        # Import AI agent
        from backend.app.services.ai_agent import AIAgent
        from backend.app.database import get_db_session, set_tenant_context
        
        # Initialize AI agent
        ai_agent = AIAgent()
        
        # Get tenant ID from sender (simplified for MVP)
        # In production, map Instagram user to tenant
        tenant_id = 1  # Default tenant for MVP
        
        # Process with AI agent
        async with get_db_session() as db:
            await set_tenant_context(db, tenant_id)
            
            # Get conversation history and catalog
            # Simplified for MVP - implement full logic later
            conversation_history = []
            catalog_items = []
            
            # Process message
            response, function_result, tokens_in, tokens_out = await ai_agent.process_message(
                tenant_id=tenant_id,
                sender=sender_id,
                message=message_text,
                conversation_history=conversation_history,
                catalog_items=catalog_items,
                business_profile=None
            )
            
            # Send response back to Instagram
            await send_instagram_message(sender_id, response)
            
            logger.info(f"Sent AI response to {sender_id}: {response}")
            
    except Exception as e:
        logger.error(f"Error processing Instagram message: {e}")


async def send_instagram_message(recipient_id: str, message: str):
    """
    Send message back to Instagram user.
    Simplified implementation for MVP.
    """
    try:
        import httpx
        
        # Get Instagram API credentials from environment
        access_token = os.getenv("META_ACCESS_TOKEN")
        page_id = os.getenv("META_PAGE_ID")
        
        if not access_token or not page_id:
            logger.error("Instagram API credentials not configured")
            return
        
        # Send message via Instagram API
        url = f"https://graph.facebook.com/v19.0/{page_id}/messages"
        
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "access_token": access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_id}")
            else:
                logger.error(f"Failed to send message: {response.text}")
                
    except Exception as e:
        logger.error(f"Error sending Instagram message: {e}")


@app.service_bus_queue_trigger(
    arg_name="msg",
    connection="SERVICE_BUS_CONNECTION_STRING",
    queue_name="instagram-messages"
)
async def process_queued_message(msg: func.ServiceBusMessage) -> None:
    """
    Process messages from Service Bus queue.
    This provides additional resilience for message processing.
    """
    try:
        message_data = json.loads(msg.get_body().decode('utf-8'))
        logger.info(f"Processing queued message: {message_data}")
        
        # Process the message
        await process_instagram_message_async(message_data)
        
    except Exception as e:
        logger.error(f"Error processing queued message: {e}")


@app.timer_trigger(schedule="0 */30 * * * *", arg_name="timer")
async def cleanup_timer(timer: func.TimerRequest) -> None:
    """
    Cleanup timer function that runs every 30 minutes.
    Cleans up old conversation data and performs maintenance.
    """
    try:
        logger.info("Running cleanup timer...")
        
        # Import database utilities
        from backend.app.database import get_db_session
        
        async with get_db_session() as db:
            # Clean up old conversations (older than 30 days)
            await db.execute("""
                DELETE FROM conversations 
                WHERE created_at < NOW() - INTERVAL '30 days'
            """)
            
            # Clean up old usage stats (older than 90 days)
            await db.execute("""
                DELETE FROM usage_stats 
                WHERE created_at < NOW() - INTERVAL '90 days'
            """)
            
            await db.commit()
            logger.info("Cleanup completed successfully")
            
    except Exception as e:
        logger.error(f"Cleanup timer error: {e}")


if __name__ == "__main__":
    # For local development
    print("Azure Functions app created successfully")
    print("Deploy to Azure using: func azure functionapp publish your-function-app") 