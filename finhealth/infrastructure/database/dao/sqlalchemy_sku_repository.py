from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.domain.entities.sku import SKUEntity
from finhealth.infrastructure.database.dao.sku_repository import SKURepository
from finhealth.infrastructure.database.models.sku import SKUModel


class SqlAlchemySKURepository(SKURepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_all(self) -> list[SKUEntity]:
        stmt = select(SKUModel).order_by(SKUModel.oid)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [row.to_entity() for row in rows]
