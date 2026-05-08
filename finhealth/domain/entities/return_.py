from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class ReturnEntity:
    return_id: str
    sku_id: str
    marketplace: str
    return_date: date
    amount: Decimal
    oid: int | None = None
