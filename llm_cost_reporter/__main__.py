"""Entry point: ``python -m llm_cost_reporter`` (or the console script).

Loads a local .env if present, then runs.
"""

from __future__ import annotations

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    from .core import run

    report = run()
    print(f"Reported costs as of {report.today.strftime('%Y-%m-%d')} (UTC).")


if __name__ == "__main__":
    main()
