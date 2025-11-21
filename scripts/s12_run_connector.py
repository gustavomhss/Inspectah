"""Wrapper responsible for executing Sprint 12 connectors."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

from scripts.s12_connectors import (
    evento_climatico_feed_nacional,
    obra_publica_diario_oficial,
    obra_publica_portal_transparencia,
)
from scripts.s12_sources_registry import DEFAULT_REGISTRY, SourceConfig, SourceRegistry

ConnectorFn = Callable[[SourceConfig, str], List[dict]]

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT_DIR / "out" / "evidence" / "S12_G1" / "raw_events"


class ConnectorNotRegistered(RuntimeError):
    """Raised when there is no handler for the given source."""


@dataclass
class ConnectorRunResult:
    """Captures the result of running a connector."""

    source_id: str
    events: List[dict]
    output_path: Path


CONNECTOR_HANDLERS: Dict[str, ConnectorFn] = {
    "obra_publica_diario_oficial": obra_publica_diario_oficial.fetch_events,
    "obra_publica_portal_transparencia": obra_publica_portal_transparencia.fetch_events,
    "evento_climatico_feed_nacional": evento_climatico_feed_nacional.fetch_events,
}


def run_for_source(
    source: SourceConfig,
    mode: str = "test",
    evidence_dir: Optional[Path] = None,
) -> ConnectorRunResult:
    """Run the connector associated with ``source`` and persist raw events."""

    handler = CONNECTOR_HANDLERS.get(source.connector)
    if handler is None:
        raise ConnectorNotRegistered(f"Connector '{source.connector}' not registered for S12.")

    events = handler(source, mode=mode)
    output_path = deliver_to_pipeline(events, source_id=source.id_fonte, evidence_dir=evidence_dir)
    return ConnectorRunResult(source.id_fonte, events, output_path)


def deliver_to_pipeline(
    raw_events: List[dict],
    *,
    source_id: str,
    evidence_dir: Optional[Path] = None,
) -> Path:
    """Persist raw events so the ingestion pipeline can consume them."""

    if evidence_dir is None:
        evidence_dir = DEFAULT_RAW_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts_label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = evidence_dir / f"raw_events_{source_id}_{ts_label}.json"
    output_path.write_text(json.dumps(raw_events, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def run_connector(source_id: str, registry: SourceRegistry | None = None, mode: str = "test") -> ConnectorRunResult:
    """Utility used by tests to run a connector by id."""

    registry = registry or DEFAULT_REGISTRY
    source = registry.get(source_id)
    return run_for_source(source, mode=mode)


__all__ = [
    "ConnectorRunResult",
    "ConnectorNotRegistered",
    "run_for_source",
    "run_connector",
    "deliver_to_pipeline",
]
