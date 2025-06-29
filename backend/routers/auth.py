from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()

@router.get("/me")
async def get_current_user():
    return {"message": "Auth endpoint working"} 