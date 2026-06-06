from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.daily_data import StockDailyData
from app.models.stock import Stock
from app.services.data_fetcher import update_all_daily_data

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/fetch")
async def fetch_data():
    count = await update_all_daily_data()
    return {"message": f"Updated {count} stocks"}


@router.get("/daily/{stock_code}")
async def get_daily_data(stock_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Stock).where(Stock.code == stock_code))
    stock = result.scalar_one_or_none()
    if not stock:
        return []
    result = await db.execute(
        select(StockDailyData)
        .where(StockDailyData.stock_id == stock.id)
        .order_by(StockDailyData.date.desc())
        .limit(250)
    )
    rows = result.scalars().all()
    return [
        {
            "date": str(r.date),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
            "change_pct": r.change_pct,
            "pe_ttm": r.pe_ttm,
            "pb": r.pb,
            "market_cap": r.market_cap,
        }
        for r in rows
    ]
