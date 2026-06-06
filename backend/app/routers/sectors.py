from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.analysis import CompositeScore

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("")
async def list_sectors(db: AsyncSession = Depends(get_db)):
    """List all sectors with average scores."""
    stocks = (await db.execute(
        select(Stock).where(Stock.is_active == True)
    )).scalars().all()

    sector_map = {}
    for stock in stocks:
        for etf in stock.etf_list.split("、"):
            etf = etf.strip()
            if etf not in sector_map:
                sector_map[etf] = {"name": etf, "stocks": [], "scores": []}
            sector_map[etf]["stocks"].append({
                "id": stock.id,
                "code": stock.code,
                "name": stock.name,
            })

    # Get latest scores
    for stock in stocks:
        cs = (await db.execute(
            select(CompositeScore)
            .where(CompositeScore.stock_id == stock.id)
            .order_by(CompositeScore.analysis_date.desc())
            .limit(1)
        )).scalar_one_or_none()

        for etf in stock.etf_list.split("、"):
            etf = etf.strip()
            if etf in sector_map and cs:
                sector_map[etf]["scores"].append(cs.total_score)

    result = []
    for name, data in sector_map.items():
        scores = data["scores"]
        avg_score = sum(scores) / len(scores) if scores else 50
        if avg_score >= 60:
            trend = 1  # 上升
        elif avg_score >= 45:
            trend = 0  # 平稳
        else:
            trend = -1  # 下降

        # Get top 5 stocks by score in this sector
        sector_scores = []
        for stock in stocks:
            if name in stock.etf_list:
                cs = (await db.execute(
                    select(CompositeScore)
                    .where(CompositeScore.stock_id == stock.id)
                    .order_by(CompositeScore.analysis_date.desc())
                    .limit(1)
                )).scalar_one_or_none()
                if cs:
                    sector_scores.append((stock.code, stock.name, cs.total_score))
        sector_scores.sort(key=lambda x: x[2], reverse=True)

        result.append({
            "name": name,
            "stock_count": len(data["stocks"]),
            "avg_score": round(avg_score, 1),
            "trend": trend,
            "top_stocks": [
                {"code": c, "name": n, "score": round(s, 1)}
                for c, n, s in sector_scores[:5]
            ],
        })

    result.sort(key=lambda x: x["avg_score"], reverse=True)
    return result


@router.get("/{sector_name}")
async def get_sector_detail(sector_name: str, db: AsyncSession = Depends(get_db)):
    """Get detailed info for a specific sector."""
    stocks = (await db.execute(
        select(Stock).where(Stock.is_active == True, Stock.etf_list.contains(sector_name))
    )).scalars().all()

    result = []
    for stock in stocks:
        cs = (await db.execute(
            select(CompositeScore)
            .where(CompositeScore.stock_id == stock.id)
            .order_by(CompositeScore.analysis_date.desc())
            .limit(1)
        )).scalar_one_or_none()
        result.append({
            "code": stock.code,
            "name": stock.name,
            "total_score": cs.total_score if cs else 50,
            "valuation_score": cs.valuation_score if cs else 50,
            "technical_score": cs.technical_score if cs else 50,
        })

    result.sort(key=lambda x: x["total_score"], reverse=True)
    return {"name": sector_name, "stocks": result}
