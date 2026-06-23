"""Base class every notifier must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..models import CostReport


class Notifier(ABC):
    """Renders a CostReport and delivers it to a destination.

    To add a new notifier (email, Discord, Teams, ...), create a module under
    ``notifiers/``, subclass this, set a unique ``name``, implement ``from_env``
    and ``send``, and decorate the class with ``@register_notifier``.
    """

    #: Unique notifier name (registry key).
    name: str = "unknown"

    @classmethod
    @abstractmethod
    def from_env(cls) -> Optional["Notifier"]:
        """Build an instance from environment variables, or ``None`` if unset."""

    @abstractmethod
    def send(self, report: CostReport) -> None:
        """Render ``report`` in this channel's format and deliver it."""
