"""Normalizers for eventos climáticos domain (Sprint 12 skeleton)."""
from __future__ import annotations

from typing import Dict


def normalize(record: Dict[str, object]) -> Dict[str, object]:
    """Transform a raw climate payload into the canonical event shape."""

    _ = record
    raise NotImplementedError("Wave 2 must implement evento_climatico normalization")


__all__ = ["normalize"]
