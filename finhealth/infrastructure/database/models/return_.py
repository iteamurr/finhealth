from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.infrastructure.database.session import Base


class ReturnModel(Base):
    __tablename__ = "returns"

    oid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    return_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    marketplace: Mapped[str] = mapped_column(String(16), index=True)
    return_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    def to_entity(self) -> ReturnEntity:
        return ReturnEntity(
            return_id=self.return_id,
            sku_id=self.sku_id,
            marketplace=self.marketplace,
            return_date=self.return_date,
            amount=self.amount,
            oid=self.oid,
        )

    @classmethod
    def from_entity(cls, entity: ReturnEntity) -> "ReturnModel":
        return cls(
            oid=entity.oid,
            return_id=entity.return_id,
            sku_id=entity.sku_id,
            marketplace=entity.marketplace,
            return_date=entity.return_date,
            amount=entity.amount,
        )
