from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.position import Position, PositionDetail, Transaction, HistorySummary
from app.models.daily_data import StockDailyData

router = APIRouter(prefix="/positions", tags=["positions"])


class BuyRequest(BaseModel):
    stock_code: str
    shares: float
    price: float
    buy_date: str | None = None
    note: str = ""


class SellRequest(BaseModel):
    stock_code: str
    shares: float
    price: float
    sell_date: str | None = None
    note: str = ""


@router.get("")
async def list_positions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Position, Stock.code, Stock.name, Stock.etf_list)
        .join(Stock, Position.stock_id == Stock.id)
        .where(Position.total_shares > 0)
    )
    rows = result.all()

    positions = []
    for pos, code, name, etf_list in rows:
        # Get latest price
        latest = (await db.execute(
            select(StockDailyData)
            .where(StockDailyData.stock_id == pos.stock_id)
            .order_by(StockDailyData.date.desc())
            .limit(1)
        )).scalar_one_or_none()

        latest_price = latest.close if latest else 0
        market_value = latest_price * pos.total_shares
        pnl = market_value - pos.total_cost
        pnl_pct = (pnl / pos.total_cost * 100) if pos.total_cost > 0 else 0

        positions.append({
            "id": pos.id,
            "stock_id": pos.stock_id,
            "code": code,
            "name": name,
            "etf_list": etf_list,
            "total_shares": pos.total_shares,
            "avg_cost": pos.avg_cost,
            "total_cost": pos.total_cost,
            "latest_price": latest_price,
            "market_value": market_value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        })

    # Summary
    total_cost = sum(p["total_cost"] for p in positions)
    total_value = sum(p["market_value"] for p in positions)
    total_pnl = total_value - total_cost

    return {
        "positions": positions,
        "summary": {
            "total_cost": total_cost,
            "total_value": total_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / total_cost * 100) if total_cost > 0 else 0,
        },
    }


@router.post("/buy")
async def buy_stock(data: BuyRequest, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(
        select(Stock).where(Stock.code == data.stock_code)
    )).scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    buy_date = date.fromisoformat(data.buy_date) if data.buy_date else date.today()

    # Record transaction
    tx = Transaction(
        stock_id=stock.id,
        type="buy",
        shares=data.shares,
        price=data.price,
        total_amount=data.shares * data.price,
        date=buy_date,
        note=data.note,
    )
    db.add(tx)

    # Update or create position
    pos = (await db.execute(
        select(Position).where(Position.stock_id == stock.id)
    )).scalar_one_or_none()

    if pos:
        new_total_cost = pos.total_cost + data.shares * data.price
        new_total_shares = pos.total_shares + data.shares
        pos.total_cost = new_total_cost
        pos.total_shares = new_total_shares
        pos.avg_cost = new_total_cost / new_total_shares if new_total_shares > 0 else 0
    else:
        pos = Position(
            stock_id=stock.id,
            total_shares=data.shares,
            avg_cost=data.price,
            total_cost=data.shares * data.price,
        )
        db.add(pos)

    # Record position detail
    detail = PositionDetail(
        position_id=pos.id if pos.id else 0,  # will be set after flush
        shares=data.shares,
        cost_price=data.price,
        buy_date=buy_date,
        note=data.note,
    )

    await db.flush()
    detail.position_id = pos.id
    db.add(detail)

    await db.commit()
    return {"message": "Buy recorded", "position_id": pos.id}


@router.post("/sell")
async def sell_stock(data: SellRequest, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(
        select(Stock).where(Stock.code == data.stock_code)
    )).scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    pos = (await db.execute(
        select(Position).where(Position.stock_id == stock.id)
    )).scalar_one_or_none()
    if not pos or pos.total_shares < data.shares:
        raise HTTPException(status_code=400, detail="Insufficient shares")

    sell_date = date.fromisoformat(data.sell_date) if data.sell_date else date.today()

    # Calculate P&L for this sell
    cost_of_sold = data.shares * pos.avg_cost
    proceeds = data.shares * data.price
    pnl = proceeds - cost_of_sold

    # Record transaction
    tx = Transaction(
        stock_id=stock.id,
        type="sell",
        shares=data.shares,
        price=data.price,
        total_amount=proceeds,
        date=sell_date,
        note=data.note,
    )
    db.add(tx)

    # Update position
    pos.total_shares -= data.shares
    pos.total_cost = pos.total_shares * pos.avg_cost
    if pos.total_shares <= 0:
        pos.total_shares = 0
        pos.total_cost = 0

    # Update history summary
    history = (await db.execute(select(HistorySummary).limit(1))).scalar_one_or_none()
    if not history:
        history = HistorySummary(total_pnl=0, total_invested=0)
        db.add(history)
    history.total_pnl += pnl
    history.total_invested += cost_of_sold

    await db.commit()
    return {"message": "Sell recorded", "pnl": round(pnl, 2)}


@router.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    history = (await db.execute(select(HistorySummary).limit(1))).scalar_one_or_none()
    if not history:
        return {"total_pnl": 0, "total_invested": 0, "return_rate": 0}
    return_rate = (history.total_pnl / history.total_invested * 100) if history.total_invested > 0 else 0
    return {
        "total_pnl": history.total_pnl,
        "total_invested": history.total_invested,
        "return_rate": round(return_rate, 2),
    }


@router.get("/transactions")
async def list_transactions(
    stock_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Transaction, Stock.code, Stock.name)
        .join(Stock, Transaction.stock_id == Stock.id)
        .order_by(Transaction.date.desc())
    )
    if stock_code:
        stmt = stmt.where(Stock.code == stock_code)
    result = await db.execute(stmt.limit(200))
    rows = result.all()
    return [
        {
            "id": tx.id,
            "code": code,
            "name": name,
            "type": tx.type,
            "shares": tx.shares,
            "price": tx.price,
            "total_amount": tx.total_amount,
            "date": str(tx.date),
            "note": tx.note,
        }
        for tx, code, name in rows
    ]


@router.post("/reset")
async def reset_positions(db: AsyncSession = Depends(get_db)):
    """Clear all positions, position details, transactions, and history."""
    from sqlalchemy import text

    await db.execute(text("DELETE FROM position_details"))
    await db.execute(text("DELETE FROM positions"))
    await db.execute(text("DELETE FROM transactions"))
    await db.execute(text("DELETE FROM history_summary"))
    await db.commit()
    return {"message": "All positions, transactions, and history cleared"}
