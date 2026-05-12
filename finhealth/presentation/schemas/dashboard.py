from typing import Any

from pydantic import BaseModel, ConfigDict

from finhealth.presentation.schemas.sku import SKUProfitResponse


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_revenue: float
    net_profit: float
    margin: float
    commission_share: float
    top_skus: list[SKUProfitResponse]
    daily_profits: list[dict[str, Any]]
