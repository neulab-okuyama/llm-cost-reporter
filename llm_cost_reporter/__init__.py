"""llm-cost-reporter: fetch actual billed LLM API costs and report them.

Importing the package eagerly imports the built-in providers and notifiers so
they register themselves with the registries.
"""

from . import notifiers, providers  # noqa: F401  (triggers registration)
from .core import build_report, run
from .models import CostReport, ProviderResult

__all__ = ["run", "build_report", "CostReport", "ProviderResult"]
__version__ = "0.1.0"
