"""
Analytics Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/")
async def get_analytics():
    """Get analytics data"""
    return {"analytics": {}} 