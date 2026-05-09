from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.domain.entities.order import OrderEntity
from finhealth.infrastructure.database.dao.order_repository import (
    OrderRepository,
)
from finhealth.infrastructure.database.models.order import OrderModel


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[OrderEntity]:
        stmt = (
            select(OrderModel)
            .where(OrderModel.sale_date >= from_date)
            .where(OrderModel.sale_date <= to_date)
            .order_by(OrderModel.sale_date, OrderModel.oid)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [row.to_entity() for row in rows]
