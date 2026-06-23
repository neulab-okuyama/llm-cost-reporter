"""Importing this package registers all built-in notifiers.

When you add a new notifier module, import it here so its
``@register_notifier`` decorator runs.
"""

from . import slack  # noqa: F401
from .base import Notifier  # noqa: F401
