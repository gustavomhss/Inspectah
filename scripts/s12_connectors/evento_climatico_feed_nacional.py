"""Connector skeleton for national climate events feed (Sprint 12)."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator


def collect_events(config: Dict[str, object]) -> Iterator[Dict[str, object]]:
    """Yield raw events from a climate feed API or CSV export."""

    _ = config
    if False:  # pragma: no cover
        yield {}
    return iter(())


__all__ = ["collect_events"]
