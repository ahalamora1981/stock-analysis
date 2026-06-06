from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock
from app.models.position import Position, Suggestion
from app.models.analysis import CompositeScore
from app.models.daily_data import StockDailyData


async def generate_suggestions():
    """Generate buy/sell/rebalance suggestions based on positions and scores."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    today = date.today()
    async with async_session() as db:
        # Clear old suggestions
        old = await db.execute(select(Suggestion))
        for s in old.scalars().all():
            await db.delete(s)
        await db.flush()

        # Get all active positions with stock info
        positions = (await db.execute(
            select(Position, Stock.code, Stock.name, Stock.etf_list)
            .join(Stock, Position.stock_id == Stock.id)
            .where(Position.total_shares > 0)
        )).all()

        # Get latest composite scores for all stocks
        score_rows = (await db.execute(
            select(CompositeScore, Stock.code, Stock.name, Stock.etf_list)
            .join(Stock, CompositeScore.stock_id == Stock.id)
        )).all()
        score_map = {}
        for cs, code, name, etf in score_rows:
            if cs.stock_id not in score_map:
                score_map[cs.stock_id] = (cs, code, name, etf)

        # Get latest daily data for price comparison
        price_map = {}
        for stock_id in [pos.stock_id for pos, _, _, _ in positions]:
            latest = (await db.execute(
                select(StockDailyData)
                .where(StockDailyData.stock_id == stock_id)
                .order_by(StockDailyData.date.desc())
                .limit(1)
            )).scalar_one_or_none()
            if latest:
                price_map[stock_id] = latest

        suggestions = []

        # Check existing positions
        held_stock_ids = set()
        for pos, code, name, etf_list in positions:
            held_stock_ids.add(pos.stock_id)
            cs_info = score_map.get(pos.stock_id)
            latest = price_map.get(pos.stock_id)

            if not cs_info:
                continue
            cs = cs_info[0]

            # Calculate loss/gain percentage
            if pos.avg_cost > 0 and latest:
                pnl_pct = (latest.close - pos.avg_cost) / pos.avg_cost * 100
            else:
                pnl_pct = 0

            # Stop loss: loss > 15%
            if pnl_pct < -15:
                suggestions.append(Suggestion(
                    stock_id=pos.stock_id,
                    type="stop_loss",
                    reason=f"持仓亏损{abs(pnl_pct):.1f}%，超过止损线(15%)，建议止损卖出",
                    priority=2,
                ))
            # Take profit: gain > 30%
            elif pnl_pct > 30:
                suggestions.append(Suggestion(
                    stock_id=pos.stock_id,
                    type="take_profit",
                    reason=f"持仓盈利{pnl_pct:.1f}%，达到止盈目标(30%)，建议止盈减仓",
                    priority=1,
                ))
            # Low score - rebalance
            elif cs.total_score < 40:
                suggestions.append(Suggestion(
                    stock_id=pos.stock_id,
                    type="rebalance",
                    reason=f"综合评分偏低({cs.total_score:.0f}分)，建议考虑调仓换股",
                    priority=1,
                ))

        # Buy recommendations: high score stocks not held
        for stock_id, (cs, code, name, etf) in score_map.items():
            if stock_id in held_stock_ids:
                continue
            if cs.total_score >= 70 and cs.grade <= 2:
                suggestions.append(Suggestion(
                    stock_id=stock_id,
                    type="buy",
                    reason=f"综合评分{cs.total_score:.0f}分({['','优秀','良好','一般','较差'][cs.grade]})，未持仓，建议关注",
                    priority=0,
                ))

        # Sector concentration check
        sector_holdings = {}
        for pos, code, name, etf_list in positions:
            for etf in etf_list.split("、"):
                etf = etf.strip()
                sector_holdings[etf] = sector_holdings.get(etf, 0) + pos.total_cost

        total_cost = sum(p.total_cost for p, _, _, _ in positions)
        if total_cost > 0:
            for sector, cost in sector_holdings.items():
                ratio = cost / total_cost * 100
                if ratio > 40:
                    suggestions.append(Suggestion(
                        stock_id=positions[0][0].stock_id if positions else 0,
                        type="sector_alert",
                        reason=f"{sector}行业持仓占比{ratio:.1f}%，超过40%集中度上限，建议分散",
                        priority=1,
                    ))

        # Sort: high priority first
        suggestions.sort(key=lambda s: s.priority, reverse=True)
        for s in suggestions:
            db.add(s)

        await db.commit()
        return len(suggestions)


async def get_suggestions():
    """Get all active suggestions."""
    async with async_session() as db:
        result = await db.execute(
            select(Suggestion, Stock.code, Stock.name)
            .join(Stock, Suggestion.stock_id == Stock.id)
            .order_by(Suggestion.priority.desc(), Suggestion.created_at.desc())
        )
        rows = result.all()
        return [
            {
                "id": s.id,
                "code": code,
                "name": name,
                "type": s.type,
                "reason": s.reason,
                "priority": s.priority,
                "is_read": s.is_read,
                "created_at": str(s.created_at),
            }
            for s, code, name in rows
        ]
