from dataclasses import dataclass
from decimal import Decimal


@dataclass
class SKUProfitEntity:
    sku_id: str
    name: str
    marketplace: str
    revenue: Decimal
    commissions: Decimal
    logistics: Decimal
    returns: Decimal
    ad_spend: Decimal
    cost_of_goods: Decimal
    profit: Decimal
    margin: Decimal
    roi: Decimal


@dataclass
class AlertEntity:
    alert_type: str
    severity: str
    message: str
    sku_id: str | None = None
    value: Decimal | None = None
