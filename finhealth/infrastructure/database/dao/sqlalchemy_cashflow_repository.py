from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.infrastructure.database.dao.cashflow_repository import (
    CashFlowRepository,
)
from finhealth.infrastructure.database.models.cashflow import (
    CashFlowEntryModel,
)


class SqlAlchemyCashFlowRepository(CashFlowRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[CashFlowEntry]:
        stmt = (
            select(CashFlowEntryModel)
            .where(CashFlowEntryModel.entry_date >= from_date)
            .where(CashFlowEntryModel.entry_date <= to_date)
            .order_by(CashFlowEntryModel.entry_date, CashFlowEntryModel.oid)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [row.to_entity() for row in rows]
