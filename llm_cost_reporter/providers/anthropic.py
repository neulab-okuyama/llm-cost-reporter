"""Anthropic cost provider.

Uses the Cost Report endpoint of the Admin API. Requires an Admin key
(``sk-ant-admin-...``), set via ANTHROPIC_ADMIN_KEY. Available on Team and
Enterprise plans.

Note: Anthropic reports ``amount`` in the smallest currency unit (e.g. cents)
as a decimal string, so it is divided by 100 to get USD.
"""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Dict, Optional

import requests

from ..registry import register_provider
from .base import CostProvider

COST_REPORT_URL = "https://api.anthropic.com/v1/organizations/cost_report"
ANTHROPIC_VERSION = "2023-06-01"
HTTP_TIMEOUT = 30


@register_provider
class AnthropicProvider(CostProvider):
    name = "Anthropic"

    def __init__(self, admin_key: str):
        self.admin_key = admin_key

    @classmethod
    def from_env(cls) -> Optional["AnthropicProvider"]:
        key = os.getenv("ANTHROPIC_ADMIN_KEY")
        return cls(key) if key else None

    def fetch_daily_costs(self, start: datetime, end: datetime) -> Dict[date, float]:
        headers = {
            "x-api-key": self.admin_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        params = {
            "starting_at": start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # inclusive
            "ending_at": end.strftime("%Y-%m-%dT%H:%M:%SZ"),      # exclusive
            "bucket_width": "1d",
            "limit": 31,
        }

        daily: Dict[date, float] = {}
        page = None
        while True:
            if page:
                params["page"] = page
            resp = requests.get(
                COST_REPORT_URL, headers=headers, params=params, timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
            body = resp.json()

            for bucket in body.get("data", []):
                day = datetime.fromisoformat(
                    bucket["starting_at"].replace("Z", "+00:00")
                ).date()
                minor_units = 0.0  # smallest currency unit (e.g. cents)
                for result in bucket.get("results", []):
                    minor_units += float(result.get("amount", 0) or 0)
                daily[day] = daily.get(day, 0.0) + (minor_units / 100.0)

            if body.get("has_more") and body.get("next_page"):
                page = body["next_page"]
            else:
                break

        return daily
