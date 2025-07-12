"""
Catalog Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

@router.get("/")
async def get_catalog():
    """Get catalog items"""
    return {"items": []} 