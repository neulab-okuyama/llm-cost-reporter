"""Importing this package registers all built-in providers.

When you add a new provider module, import it here so its
``@register_provider`` decorator runs.
"""

from . import anthropic, openai  # noqa: F401
from .base import CostProvider  # noqa: F401
