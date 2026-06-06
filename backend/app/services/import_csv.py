import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models.stock import Base, Stock

CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / "stocks" / "A股行业ETF持仓股票.csv"


async def import_stocks():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                code = row["股票代码"].strip()
                name = row["股票名称"].strip()
                etf_list = row["所属ETF"].strip()
                existing = await db.execute(select(Stock).where(Stock.code == code))
                if existing.scalar_one_or_none():
                    continue
                db.add(Stock(code=code, name=name, etf_list=etf_list))
                count += 1
            await db.commit()
            print(f"Imported {count} stocks")


if __name__ == "__main__":
    import asyncio

    asyncio.run(import_stocks())
