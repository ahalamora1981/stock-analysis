from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.suggestion import generate_suggestions, get_suggestions

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.post("/generate")
async def generate():
    count = await generate_suggestions()
    return {"message": f"Generated {count} suggestions"}


@router.get("")
async def list_suggestions():
    return await get_suggestions()
