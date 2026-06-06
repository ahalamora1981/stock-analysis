import re

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.daily_data import StockDailyData
from app.schemas.stock import StockCreate, StockResponse, StockUpdate

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=list[StockResponse])
async def list_stocks(
    search: str | None = Query(None, description="Search by code or name"),
    etf: str | None = Query(None, description="Filter by ETF name"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Stock).where(Stock.is_active == True)
    if search:
        stmt = stmt.where(
            (Stock.code.contains(search)) | (Stock.name.contains(search))
        )
    if etf:
        stmt = stmt.where(Stock.etf_list.contains(etf))
    stmt = stmt.order_by(Stock.code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/with-latest")
async def list_stocks_with_latest(
    search: str | None = Query(None),
    etf: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List stocks with latest daily data for display."""
    stmt = select(Stock).where(Stock.is_active == True)
    if search:
        stmt = stmt.where(
            (Stock.code.contains(search)) | (Stock.name.contains(search))
        )
    if etf:
        stmt = stmt.where(Stock.etf_list.contains(etf))
    stmt = stmt.order_by(Stock.code)
    result = await db.execute(stmt)
    stocks = result.scalars().all()

    rows = []
    for stock in stocks:
        sub = (
            select(StockDailyData)
            .where(StockDailyData.stock_id == stock.id)
            .order_by(StockDailyData.date.desc())
            .limit(1)
        )
        latest = (await db.execute(sub)).scalar_one_or_none()
        rows.append({
            "id": stock.id,
            "code": stock.code,
            "name": stock.name,
            "etf_list": stock.etf_list,
            "is_active": stock.is_active,
            "close": latest.close if latest else 0,
            "change_pct": latest.change_pct if latest else 0,
            "pe_ttm": latest.pe_ttm if latest else 0,
            "pb": latest.pb if latest else 0,
            "market_cap": latest.market_cap if latest else 0,
            "volume": latest.volume if latest else 0,
            "date": str(latest.date) if latest else "",
        })
    return rows


@router.get("/check-code")
async def check_stock_code(code: str):
    """Validate stock code and return name from Tencent API."""
    prefix = "sh" if code.startswith("6") else "sz"
    symbol = f"{prefix}{code}"
    try:
        resp = requests.get(f"https://qt.gtimg.cn/q={symbol}", timeout=10)
        match = re.search(r'"(.+)"', resp.text)
        if not match:
            raise HTTPException(status_code=400, detail="股票代码无效")
        data = match.group(1).split("~")
        if len(data) < 2 or not data[1]:
            raise HTTPException(status_code=400, detail="股票代码无效")
        return {"code": code, "name": data[1]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="验证失败，请稍后重试")


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock(stock_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("", response_model=StockResponse, status_code=201)
async def create_stock(data: StockCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Stock).where(Stock.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Stock code already exists")
    stock = Stock(**data.model_dump())
    db.add(stock)
    await db.commit()
    await db.refresh(stock)
    return stock


@router.get("/check-code")
async def check_stock_code(code: str):
    """Validate stock code and return name from Tencent API."""
    existing_prefix = "sh" if code.startswith("6") else "sz"
    symbol = f"{existing_prefix}{code}"
    try:
        resp = requests.get(f"https://qt.gtimg.cn/q={symbol}", timeout=10)
        match = re.search(r'"(.+)"', resp.text)
        if not match:
            raise HTTPException(status_code=400, detail="股票代码无效")
        data = match.group(1).split("~")
        if len(data) < 2 or not data[1]:
            raise HTTPException(status_code=400, detail="股票代码无效")
        return {"code": code, "name": data[1]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="验证失败，请稍后重试")


@router.post("/add-by-code", response_model=StockResponse, status_code=201)
async def add_stock_by_code(code: str, db: AsyncSession = Depends(get_db)):
    """Add a stock by code, fetching name from Tencent API."""
    existing = await db.execute(select(Stock).where(Stock.code == code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="股票已存在")

    prefix = "sh" if code.startswith("6") else "sz"
    symbol = f"{prefix}{code}"
    try:
        resp = requests.get(f"https://qt.gtimg.cn/q={symbol}", timeout=10)
        match = re.search(r'"(.+)"', resp.text)
        if not match:
            raise HTTPException(status_code=400, detail="股票代码无效")
        data = match.group(1).split("~")
        if len(data) < 2 or not data[1]:
            raise HTTPException(status_code=400, detail="股票代码无效")
        name = data[1]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="获取股票信息失败")

    stock = Stock(code=code, name=name, etf_list="")
    db.add(stock)
    await db.commit()
    await db.refresh(stock)
    return stock


@router.put("/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int, data: StockUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(stock, key, value)
    await db.commit()
    await db.refresh(stock)
    return stock


@router.delete("/{stock_id}", status_code=204)
async def delete_stock(stock_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    stock.is_active = False
    await db.commit()
