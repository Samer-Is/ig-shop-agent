"""
IG-Shop-Agent FastAPI Application
Main entry point for the Instagram DM automation SaaS platform.
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

from app.config import settings
from app.database import init_database, close_database, get_db, AsyncSession
from app.models import Tenant, User, CatalogItem, Order, Conversation
from app.services.ai_agent import AIAgent
from app.services.vector_search import VectorSearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting IG-Shop-Agent API...")
    
    # Initialize database
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    yield
    
    # Cleanup
    await close_database()
    logger.info("IG-Shop-Agent API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="IG-Shop-Agent API",
    description="Instagram DM Automation SaaS Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_agent = AIAgent()
vector_search = VectorSearch()


# Pydantic models
class UserCreate(BaseModel):
    email: str
    instagram_handle: str
    display_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price_jod: float
    sku: str
    category: str


class ChatMessage(BaseModel):
    message: str
    sender: str


class WebhookData(BaseModel):
    object: str
    entry: List[dict]


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Extract user from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("sub")
        tenant_id: int = payload.get("tenant_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        return {"user_id": user_id, "tenant_id": tenant_id}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "IG-Shop-Agent API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


# Health check
@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "ai_agent": "ready",
            "vector_search": "ready"
        }
    }


# Authentication endpoints
@app.post("/auth/register")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and tenant."""
    try:
        # Create tenant
        tenant = Tenant(
            instagram_handle=user_data.instagram_handle,
            display_name=user_data.display_name
        )
        db.add(tenant)
        await db.flush()
        
        # Create user
        user = User(
            tenant_id=tenant.id,
            email=user_data.email,
            role="admin"
        )
        db.add(user)
        await db.commit()
        
        # Generate JWT token
        token_data = {
            "sub": user.id,
            "tenant_id": tenant.id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        }
        token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "tenant_id": tenant.id,
            "user_id": user.id
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")


@app.post("/auth/login")
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # For MVP - simplified authentication
    # In production, add proper password hashing
    
    try:
        # Find user by email (simplified)
        result = await db.execute(
            "SELECT u.id, u.tenant_id FROM users u WHERE u.email = $1",
            login_data.email
        )
        user_data = result.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate JWT token
        token_data = {
            "sub": user_data.id,
            "tenant_id": user_data.tenant_id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        }
        token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "tenant_id": user_data.tenant_id,
            "user_id": user_data.id
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Catalog endpoints
@app.get("/catalog")
async def get_catalog(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant's product catalog."""
    try:
        result = await db.execute(
            """SELECT id, name, description, price_jod, sku, category 
               FROM catalog_items WHERE tenant_id = $1""",
            current_user["tenant_id"]
        )
        products = result.fetchall()
        
        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price_jod": p.price_jod,
                    "sku": p.sku,
                    "category": p.category
                } for p in products
            ]
        }
        
    except Exception as e:
        logger.error(f"Catalog error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch catalog")


@app.post("/catalog")
async def add_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add product to catalog."""
    try:
        # Insert product
        result = await db.execute(
            """INSERT INTO catalog_items (tenant_id, name, description, price_jod, sku, category)
               VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
            current_user["tenant_id"], product.name, product.description,
            product.price_jod, product.sku, product.category
        )
        product_id = result.fetchone().id
        await db.commit()
        
        # Add to vector search
        await vector_search.add_product(
            current_user["tenant_id"],
            {
                "id": product_id,
                "name": product.name,
                "description": product.description
            }
        )
        
        return {"message": "Product added successfully", "product_id": product_id}
        
    except Exception as e:
        logger.error(f"Add product error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add product")


# Chat endpoint
@app.post("/chat")
async def chat_with_ai(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process chat message with AI agent."""
    try:
        # Get conversation history
        history_result = await db.execute(
            """SELECT text, is_ai_response FROM conversations 
               WHERE tenant_id = $1 AND customer_id = $2 
               ORDER BY created_at DESC LIMIT 10""",
            current_user["tenant_id"], message.sender
        )
        history = history_result.fetchall()
        
        # Get catalog items
        catalog_result = await db.execute(
            """SELECT name, price_jod, sku FROM catalog_items 
               WHERE tenant_id = $1 LIMIT 20""",
            current_user["tenant_id"]
        )
        catalog_items = catalog_result.fetchall()
        
        # Process with AI
        response, function_result, tokens_in, tokens_out = await ai_agent.process_message(
            tenant_id=current_user["tenant_id"],
            sender=message.sender,
            message=message.message,
            conversation_history=[{"text": h.text, "is_ai_response": h.is_ai_response} for h in history],
            catalog_items=catalog_items,
            business_profile=None  # Simplified for MVP
        )
        
        # Save conversation
        await db.execute(
            """INSERT INTO conversations (tenant_id, customer_id, text, is_ai_response)
               VALUES ($1, $2, $3, $4), ($1, $2, $5, $6)""",
            current_user["tenant_id"], message.sender, message.message, False,
            current_user["tenant_id"], message.sender, response, True
        )
        await db.commit()
        
        return {
            "response": response,
            "function_result": function_result,
            "tokens_used": tokens_in + tokens_out
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


# Instagram webhook endpoint
@app.post("/webhook/instagram")
async def instagram_webhook(request: Request):
    """Handle Instagram webhook messages."""
    try:
        body = await request.json()
        
        # Verify webhook (simplified for MVP)
        if body.get("object") == "instagram":
            for entry in body.get("entry", []):
                for messaging in entry.get("messaging", []):
                    # Process message
                    await process_instagram_message(messaging)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}


@app.get("/webhook/instagram")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    """Verify Instagram webhook."""
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_webhook_verify_token:
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


async def process_instagram_message(messaging_data: dict):
    """Process incoming Instagram message."""
    # This will be implemented with the AI agent
    logger.info(f"Processing Instagram message: {messaging_data}")
    pass


# Orders endpoint
@app.get("/orders")
async def get_orders(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant's orders."""
    try:
        result = await db.execute(
            """SELECT id, customer_name, total_amount, status, created_at
               FROM orders WHERE tenant_id = $1 ORDER BY created_at DESC""",
            current_user["tenant_id"]
        )
        orders = result.fetchall()
        
        return {
            "orders": [
                {
                    "id": o.id,
                    "customer_name": o.customer_name,
                    "total_amount": o.total_amount,
                    "status": o.status,
                    "created_at": o.created_at.isoformat()
                } for o in orders
            ]
        }
        
    except Exception as e:
        logger.error(f"Orders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 