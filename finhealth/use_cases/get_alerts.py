from __future__ import annotations

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


class GetAlertsUseCase:
    def __init__(
        self,
        sku_repo: SKURepository,
        order_repo: OrderRepository,
        return_repo: ReturnRepository,
        cashflow_repo: CashFlowRepository,
        engine: FinancialEngine,
    ) -> None:
        self._sku_repo = sku_repo
        self._order_repo = order_repo
        self._return_repo = return_repo
        self._cashflow_repo = cashflow_repo
        self._engine = engine

    async def execute(
        self, from_date: date, to_date: date
    ) -> list[AlertEntity]:
        skus = await self._sku_repo.find_all()
        orders = await self._order_repo.find_by_date_range(
            from_date, to_date
        )
        returns = await self._return_repo.find_by_date_range(
            from_date, to_date
        )
        cashflow_entries = await self._cashflow_repo.find_by_date_range(
            from_date, to_date
        )

        sku_profits = [
            self._engine.compute_sku_profit(orders, returns, sku)
            for sku in skus
        ]

        return self._engine.detect_alerts(sku_profits, cashflow_entries)
