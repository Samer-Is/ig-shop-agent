from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from ..database import get_db
from ..services.auth import get_current_tenant

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Pydantic models
class OrderBase(BaseModel):
    sku: str
    qty: int
    customer: str
    phone: str
    total_amount: float
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[Literal['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None

class Order(OrderBase):
    id: str
    tenant_id: str
    status: Literal['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrdersResponse(BaseModel):
    orders: List[Order]
    total: int
    limit: int
    offset: int

class OrderResponse(BaseModel):
    success: bool
    order_id: str
    message: str

# Orders routes
@router.get("/", response_model=OrdersResponse)
async def get_orders(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Get orders for the current tenant"""
    try:
        # Build base query
        query = "SELECT * FROM orders WHERE tenant_id = $1"
        params = [tenant_id]
        param_count = 1
        
        # Add status filter
        if status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(status)
        
        # Add ordering and pagination
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        rows = await db.fetch(query, *params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM orders WHERE tenant_id = $1"
        count_params = [tenant_id]
        
        if status:
            count_query += " AND status = $2"
            count_params.append(status)
        
        total = await db.fetchval(count_query, *count_params)
        
        # Convert rows to Order objects
        orders = []
        for row in rows:
            orders.append(Order(
                id=row['id'],
                tenant_id=row['tenant_id'],
                sku=row['sku'],
                qty=row['qty'],
                customer=row['customer'],
                phone=row['phone'],
                status=row['status'],
                total_amount=row['total_amount'],
                delivery_address=row['delivery_address'],
                notes=row['notes'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return OrdersResponse(
            orders=orders,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Create a new order"""
    try:
        # Verify that the SKU exists in the catalog
        catalog_item = await db.fetchrow(
            "SELECT id, stock_quantity FROM catalog_items WHERE tenant_id = $1 AND sku = $2",
            tenant_id, order.sku
        )
        
        if not catalog_item:
            raise HTTPException(status_code=400, detail=f"SKU '{order.sku}' not found in catalog")
        
        # Check stock availability
        if catalog_item['stock_quantity'] is not None and catalog_item['stock_quantity'] < order.qty:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock. Available: {catalog_item['stock_quantity']}, Requested: {order.qty}"
            )
        
        # Generate UUID for the order
        import uuid
        order_id = str(uuid.uuid4())
        
        # Insert new order
        await db.execute(
            """
            INSERT INTO orders (
                id, tenant_id, sku, qty, customer, phone, status, 
                total_amount, delivery_address, notes, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
            order_id, tenant_id, order.sku, order.qty, order.customer, 
            order.phone, 'pending', order.total_amount, order.delivery_address, 
            order.notes, datetime.utcnow(), datetime.utcnow()
        )
        
        # Update stock quantity if applicable
        if catalog_item['stock_quantity'] is not None:
            await db.execute(
                "UPDATE catalog_items SET stock_quantity = stock_quantity - $1, updated_at = $2 WHERE tenant_id = $3 AND sku = $4",
                order.qty, datetime.utcnow(), tenant_id, order.sku
            )
        
        return OrderResponse(
            success=True,
            order_id=order_id,
            message="Order created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.put("/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: str,
    status: str,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Update order status"""
    try:
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Check if order exists and belongs to tenant
        existing = await db.fetchrow(
            "SELECT id, status, sku, qty FROM orders WHERE id = $1 AND tenant_id = $2",
            order_id, tenant_id
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order status
        await db.execute(
            "UPDATE orders SET status = $1, updated_at = $2 WHERE id = $3 AND tenant_id = $4",
            status, datetime.utcnow(), order_id, tenant_id
        )
        
        # If order is cancelled, restore stock
        if status == 'cancelled' and existing['status'] != 'cancelled':
            await db.execute(
                """
                UPDATE catalog_items 
                SET stock_quantity = COALESCE(stock_quantity, 0) + $1, updated_at = $2 
                WHERE tenant_id = $3 AND sku = $4
                """,
                existing['qty'], datetime.utcnow(), tenant_id, existing['sku']
            )
        
        return {"success": True, "message": f"Order status updated to '{status}'"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

@router.put("/{order_id}", response_model=dict)
async def update_order(
    order_id: str,
    order: OrderUpdate,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Update order details"""
    try:
        # Check if order exists and belongs to tenant
        existing = await db.fetchrow(
            "SELECT id FROM orders WHERE id = $1 AND tenant_id = $2",
            order_id, tenant_id
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in order.dict(exclude_unset=True).items():
            if value is not None:
                param_count += 1
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return {"success": True, "message": "No changes to update"}
        
        # Add updated_at field
        param_count += 1
        update_fields.append(f"updated_at = ${param_count}")
        params.append(datetime.utcnow())
        
        # Add WHERE conditions
        param_count += 1
        params.append(order_id)
        param_count += 1
        params.append(tenant_id)
        
        query = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = ${param_count - 1} AND tenant_id = ${param_count}"
        
        await db.execute(query, *params)
        
        return {"success": True, "message": "Order updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Get a specific order by ID"""
    try:
        row = await db.fetchrow(
            "SELECT * FROM orders WHERE id = $1 AND tenant_id = $2",
            order_id, tenant_id
        )
        
        if not row:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return Order(
            id=row['id'],
            tenant_id=row['tenant_id'],
            sku=row['sku'],
            qty=row['qty'],
            customer=row['customer'],
            phone=row['phone'],
            status=row['status'],
            total_amount=row['total_amount'],
            delivery_address=row['delivery_address'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order: {str(e)}")

@router.delete("/{order_id}", response_model=dict)
async def delete_order(
    order_id: str,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Delete an order (restore stock if not delivered)"""
    try:
        # Get order details before deletion
        order_row = await db.fetchrow(
            "SELECT sku, qty, status FROM orders WHERE id = $1 AND tenant_id = $2",
            order_id, tenant_id
        )
        
        if not order_row:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Delete the order
        await db.execute(
            "DELETE FROM orders WHERE id = $1 AND tenant_id = $2",
            order_id, tenant_id
        )
        
        # Restore stock if order wasn't delivered
        if order_row['status'] not in ['delivered', 'cancelled']:
            await db.execute(
                """
                UPDATE catalog_items 
                SET stock_quantity = COALESCE(stock_quantity, 0) + $1, updated_at = $2 
                WHERE tenant_id = $3 AND sku = $4
                """,
                order_row['qty'], datetime.utcnow(), tenant_id, order_row['sku']
            )
        
        return {"success": True, "message": "Order deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete order: {str(e)}") 