"""Core data structures shared between providers and notifiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ProviderResult:
    """Aggregated cost for a single provider."""

    name: str
    yesterday_cost: float  # USD, the previous UTC day
    mtd_cost: float        # USD, month-to-date (1st of month .. yesterday)


@dataclass
class CostReport:
    """A complete report for one run, independent of any notifier format."""

    today: datetime        # UTC, 00:00 of the run day
    yesterday: datetime    # UTC, 00:00 of the previous day
    month_start: datetime  # UTC, 00:00 of the 1st of the current month
    results: List[ProviderResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def total_yesterday(self) -> float:
        return sum(r.yesterday_cost for r in self.results)

    @property
    def total_mtd(self) -> float:
        return sum(r.mtd_cost for r in self.results)


def format_usd(amount: float) -> str:
    return f"${amount:,.2f}"
