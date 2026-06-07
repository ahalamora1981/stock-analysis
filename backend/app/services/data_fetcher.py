import os
import re
import time

import pandas as pd
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock
from app.models.daily_data import StockDailyData


def _get_session() -> requests.Session:
    s = requests.Session()
    # Support proxy via environment variable
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("https_proxy")
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


def _get_stock_codes():
    """Get all active stock codes (sync helper)."""
    import sqlite3
    from app.config import DATABASE_URL

    db_path = DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT code FROM stocks WHERE is_active = 1").fetchall()
    conn.close()
    return [r[0] for r in rows]


def fetch_realtime_quotes() -> pd.DataFrame:
    """Fetch real-time quotes via Tencent finance API."""
    codes = _get_stock_codes()
    prefixes = [("sh" if c.startswith("6") else "sz") for c in codes]
    symbols = [f"{p}{c}" for p, c in zip(prefixes, codes)]

    s = _get_session()
    all_rows = []
    batch_size = 50

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i : i + batch_size]
        query = ",".join(batch)
        try:
            resp = s.get(f"https://qt.gtimg.cn/q={query}", timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch batch {i}: {e}")
            continue
        for line in resp.text.strip().split("\n"):
            if "=" not in line:
                continue
            match = re.match(r'v_(\w+)="(.+)"', line.strip().rstrip(";"))
            if not match:
                continue
            symbol = match.group(1)
            data = match.group(2).split("~")
            if len(data) < 40:
                continue
            code = symbol[2:]
            try:
                row = {
                    "代码": code,
                    "名称": data[1],
                    "最新价": float(data[3] or 0),
                    "昨收": float(data[4] or 0),
                    "今开": float(data[5] or 0),
                    "成交量": float(data[6] or 0),
                    "最高": float(data[33] or 0),
                    "最低": float(data[34] or 0),
                    "涨跌幅": float(data[32] or 0),
                    "成交额": float(data[37] or 0),
                    "换手率": float(data[38] or 0),
                    "市盈率 - 动态": float(data[39] or 0),
                    "总市值": float(data[44] or 0),
                    "市净率": float(data[46] or 0) if len(data) > 46 else 0,
                }
                all_rows.append(row)
            except (ValueError, IndexError):
                continue

    print(f"Fetched quotes for {len(all_rows)} stocks")
    return pd.DataFrame(all_rows)


def fetch_stock_history(code: str, days: int = 250) -> list[dict]:
    """Fetch historical daily data via Tencent kline API."""
    prefix = "sh" if code.startswith("6") else "sz"
    symbol = f"{prefix}{code}"
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "_var": "kline_dayqfq",
        "param": f"{symbol},day,,,{days},qfq",
    }
    s = _get_session()
    try:
        resp = s.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch history for {code}: {e}")
        return []
    text = resp.text
    # Parse: kline_dayqfq={...}
    json_str = text.split("=", 1)[1] if "=" in text else text
    import json
    data = json.loads(json_str)

    records = []
    klines = data.get("data", {}).get(symbol, {}).get("qfqday", [])
    if not klines:
        klines = data.get("data", {}).get(symbol, {}).get("day", [])
    for k in klines:
        if len(k) < 6:
            continue
        records.append({
            "date": k[0],
            "open": float(k[1]),
            "close": float(k[2]),
            "high": float(k[3]),
            "low": float(k[4]),
            "volume": float(k[5]),
        })
    return records


def update_all_daily_data():
    """Fetch and store daily data for all active stocks."""
    from sqlalchemy.orm import Session

    db_path = "data/stock_analysis.db"
    engine_sync = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine_sync)

    quotes = fetch_realtime_quotes()
    quote_map = {}
    for _, row in quotes.iterrows():
        code = str(row["代码"]).strip()
        quote_map[code] = row

    with Session(engine_sync) as db:
        stocks = db.execute(select(Stock).where(Stock.is_active == True)).scalars().all()
        count = 0
        for stock in stocks:
            q = quote_map.get(stock.code)
            if q is None:
                continue
            today = pd.Timestamp.now().date()
            existing = db.execute(
                select(StockDailyData).where(
                    StockDailyData.stock_id == stock.id,
                    StockDailyData.date == today,
                )
            ).scalar_one_or_none()
            if existing:
                continue
            db.add(
                StockDailyData(
                    stock_id=stock.id,
                    date=today,
                    open=float(q.get("今开", 0) or 0),
                    high=float(q.get("最高", 0) or 0),
                    low=float(q.get("最低", 0) or 0),
                    close=float(q.get("最新价", 0) or 0),
                    volume=float(q.get("成交量", 0) or 0),
                    amount=float(q.get("成交额", 0) or 0),
                    turnover_rate=float(q.get("换手率", 0) or 0),
                    pe_ttm=float(q.get("市盈率-动态", 0) or 0),
                    pb=float(q.get("市净率", 0) or 0),
                    market_cap=float(q.get("总市值", 0) or 0),
                    change_pct=float(q.get("涨跌幅", 0) or 0),
                )
            )
            count += 1
        db.commit()
    engine_sync.dispose()
    return count


def fetch_all_history():
    """Fetch historical kline data for all active stocks."""
    import sqlalchemy
    from sqlalchemy.orm import Session

    db_path = "data/stock_analysis.db"
    engine_sync = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine_sync)

    with Session(engine_sync) as db:
        stocks = db.execute(select(Stock).where(Stock.is_active == True)).scalars().all()
        count = 0
        for stock in stocks:
            records = fetch_stock_history(stock.code, 250)
            for rec in records:
                rec_date = pd.Timestamp(rec["date"]).date()
                existing = db.execute(
                    select(StockDailyData).where(
                        StockDailyData.stock_id == stock.id,
                        StockDailyData.date == rec_date,
                    )
                ).scalar_one_or_none()
                if existing:
                    continue
                db.add(StockDailyData(
                    stock_id=stock.id,
                    date=rec_date,
                    open=rec["open"],
                    high=rec["high"],
                    low=rec["low"],
                    close=rec["close"],
                    volume=rec["volume"],
                ))
                count += 1
            db.commit()
            print(f"  {stock.code} {stock.name}: {len(records)} days")
            time.sleep(0.3)
    engine_sync.dispose()
    return count


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "history":
        n = fetch_all_history()
        print(f"Imported {n} historical records")
    else:
        n = update_all_daily_data()
        print(f"Updated {n} stocks with today's data")
