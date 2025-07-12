"""
Authentication Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.get("/status")
async def auth_status():
    """Check authentication status"""
    return {"status": "ok"} 