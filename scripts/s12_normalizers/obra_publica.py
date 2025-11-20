"""Normalizers for obras públicas domain (Sprint 12 skeleton)."""
from __future__ import annotations

from typing import Dict


def normalize(record: Dict[str, object]) -> Dict[str, object]:
    """Transform a raw obra pública payload into the canonical event shape."""

    _ = record
    raise NotImplementedError("Wave 2 must implement obra_publica normalization")


__all__ = ["normalize"]
