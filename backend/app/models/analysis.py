from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.stock import Base


class ValuationAnalysis(Base):
    __tablename__ = "valuation_analysis"
    __table_args__ = (UniqueConstraint("stock_id", "analysis_date", name="uq_valuation_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    pe_ttm: Mapped[float] = mapped_column(Float, default=0)
    pe_percentile: Mapped[float] = mapped_column(Float, default=50)
    pb: Mapped[float] = mapped_column(Float, default=0)
    pb_percentile: Mapped[float] = mapped_column(Float, default=50)
    dividend_yield: Mapped[float] = mapped_column(Float, default=0)
    valuation_score: Mapped[float] = mapped_column(Float, default=50)
    valuation_level: Mapped[str] = mapped_column(Integer, default=0)  # 0=unknown, 1=低估, 2=合理, 3=高估
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TechnicalAnalysis(Base):
    __tablename__ = "technical_analysis"
    __table_args__ = (UniqueConstraint("stock_id", "analysis_date", name="uq_technical_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    ma5: Mapped[float] = mapped_column(Float, default=0)
    ma10: Mapped[float] = mapped_column(Float, default=0)
    ma20: Mapped[float] = mapped_column(Float, default=0)
    ma60: Mapped[float] = mapped_column(Float, default=0)
    macd: Mapped[float] = mapped_column(Float, default=0)
    macd_signal: Mapped[float] = mapped_column(Float, default=0)
    macd_hist: Mapped[float] = mapped_column(Float, default=0)
    kdj_k: Mapped[float] = mapped_column(Float, default=50)
    kdj_d: Mapped[float] = mapped_column(Float, default=50)
    kdj_j: Mapped[float] = mapped_column(Float, default=50)
    rsi_6: Mapped[float] = mapped_column(Float, default=50)
    rsi_14: Mapped[float] = mapped_column(Float, default=50)
    technical_score: Mapped[float] = mapped_column(Float, default=50)
    signal: Mapped[int] = mapped_column(Integer, default=0)  # 0=unknown, 1=买入, 2=持有, 3=卖出
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class FundamentalAnalysis(Base):
    __tablename__ = "fundamental_analysis"
    __table_args__ = (UniqueConstraint("stock_id", "analysis_date", name="uq_fundamental_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    roe: Mapped[float] = mapped_column(Float, default=0)
    gross_margin: Mapped[float] = mapped_column(Float, default=0)
    net_margin: Mapped[float] = mapped_column(Float, default=0)
    revenue_growth: Mapped[float] = mapped_column(Float, default=0)
    net_profit_growth: Mapped[float] = mapped_column(Float, default=0)
    debt_ratio: Mapped[float] = mapped_column(Float, default=0)
    fundamental_score: Mapped[float] = mapped_column(Float, default=50)
    quality_level: Mapped[int] = mapped_column(Integer, default=0)  # 0=unknown, 1=优秀, 2=良好, 3=一般, 4=较差
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CapitalFlowAnalysis(Base):
    __tablename__ = "capital_flow_analysis"
    __table_args__ = (UniqueConstraint("stock_id", "analysis_date", name="uq_capital_flow_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    main_force_net: Mapped[float] = mapped_column(Float, default=0)
    northbound_flow: Mapped[float] = mapped_column(Float, default=0)
    capital_flow_score: Mapped[float] = mapped_column(Float, default=50)
    flow_level: Mapped[int] = mapped_column(Integer, default=0)  # 0=unknown, 1=大幅流入, 2=小幅流入, 3=平衡, 4=小幅流出, 5=大幅流出
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CompositeScore(Base):
    __tablename__ = "composite_score"
    __table_args__ = (UniqueConstraint("stock_id", "analysis_date", name="uq_composite_stock_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    valuation_score: Mapped[float] = mapped_column(Float, default=50)
    technical_score: Mapped[float] = mapped_column(Float, default=50)
    fundamental_score: Mapped[float] = mapped_column(Float, default=50)
    capital_flow_score: Mapped[float] = mapped_column(Float, default=50)
    momentum_score: Mapped[float] = mapped_column(Float, default=50)
    total_score: Mapped[float] = mapped_column(Float, default=50)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    grade: Mapped[int] = mapped_column(Integer, default=0)  # 0=unknown, 1=优秀, 2=良好, 3=一般, 4=较差
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
