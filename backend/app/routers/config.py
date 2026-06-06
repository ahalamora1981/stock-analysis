from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.config import AppConfig

router = APIRouter(prefix="/config", tags=["config"])

DEFAULT_WEIGHTS = {
    "valuation": 25.0,
    "technical": 20.0,
    "fundamental": 25.0,
    "capital_flow": 15.0,
    "momentum": 15.0,
}


async def get_weights(db: AsyncSession) -> dict:
    result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
    cfg = result.scalar_one_or_none()
    if not cfg:
        return DEFAULT_WEIGHTS.copy()
    return {
        "valuation": cfg.weight_valuation,
        "technical": cfg.weight_technical,
        "fundamental": cfg.weight_fundamental,
        "capital_flow": cfg.weight_capital_flow,
        "momentum": cfg.weight_momentum,
    }


@router.get("")
async def get_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
    cfg = result.scalar_one_or_none()
    if not cfg:
        return {
            "weight_valuation": 25.0,
            "weight_technical": 20.0,
            "weight_fundamental": 25.0,
            "weight_capital_flow": 15.0,
            "weight_momentum": 15.0,
        }
    return {
        "weight_valuation": cfg.weight_valuation,
        "weight_technical": cfg.weight_technical,
        "weight_fundamental": cfg.weight_fundamental,
        "weight_capital_flow": cfg.weight_capital_flow,
        "weight_momentum": cfg.weight_momentum,
    }


@router.post("")
async def save_config(data: dict, db: AsyncSession = Depends(get_db)):
    total = sum(data.values())
    if abs(total - 100) > 0.1:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"权重总和必须为100%，当前为{total:.1f}%")

    result = await db.execute(select(AppConfig).where(AppConfig.id == 1))
    cfg = result.scalar_one_or_none()
    if not cfg:
        cfg = AppConfig(id=1)
        db.add(cfg)

    cfg.weight_valuation = data.get("weight_valuation", 25.0)
    cfg.weight_technical = data.get("weight_technical", 20.0)
    cfg.weight_fundamental = data.get("weight_fundamental", 25.0)
    cfg.weight_capital_flow = data.get("weight_capital_flow", 15.0)
    cfg.weight_momentum = data.get("weight_momentum", 15.0)

    await db.commit()
    return {"message": "Saved"}
