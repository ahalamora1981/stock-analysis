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


@router.get("/detail/{stock_code}")
async def get_stock_detail(stock_code: str, db: AsyncSession = Depends(get_db)):
    """Get full analysis detail for a single stock."""
    stock = (await db.execute(
        select(Stock).where(Stock.code == stock_code)
    )).scalar_one_or_none()
    if not stock:
        return None

    # Fetch 60 days history for multi-period changes
    from app.models.daily_data import StockDailyData
    history = (await db.execute(
        select(StockDailyData)
        .where(StockDailyData.stock_id == stock.id)
        .order_by(StockDailyData.date.desc())
        .limit(60)
    )).scalars().all()

    daily = history[0] if history else None

    change_5d = 0.0
    change_20d = 0.0
    change_60d = 0.0
    if daily and len(history) > 1:
        cur = daily.close
        if len(history) >= 2:
            change_5d = (cur / max(history[min(4, len(history)-1)].close, 0.01) - 1) * 100
        if len(history) >= 20:
            change_20d = (cur / max(history[min(19, len(history)-1)].close, 0.01) - 1) * 100
        if len(history) >= 60:
            change_60d = (cur / max(history[min(59, len(history)-1)].close, 0.01) - 1) * 100

    # Valuation
    valuation = (await db.execute(
        select(ValuationAnalysis)
        .where(ValuationAnalysis.stock_id == stock.id)
        .order_by(ValuationAnalysis.analysis_date.desc())
        .limit(1)
    )).scalar_one_or_none()

    # Technical
    technical = (await db.execute(
        select(TechnicalAnalysis)
        .where(TechnicalAnalysis.stock_id == stock.id)
        .order_by(TechnicalAnalysis.analysis_date.desc())
        .limit(1)
    )).scalar_one_or_none()

    # Composite
    composite = (await db.execute(
        select(CompositeScore)
        .where(CompositeScore.stock_id == stock.id)
        .order_by(CompositeScore.analysis_date.desc())
        .limit(1)
    )).scalar_one_or_none()

    # Config weights
    from app.models.config import AppConfig
    cfg = (await db.execute(
        select(AppConfig).where(AppConfig.id == 1)
    )).scalar_one_or_none()
    weights = {
        "valuation": cfg.weight_valuation if cfg else 25,
        "technical": cfg.weight_technical if cfg else 20,
        "fundamental": cfg.weight_fundamental if cfg else 25,
        "capital_flow": cfg.weight_capital_flow if cfg else 15,
        "momentum": cfg.weight_momentum if cfg else 15,
    }

    return {
        "stock": {
            "id": stock.id,
            "code": stock.code,
            "name": stock.name,
            "etf_list": stock.etf_list,
        },
        "daily": {
            "close": daily.close if daily else 0,
            "change_pct": daily.change_pct if daily else 0,
            "change_5d": round(change_5d, 2),
            "change_20d": round(change_20d, 2),
            "change_60d": round(change_60d, 2),
            "pe_ttm": daily.pe_ttm if daily else 0,
            "pb": daily.pb if daily else 0,
            "market_cap": daily.market_cap if daily else 0,
            "volume": daily.volume if daily else 0,
            "date": str(daily.date) if daily else "",
        } if daily else None,
        "valuation": {
            "pe_ttm": valuation.pe_ttm if valuation else 0,
            "pe_percentile": valuation.pe_percentile if valuation else 0,
            "pb": valuation.pb if valuation else 0,
            "pb_percentile": valuation.pb_percentile if valuation else 0,
            "score": valuation.valuation_score if valuation else 50,
            "level": valuation.valuation_level if valuation else "",
        } if valuation else None,
        "technical": {
            "ma5": technical.ma5 if technical else 0,
            "ma10": technical.ma10 if technical else 0,
            "ma20": technical.ma20 if technical else 0,
            "ma60": technical.ma60 if technical else 0,
            "macd": technical.macd if technical else 0,
            "macd_signal": technical.macd_signal if technical else 0,
            "macd_hist": technical.macd_hist if technical else 0,
            "kdj_k": technical.kdj_k if technical else 0,
            "kdj_d": technical.kdj_d if technical else 0,
            "kdj_j": technical.kdj_j if technical else 0,
            "rsi_6": technical.rsi_6 if technical else 0,
            "rsi_14": technical.rsi_14 if technical else 0,
            "score": technical.technical_score if technical else 50,
            "signal": technical.signal if technical else "",
        } if technical else None,
        "composite": {
            "total_score": composite.total_score if composite else 50,
            "rank": composite.rank if composite else 0,
            "grade": composite.grade if composite else 0,
            "valuation_score": composite.valuation_score if composite else 50,
            "technical_score": composite.technical_score if composite else 50,
            "fundamental_score": composite.fundamental_score if composite else 50,
            "capital_flow_score": composite.capital_flow_score if composite else 50,
            "momentum_score": composite.momentum_score if composite else 50,
        } if composite else None,
        "weights": weights,
    }
