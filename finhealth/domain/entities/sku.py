from dataclasses import dataclass
from decimal import Decimal


@dataclass
class SKUEntity:
    sku_id: str
    name: str
    marketplace: str
    cost_of_goods: Decimal
    oid: int | None = None
