"""Base class every cost provider must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime


class CostProvider(ABC):
    """Fetches actual billed daily costs from a provider's billing API.

    To add a new provider, create a module under ``providers/``, subclass this,
    set a unique ``name``, implement ``from_env`` and ``fetch_daily_costs``,
    and decorate the class with ``@register_provider``.
    """

    #: Human-readable, unique provider name (used as the registry key and in
    #: the rendered report, e.g. "OpenAI", "Anthropic").
    name: str = "unknown"

    @classmethod
    @abstractmethod
    def from_env(cls) -> CostProvider | None:
        """Build an instance from environment variables.

        Return ``None`` when the provider is not configured (e.g. its API key
        is absent), so it is silently skipped.
        """

    @abstractmethod
    def fetch_daily_costs(self, start: datetime, end: datetime) -> dict[date, float]:
        """Return ``{utc_date: usd_amount}`` for every day in ``[start, end)``.

        ``start`` is inclusive, ``end`` is exclusive. Both are UTC datetimes
        aligned to 00:00. Amounts are floats in USD.
        """
