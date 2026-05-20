from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from finhealth.domain.entities.profit import AlertEntity
from finhealth.domain.services.financial_engine import FinancialEngine
from finhealth.infrastructure.database.dao.cashflow_repository import (
    CashFlowRepository,
)
from finhealth.infrastructure.database.dao.order_repository import (
    OrderRepository,
)
from finhealth.infrastructure.database.dao.return_repository import (
    ReturnRepository,
)
from finhealth.infrastructure.database.dao.sku_repository import SKURepository


@dataclass
class GetAlertsUseCase:
    sku_repo: SKURepository
    order_repo: OrderRepository
    return_repo: ReturnRepository
    cashflow_repo: CashFlowRepository
    engine: FinancialEngine

    async def execute(
        self, from_date: date, to_date: date
    ) -> list[AlertEntity]:
        skus = await self.sku_repo.find_all()
        orders = await self.order_repo.find_by_date_range(from_date, to_date)
        returns = await self.return_repo.find_by_date_range(from_date, to_date)
        cashflow_entries = await self.cashflow_repo.find_by_date_range(
            from_date, to_date
        )

        sku_profits = [
            self.engine.compute_sku_profit(orders, returns, sku)
            for sku in skus
        ]

        return self.engine.detect_alerts(sku_profits, cashflow_entries)
