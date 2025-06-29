from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_kb_documents():
    return {"message": "Knowledge Base endpoint working"} 