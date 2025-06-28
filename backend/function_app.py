"""
Simplified Azure Functions application for IG-Shop-Agent API Backend.
This version uses minimal dependencies to ensure it runs properly.
"""
import azure.functions as func
import logging
import json
import os
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the main Function App
app = func.FunctionApp()

# === NEW: AI Agent and Storage ===
# In-memory storage (in production, use Azure Cosmos DB)
instagram_tokens = {}
customer_database = {}
message_history = []
analytics_data = {"total_messages": 0, "total_orders": 0}

# Enhanced Product Catalog
PRODUCT_CATALOG = [
    {
        "id": "prod_1",
        "name": "قميص أبيض",
        "name_en": "White Shirt",
        "price": 25.00,
        "currency": "JOD",
        "description": "قميص أبيض عالي الجودة من القطن الطبيعي",
        "description_en": "High quality white cotton shirt",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        "in_stock": True,
        "quantity": 50
    },
    {
        "id": "prod_2", 
        "name": "بنطال جينز",
        "name_en": "Jeans Pants",
        "price": 45.00,
        "currency": "JOD",
        "description": "بنطال جينز مريح وأنيق للاستخدام اليومي",
        "description_en": "Comfortable and stylish jeans for daily wear",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
        "in_stock": True,
        "quantity": 30
    },
    {
        "id": "prod_3",
        "name": "حذاء رياضي",
        "name_en": "Sports Shoes",
        "price": 60.00,
        "currency": "JOD",
        "description": "حذاء رياضي مريح للجري والتمارين",
        "description_en": "Comfortable sports shoes for running and exercise",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
        "in_stock": True,
        "quantity": 25
    }
]

