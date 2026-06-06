from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.daily_data import StockDailyData
from app.models.analysis import CompositeScore

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/overview")
async def market_overview(db: AsyncSession = Depends(get_db)):
    """Market overview with aggregate stats."""
    stocks = (await db.execute(
        select(Stock).where(Stock.is_active == True)
    )).scalars().all()

    total_market_cap = 0
    pe_values = []
    pb_values = []
    advance_count = 0
    decline_count = 0
    flat_count = 0
    limit_up = 0
    limit_down = 0

    for stock in stocks:
        latest = (await db.execute(
            select(StockDailyData)
            .where(StockDailyData.stock_id == stock.id)
            .order_by(StockDailyData.date.desc())
            .limit(1)
        )).scalar_one_or_none()

        if not latest:
            continue

        total_market_cap += latest.market_cap or 0
        if latest.pe_ttm > 0:
            pe_values.append(latest.pe_ttm)
        if latest.pb > 0:
            pb_values.append(latest.pb)

        if latest.change_pct > 0:
            advance_count += 1
        elif latest.change_pct < 0:
            decline_count += 1
        else:
            flat_count += 1

        if latest.change_pct >= 9.9:
            limit_up += 1
        elif latest.change_pct <= -9.9:
            limit_down += 1

    # Score distribution
    grade_dist = {1: 0, 2: 0, 3: 0, 4: 0}
    scores = (await db.execute(select(CompositeScore))).scalars().all()
    for cs in scores:
        if cs.grade in grade_dist:
            grade_dist[cs.grade] += 1

    avg_pe = sum(pe_values) / len(pe_values) if pe_values else 0
    avg_pb = sum(pb_values) / len(pb_values) if pb_values else 0

    # Sentiment: based on advance/decline ratio
    total = advance_count + decline_count + flat_count
    if total > 0:
        sentiment = (advance_count - decline_count) / total * 100
    else:
        sentiment = 0

    if sentiment > 30:
        sentiment_label = "贪婪"
    elif sentiment > 10:
        sentiment_label = "偏多"
    elif sentiment > -10:
        sentiment_label = "中性"
    elif sentiment > -30:
        sentiment_label = "偏空"
    else:
        sentiment_label = "恐惧"

    return {
        "total_market_cap": total_market_cap,
        "avg_pe": round(avg_pe, 2),
        "avg_pb": round(avg_pb, 2),
        "advance_count": advance_count,
        "decline_count": decline_count,
        "flat_count": flat_count,
        "limit_up": limit_up,
        "limit_down": limit_down,
        "sentiment_score": round(sentiment, 1),
        "sentiment_label": sentiment_label,
        "grade_distribution": grade_dist,
        "stock_count": len(stocks),
    }
