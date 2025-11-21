"""Normalizers for obras públicas domain (Sprint 12)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Dict

from scripts.s12_sources_registry import SourceConfig


def _event_id(source_id: str, payload: Dict[str, object]) -> str:
    digest = hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"{source_id}:{digest[:16]}"


def normalize_diario_oficial_event(raw_event: Dict[str, object], source: SourceConfig) -> Dict[str, object]:
    """Normalize Diário Oficial payloads for obras públicas."""

    payload = raw_event.get("raw_payload", {})
    contrato = str(payload.get("contrato", "desconhecido"))
    status = payload.get("status", "atualizacao")
    edicao = payload.get("edicao") or datetime.utcnow().strftime("%Y-%m-%d")
    case_key = f"obra_publica:{contrato}"
    resumo = payload.get("objeto") or "Atualização de contrato"
    event_id = _event_id(source.id_fonte, payload)

    return {
        "id_evento": event_id,
        "source_id": source.id_fonte,
        "dominio": source.dominio,
        "case_key": case_key,
        "tipo_evento": status,
        "event_timestamp": f"{edicao}T00:00:00Z",
        "captured_at": raw_event.get("fetched_at"),
        "titulo": f"Contrato {contrato} — {status}",
        "resumo": resumo,
        "payload": payload,
        "eligible": True,
        "metadata": {"municipio": payload.get("municipio")},
    }


def normalize_portal_transparencia_event(raw_event: Dict[str, object], source: SourceConfig) -> Dict[str, object]:
    """Normalize portal da transparência payloads for obras públicas."""

    payload = raw_event.get("raw_payload", {})
    contrato = str(payload.get("contrato", "desconhecido"))
    evento = payload.get("evento", "movimentacao")
    case_key = f"obra_publica:{contrato}"
    resumo = payload.get("observacao") or "Atualização financeira"
    event_id = _event_id(source.id_fonte, payload)

    return {
        "id_evento": event_id,
        "source_id": source.id_fonte,
        "dominio": source.dominio,
        "case_key": case_key,
        "tipo_evento": evento,
        "event_timestamp": raw_event.get("fetched_at"),
        "captured_at": raw_event.get("fetched_at"),
        "titulo": f"Contrato {contrato} — {evento}",
        "resumo": resumo,
        "payload": payload,
        "eligible": True,
        "metadata": {"valor": payload.get("valor")},
    }


def normalize_raw_event(raw_event: Dict[str, object], source: SourceConfig) -> Dict[str, object]:
    """Route to the proper obra pública normalizer based on source metadata."""

    if source.connector == "obra_publica_diario_oficial":
        return normalize_diario_oficial_event(raw_event, source)
    if source.connector == "obra_publica_portal_transparencia":
        return normalize_portal_transparencia_event(raw_event, source)
    raise ValueError(f"Conector de obras públicas desconhecido: {source.connector}")


__all__ = [
    "normalize_diario_oficial_event",
    "normalize_portal_transparencia_event",
    "normalize_raw_event",
]
