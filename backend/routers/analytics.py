from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from database import get_database, DatabaseService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyticsResponse(BaseModel):
    orders: Dict[str, Any] = {
        "total": 0,
        "revenue": 0.0,
        "average_value": 0.0,
        "pending": 0,
        "completed": 0
    }
    catalog: Dict[str, Any] = {
        "total_products": 0,
        "active_products": 0,
        "out_of_stock": 0
    }
    conversations: Dict[str, Any] = {
        "total_messages": 0,
        "ai_responses": 0,
        "customer_messages": 0
    }
    recent_orders: List[Dict[str, Any]] = []

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_database()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(db: DatabaseService = Depends(get_db)):
    """Get dashboard analytics"""
    try:
        # Get total conversations
        total_conversations_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM conversations"
        )
        total_conversations = total_conversations_result["count"] if total_conversations_result else 0
        
        # Get AI vs customer messages
        ai_messages_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM conversations WHERE is_ai_response = true"
        )
        ai_messages = ai_messages_result["count"] if ai_messages_result else 0
        customer_messages = total_conversations - ai_messages
        
        # Get total orders
        total_orders_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM orders"
        )
        total_orders = total_orders_result["count"] if total_orders_result else 0
        
        # Get total revenue
        total_revenue_result = await db.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE status != 'cancelled'"
        )
        total_revenue = float(total_revenue_result["revenue"]) if total_revenue_result else 0.0
        
        # Calculate average order value
        average_value = (total_revenue / total_orders) if total_orders > 0 else 0.0
        
        # Get order status counts
        pending_orders_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM orders WHERE status IN ('pending', 'processing')"
        )
        pending_orders = pending_orders_result["count"] if pending_orders_result else 0
        
        completed_orders_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM orders WHERE status = 'completed'"
        )
        completed_orders = completed_orders_result["count"] if completed_orders_result else 0
        
        # Get catalog stats
        total_products_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM catalog_items"
        )
        total_products = total_products_result["count"] if total_products_result else 0
        
        active_products_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM catalog_items WHERE is_active = true"
        )
        active_products = active_products_result["count"] if active_products_result else 0
        
        out_of_stock_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM catalog_items WHERE stock_quantity = 0"
        )
        out_of_stock = out_of_stock_result["count"] if out_of_stock_result else 0
        
        # Get recent orders
        recent_orders_result = await db.fetch_all(
            "SELECT id, customer_name, total_amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT 5"
        )
        
        recent_orders = []
        if recent_orders_result:
            for order in recent_orders_result:
                recent_orders.append({
                    "id": order["id"],
                    "customer_name": order["customer_name"],
                    "total_amount": float(order["total_amount"]),
                    "status": order["status"],
                    "created_at": order["created_at"].isoformat() if order["created_at"] else "",
                    "items": []  # Would need to fetch from order_items table if it exists
                })
        
        return AnalyticsResponse(
            orders={
                "total": total_orders,
                "revenue": total_revenue,
                "average_value": round(average_value, 2),
                "pending": pending_orders,
                "completed": completed_orders
            },
            catalog={
                "total_products": total_products,
                "active_products": active_products,
                "out_of_stock": out_of_stock
            },
            conversations={
                "total_messages": total_conversations,
                "ai_responses": ai_messages,
                "customer_messages": customer_messages
            },
            recent_orders=recent_orders
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        # Return default analytics on error to prevent complete failure
        return AnalyticsResponse(
            orders={
                "total": 0,
                "revenue": 0.0,
                "average_value": 0.0,
                "pending": 0,
                "completed": 0
            },
            catalog={
                "total_products": 0,
                "active_products": 0,
                "out_of_stock": 0
            },
            conversations={
                "total_messages": 0,
                "ai_responses": 0,
                "customer_messages": 0
            },
            recent_orders=[]
        ) 