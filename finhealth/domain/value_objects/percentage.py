from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Percentage:
    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    @classmethod
    def from_ratio(cls, ratio: Decimal) -> Percentage:
        # Ratio is already in 0..1 space, store as-is
        if not isinstance(ratio, Decimal):
            ratio = Decimal(str(ratio))
        return cls(ratio)

    def display(self) -> Decimal:
        # Return percent form rounded to 2dp
        return (self.value * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def __str__(self) -> str:
        return f"{self.display()}%"
