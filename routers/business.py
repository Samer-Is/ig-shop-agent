"""
Business Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/business", tags=["business"])

@router.get("/")
async def get_business_info():
    """Get business information"""
    return {"business": "info"}
