from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from finhealth.domain.entities.sku import SKUEntity
from finhealth.infrastructure.database.session import Base


class SKUModel(Base):
    __tablename__ = "skus"

    oid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    marketplace: Mapped[str] = mapped_column(String(16), index=True)
    cost_of_goods: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    def to_entity(self) -> SKUEntity:
        return SKUEntity(
            sku_id=self.sku_id,
            name=self.name,
            marketplace=self.marketplace,
            cost_of_goods=self.cost_of_goods,
            oid=self.oid,
        )

    @classmethod
    def from_entity(cls, entity: SKUEntity) -> "SKUModel":
        return cls(
            oid=entity.oid,
            sku_id=entity.sku_id,
            name=entity.name,
            marketplace=entity.marketplace,
            cost_of_goods=entity.cost_of_goods,
        )
