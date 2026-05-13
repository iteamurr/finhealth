from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from finhealth.domain.exceptions import DomainException
from finhealth.domain.value_objects.date_range import DateRange
from finhealth.domain.value_objects.money import Money
from finhealth.domain.value_objects.percentage import Percentage


def test_date_range_invalid() -> None:
    with pytest.raises(DomainException):
        DateRange(from_date=date(2026, 5, 10), to_date=date(2026, 5, 1))


def test_date_range_valid_inclusive_days() -> None:
    rng = DateRange(from_date=date(2026, 5, 1), to_date=date(2026, 5, 7))
    assert rng.days() == 7
    assert rng.contains(date(2026, 5, 3))
    assert not rng.contains(date(2026, 5, 8))


def test_percentage_from_ratio() -> None:
    p = Percentage.from_ratio(Decimal("0.15"))
    assert p.value == Decimal("0.15")


def test_percentage_display_two_decimals() -> None:
    p = Percentage.from_ratio(Decimal("0.12345"))
    assert p.display() == Decimal("12.35")


def test_money_addition() -> None:
    a = Money(Decimal("100"))
    b = Money(Decimal("50"))
    result = a + b
    assert result.amount == Decimal("150")
    assert result.currency == "RUB"


def test_money_subtraction() -> None:
    a = Money(Decimal("100"))
    b = Money(Decimal("30"))
    result = a - b
    assert result.amount == Decimal("70")


def test_money_scalar_multiplication() -> None:
    a = Money(Decimal("100"))
    result = a * Decimal("1.5")
    assert result.amount == Decimal("150.0")


def test_money_currency_mismatch_raises() -> None:
    a = Money(Decimal("100"), currency="RUB")
    b = Money(Decimal("100"), currency="USD")
    with pytest.raises(DomainException):
        _ = a + b
