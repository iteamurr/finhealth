from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from finhealth.domain.entities.profit import SKUProfitEntity
from finhealth.domain.services.financial_engine import FinancialEngine
from finhealth.infrastructure.database.dao.order_repository import (
    OrderRepository,
)
from finhealth.infrastructure.database.dao.return_repository import (
    ReturnRepository,
)
from finhealth.infrastructure.database.dao.sku_repository import SKURepository


@dataclass
class GetUnitEconomicsUseCase:
    sku_repo: SKURepository
    order_repo: OrderRepository
    return_repo: ReturnRepository
    engine: FinancialEngine

    async def execute(
        self, from_date: date, to_date: date
    ) -> list[SKUProfitEntity]:
        skus = await self.sku_repo.find_all()
        orders = await self.order_repo.find_by_date_range(from_date, to_date)
        returns = await self.return_repo.find_by_date_range(from_date, to_date)

        return [
            self.engine.compute_sku_profit(orders, returns, sku)
            for sku in skus
        ]
