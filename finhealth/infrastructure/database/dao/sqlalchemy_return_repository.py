from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.infrastructure.database.dao.return_repository import (
    ReturnRepository,
)
from finhealth.infrastructure.database.models.return_ import ReturnModel


class SqlAlchemyReturnRepository(ReturnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[ReturnEntity]:
        stmt = (
            select(ReturnModel)
            .where(ReturnModel.return_date >= from_date)
            .where(ReturnModel.return_date <= to_date)
            .order_by(ReturnModel.return_date, ReturnModel.oid)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [row.to_entity() for row in rows]
