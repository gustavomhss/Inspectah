"""Connector for portal da transparência (Sprint 12)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from scripts.s12_sources_registry import SourceConfig

_TEST_ENTRIES = [
    {
        "contrato": "2024-778",
        "municipio": "Rio de Janeiro",
        "evento": "Empenho complementar autorizado",
        "valor": 350000.0,
        "observacao": "Complemento para infraestrutura de drenagem.",
    },
    {
        "contrato": "2024-778",
        "municipio": "Rio de Janeiro",
        "evento": "Pagamento parcial efetuado",
        "valor": 175000.0,
        "observacao": "Parcela liberada após vistoria da etapa 2.",
    },
]


def fetch_events(source: SourceConfig, mode: str = "test") -> List[dict]:
    """Return transparency portal updates with deterministic payloads."""

    if mode not in {"test", "live"}:
        raise ValueError(f"Unsupported mode '{mode}' for {source.id_fonte}")

    if mode == "live":
        raise NotImplementedError("Modo live ainda não foi habilitado para este conector.")

    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    events = []
    for payload in _TEST_ENTRIES:
        events.append(
            {
                "source_id": source.id_fonte,
                "domain": source.dominio,
                "fetched_at": fetched_at,
                "raw_payload": payload,
            }
        )
    return events


__all__ = ["fetch_events"]
