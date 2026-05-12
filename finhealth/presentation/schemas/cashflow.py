from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class CashFlowEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_date: date
    marketplace: str
    amount: float
    entry_type: str


class CashFlowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_inflow: float
    total_outflow: float
    net_cash: float
    entries: list[CashFlowEntryResponse]
    gaps: list[dict[str, Any]]
