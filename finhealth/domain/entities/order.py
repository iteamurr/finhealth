from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class OrderEntity:
    order_id: str
    sku_id: str
    marketplace: str
    sale_date: date
    revenue: Decimal
    commission: Decimal
    logistics: Decimal
    ad_spend: Decimal
    oid: int | None = None
