from datetime import date

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock
from app.models.daily_data import StockDailyData
from app.models.analysis import ValuationAnalysis, TechnicalAnalysis


def _percentile_rank(values: list[float], current: float) -> float:
    """Calculate percentile rank of current value in values list."""
    arr = np.array(values, dtype=float)
    arr = arr[arr > 0]
    if len(arr) < 10 or current <= 0:
        return 50.0
    return float(np.sum(arr < current) / len(arr) * 100)


def _calc_valuation_score(pe_pct: float, pb_pct: float) -> float:
    """Score: lower PE/PB percentile = higher score (undervalued = good)."""
    pe_score = max(0, min(100, 100 - pe_pct))
    pb_score = max(0, min(100, 100 - pb_pct))
    return pe_score * 0.6 + pb_score * 0.4


def _valuation_level(score: float) -> int:
    if score >= 65:
        return 1  # 低估
    elif score >= 35:
        return 2  # 合理
    else:
        return 3  # 高估


async def run_valuation_analysis():
    """Run valuation analysis for all active stocks."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    today = date.today()
    async with async_session() as db:
        result = await db.execute(select(Stock).where(Stock.is_active == True))
        stocks = result.scalars().all()
        count = 0

        for stock in stocks:
            history = await db.execute(
                select(StockDailyData)
                .where(StockDailyData.stock_id == stock.id)
                .order_by(StockDailyData.date.asc())
            )
            rows = history.scalars().all()
            if len(rows) < 10:
                continue

            pe_values = [r.pe_ttm for r in rows if r.pe_ttm > 0]
            pb_values = [r.pb for r in rows if r.pb > 0]
            latest = rows[-1]

            pe_pct = _percentile_rank(pe_values, latest.pe_ttm) if pe_values else 50
            pb_pct = _percentile_rank(pb_values, latest.pb) if pb_values else 50
            score = _calc_valuation_score(pe_pct, pb_pct)
            level = _valuation_level(score)

            existing = await db.execute(
                select(ValuationAnalysis).where(
                    ValuationAnalysis.stock_id == stock.id,
                    ValuationAnalysis.analysis_date == today,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.pe_ttm = latest.pe_ttm
                row.pe_percentile = pe_pct
                row.pb = latest.pb
                row.pb_percentile = pb_pct
                row.valuation_score = score
                row.valuation_level = level
            else:
                db.add(ValuationAnalysis(
                    stock_id=stock.id,
                    analysis_date=today,
                    pe_ttm=latest.pe_ttm,
                    pe_percentile=pe_pct,
                    pb=latest.pb,
                    pb_percentile=pb_pct,
                    valuation_score=score,
                    valuation_level=level,
                ))
            count += 1

        await db.commit()
        return count


def _ema(data: list[float], period: int) -> list[float]:
    result = []
    k = 2 / (period + 1)
    result.append(data[0])
    for i in range(1, len(data)):
        result.append(data[i] * k + result[-1] * (1 - k))
    return result


def _calc_macd(closes: list[float]) -> tuple[list, list, list]:
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    dif = [a - b for a, b in zip(ema12, ema26)]
    dea = _ema(dif, 9)
    hist = [(d - e) * 2 for d, e in zip(dif, dea)]
    return dif, dea, hist


def _calc_kdj(highs, lows, closes, period=9):
    k_vals, d_vals, j_vals = [], [], []
    k, d = 50, 50
    for i in range(len(closes)):
        start = max(0, i - period + 1)
        h = max(highs[start:i+1])
        l = min(lows[start:i+1])
        if h == l:
            rsv = 50
        else:
            rsv = (closes[i] - l) / (h - l) * 100
        k = k * 2/3 + rsv * 1/3
        d = d * 2/3 + k * 1/3
        j = 3 * k - 2 * d
        k_vals.append(k)
        d_vals.append(d)
        j_vals.append(j)
    return k_vals, d_vals, j_vals


def _calc_rsi(closes: list[float], period: int = 14) -> list[float]:
    if len(closes) < period + 1:
        return [50.0] * len(closes)
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [max(0, d) for d in deltas]
    losses = [max(0, -d) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsi = [50.0] * period
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - 100 / (1 + rs))
    return rsi


async def run_technical_analysis():
    """Run technical analysis for all active stocks."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    today = date.today()
    async with async_session() as db:
        result = await db.execute(select(Stock).where(Stock.is_active == True))
        stocks = result.scalars().all()
        count = 0

        for stock in stocks:
            history = await db.execute(
                select(StockDailyData)
                .where(StockDailyData.stock_id == stock.id)
                .order_by(StockDailyData.date.asc())
            )
            rows = history.scalars().all()
            if len(rows) < 20:
                continue

            closes = [r.close for r in rows]
            highs = [r.high for r in rows]
            lows = [r.low for r in rows]

            ma5 = np.mean(closes[-5:])
            ma10 = np.mean(closes[-10:])
            ma20 = np.mean(closes[-20:])
            ma60 = np.mean(closes[-60:]) if len(closes) >= 60 else ma20

            dif, dea, hist = _calc_macd(closes)
            k_vals, d_vals, j_vals = _calc_kdj(highs, lows, closes)
            rsi6 = _calc_rsi(closes, 6)
            rsi14 = _calc_rsi(closes, 14)

            # Score
            score = 50.0
            # MA trend
            if closes[-1] > ma5 > ma10 > ma20:
                score += 15
            elif closes[-1] < ma5 < ma10 < ma20:
                score -= 15
            # MACD
            if dif[-1] > dea[-1] and dif[-2] <= dea[-2]:
                score += 15  # 金叉
            elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]:
                score -= 15  # 死叉
            elif dif[-1] > dea[-1]:
                score += 5
            # KDJ
            if k_vals[-1] < 20 and k_vals[-1] > d_vals[-1]:
                score += 10  # 超卖金叉
            elif k_vals[-1] > 80 and k_vals[-1] < d_vals[-1]:
                score -= 10  # 超买死叉
            # RSI
            if rsi14[-1] < 30:
                score += 10
            elif rsi14[-1] > 70:
                score -= 10

            score = max(0, min(100, score))
            if score >= 65:
                signal = 1
            elif score >= 35:
                signal = 2
            else:
                signal = 3

            existing = await db.execute(
                select(TechnicalAnalysis).where(
                    TechnicalAnalysis.stock_id == stock.id,
                    TechnicalAnalysis.analysis_date == today,
                )
            )
            row = existing.scalar_one_or_none()
            data = dict(
                stock_id=stock.id, analysis_date=today,
                ma5=ma5, ma10=ma10, ma20=ma20, ma60=ma60,
                macd=dif[-1], macd_signal=dea[-1], macd_hist=hist[-1],
                kdj_k=k_vals[-1], kdj_d=d_vals[-1], kdj_j=j_vals[-1],
                rsi_6=rsi6[-1], rsi_14=rsi14[-1],
                technical_score=score, signal=signal,
            )
            if row:
                for k, v in data.items():
                    if k not in ("stock_id", "analysis_date"):
                        setattr(row, k, v)
            else:
                db.add(TechnicalAnalysis(**data))
            count += 1

        await db.commit()
        return count
