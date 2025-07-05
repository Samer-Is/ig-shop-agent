# Instagram AI Agent SaaS - Main FastAPI Application
# Force deployment trigger - updated for Central US deployment

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from database import get_db_connection, DatabaseService
from azure_openai_service import get_openai_client
from tenant_middleware import TenantMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import secrets
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="IG Shop Agent API")

# Settings are already loaded in the config module

# Add session middleware with a secure key
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    same_site="none",
    https_only=True
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.add_middleware(TenantMiddleware)

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_db_connection()

@app.get("/")
async def root():
    return {"message": "IG Shop Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Analytics endpoint
class AnalyticsResponse(BaseModel):
    total_orders: int
    pending_orders: int
    confirmed_orders: int
    total_products: int
    total_revenue: float
    top_products: List[dict] = []
    orders: dict
    catalog: dict
    conversations: dict
    recent_orders: List[dict] = []

@app.get("/api/analytics/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(db: DatabaseService = Depends(get_db)):
    """Get dashboard analytics"""
    try:
        # Order statistics
        total_orders = await db.fetch_val("SELECT COUNT(*) FROM orders") or 0
        pending_orders = await db.fetch_val("SELECT COUNT(*) FROM orders WHERE status = 'pending'") or 0
        confirmed_orders = await db.fetch_val("SELECT COUNT(*) FROM orders WHERE status = 'confirmed'") or 0
        total_revenue = await db.fetch_val("SELECT COALESCE(SUM(total_amount), 0) FROM orders") or 0.0
        
        # Product statistics
        total_products = await db.fetch_val("SELECT COUNT(*) FROM catalog_items") or 0
        active_products = total_products
        out_of_stock = await db.fetch_val("SELECT COUNT(*) FROM catalog_items WHERE stock_quantity = 0") or 0
        
        # Conversation statistics
        total_messages = await db.fetch_val("SELECT COUNT(*) FROM conversations") or 0
        ai_responses = await db.fetch_val("SELECT COUNT(*) FROM conversations WHERE is_ai_response = true") or 0
        customer_messages = total_messages - ai_responses
        
        # Recent orders
        recent_orders_data = await db.fetch_all(
            "SELECT id, customer, total_amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT 5"
        )
        
        # Top products (placeholder)
        top_products_data = await db.fetch_all(
            "SELECT id, name, price_jod, stock_quantity FROM catalog_items LIMIT 5"
        )
        
        return AnalyticsResponse(
            total_orders=total_orders,
            pending_orders=pending_orders,
            confirmed_orders=confirmed_orders,
            total_products=total_products,
            total_revenue=float(total_revenue),
            top_products=[{
                "id": p["id"],
                "name": p["name"],
                "price_jod": float(p["price_jod"]),
                "stock_quantity": p["stock_quantity"]
            } for p in top_products_data],
            orders={
                "total": total_orders,
                "revenue": float(total_revenue),
                "average_value": float(total_revenue) / total_orders if total_orders > 0 else 0,
                "pending": pending_orders,
                "completed": confirmed_orders
            },
            catalog={
                "total_products": total_products,
                "active_products": active_products,
                "out_of_stock": out_of_stock
            },
            conversations={
                "total_messages": total_messages,
                "ai_responses": ai_responses,
                "customer_messages": customer_messages
            },
            recent_orders=[{
                "id": o["id"],
                "customer_name": o["customer"],
                "total_amount": float(o["total_amount"]),
                "status": o["status"],
                "created_at": o["created_at"].isoformat() if o["created_at"] else ""
            } for o in recent_orders_data]
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Import and include routers
from routers import auth, catalog, orders, conversations, kb

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["catalog"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(kb.router, prefix="/api/kb", tags=["knowledge-base"]) 