class AIAgent:
    """Simple AI Agent for customer interactions"""
    
    def detect_language(self, message):
        """Detect Arabic or English"""
        arabic_chars = len([c for c in message if '\u0600' <= c <= '\u06FF'])
        return "ar" if arabic_chars > len(message) * 0.3 else "en"
    
    def detect_intent(self, message):
        """Simple intent detection"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["مرحبا", "أهلا", "hi", "hello"]):
            return "greeting"
        elif any(word in message_lower for word in ["منتجات", "أريد", "products", "want", "buy"]):
            return "product_inquiry"
        elif any(word in message_lower for word in ["سعر", "price", "cost"]):
            return "price_inquiry"
        elif any(word in message_lower for word in ["أطلب", "order", "شراء"]):
            return "order_request"
        else:
            return "general"
    
    def generate_response(self, message, customer_id="unknown"):
        """Generate AI response"""
        language = self.detect_language(message)
        intent = self.detect_intent(message)
        
        if intent == "greeting":
            if language == "ar":
                response = "مرحباً بك! أنا مساعدك في متجر الأزياء. كيف يمكنني مساعدتك؟ 😊"
            else:
                response = "Hello! I'm your fashion store assistant. How can I help you? 😊"
        elif intent == "product_inquiry":
            if language == "ar":
                response = "لدينا مجموعة رائعة من المنتجات! قمصان، بناطيل، وأحذية بأفضل الأسعار."
            else:
                response = "We have amazing products! Shirts, pants, and shoes at great prices."
        elif intent == "price_inquiry":
            if language == "ar":
                response = "أسعارنا: قميص أبيض (25 دينار)، بنطال جينز (45 دينار)، حذاء رياضي (60 دينار)"
            else:
                response = "Our prices: White Shirt (25 JOD), Jeans (45 JOD), Sports Shoes (60 JOD)"
        elif intent == "order_request":
            if language == "ar":
                response = "ممتاز! أي منتج تريد طلبه؟ سأساعدك في إتمام الطلب."
            else:
                response = "Great! Which product would you like to order? I'll help you complete it."
        else:
            if language == "ar":
                response = "شكراً لتواصلك معنا! اسأل عن المنتجات أو الأسعار أو أي شيء آخر."
            else:
                response = "Thanks for contacting us! Ask about products, prices, or anything else."
        
        return {
            "response": response,
            "intent": intent,
            "language": language,
            "suggested_products": PRODUCT_CATALOG[:2] if intent in ["product_inquiry", "price_inquiry"] else []
        }

# Initialize AI Agent
ai_agent = AIAgent()

@app.function_name(name="HttpTrigger")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health endpoint accessed')
    
    response_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "message": "IG-Shop-Agent API with AI is running",
        "features": {
            "ai_agent": True,
            "instagram_oauth": True,
            "customer_db": True,
            "analytics": True
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

@app.function_name(name="RootEndpoint")
@app.route(route="", auth_level=func.AuthLevel.ANONYMOUS)
def root(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Root endpoint accessed')
    
    response_data = {
        "message": "IG-Shop-Agent API with AI",
        "status": "running",
        "version": "2.0.0",
        "features": ["ai_agent", "instagram_oauth", "customer_db", "analytics"],
        "endpoints": {
            "health": "/api/health",
            "catalog": "/api/catalog",
            "ai_test": "/api/ai/test-response",
            "instagram_config": "/api/instagram/config",
            "instagram_status": "/api/instagram/status",
            "analytics": "/api/analytics",
            "messages": "/api/messages/recent",
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

# === NEW: AI Test Endpoint ===
@app.function_name(name="AITestResponse")
@app.route(route="ai/test-response", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])
def ai_test_response(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('AI test response requested')
    
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
        message = req_body.get('message', '') if req_body else ""
        
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                status_code=400,
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
        # Generate AI response
        ai_response = ai_agent.generate_response(message)
        
        response_data = {
            "ai_response": ai_response["response"],
            "detected_intent": ai_response["intent"],
            "detected_language": ai_response["language"],
            "suggested_products": ai_response.get("suggested_products", [])
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logging.error(f"AI test error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )

# === NEW: Instagram OAuth Endpoints ===
@app.function_name(name="InstagramConfig")
@app.route(route="instagram/config", auth_level=func.AuthLevel.ANONYMOUS)
def instagram_config(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Instagram config requested')
    
    # Mock Instagram app configuration
    config = {
        "app_id": "mock_instagram_app_id",
        "oauth_url": "https://api.instagram.com/oauth/authorize",
        "available": True,
        "status": "Mock configuration - setup your real Instagram app credentials"
    }
    
    return func.HttpResponse(
        json.dumps(config),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.function_name(name="InstagramStatus")
@app.route(route="instagram/status", auth_level=func.AuthLevel.ANONYMOUS)
def instagram_status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Instagram status checked')
    
    # Check if we have stored tokens
    connected = "access_token" in instagram_tokens
    
    response_data = {
        "connected": connected,
        "page_info": instagram_tokens.get("user_info") if connected else None,
        "connected_at": instagram_tokens.get("connected_at") if connected else None,
        "message": "Connected to Instagram" if connected else "Not connected to Instagram"
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

# === NEW: Analytics Endpoint ===
@app.function_name(name="Analytics")
@app.route(route="analytics", auth_level=func.AuthLevel.ANONYMOUS)
def analytics(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Analytics endpoint accessed')
    
    total_customers = len(customer_database)
    total_messages = len(message_history)
    
    analytics_response = {
        "total_messages": total_messages,
        "total_orders": analytics_data.get("total_orders", 0),
        "total_customers": total_customers,
        "response_rate": 100,
        "conversion_rate": 15.5,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return func.HttpResponse(
        json.dumps(analytics_response),
        status_code=200,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )

# === NEW: Recent Messages Endpoint ===
@app.function_name(name="RecentMessages")
@app.route(route="messages/recent", auth_level=func.AuthLevel.ANONYMOUS)
def recent_messages(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Recent messages requested')
    
    # Return recent messages (last 10)
    recent_msgs = message_history[-10:] if message_history else []
    
    response_data = {
        "messages": recent_msgs,
        "total": len(message_history),
        "last_updated": datetime.utcnow().isoformat()
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
    
    # Return enhanced catalog
    catalog_data = {
        "products": PRODUCT_CATALOG,
        "total": len(PRODUCT_CATALOG),
        "last_updated": datetime.utcnow().isoformat()
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
    This is where the AI agent processes incoming messages
    """
    logging.info('Instagram webhook event received')
    
    try:
        # Get the webhook payload
        webhook_data = req.get_json()
        logging.info(f"Webhook payload: {json.dumps(webhook_data, indent=2)}")
        
        # Process webhook events with AI
        if webhook_data and 'entry' in webhook_data:
            for entry in webhook_data['entry']:
                # Process each entry (could be message, comment, etc.)
                if 'messaging' in entry:
                    # This is a message event
                    for message_event in entry['messaging']:
                        sender_id = message_event.get('sender', {}).get('id')
                        message_text = message_event.get('message', {}).get('text', '')
                        
                        if sender_id and message_text:
                            logging.info(f"Processing message from {sender_id}: {message_text}")
                            
                            # Generate AI response
                            ai_response = ai_agent.generate_response(message_text, sender_id)
                            
                            # Store message in history
                            message_record = {
                                "id": len(message_history) + 1,
                                "customer_id": sender_id,
                                "customer_name": f"Customer {sender_id[-4:]}",
                                "message": message_text,
                                "ai_response": ai_response["response"],
                                "intent": ai_response["intent"],
                                "language": ai_response["language"],
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            message_history.append(message_record)
                            
                            # Update customer database
                            if sender_id not in customer_database:
                                customer_database[sender_id] = {
                                    "id": sender_id,
                                    "first_contact": datetime.utcnow().isoformat(),
                                    "total_messages": 0
                                }
                            customer_database[sender_id]["total_messages"] += 1
                            customer_database[sender_id]["last_contact"] = datetime.utcnow().isoformat()
                            
                            logging.info(f"AI Response: {ai_response['response']}")
                        
        return func.HttpResponse("OK", status_code=200)
         
    except Exception as e:
        logging.error(f"Webhook processing error: {str(e)}")
        return func.HttpResponse("Error", status_code=500) 