from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from finhealth.domain.exceptions import DomainException


@dataclass(frozen=True)
class DateRange:
    from_date: date
    to_date: date

    def __post_init__(self) -> None:
        if self.from_date > self.to_date:
            raise DomainException(
                f"Invalid date range: from_date {self.from_date} > to_date {self.to_date}"
            )

    def days(self) -> int:
        return (self.to_date - self.from_date).days + 1

    def contains(self, target: date) -> bool:
        return self.from_date <= target <= self.to_date

    def span(self) -> timedelta:
        return self.to_date - self.from_date
