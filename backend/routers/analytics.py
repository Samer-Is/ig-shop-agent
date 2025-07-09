from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from database import get_database, DatabaseService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyticsResponse(BaseModel):
    total_conversations: int
    total_orders: int
    total_revenue: float
    active_conversations: int
    catalog_items: int
    conversion_rate: float
    revenue_this_month: float
    orders_this_month: int

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
        
        # Get active conversations (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        active_conversations_result = await db.fetch_one(
            "SELECT COUNT(DISTINCT customer) as count FROM conversations WHERE created_at > $1",
            yesterday
        )
        active_conversations = active_conversations_result["count"] if active_conversations_result else 0
        
        # Get catalog items count
        catalog_items_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM catalog_items"
        )
        catalog_items = catalog_items_result["count"] if catalog_items_result else 0
        
        # Calculate conversion rate (orders / unique customers)
        unique_customers_result = await db.fetch_one(
            "SELECT COUNT(DISTINCT customer) as count FROM conversations"
        )
        unique_customers = unique_customers_result["count"] if unique_customers_result else 1
        conversion_rate = (total_orders / unique_customers * 100) if unique_customers > 0 else 0
        
        # Get this month's revenue
        first_day_of_month = datetime.now().replace(day=1)
        monthly_revenue_result = await db.fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= $1",
            first_day_of_month
        )
        revenue_this_month = float(monthly_revenue_result["revenue"]) if monthly_revenue_result else 0.0
        
        # Get this month's orders
        monthly_orders_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM orders WHERE created_at >= $1",
            first_day_of_month
        )
        orders_this_month = monthly_orders_result["count"] if monthly_orders_result else 0
        
        return AnalyticsResponse(
            total_conversations=total_conversations,
            total_orders=total_orders,
            total_revenue=total_revenue,
            active_conversations=active_conversations,
            catalog_items=catalog_items,
            conversion_rate=round(conversion_rate, 2),
            revenue_this_month=revenue_this_month,
            orders_this_month=orders_this_month
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        # Return default analytics on error to prevent complete failure
        return AnalyticsResponse(
            total_conversations=0,
            total_orders=0,
            total_revenue=0.0,
            active_conversations=0,
            catalog_items=0,
            conversion_rate=0.0,
            revenue_this_month=0.0,
            orders_this_month=0
        ) 