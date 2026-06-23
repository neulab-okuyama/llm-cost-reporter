"""Registries that let providers and notifiers self-register.

A new provider or notifier becomes available simply by decorating its class
with @register_provider / @register_notifier and making sure the module is
imported (see providers/__init__.py and notifiers/__init__.py).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type annotations below; importing these for real at module load
    # time would create an import cycle (providers/notifiers import this
    # module to register themselves).
    from .notifiers.base import Notifier
    from .providers.base import CostProvider

PROVIDERS: dict[str, type[CostProvider]] = {}
NOTIFIERS: dict[str, type[Notifier]] = {}


def register_provider[P: type[CostProvider]](cls: P) -> P:
    PROVIDERS[cls.name] = cls
    return cls


def register_notifier[N: type[Notifier]](cls: N) -> N:
    NOTIFIERS[cls.name] = cls
    return cls
