from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..database import get_db
from ..services.auth import get_current_tenant

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

# Pydantic models
class CatalogItemBase(BaseModel):
    sku: str
    name: str
    price_jod: float
    description: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    media_url: Optional[str] = None

class CatalogItemCreate(CatalogItemBase):
    pass

class CatalogItemUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    price_jod: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    media_url: Optional[str] = None

class CatalogItem(CatalogItemBase):
    id: str
    tenant_id: str
    extras: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CatalogResponse(BaseModel):
    items: List[CatalogItem]
    total: int
    limit: int
    offset: int

class CatalogItemResponse(BaseModel):
    success: bool
    item_id: str
    message: str

# Catalog routes
@router.get("/", response_model=CatalogResponse)
async def get_catalog(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Get catalog items for the current tenant"""
    try:
        # Build base query
        query = "SELECT * FROM catalog_items WHERE tenant_id = $1"
        params = [tenant_id]
        param_count = 1
        
        # Add category filter
        if category:
            param_count += 1
            query += f" AND category = ${param_count}"
            params.append(category)
        
        # Add search filter
        if search:
            param_count += 1
            query += f" AND (name ILIKE ${param_count} OR description ILIKE ${param_count})"
            params.append(f"%{search}%")
        
        # Add ordering and pagination
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        rows = await db.fetch(query, *params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM catalog_items WHERE tenant_id = $1"
        count_params = [tenant_id]
        
        if category:
            count_query += " AND category = $2"
            count_params.append(category)
        
        if search:
            count_query += f" AND (name ILIKE ${'3' if category else '2'} OR description ILIKE ${'3' if category else '2'})"
            count_params.append(f"%{search}%")
        
        total = await db.fetchval(count_query, *count_params)
        
        # Convert rows to CatalogItem objects
        items = []
        for row in rows:
            items.append(CatalogItem(
                id=row['id'],
                tenant_id=row['tenant_id'],
                sku=row['sku'],
                name=row['name'],
                price_jod=row['price_jod'],
                media_url=row['media_url'] or "",
                extras=row['extras'] or {},
                description=row['description'],
                category=row['category'],
                stock_quantity=row['stock_quantity'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return CatalogResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get catalog: {str(e)}")

@router.post("/", response_model=CatalogItemResponse)
async def create_catalog_item(
    item: CatalogItemCreate,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Create a new catalog item"""
    try:
        # Check if SKU already exists for this tenant
        existing = await db.fetchrow(
            "SELECT id FROM catalog_items WHERE tenant_id = $1 AND sku = $2",
            tenant_id, item.sku
        )
        
        if existing:
            raise HTTPException(status_code=400, detail=f"SKU '{item.sku}' already exists")
        
        # Generate UUID for the item
        import uuid
        item_id = str(uuid.uuid4())
        
        # Insert new catalog item
        await db.execute(
            """
            INSERT INTO catalog_items (
                id, tenant_id, sku, name, price_jod, description, 
                category, stock_quantity, media_url, extras, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
            item_id, tenant_id, item.sku, item.name, item.price_jod,
            item.description, item.category, item.stock_quantity,
            item.media_url or "", {}, datetime.utcnow(), datetime.utcnow()
        )
        
        return CatalogItemResponse(
            success=True,
            item_id=item_id,
            message="Catalog item created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create catalog item: {str(e)}")

@router.put("/{item_id}", response_model=dict)
async def update_catalog_item(
    item_id: str,
    item: CatalogItemUpdate,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Update an existing catalog item"""
    try:
        # Check if item exists and belongs to tenant
        existing = await db.fetchrow(
            "SELECT id FROM catalog_items WHERE id = $1 AND tenant_id = $2",
            item_id, tenant_id
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in item.dict(exclude_unset=True).items():
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
        params.append(item_id)
        param_count += 1
        params.append(tenant_id)
        
        query = f"UPDATE catalog_items SET {', '.join(update_fields)} WHERE id = ${param_count - 1} AND tenant_id = ${param_count}"
        
        await db.execute(query, *params)
        
        return {"success": True, "message": "Catalog item updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update catalog item: {str(e)}")

@router.delete("/{item_id}", response_model=dict)
async def delete_catalog_item(
    item_id: str,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Delete a catalog item"""
    try:
        # Check if item exists and belongs to tenant
        existing = await db.fetchrow(
            "SELECT id FROM catalog_items WHERE id = $1 AND tenant_id = $2",
            item_id, tenant_id
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Delete the item
        await db.execute(
            "DELETE FROM catalog_items WHERE id = $1 AND tenant_id = $2",
            item_id, tenant_id
        )
        
        return {"success": True, "message": "Catalog item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete catalog item: {str(e)}")

@router.get("/{item_id}", response_model=CatalogItem)
async def get_catalog_item(
    item_id: str,
    tenant_id: str = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Get a specific catalog item by ID"""
    try:
        row = await db.fetchrow(
            "SELECT * FROM catalog_items WHERE id = $1 AND tenant_id = $2",
            item_id, tenant_id
        )
        
        if not row:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        return CatalogItem(
            id=row['id'],
            tenant_id=row['tenant_id'],
            sku=row['sku'],
            name=row['name'],
            price_jod=row['price_jod'],
            media_url=row['media_url'] or "",
            extras=row['extras'] or {},
            description=row['description'],
            category=row['category'],
            stock_quantity=row['stock_quantity'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get catalog item: {str(e)}") 