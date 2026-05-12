from pydantic import BaseModel, ConfigDict


class ProfitLossResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gross_profit: float
    net_profit: float
    total_revenue: float
    total_commissions: float
    total_logistics: float
    total_returns: float
    total_ad_spend: float
    total_cogs: float
