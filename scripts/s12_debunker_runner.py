"""Debunker v0 runner skeleton for Sprint 12."""
from __future__ import annotations

from typing import Dict, Iterable, List


class DebunkerDecision(Dict[str, object]):
    """Simple structure to carry decision, rationale and metadata."""


def evaluate_events(events: Iterable[dict]) -> List[DebunkerDecision]:
    """Evaluate normalized events via Debunker v0.

    Wave 2 will implement the integration with the existing Debunker artifacts
    from previous sprints. The skeleton returns an empty list to keep tests
    deterministic while making it clear that the functionality is pending.
    """

    _ = list(events)
    raise NotImplementedError("Wire Debunker v0 in Wave 2 before triggering gates")


__all__ = ["DebunkerDecision", "evaluate_events"]
