from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from finhealth.domain.entities.profit import SKUProfitEntity
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
class DashboardSummaryDTO:
    total_revenue: Decimal
    net_profit: Decimal
    margin: Decimal
    commission_share: Decimal
    top_skus: list[SKUProfitEntity] = field(default_factory=list)
    daily_profits: list[dict[str, Any]] = field(default_factory=list)


class GetDashboardSummaryUseCase:
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
    ) -> DashboardSummaryDTO:
        skus = await self._sku_repo.find_all()
        orders = await self._order_repo.find_by_date_range(
            from_date, to_date
        )
        returns = await self._return_repo.find_by_date_range(
            from_date, to_date
        )

        pnl = self._engine.compute_pnl(orders, returns, skus)
        total_revenue: Decimal = pnl["total_revenue"]
        net_profit: Decimal = pnl["net_profit"]
        total_commissions: Decimal = pnl["total_commissions"]

        margin = (
            net_profit / total_revenue
            if total_revenue > Decimal("0")
            else Decimal("0")
        )
        commission_share = (
            total_commissions / total_revenue
            if total_revenue > Decimal("0")
            else Decimal("0")
        )

        sku_profits = [
            self._engine.compute_sku_profit(orders, returns, sku)
            for sku in skus
        ]
        top_skus = sorted(
            sku_profits, key=lambda s: s.profit, reverse=True
        )[:5]

        daily_profits = self._build_daily_profits(orders, returns)

        return DashboardSummaryDTO(
            total_revenue=total_revenue,
            net_profit=net_profit,
            margin=margin,
            commission_share=commission_share,
            top_skus=top_skus,
            daily_profits=daily_profits,
        )

    @staticmethod
    def _build_daily_profits(
        orders: list[Any], returns: list[Any]
    ) -> list[dict[str, Any]]:
        # date -> marketplace -> running profit
        bucket: dict[date, dict[str, Decimal]] = defaultdict(
            lambda: defaultdict(lambda: Decimal("0"))
        )
        for o in orders:
            bucket[o.sale_date][o.marketplace] += (
                o.revenue - o.commission - o.logistics - o.ad_spend
            )
        for r in returns:
            bucket[r.return_date][r.marketplace] -= r.amount

        result: list[dict[str, Any]] = []
        for day in sorted(bucket.keys()):
            entry: dict[str, Any] = {"date": day}
            for mp, value in bucket[day].items():
                entry[mp] = value
            result.append(entry)
        return result
