"""Connector for national climate events feed (Sprint 12)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from scripts.s12_sources_registry import SourceConfig

_TEST_ALERTS = [
    {
        "alert_id": "inmet-2025-0901",
        "regiao": "Costa Verde / RJ",
        "nivel": "laranja",
        "fenomeno": "Chuvas intensas",
        "previsao": "Acumulado acima de 60mm em 24h; monitorar encostas.",
    },
    {
        "alert_id": "inmet-2025-0902",
        "regiao": "Serra do Mar",
        "nivel": "amarelo",
        "fenomeno": "Ventos costeiros",
        "previsao": "Ráfagas até 70km/h; risco a estruturas provisórias de obras.",
    },
]


def fetch_events(source: SourceConfig, mode: str = "test") -> List[dict]:
    """Return deterministic climate alerts for S12 fixtures."""

    if mode not in {"test", "live"}:
        raise ValueError(f"Unsupported mode '{mode}' for {source.id_fonte}")

    if mode == "live":
        raise NotImplementedError("Modo live ainda não foi habilitado para este conector.")

    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    events = []
    for payload in _TEST_ALERTS:
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
