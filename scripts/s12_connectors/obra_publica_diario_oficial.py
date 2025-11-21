"""Connector for Diário Oficial de obras públicas (Sprint 12)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from scripts.s12_sources_registry import SourceConfig

_TEST_PAYLOADS = [
    {
        "edicao": "2025-09-18",
        "municipio": "Niterói",
        "contrato": "2025-123",
        "objeto": "Reforma estrutural da Escola Municipal Vila Verde",
        "valor": 1250000.0,
        "status": "ordem_de_inicio",
    },
    {
        "edicao": "2025-09-19",
        "municipio": "Niterói",
        "contrato": "2025-123",
        "objeto": "Relatório semanal de acompanhamento físico-financeiro",
        "valor": 0.0,
        "status": "relatorio_progresso",
    },
]


def fetch_events(source: SourceConfig, mode: str = "test") -> List[dict]:
    """Yield raw events from the Diário Oficial feed.

    Mode ``test`` relies on static payloads to keep gate G1 deterministic. A
    later Wave can extend this function with a ``live`` branch that reads from
    HTTP/HTML sources.
    """

    if mode not in {"test", "live"}:
        raise ValueError(f"Unsupported mode '{mode}' for {source.id_fonte}")

    if mode == "live":
        raise NotImplementedError("Modo live ainda não foi habilitado para este conector.")

    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    events = []
    for payload in _TEST_PAYLOADS:
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
