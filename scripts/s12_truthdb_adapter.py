"""Adapter skeleton between Sprint 12 pipeline and the Truth-DB/Guardião."""
from __future__ import annotations

from typing import Dict, Iterable


def register_event_for_case(event: Dict[str, object]) -> None:
    """Placeholder for the Guardião action that persists an event."""

    _ = event
    raise NotImplementedError("Wave 2 must implement Truth-DB adapter operations")


def apply_debunker_decision(event_id: str, decision: Dict[str, object]) -> None:
    """Placeholder for applying the decision outcome."""

    _ = (event_id, decision)
    raise NotImplementedError("Wave 2 must record Debunker decisions in Truth-DB")


def get_case_snapshot(case_id: str) -> Dict[str, object]:
    """Return a snapshot of the case/timeline required by Explorer v0."""

    _ = case_id
    raise NotImplementedError("Wave 2 must expose case snapshots for downstream services")


__all__ = ["register_event_for_case", "apply_debunker_decision", "get_case_snapshot"]
