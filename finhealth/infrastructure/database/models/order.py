from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from finhealth.domain.entities.order import OrderEntity
from finhealth.infrastructure.database.session import Base


class OrderModel(Base):
    __tablename__ = "orders"

    oid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    sku_id: Mapped[str] = mapped_column(String(64), index=True)
    marketplace: Mapped[str] = mapped_column(String(16), index=True)
    sale_date: Mapped[date] = mapped_column(Date, index=True)
    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    commission: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    logistics: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    ad_spend: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    def to_entity(self) -> OrderEntity:
        return OrderEntity(
            order_id=self.order_id,
            sku_id=self.sku_id,
            marketplace=self.marketplace,
            sale_date=self.sale_date,
            revenue=self.revenue,
            commission=self.commission,
            logistics=self.logistics,
            ad_spend=self.ad_spend,
            oid=self.oid,
        )

    @classmethod
    def from_entity(cls, entity: OrderEntity) -> "OrderModel":
        return cls(
            oid=entity.oid,
            order_id=entity.order_id,
            sku_id=entity.sku_id,
            marketplace=entity.marketplace,
            sale_date=entity.sale_date,
            revenue=entity.revenue,
            commission=entity.commission,
            logistics=entity.logistics,
            ad_spend=entity.ad_spend,
        )
