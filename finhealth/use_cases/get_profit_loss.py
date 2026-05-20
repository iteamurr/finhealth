from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finhealth.domain.services.financial_engine import FinancialEngine
from finhealth.infrastructure.database.dao.order_repository import (
    OrderRepository,
)
from finhealth.infrastructure.database.dao.return_repository import (
    ReturnRepository,
)
from finhealth.infrastructure.database.dao.sku_repository import SKURepository


@dataclass
class ProfitLossDTO:
    gross_profit: Decimal
    net_profit: Decimal
    total_revenue: Decimal
    total_commissions: Decimal
    total_logistics: Decimal
    total_returns: Decimal
    total_ad_spend: Decimal
    total_cogs: Decimal


@dataclass
class GetProfitLossUseCase:
    sku_repo: SKURepository
    order_repo: OrderRepository
    return_repo: ReturnRepository
    engine: FinancialEngine

    async def execute(
        self,
        from_date: date,
        to_date: date,
        marketplace: str | None,
    ) -> ProfitLossDTO:
        skus = await self.sku_repo.find_all()
        orders = await self.order_repo.find_by_date_range(from_date, to_date)
        returns = await self.return_repo.find_by_date_range(from_date, to_date)

        if marketplace is not None:
            orders = [o for o in orders if o.marketplace == marketplace]
            returns = [r for r in returns if r.marketplace == marketplace]
            skus = [s for s in skus if s.marketplace == marketplace]

        pnl = self.engine.compute_pnl(orders, returns, skus)

        return ProfitLossDTO(
            gross_profit=pnl["gross_profit"],
            net_profit=pnl["net_profit"],
            total_revenue=pnl["total_revenue"],
            total_commissions=pnl["total_commissions"],
            total_logistics=pnl["total_logistics"],
            total_returns=pnl["total_returns"],
            total_ad_spend=pnl["total_ad_spend"],
            total_cogs=pnl["total_cogs"],
        )
