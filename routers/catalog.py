"""
Catalog Router - Product Catalog Management
Handles CRUD operations for merchant product catalogs
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from database import get_database
from auth_middleware import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

# Pydantic models
class CatalogItem(BaseModel):
    """Catalog item model"""
    id: Optional[str] = None
    sku: str = Field(..., description="Product SKU")
    name: str = Field(..., description="Product name")
    description: Optional[str] = None
    price_jod: float = Field(..., description="Price in JOD")
    media_url: str = Field(default="", description="Product image URL")
    product_link: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    extras: Optional[dict] = None

class CatalogItemResponse(BaseModel):
    """Catalog item response model"""
    id: str
    sku: str
    name: str
    description: Optional[str]
    price_jod: float
    media_url: str
    product_link: Optional[str]
    category: Optional[str]
    stock_quantity: Optional[int]
    extras: Optional[dict]
    created_at: str
    updated_at: str

class CatalogCreateRequest(BaseModel):
    """Create catalog item request"""
    sku: str
    name: str
    description: Optional[str] = None
    price_jod: float
    media_url: str = ""
    product_link: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    extras: Optional[dict] = None

class CatalogUpdateRequest(BaseModel):
    """Update catalog item request"""
    name: Optional[str] = None
    description: Optional[str] = None
    price_jod: Optional[float] = None
    media_url: Optional[str] = None
    product_link: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    extras: Optional[dict] = None

@router.get("/", response_model=List[CatalogItemResponse])
async def get_catalog(request: Request):
    """Get all catalog items for the authenticated user"""
    try:
        # Get user ID from request
        user_id = get_current_user_id(request)
        if not user_id:
            # For development, try to get from header
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get database connection
        db = await get_database()
        
        # Fetch catalog items
        items = await db.fetch_all("""
            SELECT id, sku, name, description, price_jod, media_url, product_link, 
                   category, stock_quantity, extras, created_at, updated_at
            FROM catalog_items 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """, user_id)
        
        # Convert to response format
        catalog_items = []
        for item in items:
            catalog_items.append(CatalogItemResponse(
                id=item['id'],
                sku=item['sku'],
                name=item['name'],
                description=item['description'],
                price_jod=float(item['price_jod']),
                media_url=item['media_url'] or "",
                product_link=item['product_link'],
                category=item['category'],
                stock_quantity=item['stock_quantity'],
                extras=item['extras'] or {},
                created_at=item['created_at'].isoformat(),
                updated_at=item['updated_at'].isoformat()
            ))
        
        logger.info(f"Retrieved {len(catalog_items)} catalog items for user {user_id}")
        return catalog_items
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting catalog: {e}")
        raise HTTPException(status_code=500, detail="Failed to get catalog items")

@router.get("/{item_id}", response_model=CatalogItemResponse)
async def get_catalog_item(item_id: str, request: Request):
    """Get a specific catalog item"""
    try:
        # Get user ID from request
        user_id = get_current_user_id(request)
        if not user_id:
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get database connection
        db = await get_database()
        
        # Fetch catalog item
        item = await db.fetch_one("""
            SELECT id, sku, name, description, price_jod, media_url, product_link, 
                   category, stock_quantity, extras, created_at, updated_at
            FROM catalog_items 
            WHERE id = $1 AND user_id = $2
        """, item_id, user_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        return CatalogItemResponse(
            id=item['id'],
            sku=item['sku'],
            name=item['name'],
            description=item['description'],
            price_jod=float(item['price_jod']),
            media_url=item['media_url'] or "",
            product_link=item['product_link'],
            category=item['category'],
            stock_quantity=item['stock_quantity'],
            extras=item['extras'] or {},
            created_at=item['created_at'].isoformat(),
            updated_at=item['updated_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting catalog item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get catalog item")

@router.post("/", response_model=CatalogItemResponse)
async def create_catalog_item(item: CatalogCreateRequest, request: Request):
    """Create a new catalog item"""
    try:
        # Get user ID from request
        user_id = get_current_user_id(request)
        if not user_id:
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get database connection
        db = await get_database()
        
        # Check if SKU already exists for this user
        existing = await db.fetch_one("""
            SELECT id FROM catalog_items WHERE user_id = $1 AND sku = $2
        """, user_id, item.sku)
        
        if existing:
            raise HTTPException(status_code=409, detail="SKU already exists")
        
        # Insert new catalog item
        item_id = await db.fetch_val("""
            INSERT INTO catalog_items (user_id, sku, name, description, price_jod, media_url, 
                                     product_link, category, stock_quantity, extras, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
            RETURNING id
        """, user_id, item.sku, item.name, item.description, item.price_jod, item.media_url,
        item.product_link, item.category, item.stock_quantity, item.extras)
        
        # Fetch the created item
        created_item = await db.fetch_one("""
            SELECT id, sku, name, description, price_jod, media_url, product_link, 
                   category, stock_quantity, extras, created_at, updated_at
            FROM catalog_items 
            WHERE id = $1
        """, item_id)
        
        logger.info(f"Created catalog item {item_id} for user {user_id}")
        
        return CatalogItemResponse(
            id=created_item['id'],
            sku=created_item['sku'],
            name=created_item['name'],
            description=created_item['description'],
            price_jod=float(created_item['price_jod']),
            media_url=created_item['media_url'] or "",
            product_link=created_item['product_link'],
            category=created_item['category'],
            stock_quantity=created_item['stock_quantity'],
            extras=created_item['extras'] or {},
            created_at=created_item['created_at'].isoformat(),
            updated_at=created_item['updated_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating catalog item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create catalog item")

@router.put("/{item_id}", response_model=CatalogItemResponse)
async def update_catalog_item(item_id: str, item: CatalogUpdateRequest, request: Request):
    """Update an existing catalog item"""
    try:
        # Get user ID from request
        user_id = get_current_user_id(request)
        if not user_id:
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get database connection
        db = await get_database()
        
        # Check if item exists
        existing = await db.fetch_one("""
            SELECT id FROM catalog_items WHERE id = $1 AND user_id = $2
        """, item_id, user_id)
        
        if not existing:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        param_count = 1
        
        if item.name is not None:
            update_fields.append(f"name = ${param_count}")
            update_values.append(item.name)
            param_count += 1
        
        if item.description is not None:
            update_fields.append(f"description = ${param_count}")
            update_values.append(item.description)
            param_count += 1
        
        if item.price_jod is not None:
            update_fields.append(f"price_jod = ${param_count}")
            update_values.append(item.price_jod)
            param_count += 1
        
        if item.media_url is not None:
            update_fields.append(f"media_url = ${param_count}")
            update_values.append(item.media_url)
            param_count += 1
        
        if item.product_link is not None:
            update_fields.append(f"product_link = ${param_count}")
            update_values.append(item.product_link)
            param_count += 1
        
        if item.category is not None:
            update_fields.append(f"category = ${param_count}")
            update_values.append(item.category)
            param_count += 1
        
        if item.stock_quantity is not None:
            update_fields.append(f"stock_quantity = ${param_count}")
            update_values.append(item.stock_quantity)
            param_count += 1
        
        if item.extras is not None:
            update_fields.append(f"extras = ${param_count}")
            update_values.append(item.extras)
            param_count += 1
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Add updated_at field
        update_fields.append(f"updated_at = ${param_count}")
        update_values.append("NOW()")
        param_count += 1
        
        # Add WHERE clause parameters
        update_values.extend([item_id, user_id])
        
        # Execute update
        await db.execute_query(f"""
            UPDATE catalog_items 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count} AND user_id = ${param_count + 1}
        """, *update_values)
        
        # Fetch updated item
        updated_item = await db.fetch_one("""
            SELECT id, sku, name, description, price_jod, media_url, product_link, 
                   category, stock_quantity, extras, created_at, updated_at
            FROM catalog_items 
            WHERE id = $1
        """, item_id)
        
        logger.info(f"Updated catalog item {item_id} for user {user_id}")
        
        return CatalogItemResponse(
            id=updated_item['id'],
            sku=updated_item['sku'],
            name=updated_item['name'],
            description=updated_item['description'],
            price_jod=float(updated_item['price_jod']),
            media_url=updated_item['media_url'] or "",
            product_link=updated_item['product_link'],
            category=updated_item['category'],
            stock_quantity=updated_item['stock_quantity'],
            extras=updated_item['extras'] or {},
            created_at=updated_item['created_at'].isoformat(),
            updated_at=updated_item['updated_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating catalog item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update catalog item")

@router.delete("/{item_id}")
async def delete_catalog_item(item_id: str, request: Request):
    """Delete a catalog item"""
    try:
        # Get user ID from request
        user_id = get_current_user_id(request)
        if not user_id:
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get database connection
        db = await get_database()
        
        # Check if item exists
        existing = await db.fetch_one("""
            SELECT id FROM catalog_items WHERE id = $1 AND user_id = $2
        """, item_id, user_id)
        
        if not existing:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Delete the item
        await db.execute_query("""
            DELETE FROM catalog_items WHERE id = $1 AND user_id = $2
        """, item_id, user_id)
        
        logger.info(f"Deleted catalog item {item_id} for user {user_id}")
        
        return {"message": "Catalog item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting catalog item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete catalog item") 