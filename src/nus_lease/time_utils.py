from __future__ import annotations

from dataclasses import dataclass
from datetime import date


def month_floor(value: date) -> date:
    return date(value.year, value.month, 1)


def shift_month(value: date, delta: int) -> date:
    total = value.year * 12 + value.month - 1 + delta
    year = total // 12
    month = total % 12 + 1
    return date(year, month, 1)


def rolling_month_window(as_of: date, months: int) -> tuple[date, date]:
    if months < 1:
        raise ValueError("months must be >= 1")
    end_month = month_floor(as_of)
    start_month = shift_month(end_month, -(months - 1))
    return start_month, end_month


@dataclass(frozen=True)
class QuarterRef:
    year: int
    quarter: int

    @property
    def api_value(self) -> str:
        return f"{self.year % 100:02d}q{self.quarter}"


def quarter_for_month(value: date) -> QuarterRef:
    quarter = (value.month - 1) // 3 + 1
    return QuarterRef(year=value.year, quarter=quarter)


def quarter_refs_for_window(as_of: date, months: int) -> list[str]:
    start_month, end_month = rolling_month_window(as_of, months)
    refs = []
    cursor = start_month
    seen = set()
    while cursor <= end_month:
        ref = quarter_for_month(cursor).api_value
        if ref not in seen:
            refs.append(ref)
            seen.add(ref)
        cursor = shift_month(cursor, 1)
    return refs
