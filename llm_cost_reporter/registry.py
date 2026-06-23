"""Registries that let providers and notifiers self-register.

A new provider or notifier becomes available simply by decorating its class
with @register_provider / @register_notifier and making sure the module is
imported (see providers/__init__.py and notifiers/__init__.py).
"""

from __future__ import annotations

from typing import Dict, Type

PROVIDERS: Dict[str, Type] = {}
NOTIFIERS: Dict[str, Type] = {}


def register_provider(cls):
    PROVIDERS[cls.name] = cls
    return cls


def register_notifier(cls):
    NOTIFIERS[cls.name] = cls
    return cls
