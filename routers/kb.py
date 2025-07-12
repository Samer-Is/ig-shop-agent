"""
Knowledge Base Router
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])

@router.get("/")
async def get_kb_documents():
    """Get knowledge base documents"""
    return {"documents": []} 