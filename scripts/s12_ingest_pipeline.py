"""Sprint 12 ingestion pipeline skeleton."""
from __future__ import annotations

from typing import Iterable, List


def process_raw_events(raw_events: Iterable[dict]) -> List[dict]:
    """Process connector output and return normalized events.

    Wave 2 wires normalization, case resolution and Debunker integration. Until
    then this function just guards the contract by raising a descriptive error.
    """

    _ = list(raw_events)
    raise NotImplementedError("Wave 2 must implement the S12 ingestion pipeline")


__all__ = ["process_raw_events"]
