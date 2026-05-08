from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class CashFlowEntry:
    entry_date: date
    marketplace: str
    amount: Decimal
    entry_type: str
    oid: int | None = None
