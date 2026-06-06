from datetime import date

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock
from app.models.daily_data import StockDailyData
from app.models.analysis import (
    ValuationAnalysis, TechnicalAnalysis,
    FundamentalAnalysis, CapitalFlowAnalysis,
)


def _percentile_rank(values: list[float], current: float) -> float:
    """Calculate percentile rank of current value in values list."""
    arr = np.array(values, dtype=float)
    arr = arr[arr > 0]
    if len(arr) < 3 or current <= 0:
        return 50.0
    return float(np.sum(arr < current) / len(arr) * 100)


def _calc_valuation_score(pe_pct: float, pb_pct: float) -> float:
    pe_score = max(0, min(100, 100 - pe_pct))
    pb_score = max(0, min(100, 100 - pb_pct))
    return pe_score * 0.6 + pb_score * 0.4


def _valuation_level(score: float) -> int:
    if score >= 65:
        return 1
    elif score >= 35:
        return 2
    else:
        return 3


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
            if len(rows) < 1:
                continue

            pe_values = [r.pe_ttm for r in rows if r.pe_ttm > 0]
            pb_values = [r.pb for r in rows if r.pb > 0]
            latest = rows[-1]

            pe_pct = _percentile_rank(pe_values, latest.pe_ttm) if pe_values else 50
            pb_pct = _percentile_rank(pb_values, latest.pb) if pb_values else 50

            # If very few data points, blend toward neutral
            blend = min(1.0, len(rows) / 10.0)
            raw_score = _calc_valuation_score(pe_pct, pb_pct)
            score = 50 + (raw_score - 50) * blend

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
            if len(rows) < 2:
                continue

            closes = [r.close for r in rows]
            highs = [r.high for r in rows]
            lows = [r.low for r in rows]

            score = 50.0

            # MA trend - calculate what we can
            if len(closes) >= 5:
                ma5 = np.mean(closes[-5:])
                if len(closes) >= 10:
                    ma10 = np.mean(closes[-10:])
                else:
                    ma10 = ma5
                if len(closes) >= 20:
                    ma20 = np.mean(closes[-20:])
                else:
                    ma20 = ma10
                if len(closes) >= 60:
                    ma60 = np.mean(closes[-60:])
                else:
                    ma60 = ma20

                if closes[-1] > ma5 > ma10 > ma20:
                    score += 15
                elif closes[-1] < ma5 < ma10 < ma20:
                    score -= 15
            else:
                ma5 = ma10 = ma20 = ma60 = closes[-1]

            # MACD - needs at least 26 points for proper EMA
            if len(closes) >= 26:
                dif, dea, hist = _calc_macd(closes)
                if len(dif) >= 2:
                    if dif[-1] > dea[-1] and dif[-2] <= dea[-2]:
                        score += 15
                    elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]:
                        score -= 15
                    elif dif[-1] > dea[-1]:
                        score += 5
            else:
                dif = dea = hist = [0]

            # KDJ
            if len(closes) >= 9:
                k_vals, d_vals, j_vals = _calc_kdj(highs, lows, closes)
                if k_vals[-1] < 20 and k_vals[-1] > d_vals[-1]:
                    score += 10
                elif k_vals[-1] > 80 and k_vals[-1] < d_vals[-1]:
                    score -= 10
            else:
                k_vals = d_vals = j_vals = [50]

            # RSI
            rsi6 = _calc_rsi(closes, 6)
            rsi14 = _calc_rsi(closes, 14)
            if rsi14[-1] < 30:
                score += 10
            elif rsi14[-1] > 70:
                score -= 10

            # Price momentum bonus - simple trend
            if len(closes) >= 5:
                pct_5d = (closes[-1] / max(closes[-5], 0.01) - 1) * 100
                if pct_5d > 5:
                    score += 5
                elif pct_5d < -5:
                    score -= 5

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
                macd=dif[-1] if dif else 0,
                macd_signal=dea[-1] if dea else 0,
                macd_hist=hist[-1] if hist else 0,
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


