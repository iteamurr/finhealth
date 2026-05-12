from __future__ import annotations

import punq
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.domain.services.financial_engine import FinancialEngine
from finhealth.domain.services.financial_engine_impl import (
    DefaultFinancialEngine,
)
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
from finhealth.infrastructure.database.dao.sqlalchemy_cashflow_repository import (
    SqlAlchemyCashFlowRepository,
)
from finhealth.infrastructure.database.dao.sqlalchemy_order_repository import (
    SqlAlchemyOrderRepository,
)
from finhealth.infrastructure.database.dao.sqlalchemy_return_repository import (
    SqlAlchemyReturnRepository,
)
from finhealth.infrastructure.database.dao.sqlalchemy_sku_repository import (
    SqlAlchemySKURepository,
)
from finhealth.use_cases.get_alerts import GetAlertsUseCase
from finhealth.use_cases.get_cashflow import GetCashFlowUseCase
from finhealth.use_cases.get_dashboard_summary import (
    GetDashboardSummaryUseCase,
)
from finhealth.use_cases.get_profit_loss import GetProfitLossUseCase
from finhealth.use_cases.get_unit_economics import GetUnitEconomicsUseCase


def build_container(session: AsyncSession) -> punq.Container:
    container = punq.Container()

    # Session — fresh instance per container build (per request)
    container.register(AsyncSession, instance=session)

    # Domain services
    container.register(
        FinancialEngine,
        factory=DefaultFinancialEngine,
        scope=punq.Scope.singleton,
    )

    # DAOs — bind abstract interfaces to SqlAlchemy implementations
    container.register(
        SKURepository,
        factory=lambda: SqlAlchemySKURepository(session),
    )
    container.register(
        OrderRepository,
        factory=lambda: SqlAlchemyOrderRepository(session),
    )
    container.register(
        ReturnRepository,
        factory=lambda: SqlAlchemyReturnRepository(session),
    )
    container.register(
        CashFlowRepository,
        factory=lambda: SqlAlchemyCashFlowRepository(session),
    )

    # Use cases
    container.register(GetDashboardSummaryUseCase)
    container.register(GetProfitLossUseCase)
    container.register(GetUnitEconomicsUseCase)
    container.register(GetCashFlowUseCase)
    container.register(GetAlertsUseCase)

    return container
