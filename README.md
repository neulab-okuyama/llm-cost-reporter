# llm-cost-reporter

Fetch **actual billed** API costs from LLM providers and report them to Slack
and other channels. This is not a token-based estimator — it reads the real
spend from each provider's billing/usage API.

Each run reports, per provider:

- **Yesterday** — the previous UTC day
- **Month-to-date** — from the 1st of the current month through yesterday

…plus a combined total when more than one provider is configured.

## Install

This project uses [uv](https://docs.astral.sh/uv/) for environment and
dependency management.

```bash
uv sync
```

Requires Python 3.12+.

## Configure

Costs endpoints require **Admin** API keys (not your normal request keys).

| Variable | Description |
| --- | --- |
| `OPENAI_ADMIN_KEY` | OpenAI Admin key (`sk-admin-...`). Optional; skipped if unset. |
| `ANTHROPIC_ADMIN_KEY` | Anthropic Admin key (`sk-ant-admin-...`), Team/Enterprise plans. Optional; skipped if unset. |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL. |

Copy `.env.example` to `.env` and fill in the values, or export the variables
in your environment.

## Run

```bash
uv run llm-cost-reporter
# or:
uv run python -m llm_cost_reporter
```

## Schedule

A ready-made GitHub Actions workflow is in
`.github/workflows/daily-report.yml`. Put your keys in the repository's
**Settings → Secrets and variables → Actions**; no `.env` file is needed there.
It runs at 00:00 UTC (09:00 JST) daily and can also be triggered manually.

For cron on your own machine:

```cron
0 9 * * * cd /path/to/repo && uv run llm-cost-reporter
```

## A note on dates and currency

Provider cost APIs bucket by **UTC** day, so "yesterday" means the completed
UTC day. Amounts are reported in **USD**. (OpenAI returns dollars; Anthropic
returns the smallest unit, e.g. cents, which this tool divides by 100.)

## Extending

The core is provider- and notifier-agnostic. Adding either is one small file
plus one import.

### Add a provider

1. Create `llm_cost_reporter/providers/yourprovider.py`:

   ```python
   import os
   from datetime import date, datetime
   from typing import Dict, Optional

   from ..registry import register_provider
   from .base import CostProvider


   @register_provider
   class YourProvider(CostProvider):
       name = "YourProvider"

       def __init__(self, api_key: str):
           self.api_key = api_key

       @classmethod
       def from_env(cls) -> Optional["YourProvider"]:
           key = os.getenv("YOURPROVIDER_ADMIN_KEY")
           return cls(key) if key else None

       def fetch_daily_costs(
           self, start: datetime, end: datetime
       ) -> Dict[date, float]:
           # Return {utc_date: usd_amount} for [start, end).
           ...
   ```

2. Import it in `llm_cost_reporter/providers/__init__.py`.

### Add a notifier

1. Create `llm_cost_reporter/notifiers/yourchannel.py`:

   ```python
   import os
   from typing import Optional

   from ..models import CostReport, format_usd
   from ..registry import register_notifier
   from .base import Notifier


   @register_notifier
   class YourNotifier(Notifier):
       name = "yourchannel"

       def __init__(self, target: str):
           self.target = target

       @classmethod
       def from_env(cls) -> Optional["YourNotifier"]:
           target = os.getenv("YOURCHANNEL_TARGET")
           return cls(target) if target else None

       def send(self, report: CostReport) -> None:
           # Render report.results / report.total_* and deliver.
           ...
   ```

2. Import it in `llm_cost_reporter/notifiers/__init__.py`.

That's it — `from_env` returning `None` means "not configured, skip", so users
only get the providers and channels they've set up.

## License

MIT
