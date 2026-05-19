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
        # ratio уже в диапазоне 0..1, сохраняем как есть
        if not isinstance(ratio, Decimal):
            ratio = Decimal(str(ratio))
        return cls(ratio)

    def display(self) -> Decimal:
        # возвращает значение в процентах, округленное до 2 знаков
        return (self.value * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def __str__(self) -> str:
        return f"{self.display()}%"
