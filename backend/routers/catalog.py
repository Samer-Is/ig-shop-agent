from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from database import get_database, DatabaseService
from azure_openai_service import get_openai_client
import logging
import time
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class CatalogItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price_jod: float
    category: Optional[str] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None
    product_link: Optional[str] = None

class CatalogItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_jod: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None

class CatalogItemResponse(BaseModel):
    id: str
    sku: str
    name: str
    description: Optional[str]
    price_jod: float
    category: Optional[str]
    image_url: Optional[str]
    stock_quantity: int
    created_at: str

# Dependency to get database connection
async def get_db() -> DatabaseService:
    """Get database connection"""
    return await get_database()

@router.get("/", response_model=List[CatalogItemResponse])
async def get_catalog(db: DatabaseService = Depends(get_db)):
    """Get all catalog items"""
    try:
        items = await db.fetch_all(
            "SELECT id, sku, name, description, price_jod, category, media_url as image_url, stock_quantity, created_at FROM catalog_items ORDER BY created_at DESC"
        )
        return [CatalogItemResponse(
            id=item["id"],
            sku=item["sku"],
            name=item["name"],
            description=item["description"],
            price_jod=float(item["price_jod"]),
            category=item["category"],
            image_url=item["image_url"],
            stock_quantity=item["stock_quantity"] or 0,
            created_at=item["created_at"].isoformat() if item["created_at"] else ""
        ) for item in items]
    except Exception as e:
        logger.error(f"Error getting catalog: {e}")
        raise HTTPException(status_code=500, detail="Failed to get catalog items")

@router.post("/")
async def create_catalog_item(
    item: CatalogItemCreate,
    db: DatabaseService = Depends(get_db)
):
    """Create a new catalog item"""
    try:
        # Generate SKU and ID
        sku = f"SKU{int(time.time())}"
        item_id = str(uuid.uuid4())
        
        # Create database item
        await db.execute_query(
            """
            INSERT INTO catalog_items (id, user_id, sku, name, description, price_jod, category, stock_quantity, media_url, product_link)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            item_id,
            "default-user",  # TODO: Get from auth context
            sku,
            item.name,
            item.description,
            item.price_jod,
            item.category,
            item.stock_quantity,
            item.image_url or "",
            item.product_link or ""
        )
        
        # Enhance description with AI if needed
        enhanced_description = item.description
        if item.description and len(item.description) < 50:
            try:
                openai_client = get_openai_client()
                response = await openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates enhanced product descriptions for e-commerce. Keep descriptions concise but informative."},
                        {"role": "user", "content": f"Enhance this product description: {item.description}"}
                    ],
                    max_tokens=100
                )
                enhanced_description = response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Failed to enhance description: {e}")
        
        return {
            "id": item_id,
            "message": "Catalog item created successfully",
            "enhanced_description": enhanced_description
        }
        
    except Exception as e:
        logger.error(f"Error creating catalog item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create catalog item")

@router.put("/{item_id}")
async def update_catalog_item(
    item_id: str,
    item: CatalogItemUpdate,
    db: DatabaseService = Depends(get_db)
):
    """Update a catalog item"""
    try:
        # Check if item exists
        existing_item = await db.fetch_one("SELECT id FROM catalog_items WHERE id = $1", item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        param_count = 1
        
        for field, value in item.dict(exclude_unset=True).items():
            if field == "image_url":
                update_fields.append(f"media_url = ${param_count}")
            else:
                update_fields.append(f"{field} = ${param_count}")
            update_values.append(value)
            param_count += 1
        
        if update_fields:
            update_values.append(item_id)
            query = f"UPDATE catalog_items SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = ${param_count}"
            await db.execute_query(query, *update_values)
        
        return {"message": "Catalog item updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating catalog item: {e}")
        raise HTTPException(status_code=500, detail="Failed to update catalog item")

@router.delete("/{item_id}")
async def delete_catalog_item(item_id: str, db: DatabaseService = Depends(get_db)):
    """Delete a catalog item"""
    try:
        # Check if item exists
        existing_item = await db.fetch_one("SELECT id FROM catalog_items WHERE id = $1", item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        
        # Delete item
        await db.execute_query("DELETE FROM catalog_items WHERE id = $1", item_id)
        return {"message": "Catalog item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting catalog item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete catalog item") 