from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from database import get_database, DatabaseService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class OrderItemResponse(BaseModel):
    product_name: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer: str  # Alternative property name
    sku: str
    total_amount: float
    status: str
    created_at: str
    items: List[OrderItemResponse] = []

class OrderStatusUpdate(BaseModel):
    status: str

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_database()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: DatabaseService = Depends(get_db)):
    """Get all orders"""
    try:
        orders = await db.fetch_all(
            "SELECT id, sku, qty, customer, phone, status, total_amount, created_at FROM orders ORDER BY created_at DESC"
        )
        result = []
        
        for order in orders:
            result.append(OrderResponse(
                id=order["id"],
                customer_name=order["customer"],
                customer=order["customer"],  # Alternative property
                sku=order["sku"],
                total_amount=float(order["total_amount"]),
                status=order["status"],
                created_at=order["created_at"].isoformat() if order["created_at"] else "",
                items=[OrderItemResponse(
                    product_name=order["sku"],  # Use SKU as product name for now
                    quantity=order["qty"],
                    price=float(order["total_amount"])
                )]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: DatabaseService = Depends(get_db)):
    """Get a specific order"""
    try:
        order = await db.fetch_one(
            "SELECT id, sku, qty, customer, phone, status, total_amount, created_at FROM orders WHERE id = $1",
            order_id
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return OrderResponse(
            id=order["id"],
            customer_name=order["customer"],
            customer=order["customer"],
            sku=order["sku"],
            total_amount=float(order["total_amount"]),
            status=order["status"],
            created_at=order["created_at"].isoformat() if order["created_at"] else "",
            items=[OrderItemResponse(
                product_name=order["sku"],  # Use SKU as product name for now
                quantity=order["qty"],
                price=float(order["total_amount"])
            )]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=500, detail="Failed to get order")

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: DatabaseService = Depends(get_db)
):
    """Update order status"""
    try:
        # Check if order exists
        order = await db.fetch_one("SELECT id FROM orders WHERE id = $1", order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Validate status
        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update status
        await db.execute_query(
            "UPDATE orders SET status = $1, updated_at = NOW() WHERE id = $2",
            status_update.status,
            order_id
        )
        
        return {"message": "Order status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order status") 