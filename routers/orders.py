"""
Orders API Router - Phase 5.2: Order Data Model and API endpoints
IG-Shop-Agent: Enterprise SaaS Platform
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database import get_database, DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Pydantic models for API requests/responses
class OrderItemResponse(BaseModel):
    product_name: str
    quantity: int
    price: float
    size: Optional[str] = None
    color: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer: str  # Alternative property for compatibility
    phone: str
    sku: str
    total_amount: float
    status: str
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse]
    created_at: str
    updated_at: Optional[str] = None

class OrderUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderStatsResponse(BaseModel):
    total_orders: int
    pending_orders: int
    confirmed_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    recent_orders: List[OrderResponse]

class OrderCreateRequest(BaseModel):
    sku: str
    qty: int
    customer: str
    phone: str
    total_amount: float
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

# Temporary user for development
TEST_USER_ID = "test-user-123"

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    limit: int = Query(50, description="Maximum number of orders to return")
):
    """Get all orders for the test user with optional filtering"""
    try:
        db = await get_database()
        
        # Build query based on filters
        base_query = """
            SELECT o.id, o.sku, o.qty, o.customer, o.phone, o.status, 
                   o.total_amount, o.delivery_address, o.notes, 
                   o.created_at, o.updated_at,
                   c.name as product_name, c.price_jod
            FROM orders o
            LEFT JOIN catalog_items c ON o.sku = c.sku AND o.user_id = c.user_id
            WHERE o.user_id = $1
        """
        
        params = [TEST_USER_ID]
        
        if status:
            base_query += " AND o.status = $2"
            params.append(status)
        
        base_query += " ORDER BY o.created_at DESC"
        
        if limit:
            base_query += f" LIMIT ${len(params) + 1}"
            params.append(limit)
        
        orders = await db.fetch_all(base_query, *params)
        
        result = []
        for order in orders:
            # Parse notes for size and color
            size = None
            color = None
            if order["notes"]:
                notes_parts = order["notes"].split(";")
                for part in notes_parts:
                    part = part.strip()
                    if part.startswith("Size:"):
                        size = part.replace("Size:", "").strip()
                    elif part.startswith("Color:"):
                        color = part.replace("Color:", "").strip()
            
            result.append(OrderResponse(
                id=order["id"],
                customer_name=order["customer"],
                customer=order["customer"],  # Alternative property
                phone=order["phone"],
                sku=order["sku"],
                total_amount=float(order["total_amount"]),
                status=order["status"],
                delivery_address=order["delivery_address"],
                notes=order["notes"],
                created_at=order["created_at"].isoformat() if order["created_at"] else "",
                updated_at=order["updated_at"].isoformat() if order["updated_at"] else None,
                items=[OrderItemResponse(
                    product_name=order["product_name"] or order["sku"],
                    quantity=order["qty"],
                    price=float(order["price_jod"]) if order["price_jod"] else float(order["total_amount"]),
                    size=size,
                    color=color
                )]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@router.get("/stats", response_model=OrderStatsResponse)
async def get_order_stats():
    """Get order statistics for the test user"""
    try:
        db = await get_database()
        
        # Get total orders count
        total_orders = await db.fetch_val(
            "SELECT COUNT(*) FROM orders WHERE user_id = $1",
            TEST_USER_ID
        )
        
        # Get orders by status
        status_counts = await db.fetch_all(
            "SELECT status, COUNT(*) as count FROM orders WHERE user_id = $1 GROUP BY status",
            TEST_USER_ID
        )
        
        # Convert to dict for easy access
        status_dict = {row["status"]: row["count"] for row in status_counts}
        
        # Get total revenue
        total_revenue = await db.fetch_val(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE user_id = $1 AND status IN ('confirmed', 'shipped', 'delivered')",
            TEST_USER_ID
        )
        
        # Get recent orders (last 10)
        recent_orders_data = await db.fetch_all(
            """
            SELECT o.id, o.sku, o.qty, o.customer, o.phone, o.status, 
                   o.total_amount, o.delivery_address, o.notes, 
                   o.created_at, o.updated_at,
                   c.name as product_name, c.price_jod
            FROM orders o
            LEFT JOIN catalog_items c ON o.sku = c.sku AND o.user_id = c.user_id
            WHERE o.user_id = $1
            ORDER BY o.created_at DESC
            LIMIT 10
            """,
            TEST_USER_ID
        )
        
        recent_orders = []
        for order in recent_orders_data:
            # Parse notes for size and color
            size = None
            color = None
            if order["notes"]:
                notes_parts = order["notes"].split(";")
                for part in notes_parts:
                    part = part.strip()
                    if part.startswith("Size:"):
                        size = part.replace("Size:", "").strip()
                    elif part.startswith("Color:"):
                        color = part.replace("Color:", "").strip()
            
            recent_orders.append(OrderResponse(
                id=order["id"],
                customer_name=order["customer"],
                customer=order["customer"],
                phone=order["phone"],
                sku=order["sku"],
                total_amount=float(order["total_amount"]),
                status=order["status"],
                delivery_address=order["delivery_address"],
                notes=order["notes"],
                created_at=order["created_at"].isoformat() if order["created_at"] else "",
                updated_at=order["updated_at"].isoformat() if order["updated_at"] else None,
                items=[OrderItemResponse(
                    product_name=order["product_name"] or order["sku"],
                    quantity=order["qty"],
                    price=float(order["price_jod"]) if order["price_jod"] else float(order["total_amount"]),
                    size=size,
                    color=color
                )]
            ))
        
        return OrderStatsResponse(
            total_orders=total_orders or 0,
            pending_orders=status_dict.get("pending", 0),
            confirmed_orders=status_dict.get("confirmed", 0),
            shipped_orders=status_dict.get("shipped", 0),
            delivered_orders=status_dict.get("delivered", 0),
            cancelled_orders=status_dict.get("cancelled", 0),
            total_revenue=float(total_revenue or 0),
            recent_orders=recent_orders
        )
        
    except Exception as e:
        logger.error(f"Error getting order stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order statistics")

@router.post("/", response_model=OrderResponse)
async def create_order(order_data: OrderCreateRequest):
    """Create a new order manually"""
    try:
        db = await get_database()
        
        # Create order
        order_id = str(uuid.uuid4())
        
        insert_query = """
            INSERT INTO orders (
                id, user_id, sku, qty, customer, phone, 
                total_amount, delivery_address, notes, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        await db.execute_query(
            insert_query,
            order_id, TEST_USER_ID, order_data.sku, order_data.qty,
            order_data.customer, order_data.phone, order_data.total_amount,
            order_data.delivery_address, order_data.notes, "pending"
        )
        
        logger.info(f"Order created manually with ID: {order_id}")
        
        # Return created order
        return await get_order(order_id)
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get a specific order by ID"""
    try:
        db = await get_database()
        
        order = await db.fetch_one(
            """
            SELECT o.id, o.sku, o.qty, o.customer, o.phone, o.status, 
                   o.total_amount, o.delivery_address, o.notes, 
                   o.created_at, o.updated_at,
                   c.name as product_name, c.price_jod
            FROM orders o
            LEFT JOIN catalog_items c ON o.sku = c.sku AND o.user_id = c.user_id
            WHERE o.id = $1 AND o.user_id = $2
            """,
            order_id, TEST_USER_ID
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Parse notes for size and color
        size = None
        color = None
        if order["notes"]:
            notes_parts = order["notes"].split(";")
            for part in notes_parts:
                part = part.strip()
                if part.startswith("Size:"):
                    size = part.replace("Size:", "").strip()
                elif part.startswith("Color:"):
                    color = part.replace("Color:", "").strip()
        
        return OrderResponse(
            id=order["id"],
            customer_name=order["customer"],
            customer=order["customer"],
            phone=order["phone"],
            sku=order["sku"],
            total_amount=float(order["total_amount"]),
            status=order["status"],
            delivery_address=order["delivery_address"],
            notes=order["notes"],
            created_at=order["created_at"].isoformat() if order["created_at"] else "",
            updated_at=order["updated_at"].isoformat() if order["updated_at"] else None,
            items=[OrderItemResponse(
                product_name=order["product_name"] or order["sku"],
                quantity=order["qty"],
                price=float(order["price_jod"]) if order["price_jod"] else float(order["total_amount"]),
                size=size,
                color=color
            )]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order") 