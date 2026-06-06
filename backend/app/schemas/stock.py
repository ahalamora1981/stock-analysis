from datetime import datetime

from pydantic import BaseModel


class StockCreate(BaseModel):
    code: str
    name: str
    etf_list: str = ""


class StockUpdate(BaseModel):
    name: str | None = None
    etf_list: str | None = None
    is_active: bool | None = None


class StockResponse(BaseModel):
    id: int
    code: str
    name: str
    etf_list: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
