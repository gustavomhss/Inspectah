"""Wrapper responsible for executing a Sprint 12 connector by ``id_fonte``."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List

from scripts.s12_sources_registry import DEFAULT_REGISTRY, SourceRegistry

ConnectorFn = Callable[[dict], Iterable[dict]]


class ConnectorNotRegistered(RuntimeError):
    """Raised when a connector id is missing from the registry."""


CONNECTOR_HANDLERS: Dict[str, ConnectorFn] = {}
"""Mapping ``id_fonte`` → callable that collects raw events.

Wave 1 will populate this dictionary with the pilot connectors hosted under
``scripts/s12_connectors``.
"""


def run_connector(source_id: str, registry: SourceRegistry | None = None) -> List[dict]:
    """Run a connector and return the collected raw events.

    The returned events will later be handed to ``s12_ingest_pipeline``.
    """

    registry = registry or DEFAULT_REGISTRY
    config = registry.get(source_id)
    handler = CONNECTOR_HANDLERS.get(source_id)
    if handler is None:
        raise ConnectorNotRegistered(
            f"Connector '{source_id}' not wired yet. Register it in CONNECTOR_HANDLERS during Wave 1."
        )
    events = list(handler(config.to_payload()))
    return events


def deliver_to_pipeline(raw_events: Iterable[dict]) -> None:
    """Placeholder for the bridge into ``s12_ingest_pipeline``."""

    _ = list(raw_events)
    raise NotImplementedError("Wave 1 should stream connector output into s12_ingest_pipeline")


__all__ = ["run_connector", "deliver_to_pipeline", "CONNECTOR_HANDLERS", "ConnectorNotRegistered"]
