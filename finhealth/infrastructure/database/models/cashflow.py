from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.infrastructure.database.session import Base


class CashFlowEntryModel(Base):
    __tablename__ = "cashflow_entries"

    oid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    marketplace: Mapped[str] = mapped_column(String(16), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    entry_type: Mapped[str] = mapped_column(String(32), index=True)

    def to_entity(self) -> CashFlowEntry:
        return CashFlowEntry(
            entry_date=self.entry_date,
            marketplace=self.marketplace,
            amount=self.amount,
            entry_type=self.entry_type,
            oid=self.oid,
        )

    @classmethod
    def from_entity(cls, entity: CashFlowEntry) -> "CashFlowEntryModel":
        return cls(
            oid=entity.oid,
            entry_date=entity.entry_date,
            marketplace=entity.marketplace,
            amount=entity.amount,
            entry_type=entity.entry_type,
        )
