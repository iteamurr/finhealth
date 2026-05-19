from __future__ import annotations

from decimal import Decimal

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.domain.entities.order import OrderEntity
from finhealth.domain.entities.profit import AlertEntity, SKUProfitEntity
from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.domain.entities.sku import SKUEntity
from finhealth.domain.services.financial_engine import FinancialEngine

MARGIN_ALERT_THRESHOLD: Decimal = Decimal("0.05")
LOSS_ALERT_THRESHOLD: Decimal = Decimal("0.0")
CASHFLOW_GAP_DAYS: int = 7


class DefaultFinancialEngine(FinancialEngine):
    def compute_sku_profit(
        self,
        orders: list[OrderEntity],
        returns: list[ReturnEntity],
        sku: SKUEntity,
    ) -> SKUProfitEntity:
        sku_orders = [o for o in orders if o.sku_id == sku.sku_id]
        sku_returns = [r for r in returns if r.sku_id == sku.sku_id]

        revenue = sum((o.revenue for o in sku_orders), Decimal("0"))
        commissions = sum((o.commission for o in sku_orders), Decimal("0"))
        logistics = sum((o.logistics for o in sku_orders), Decimal("0"))
        ad_spend = sum((o.ad_spend for o in sku_orders), Decimal("0"))
        returns_amount = sum((r.amount for r in sku_returns), Decimal("0"))

        profit = revenue - commissions - logistics - returns_amount - ad_spend
        margin = (
            profit / revenue if revenue > Decimal("0") else Decimal("0")
        )
        roi = (
            profit / sku.cost_of_goods
            if sku.cost_of_goods > Decimal("0")
            else Decimal("0")
        )

        return SKUProfitEntity(
            sku_id=sku.sku_id,
            name=sku.name,
            marketplace=sku.marketplace,
            revenue=revenue,
            commissions=commissions,
            logistics=logistics,
            returns=returns_amount,
            ad_spend=ad_spend,
            cost_of_goods=sku.cost_of_goods,
            profit=profit,
            margin=margin,
            roi=roi,
        )

    def compute_pnl(
        self,
        orders: list[OrderEntity],
        returns: list[ReturnEntity],
        skus: list[SKUEntity],
    ) -> dict:
        total_revenue = sum((o.revenue for o in orders), Decimal("0"))
        total_commissions = sum((o.commission for o in orders), Decimal("0"))
        total_logistics = sum((o.logistics for o in orders), Decimal("0"))
        total_ad_spend = sum((o.ad_spend for o in orders), Decimal("0"))
        total_returns = sum((r.amount for r in returns), Decimal("0"))

        # себестоимость: cost_of_goods на заказ по таблице SKU
        sku_cost_map = {s.sku_id: s.cost_of_goods for s in skus}
        total_cogs = sum(
            (sku_cost_map.get(o.sku_id, Decimal("0")) for o in orders),
            Decimal("0"),
        )

        gross_profit = (
            total_revenue - total_commissions - total_logistics - total_returns
        )
        net_profit = gross_profit - total_ad_spend - total_cogs

        return {
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "total_revenue": total_revenue,
            "total_commissions": total_commissions,
            "total_logistics": total_logistics,
            "total_returns": total_returns,
            "total_ad_spend": total_ad_spend,
            "total_cogs": total_cogs,
        }

    def detect_alerts(
        self,
        sku_profits: list[SKUProfitEntity],
        cashflow_entries: list[CashFlowEntry],
    ) -> list[AlertEntity]:
        alerts: list[AlertEntity] = []

        for sp in sku_profits:
            if sp.profit < LOSS_ALERT_THRESHOLD:
                alerts.append(
                    AlertEntity(
                        alert_type="loss",
                        severity="critical",
                        message=(
                            f"SKU {sp.sku_id} ({sp.name}) is loss-making: "
                            f"profit={sp.profit}"
                        ),
                        sku_id=sp.sku_id,
                        value=sp.profit,
                    )
                )
                continue

            if (
                sp.revenue > Decimal("0")
                and sp.margin < MARGIN_ALERT_THRESHOLD
            ):
                alerts.append(
                    AlertEntity(
                        alert_type="low_margin",
                        severity="warning",
                        message=(
                            f"SKU {sp.sku_id} ({sp.name}) margin below "
                            f"threshold: margin={sp.margin}"
                        ),
                        sku_id=sp.sku_id,
                        value=sp.margin,
                    )
                )

        payouts = sorted(
            (e for e in cashflow_entries if e.entry_type == "payout"),
            key=lambda e: e.entry_date,
        )
        for prev, curr in zip(payouts, payouts[1:]):
            gap = (curr.entry_date - prev.entry_date).days
            if gap > CASHFLOW_GAP_DAYS:
                alerts.append(
                    AlertEntity(
                        alert_type="cash_gap",
                        severity="warning",
                        message=(
                            f"Cash gap of {gap} days between "
                            f"{prev.entry_date} and {curr.entry_date}"
                        ),
                        sku_id=None,
                        value=Decimal(gap),
                    )
                )

        return alerts
