from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(title="IG-Shop-Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "IG-Shop-Agent API is running",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "auth": "/auth/login",
            "catalog": "/catalog",
            "webhook": "/webhook/instagram"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/catalog")
async def get_catalog():
    return {
        "products": [
            {
                "id": "prod_1",
                "name": "قميص أبيض",
                "name_en": "White Shirt",
                "price": 25.00,
                "currency": "JOD",
                "description": "قميص أبيض عالي الجودة",
                "description_en": "High quality white shirt",
                "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
                "in_stock": True,
                "category": "clothing"
            },
            {
                "id": "prod_2",
                "name": "بنطال جينز",
                "name_en": "Jeans Pants",
                "price": 45.00,
                "currency": "JOD",
                "description": "بنطال جينز مريح",
                "description_en": "Comfortable jeans pants",
                "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
                "in_stock": True,
                "category": "clothing"
            }
        ],
        "total": 2,
        "page": 1,
        "per_page": 10
    }

@app.post("/auth/login")
async def login(email: str, password: str):
    if email and password:
        return {
            "success": True,
            "token": "mock_jwt_token_123",
            "user": {
                "id": "user_123",
                "email": email,
                "name": "Test User"
            }
        }
    return {"error": "Email and password required"}

@app.get("/webhook/instagram")
async def instagram_webhook_verify(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    verify_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "ig_shop_webhook_verify_123")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        return hub_challenge
    return {"error": "Forbidden"}

@app.post("/webhook/instagram")
async def instagram_webhook_handler(request_data: dict):
    # Process webhook data here
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 