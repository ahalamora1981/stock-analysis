from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime

from app.models.stock import Base


class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True, default=1)
    weight_valuation = Column(Float, default=25.0)
    weight_technical = Column(Float, default=20.0)
    weight_fundamental = Column(Float, default=25.0)
    weight_capital_flow = Column(Float, default=15.0)
    weight_momentum = Column(Float, default=15.0)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
