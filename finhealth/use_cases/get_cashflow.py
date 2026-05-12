from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.infrastructure.database.dao.cashflow_repository import (
    CashFlowRepository,
)

CASHFLOW_GAP_DAYS: int = 7


@dataclass
class CashFlowDTO:
    total_inflow: Decimal
    total_outflow: Decimal
    net_cash: Decimal
    entries: list[CashFlowEntry] = field(default_factory=list)
    gaps: list[dict[str, Any]] = field(default_factory=list)


class GetCashFlowUseCase:
    def __init__(self, cashflow_repo: CashFlowRepository) -> None:
        self._cashflow_repo = cashflow_repo

    async def execute(
        self, from_date: date, to_date: date
    ) -> CashFlowDTO:
        entries = await self._cashflow_repo.find_by_date_range(
            from_date, to_date
        )

        total_inflow = sum(
            (e.amount for e in entries if e.amount > Decimal("0")),
            Decimal("0"),
        )
        total_outflow = sum(
            (-e.amount for e in entries if e.amount < Decimal("0")),
            Decimal("0"),
        )
        net_cash = total_inflow - total_outflow

        gaps = self._detect_gaps(entries)

        return CashFlowDTO(
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            net_cash=net_cash,
            entries=entries,
            gaps=gaps,
        )

    @staticmethod
    def _detect_gaps(
        entries: list[CashFlowEntry],
    ) -> list[dict[str, Any]]:
        payouts = sorted(
            (e for e in entries if e.entry_type == "payout"),
            key=lambda e: e.entry_date,
        )
        gaps: list[dict[str, Any]] = []
        for prev, curr in zip(payouts, payouts[1:]):
            days = (curr.entry_date - prev.entry_date).days
            if days > CASHFLOW_GAP_DAYS:
                gaps.append(
                    {
                        "gap_start": prev.entry_date,
                        "gap_end": curr.entry_date,
                        "days": days,
                    }
                )
        return gaps
