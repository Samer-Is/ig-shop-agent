from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_orders():
    return {"message": "Orders endpoint working"} 