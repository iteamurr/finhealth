from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import date

import punq
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from finhealth.container import build_container
from finhealth.infrastructure.database.session import get_session_factory
from finhealth.use_cases.get_alerts import GetAlertsUseCase
from finhealth.use_cases.get_cashflow import GetCashFlowUseCase
from finhealth.use_cases.get_dashboard_summary import (
    GetDashboardSummaryUseCase,
)
from finhealth.use_cases.get_profit_loss import GetProfitLossUseCase
from finhealth.use_cases.get_unit_economics import GetUnitEconomicsUseCase

MAX_DATE_RANGE_DAYS = 90


@dataclass(frozen=True)
class ValidatedDateRange:
    from_date: date
    to_date: date


def validate_date_range(
    from_date: date = Query(...),
    to_date: date = Query(...),
) -> ValidatedDateRange:
    if from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="from_date must be <= to_date",
        )
    span_days = (to_date - from_date).days
    if span_days > MAX_DATE_RANGE_DAYS:
        raise HTTPException(
            status_code=422,
            detail="Date range cannot exceed 90 days",
        )
    return ValidatedDateRange(from_date=from_date, to_date=to_date)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session


def get_container(
    session: AsyncSession = Depends(get_session),
) -> punq.Container:
    return build_container(session)


def get_dashboard_use_case(
    container: punq.Container = Depends(get_container),
) -> GetDashboardSummaryUseCase:
    return container.resolve(GetDashboardSummaryUseCase)


def get_profit_loss_use_case(
    container: punq.Container = Depends(get_container),
) -> GetProfitLossUseCase:
    return container.resolve(GetProfitLossUseCase)


def get_unit_economics_use_case(
    container: punq.Container = Depends(get_container),
) -> GetUnitEconomicsUseCase:
    return container.resolve(GetUnitEconomicsUseCase)


def get_cashflow_use_case(
    container: punq.Container = Depends(get_container),
) -> GetCashFlowUseCase:
    return container.resolve(GetCashFlowUseCase)


def get_alerts_use_case(
    container: punq.Container = Depends(get_container),
) -> GetAlertsUseCase:
    return container.resolve(GetAlertsUseCase)
