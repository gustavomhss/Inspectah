"""Connector skeleton for Diário Oficial de obras públicas (Sprint 12)."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator


def collect_events(config: Dict[str, object]) -> Iterator[Dict[str, object]]:
    """Yield raw events from the Diário Oficial feed.

    Wave 1 will replace this placeholder with HTML/JSON fetching logic that
    honors the cadence defined in ``s12_sources_registry``. The skeleton keeps
    the contract explicit for downstream consumers.
    """

    _ = config
    if False:  # pragma: no cover - placeholder for future implementation
        yield {}
    return iter(())


__all__ = ["collect_events"]