async def run_fundamental_analysis():
    """Run fundamental analysis using available financial indicators."""
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
            if len(rows) < 1:
                continue

            latest = rows[-1]
            score = 50.0

            # PE assessment - lower is better (within reason)
            if latest.pe_ttm > 0:
                if latest.pe_ttm < 10:
                    score += 15
                elif latest.pe_ttm < 20:
                    score += 10
                elif latest.pe_ttm < 30:
                    score += 5
                elif latest.pe_ttm > 60:
                    score -= 10
                elif latest.pe_ttm > 100:
                    score -= 15

            # PB assessment - lower is better
            if latest.pb > 0:
                if latest.pb < 1:
                    score += 15
                elif latest.pb < 2:
                    score += 10
                elif latest.pb < 3:
                    score += 5
                elif latest.pb > 8:
                    score -= 10
                elif latest.pb > 15:
                    score -= 15

            # Market cap stability - larger cap = more stable
            if latest.market_cap > 0:
                cap_b = latest.market_cap / 1e8
                if cap_b > 1000:
                    score += 5
                elif cap_b > 500:
                    score += 3
                elif cap_b < 50:
                    score -= 3

            # Earnings yield (inverse PE) vs risk-free rate proxy
            if latest.pe_ttm > 0:
                earnings_yield = 100 / latest.pe_ttm
                if earnings_yield > 10:
                    score += 5
                elif earnings_yield > 5:
                    score += 3

            # PB-ROE relationship proxy (lower PB with positive PE is good)
            if latest.pe_ttm > 0 and latest.pb > 0:
                pe_pb_ratio = latest.pe_ttm / latest.pb
                if pe_pb_ratio > 20:
                    score += 3
                elif pe_pb_ratio < 2:
                    score -= 3

            score = max(0, min(100, score))

            existing = await db.execute(
                select(FundamentalAnalysis).where(
                    FundamentalAnalysis.stock_id == stock.id,
                    FundamentalAnalysis.analysis_date == today,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.fundamental_score = score
            else:
                db.add(FundamentalAnalysis(
                    stock_id=stock.id,
                    analysis_date=today,
                    fundamental_score=score,
                ))
            count += 1

        await db.commit()
        return count


async def run_capital_flow_analysis():
    """Run capital flow analysis using volume and price changes."""
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
            if len(rows) < 5:
                continue

            closes = [r.close for r in rows]
            volumes = [r.volume for r in rows]
            score = 50.0

            # Volume trend - increasing volume with price up = bullish
            if len(volumes) >= 10:
                vol_5 = np.mean(volumes[-5:])
                vol_10 = np.mean(volumes[-10:])
                vol_change = (vol_5 / max(vol_10, 1) - 1) * 100

                price_change = (closes[-1] / max(closes[-5], 0.01) - 1) * 100

                # Bullish: volume up + price up
                if vol_change > 20 and price_change > 0:
                    score += 15
                elif vol_change > 10 and price_change > 0:
                    score += 10
                # Bearish: volume up + price down (selling pressure)
                elif vol_change > 20 and price_change < 0:
                    score -= 15
                elif vol_change > 10 and price_change < 0:
                    score -= 10
                # Quiet accumulation: volume down + price stable
                elif vol_change < -20 and abs(price_change) < 2:
                    score += 5

            # Recent volume spike
            if len(volumes) >= 20:
                vol_20 = np.mean(volumes[-20:])
                if volumes[-1] > vol_20 * 2:
                    if closes[-1] > closes[-2]:
                        score += 10
                    else:
                        score -= 10

            # Price-volume divergence
            if len(closes) >= 10 and len(volumes) >= 10:
                price_trend = closes[-1] - closes[-10]
                vol_trend = np.mean(volumes[-5:]) - np.mean(volumes[-10:])
                if price_trend > 0 and vol_trend < 0:
                    score -= 5  # Price up on declining volume - weak
                elif price_trend < 0 and vol_trend > 0:
                    score -= 5  # Price down on increasing volume - distribution

            score = max(0, min(100, score))

            existing = await db.execute(
                select(CapitalFlowAnalysis).where(
                    CapitalFlowAnalysis.stock_id == stock.id,
                    CapitalFlowAnalysis.analysis_date == today,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.capital_flow_score = score
            else:
                db.add(CapitalFlowAnalysis(
                    stock_id=stock.id,
                    analysis_date=today,
                    capital_flow_score=score,
                ))
            count += 1

        await db.commit()
        return count


async def run_all_analysis():
    """Run all analysis steps: valuation, technical, fundamental, capital flow."""
    await run_valuation_analysis()
    await run_technical_analysis()
    await run_fundamental_analysis()
    await run_capital_flow_analysis()
