from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_conversations():
    return {"message": "Conversations endpoint working"} 