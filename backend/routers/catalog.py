from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_catalog():
    return {"message": "Catalog endpoint working"} 