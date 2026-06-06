from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analysis import (
    ValuationAnalysis, TechnicalAnalysis, FundamentalAnalysis,
    CompositeScore,
)
from app.models.stock import Stock
from app.services.analyzer import run_valuation_analysis, run_technical_analysis
from app.services.scorer import run_composite_scoring

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis():
    v = await run_valuation_analysis()
    t = await run_technical_analysis()
    c = await run_composite_scoring()
    return {
        "valuation": v,
        "technical": t,
        "composite": c,
    }


@router.get("/composite")
async def get_composite_scores(
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CompositeScore, Stock.code, Stock.name, Stock.etf_list)
        .join(Stock, CompositeScore.stock_id == Stock.id)
        .order_by(CompositeScore.rank)
    )
    if search:
        stmt = stmt.where(
            (Stock.code.contains(search)) | (Stock.name.contains(search))
        )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "stock_id": cs.stock_id,
            "code": code,
            "name": name,
            "etf_list": etf_list,
            "rank": cs.rank,
            "total_score": cs.total_score,
            "valuation_score": cs.valuation_score,
            "technical_score": cs.technical_score,
            "fundamental_score": cs.fundamental_score,
            "capital_flow_score": cs.capital_flow_score,
            "momentum_score": cs.momentum_score,
            "grade": cs.grade,
        }
        for cs, code, name, etf_list in rows
    ]


@router.get("/valuation/{stock_code}")
async def get_valuation(stock_code: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(
        select(Stock).where(Stock.code == stock_code)
    )).scalar_one_or_none()
    if not stock:
        return None
    row = (await db.execute(
        select(ValuationAnalysis)
        .where(ValuationAnalysis.stock_id == stock.id)
        .order_by(ValuationAnalysis.analysis_date.desc())
        .limit(1)
    )).scalar_one_or_none()
    if not row:
        return None
    return {
        "pe_ttm": row.pe_ttm,
        "pe_percentile": row.pe_percentile,
        "pb": row.pb,
        "pb_percentile": row.pb_percentile,
        "valuation_score": row.valuation_score,
        "valuation_level": row.valuation_level,
    }


@router.get("/technical/{stock_code}")
async def get_technical(stock_code: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(
        select(Stock).where(Stock.code == stock_code)
    )).scalar_one_or_none()
    if not stock:
        return None
    row = (await db.execute(
        select(TechnicalAnalysis)
        .where(TechnicalAnalysis.stock_id == stock.id)
        .order_by(TechnicalAnalysis.analysis_date.desc())
        .limit(1)
    )).scalar_one_or_none()
    if not row:
        return None
    return {
        "ma5": row.ma5, "ma10": row.ma10, "ma20": row.ma20, "ma60": row.ma60,
        "macd": row.macd, "macd_signal": row.macd_signal, "macd_hist": row.macd_hist,
        "kdj_k": row.kdj_k, "kdj_d": row.kdj_d, "kdj_j": row.kdj_j,
        "rsi_6": row.rsi_6, "rsi_14": row.rsi_14,
        "technical_score": row.technical_score, "signal": row.signal,
    }
