from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock
from app.models.daily_data import StockDailyData
from app.models.analysis import (
    ValuationAnalysis, TechnicalAnalysis, FundamentalAnalysis,
    CapitalFlowAnalysis, CompositeScore,
)

DEFAULT_WEIGHTS = {
    "valuation": 0.25,
    "technical": 0.20,
    "fundamental": 0.25,
    "capital_flow": 0.15,
    "momentum": 0.15,
}


async def run_composite_scoring():
    """Calculate composite scores for all active stocks."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    today = date.today()
    async with async_session() as db:
        result = await db.execute(select(Stock).where(Stock.is_active == True))
        stocks = result.scalars().all()
        scores = []

        for stock in stocks:
            # Get latest analysis for each dimension
            va = (await db.execute(
                select(ValuationAnalysis)
                .where(ValuationAnalysis.stock_id == stock.id)
                .order_by(ValuationAnalysis.analysis_date.desc())
                .limit(1)
            )).scalar_one_or_none()

            ta = (await db.execute(
                select(TechnicalAnalysis)
                .where(TechnicalAnalysis.stock_id == stock.id)
                .order_by(TechnicalAnalysis.analysis_date.desc())
                .limit(1)
            )).scalar_one_or_none()

            fa = (await db.execute(
                select(FundamentalAnalysis)
                .where(FundamentalAnalysis.stock_id == stock.id)
                .order_by(FundamentalAnalysis.analysis_date.desc())
                .limit(1)
            )).scalar_one_or_none()

            cf = (await db.execute(
                select(CapitalFlowAnalysis)
                .where(CapitalFlowAnalysis.stock_id == stock.id)
                .order_by(CapitalFlowAnalysis.analysis_date.desc())
                .limit(1)
            )).scalar_one_or_none()

            # Momentum: recent price changes
            history = (await db.execute(
                select(StockDailyData)
                .where(StockDailyData.stock_id == stock.id)
                .order_by(StockDailyData.date.desc())
                .limit(60)
            )).scalars().all()

            momentum_score = 50.0
            if len(history) >= 20:
                recent_20d = history[0].close / max(history[min(19, len(history)-1)].close, 0.01) - 1
                recent_60d = history[0].close / max(history[min(59, len(history)-1)].close, 0.01) - 1
                momentum_score = 50 + recent_20d * 200 * 0.6 + recent_60d * 200 * 0.4
                momentum_score = max(0, min(100, momentum_score))

            v_score = va.valuation_score if va else 50
            t_score = ta.technical_score if ta else 50
            f_score = fa.fundamental_score if fa else 50
            c_score = cf.capital_flow_score if cf else 50

            total = (
                v_score * DEFAULT_WEIGHTS["valuation"]
                + t_score * DEFAULT_WEIGHTS["technical"]
                + f_score * DEFAULT_WEIGHTS["fundamental"]
                + c_score * DEFAULT_WEIGHTS["capital_flow"]
                + momentum_score * DEFAULT_WEIGHTS["momentum"]
            )

            if total >= 70:
                grade = 1
            elif total >= 55:
                grade = 2
            elif total >= 40:
                grade = 3
            else:
                grade = 4

            scores.append((stock.id, v_score, t_score, f_score, c_score, momentum_score, total, grade))

        # Rank by total score
        scores.sort(key=lambda x: x[6], reverse=True)
        for rank, (sid, vs, ts, fs, cs, ms, total, grade) in enumerate(scores, 1):
            existing = await db.execute(
                select(CompositeScore).where(
                    CompositeScore.stock_id == sid,
                    CompositeScore.analysis_date == today,
                )
            )
            row = existing.scalar_one_or_none()
            data = dict(
                stock_id=sid, analysis_date=today,
                valuation_score=vs, technical_score=ts,
                fundamental_score=fs, capital_flow_score=cs,
                momentum_score=ms, total_score=total,
                rank=rank, grade=grade,
            )
            if row:
                for k, v in data.items():
                    if k not in ("stock_id", "analysis_date"):
                        setattr(row, k, v)
            else:
                db.add(CompositeScore(**data))

        await db.commit()
        return len(scores)
