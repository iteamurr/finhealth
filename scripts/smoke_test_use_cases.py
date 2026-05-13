import asyncio
import os
import sys
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from finhealth.container import build_container
from finhealth.use_cases.get_alerts import GetAlertsUseCase
from finhealth.use_cases.get_cashflow import GetCashFlowUseCase
from finhealth.use_cases.get_dashboard_summary import (
    GetDashboardSummaryUseCase,
)
from finhealth.use_cases.get_profit_loss import GetProfitLossUseCase
from finhealth.use_cases.get_unit_economics import GetUnitEconomicsUseCase


def _fmt(value: Decimal) -> str:
    return f"{value:,.2f}"


def _section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


async def _run_dashboard(
    uc: GetDashboardSummaryUseCase, from_date: date, to_date: date
) -> None:
    _section("1. Dashboard summary")
    dto = await uc.execute(from_date, to_date)
    print(f"Total revenue:     {_fmt(dto.total_revenue)}")
    print(f"Net profit:        {_fmt(dto.net_profit)}")
    print(f"Margin:            {dto.margin:.2%}")
    print(f"Commission share:  {dto.commission_share:.2%}")
    print(f"Top SKUs ({len(dto.top_skus)}):")
    for sku in dto.top_skus:
        print(
            f"  - {sku.sku_id:>10} [{sku.marketplace}] "
            f"profit={_fmt(sku.profit)} margin={sku.margin:.2%}"
        )
    print(f"Daily profit buckets: {len(dto.daily_profits)} days")


async def _run_pnl(
    uc: GetProfitLossUseCase, from_date: date, to_date: date
) -> None:
    _section("2. Profit & Loss (all marketplaces)")
    dto = await uc.execute(from_date, to_date, marketplace=None)
    print(f"Revenue:       {_fmt(dto.total_revenue)}")
    print(f"Commissions:   {_fmt(dto.total_commissions)}")
    print(f"Logistics:     {_fmt(dto.total_logistics)}")
    print(f"Returns:       {_fmt(dto.total_returns)}")
    print(f"Ad spend:      {_fmt(dto.total_ad_spend)}")
    print(f"COGS:          {_fmt(dto.total_cogs)}")
    print(f"Gross profit:  {_fmt(dto.gross_profit)}")
    print(f"Net profit:    {_fmt(dto.net_profit)}")

    for mp in ("WB", "OZON"):
        dto_mp = await uc.execute(from_date, to_date, marketplace=mp)
        print(
            f"  [{mp}] revenue={_fmt(dto_mp.total_revenue)} "
            f"net={_fmt(dto_mp.net_profit)}"
        )


async def _run_unit_economics(
    uc: GetUnitEconomicsUseCase, from_date: date, to_date: date
) -> None:
    _section("3. Unit economics")
    rows = await uc.execute(from_date, to_date)
    print(f"SKUs analyzed: {len(rows)}")
    losers = [r for r in rows if r.profit < Decimal("0")]
    print(f"Loss-making SKUs: {len(losers)}")
    for r in losers[:5]:
        print(
            f"  - {r.sku_id:>10} [{r.marketplace}] "
            f"revenue={_fmt(r.revenue)} profit={_fmt(r.profit)} "
            f"margin={r.margin:.2%}"
        )


async def _run_cashflow(
    uc: GetCashFlowUseCase, from_date: date, to_date: date
) -> None:
    _section("4. Cash flow")
    dto = await uc.execute(from_date, to_date)
    print(f"Inflow:    {_fmt(dto.total_inflow)}")
    print(f"Outflow:   {_fmt(dto.total_outflow)}")
    print(f"Net cash:  {_fmt(dto.net_cash)}")
    print(f"Entries:   {len(dto.entries)}")
    print(f"Gaps:      {len(dto.gaps)}")
    for g in dto.gaps[:5]:
        print(
            f"  - {g['gap_start']} -> {g['gap_end']} "
            f"({g['days']} days)"
        )


async def _run_alerts(
    uc: GetAlertsUseCase, from_date: date, to_date: date
) -> None:
    _section("5. Alerts")
    alerts = await uc.execute(from_date, to_date)
    print(f"Alerts produced: {len(alerts)}")
    by_type: dict[str, int] = {}
    for a in alerts:
        by_type[a.alert_type] = by_type.get(a.alert_type, 0) + 1
    for k, v in by_type.items():
        print(f"  - {k}: {v}")
    print("Sample (up to 5):")
    for a in alerts[:5]:
        print(f"  [{a.severity:>8}] {a.alert_type}: {a.message}")


async def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL is not set", file=sys.stderr)
        return 1

    engine = create_async_engine(url, echo=False, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        bind=engine, expire_on_commit=False
    )

    today = date.today()
    from_date = today - timedelta(days=30)

    print(f"Window: {from_date} -> {today}")

    try:
        async with session_factory() as session:
            container = build_container(session)

            dashboard_uc = container.resolve(GetDashboardSummaryUseCase)
            pnl_uc = container.resolve(GetProfitLossUseCase)
            unit_uc = container.resolve(GetUnitEconomicsUseCase)
            cashflow_uc = container.resolve(GetCashFlowUseCase)
            alerts_uc = container.resolve(GetAlertsUseCase)

            await _run_dashboard(dashboard_uc, from_date, today)
            await _run_pnl(pnl_uc, from_date, today)
            await _run_unit_economics(unit_uc, from_date, today)
            await _run_cashflow(cashflow_uc, from_date, today)
            await _run_alerts(alerts_uc, from_date, today)

        print()
        print("OK: all 5 use cases executed")
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
