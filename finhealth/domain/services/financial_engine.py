from __future__ import annotations

from abc import ABC, abstractmethod

from finhealth.domain.entities.cashflow import CashFlowEntry
from finhealth.domain.entities.order import OrderEntity
from finhealth.domain.entities.profit import AlertEntity, SKUProfitEntity
from finhealth.domain.entities.return_ import ReturnEntity
from finhealth.domain.entities.sku import SKUEntity


class FinancialEngine(ABC):
    @abstractmethod
    def compute_sku_profit(
        self,
        orders: list[OrderEntity],
        returns: list[ReturnEntity],
        sku: SKUEntity,
    ) -> SKUProfitEntity: ...

    @abstractmethod
    def compute_pnl(
        self,
        orders: list[OrderEntity],
        returns: list[ReturnEntity],
        skus: list[SKUEntity],
    ) -> dict: ...

    @abstractmethod
    def detect_alerts(
        self,
        sku_profits: list[SKUProfitEntity],
        cashflow_entries: list[CashFlowEntry],
    ) -> list[AlertEntity]: ...
