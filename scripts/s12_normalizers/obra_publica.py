"""Normalizers for obras públicas domain (Sprint 12)."""
from __future__ import annotations

from typing import Dict


def normalize(record: Dict[str, object]) -> Dict[str, object]:
    """Transform a raw obra pública payload into a minimal canonical shape.

    The full normalization with schema validation arrives in Wave 2. For Wave 1
    we keep the structure predictable so that tests can exercise the entrypoint
    without failing.
    """

    payload = record.get("raw_payload", {}) if isinstance(record, dict) else {}
    return {
        "source_id": record.get("source_id"),
        "domain": record.get("domain"),
        "fetched_at": record.get("fetched_at"),
        "contrato": payload.get("contrato"),
        "descricao": payload.get("objeto") or payload.get("evento"),
        "valor": payload.get("valor"),
        "status": payload.get("status") or payload.get("observacao"),
        "raw_payload": payload,
    }


def normalize_raw_event(record: Dict[str, object]) -> Dict[str, object]:
    """Alias kept for Wave 2 compatibility when the pipeline hooks up."""

    return normalize(record)


__all__ = ["normalize", "normalize_raw_event"]
