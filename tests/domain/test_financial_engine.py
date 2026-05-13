from __future__ import annotations

from datetime import date
from decimal import Decimal

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.domain.entities.order import OrderEntity
from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.domain.entities.sku import SKUEntity
from finhealth.domain.services.financial_engine_impl import (
    DefaultFinancialEngine,
)


def _make_sku(
    sku_id: str = "SKU-1",
    cost: Decimal = Decimal("100"),
) -> SKUEntity:
    return SKUEntity(
        sku_id=sku_id,
        name="Test SKU",
        marketplace="WB",
        cost_of_goods=cost,
    )


def _make_order(
    sku_id: str = "SKU-1",
    revenue: Decimal = Decimal("1000"),
    commission: Decimal = Decimal("100"),
    logistics: Decimal = Decimal("50"),
    ad_spend: Decimal = Decimal("30"),
) -> OrderEntity:
    return OrderEntity(
        order_id="ORD-1",
        sku_id=sku_id,
        marketplace="WB",
        sale_date=date(2026, 5, 1),
        revenue=revenue,
        commission=commission,
        logistics=logistics,
        ad_spend=ad_spend,
    )


def test_sku_profit_known_values() -> None:
    engine = DefaultFinancialEngine()
    sku = _make_sku(cost=Decimal("400"))
    orders = [
        _make_order(
            revenue=Decimal("1000"),
            commission=Decimal("100"),
            logistics=Decimal("50"),
            ad_spend=Decimal("30"),
        )
    ]
    returns = [
        ReturnEntity(
            return_id="R-1",
            sku_id="SKU-1",
            marketplace="WB",
            return_date=date(2026, 5, 2),
            amount=Decimal("20"),
        )
    ]

    result = engine.compute_sku_profit(orders, returns, sku)

    # profit = 1000 - 100 - 50 - 20 - 30 = 800
    assert result.profit == Decimal("800")
    # margin = 800 / 1000 = 0.8
    assert result.margin == Decimal("0.8")
    # roi = 800 / 400 = 2
    assert result.roi == Decimal("2")
    assert result.revenue == Decimal("1000")
    assert result.commissions == Decimal("100")
    assert result.logistics == Decimal("50")
    assert result.returns == Decimal("20")
    assert result.ad_spend == Decimal("30")


def test_sku_margin_zero_revenue() -> None:
    engine = DefaultFinancialEngine()
    sku = _make_sku(cost=Decimal("100"))

    result = engine.compute_sku_profit([], [], sku)

    assert result.revenue == Decimal("0")
    assert result.margin == Decimal("0")
    assert result.profit == Decimal("0")
    assert result.roi == Decimal("0")


def test_sku_roi_zero_cost() -> None:
    engine = DefaultFinancialEngine()
    sku = _make_sku(cost=Decimal("0"))
    orders = [_make_order()]

    result = engine.compute_sku_profit(orders, [], sku)

    assert result.roi == Decimal("0")


def test_pnl_aggregation() -> None:
    engine = DefaultFinancialEngine()
    skus = [
        _make_sku("SKU-1", cost=Decimal("100")),
        _make_sku("SKU-2", cost=Decimal("200")),
    ]
    orders = [
        _make_order(
            sku_id="SKU-1",
            revenue=Decimal("500"),
            commission=Decimal("50"),
            logistics=Decimal("20"),
            ad_spend=Decimal("10"),
        ),
        _make_order(
            sku_id="SKU-2",
            revenue=Decimal("800"),
            commission=Decimal("80"),
            logistics=Decimal("30"),
            ad_spend=Decimal("40"),
        ),
    ]
    returns = [
        ReturnEntity(
            return_id="R-1",
            sku_id="SKU-1",
            marketplace="WB",
            return_date=date(2026, 5, 3),
            amount=Decimal("25"),
        )
    ]

    pnl = engine.compute_pnl(orders, returns, skus)

    assert pnl["total_revenue"] == Decimal("1300")
    assert pnl["total_commissions"] == Decimal("130")
    assert pnl["total_logistics"] == Decimal("50")
    assert pnl["total_returns"] == Decimal("25")
    assert pnl["total_ad_spend"] == Decimal("50")
    assert pnl["total_cogs"] == Decimal("300")
    # gross = 1300 - 130 - 50 - 25 = 1095
    assert pnl["gross_profit"] == Decimal("1095")
    # net = 1095 - 50 - 300 = 745
    assert pnl["net_profit"] == Decimal("745")


def test_alert_low_margin() -> None:
    engine = DefaultFinancialEngine()
    sku = _make_sku(cost=Decimal("400"))
    # revenue=1000, total costs=970 -> profit=30, margin=0.03 < 0.05
    orders = [
        _make_order(
            revenue=Decimal("1000"),
            commission=Decimal("900"),
            logistics=Decimal("40"),
            ad_spend=Decimal("30"),
        )
    ]
    sku_profit = engine.compute_sku_profit(orders, [], sku)

    alerts = engine.detect_alerts([sku_profit], [])

    assert any(a.alert_type == "low_margin" for a in alerts)
    low = next(a for a in alerts if a.alert_type == "low_margin")
    assert low.severity == "warning"
    assert low.sku_id == sku.sku_id


def test_alert_loss() -> None:
    engine = DefaultFinancialEngine()
    sku = _make_sku(cost=Decimal("100"))
    orders = [
        _make_order(
            revenue=Decimal("100"),
            commission=Decimal("200"),
            logistics=Decimal("50"),
            ad_spend=Decimal("30"),
        )
    ]
    sku_profit = engine.compute_sku_profit(orders, [], sku)

    assert sku_profit.profit < Decimal("0")

    alerts = engine.detect_alerts([sku_profit], [])

    assert any(a.alert_type == "loss" for a in alerts)
    loss = next(a for a in alerts if a.alert_type == "loss")
    assert loss.severity == "critical"
    assert loss.sku_id == sku.sku_id
    # Loss SKU should not also trigger low_margin alert
    assert not any(
        a.alert_type == "low_margin" and a.sku_id == sku.sku_id
        for a in alerts
    )


def test_cashflow_gap_detection() -> None:
    engine = DefaultFinancialEngine()
    entries = [
        CashFlowEntry(
            entry_date=date(2026, 5, 1),
            marketplace="WB",
            amount=Decimal("10000"),
            entry_type="payout",
        ),
        CashFlowEntry(
            entry_date=date(2026, 5, 10),
            marketplace="WB",
            amount=Decimal("8000"),
            entry_type="payout",
        ),
    ]

    alerts = engine.detect_alerts([], entries)

    gap_alerts = [a for a in alerts if a.alert_type == "cash_gap"]
    assert len(gap_alerts) == 1
    assert gap_alerts[0].severity == "warning"
    assert gap_alerts[0].value == Decimal("9")


def test_cashflow_no_gap_when_within_threshold() -> None:
    engine = DefaultFinancialEngine()
    entries = [
        CashFlowEntry(
            entry_date=date(2026, 5, 1),
            marketplace="WB",
            amount=Decimal("10000"),
            entry_type="payout",
        ),
        CashFlowEntry(
            entry_date=date(2026, 5, 8),
            marketplace="WB",
            amount=Decimal("8000"),
            entry_type="payout",
        ),
    ]

    alerts = engine.detect_alerts([], entries)

    assert not any(a.alert_type == "cash_gap" for a in alerts)
