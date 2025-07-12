"""
Conversations Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("/")
async def get_conversations():
    """Get conversations"""
    return {"conversations": []} 