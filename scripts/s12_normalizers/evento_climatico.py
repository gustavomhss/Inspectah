"""Normalizers for eventos climáticos domain (Sprint 12)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict

from scripts.s12_sources_registry import SourceConfig


def _event_id(source_id: str, payload: Dict[str, object]) -> str:
    digest = hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"{source_id}:{digest[:16]}"


def normalize_alert_event(raw_event: Dict[str, object], source: SourceConfig) -> Dict[str, object]:
    """Normalize a climate alert feed entry."""

    payload = raw_event.get("raw_payload", {})
    alert_id = payload.get("alert_id") or payload.get("regiao", "desconhecido").lower()
    event_id = _event_id(source.id_fonte, payload)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    nivel = str(payload.get("nivel", "incerto")).lower()
    resumo = payload.get("previsao") or payload.get("fenomeno") or "Alerta meteorológico"
    case_key = f"evento_climatico:{alert_id}"

    return {
        "id_evento": event_id,
        "source_id": source.id_fonte,
        "dominio": source.dominio,
        "case_key": case_key,
        "tipo_evento": payload.get("fenomeno", "alerta"),
        "event_timestamp": timestamp,
        "captured_at": raw_event.get("fetched_at", timestamp),
        "titulo": f"Alerta {nivel.upper()} - {payload.get('regiao', 'região desconhecida')}",
        "resumo": resumo,
        "payload": payload,
        "eligible": True,
        "metadata": {"nivel": nivel},
    }


__all__ = ["normalize_alert_event"]
