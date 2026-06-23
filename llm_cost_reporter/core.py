"""Orchestration: compute the date range, fetch from every configured
provider, build a CostReport, and dispatch it to every configured notifier.

This module knows nothing about specific providers or notifiers; it only talks
to the registries and the abstract base classes.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from .models import CostReport, ProviderResult
from .providers.base import CostProvider
from .registry import NOTIFIERS, PROVIDERS


def _utc_day_bounds(now: datetime) -> tuple[datetime, datetime, datetime]:
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    return today, yesterday, month_start


def _summarize(
    daily: dict[date, float], yesterday_date: date, month_start_date: date
) -> tuple[float, float]:
    yesterday_cost = daily.get(yesterday_date, 0.0)
    mtd_cost = sum(usd for day, usd in daily.items() if day >= month_start_date)
    return yesterday_cost, mtd_cost


def build_report(
    providers: list[CostProvider], now: datetime | None = None
) -> CostReport:
    """Fetch costs from each provider and assemble a CostReport.

    A failure in one provider is captured in ``report.errors`` and does not
    stop the others.
    """
    if now is None:
        now = datetime.now(UTC)

    today, yesterday, month_start = _utc_day_bounds(now)
    # Fetch from the earlier of (month start, yesterday) so the previous day is
    # always covered, even when the job runs on the 1st of the month.
    fetch_start = min(month_start, yesterday)
    fetch_end = today  # exclusive

    report = CostReport(today=today, yesterday=yesterday, month_start=month_start)

    for provider in providers:
        try:
            daily = provider.fetch_daily_costs(fetch_start, fetch_end)
            y_cost, mtd_cost = _summarize(daily, yesterday.date(), month_start.date())
            report.results.append(ProviderResult(provider.name, y_cost, mtd_cost))
        except Exception as e:  # noqa: BLE001
            report.errors.append(f"{provider.name}: {e}")

    return report


def run() -> CostReport:
    """Entry point used by __main__: build providers/notifiers from env and run."""
    providers = [p for cls in PROVIDERS.values() if (p := cls.from_env()) is not None]
    notifiers = [n for cls in NOTIFIERS.values() if (n := cls.from_env()) is not None]

    if not providers:
        raise SystemExit(
            "No provider configured. Set at least one provider API key "
            "(e.g. OPENAI_ADMIN_KEY or ANTHROPIC_ADMIN_KEY)."
        )
    if not notifiers:
        raise SystemExit(
            "No notifier configured. Set at least one notifier "
            "(e.g. SLACK_WEBHOOK_URL)."
        )

    report = build_report(providers)
    for notifier in notifiers:
        notifier.send(report)
    return report
