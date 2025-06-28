"""
Simplified Azure Functions application for IG-Shop-Agent API Backend.
This version uses minimal dependencies to ensure it runs properly.
"""
import azure.functions as func
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the main Function App
app = func.FunctionApp()

@app.function_name(name="HttpTrigger")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health endpoint accessed')
    
    response_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "message": "IG-Shop-Agent API is running"
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.function_name(name="RootEndpoint")
@app.route(route="", auth_level=func.AuthLevel.ANONYMOUS)
def root(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Root endpoint accessed')
    
    response_data = {
        "message": "IG-Shop-Agent API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "auth": "/api/auth/login",
            "catalog": "/api/catalog",
            "webhook": "/api/webhook/instagram"
        }
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.function_name(name="AuthLogin")
@app.route(route="auth/login", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])
def auth_login(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Auth login endpoint accessed')
    
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    try:
        req_body = req.get_json()
        email = req_body.get('email') if req_body else ""
        password = req_body.get('password') if req_body else ""
        
        if email and password:
            response_data = {
                "success": True,
                "token": "mock_jwt_token_123",
                "user": {
                    "id": "user_123",
                    "email": email,
                    "name": "Test User"
                }
            }
            return func.HttpResponse(
                json.dumps(response_data),
                status_code=200,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Email and password required"}),
                status_code=400,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except Exception as e:
        logging.error(f"Auth error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid request"}),
            status_code=400,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )

@app.function_name(name="Catalog")
@app.route(route="catalog", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])
def catalog(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Catalog endpoint accessed')
    
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    # Mock catalog data
    catalog_data = {
        "products": [
            {
                "id": "prod_1",
                "name": "قميص أبيض",
                "name_en": "White Shirt",
                "price": 25.00,
                "currency": "JOD",
                "description": "قميص أبيض عالي الجودة",
                "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
                "in_stock": True
            },
            {
                "id": "prod_2", 
                "name": "بنطال جينز",
                "name_en": "Jeans Pants",
                "price": 45.00,
                "currency": "JOD",
                "description": "بنطال جينز مريح",
                "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
                "in_stock": True
            }
        ],
        "total": 2
    }
    
    return func.HttpResponse(
        json.dumps(catalog_data),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.function_name(name="InstagramWebhookVerify")
@app.route(route="webhook/instagram", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def instagram_webhook_verify(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook verification for Instagram/Meta
    This endpoint is called by Meta to verify your webhook URL
    """
    logging.info('Instagram webhook verification requested')
    
    # Get verification parameters from Meta
    hub_mode = req.params.get("hub.mode")
    hub_challenge = req.params.get("hub.challenge") 
    hub_verify_token = req.params.get("hub.verify_token")
    
    # This should match the verify token you set in Meta app
    expected_verify_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "igshop_webhook_verify_2024")
    
    logging.info(f"Webhook verification - Mode: {hub_mode}, Token received: {hub_verify_token}")
    
    # Verify the token matches and mode is subscribe
    if hub_mode == "subscribe" and hub_verify_token == expected_verify_token:
        logging.info("Webhook verification successful")
        # Return the challenge to complete verification
        return func.HttpResponse(hub_challenge, status_code=200)
    else:
        logging.warning(f"Webhook verification failed - Expected token: {expected_verify_token}")
        return func.HttpResponse("Forbidden", status_code=403)

@app.function_name(name="InstagramWebhookReceive")
@app.route(route="webhook/instagram", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def instagram_webhook_receive(req: func.HttpRequest) -> func.HttpResponse:
    """
    Receive Instagram webhook events (messages, comments, etc.)
    This is where the AI agent will process incoming messages
    """
    logging.info('Instagram webhook event received')
    
    try:
        # Get the webhook payload
        webhook_data = req.get_json()
        logging.info(f"Webhook payload: {json.dumps(webhook_data, indent=2)}")
        
        # Basic webhook event processing
        if webhook_data and 'entry' in webhook_data:
            for entry in webhook_data['entry']:
                # Process each entry (could be message, comment, etc.)
                if 'messaging' in entry:
                    # This is a message event
                    for message_event in entry['messaging']:
                        sender_id = message_event.get('sender', {}).get('id')
                        message_text = message_event.get('message', {}).get('text', '')
                        
                        logging.info(f"Message from {sender_id}: {message_text}")
                        
                        # TODO: Add AI agent processing here
                        # For now, just log the message
                        
        return func.HttpResponse("OK", status_code=200)
        
    except Exception as e:
        logging.error(f"Webhook processing error: {str(e)}")
        return func.HttpResponse("Error", status_code=500) 