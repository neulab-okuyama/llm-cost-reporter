"""Slack notifier using an incoming webhook (SLACK_WEBHOOK_URL)."""

from __future__ import annotations

import os
from typing import Optional

import requests

from ..models import CostReport, format_usd
from ..registry import register_notifier
from .base import Notifier

HTTP_TIMEOUT = 30


@register_notifier
class SlackNotifier(Notifier):
    name = "slack"

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @classmethod
    def from_env(cls) -> Optional["SlackNotifier"]:
        url = os.getenv("SLACK_WEBHOOK_URL")
        return cls(url) if url else None

    def _render(self, report: CostReport) -> str:
        y_label = report.yesterday.strftime("%m/%d")
        mtd_label = (
            f"{report.month_start.strftime('%m/%d')}"
            f"-{report.yesterday.strftime('%m/%d')}"
        )

        lines = [
            f"*:bar_chart: API cost report*  "
            f"(as of {report.today.strftime('%Y-%m-%d')}, UTC)",
            "",
        ]
        for r in report.results:
            lines.append(f"*{r.name}*")
            lines.append(f"- Yesterday ({y_label}): {format_usd(r.yesterday_cost)}")
            lines.append(f"- MTD ({mtd_label}): {format_usd(r.mtd_cost)}")
            lines.append("")

        if len(report.results) > 1:
            lines.append("*Total*")
            lines.append(f"- Yesterday: {format_usd(report.total_yesterday)}")
            lines.append(f"- MTD: {format_usd(report.total_mtd)}")

        if report.errors:
            lines.append("")
            lines.append(":warning: Some providers failed:")
            for e in report.errors:
                lines.append(f"- {e}")

        return "\n".join(lines)

    def send(self, report: CostReport) -> None:
        text = self._render(report)
        payload = {
            "text": text,
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": text}}
            ],
        }
        resp = requests.post(self.webhook_url, json=payload, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
