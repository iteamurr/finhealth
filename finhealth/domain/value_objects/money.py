from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from finhealth.domain.exceptions import DomainException


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "RUB"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def _check_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise DomainException(
                f"Currency mismatch: {self.currency} vs {other.currency}"
            )

    def __add__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, scalar: Decimal | int) -> Money:
        if isinstance(scalar, Money):
            raise DomainException("Cannot multiply Money by Money")
        factor = scalar if isinstance(scalar, Decimal) else Decimal(str(scalar))
        return Money(self.amount * factor, self.currency)
