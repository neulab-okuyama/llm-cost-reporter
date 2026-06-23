"""OpenAI cost provider.

Uses the Costs endpoint of the Organization API, which reconciles with the
invoice. Requires an Admin key (``sk-admin-...``), set via OPENAI_ADMIN_KEY.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Dict, Optional

import requests

from ..registry import register_provider
from .base import CostProvider

COSTS_URL = "https://api.openai.com/v1/organization/costs"
HTTP_TIMEOUT = 30


@register_provider
class OpenAIProvider(CostProvider):
    name = "OpenAI"

    def __init__(self, admin_key: str):
        self.admin_key = admin_key

    @classmethod
    def from_env(cls) -> Optional["OpenAIProvider"]:
        key = os.getenv("OPENAI_ADMIN_KEY")
        return cls(key) if key else None

    def fetch_daily_costs(self, start: datetime, end: datetime) -> Dict[date, float]:
        headers = {"Authorization": f"Bearer {self.admin_key}"}
        params = {
            "start_time": int(start.timestamp()),  # inclusive
            "end_time": int(end.timestamp()),      # exclusive
            "bucket_width": "1d",
            "limit": 31,
        }

        daily: Dict[date, float] = {}
        page = None
        while True:
            if page:
                params["page"] = page
            resp = requests.get(
                COSTS_URL, headers=headers, params=params, timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
            body = resp.json()

            for bucket in body.get("data", []):
                day = datetime.fromtimestamp(
                    bucket["start_time"], tz=timezone.utc
                ).date()
                usd = 0.0
                for result in bucket.get("results", []):
                    amount = result.get("amount") or {}
                    # OpenAI reports amount.value directly in the currency unit.
                    usd += float(amount.get("value", 0) or 0)
                daily[day] = daily.get(day, 0.0) + usd

            if body.get("has_more") and body.get("next_page"):
                page = body["next_page"]
            else:
                break

        return daily
