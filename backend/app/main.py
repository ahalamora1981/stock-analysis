from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_V1_PREFIX
from app.database import engine
from app.models.stock import Base
from app.models.daily_data import StockDailyData  # noqa: F401
from app.models.analysis import (  # noqa: F401
    ValuationAnalysis, TechnicalAnalysis,
    FundamentalAnalysis, CapitalFlowAnalysis, CompositeScore,
)
from app.models.position import Position, PositionDetail, Transaction, Suggestion, HistorySummary  # noqa: F401
from app.models.config import AppConfig  # noqa: F401
from app.routers.stocks import router as stocks_router
from app.routers.data import router as data_router
from app.routers.analysis import router as analysis_router
from app.routers.positions import router as positions_router
from app.routers.suggestions import router as suggestions_router
from app.routers.sectors import router as sectors_router
from app.routers.market import router as market_router
from app.routers.export import router as export_router
from app.routers.config import router as config_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Stock Analysis API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks_router, prefix=API_V1_PREFIX)
app.include_router(data_router, prefix=API_V1_PREFIX)
app.include_router(analysis_router, prefix=API_V1_PREFIX)
app.include_router(positions_router, prefix=API_V1_PREFIX)
app.include_router(suggestions_router, prefix=API_V1_PREFIX)
app.include_router(sectors_router, prefix=API_V1_PREFIX)
app.include_router(market_router, prefix=API_V1_PREFIX)
app.include_router(export_router, prefix=API_V1_PREFIX)
app.include_router(config_router, prefix=API_V1_PREFIX)


@app.get(f"{API_V1_PREFIX}/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
