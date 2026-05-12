from pydantic import BaseModel, ConfigDict


class SKUProfitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku_id: str
    name: str
    marketplace: str
    revenue: float
    commissions: float
    logistics: float
    returns: float
    ad_spend: float
    cost_of_goods: float
    profit: float
    margin: float
    roi: float
