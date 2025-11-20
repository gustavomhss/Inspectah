"""Sprint 12 source registry skeleton.

This module centralizes the configuration for continuous ingestion sources
introduced in Sprint 12. The Wave 1 implementation will populate the registry
with the pilot sources for obras públicas and eventos climáticos, expose helper
functions to query them by domain/cadence, and support exporting the snapshot
used as evidence for gate S12-G1.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class SourceConfig:
    """Structured description of a source handled by the S12 scheduler."""

    id_fonte: str
    dominio: str
    tipo: str
    url: str
    cadencia: str
    ativo: bool = True
    autenticacao: Optional[Dict[str, str]] = None
    flags: Optional[Dict[str, str]] = None

    def to_payload(self) -> Dict[str, object]:
        """Return a serializable payload for scorecards/evidence exports."""

        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


class SourceRegistry:
    """In-memory registry that Wave 1 will populate with pilot sources."""

    def __init__(self, entries: Optional[Iterable[SourceConfig]] = None) -> None:
        self._sources: Dict[str, SourceConfig] = {}
        if entries:
            for config in entries:
                self.register(config)

    def register(self, config: SourceConfig) -> None:
        """Add or replace a source configuration."""

        self._sources[config.id_fonte] = config

    def get(self, source_id: str) -> SourceConfig:
        """Return a source configuration or raise a KeyError."""

        return self._sources[source_id]

    def list_all(self) -> List[SourceConfig]:
        """Return all sources preserving insertion order."""

        return list(self._sources.values())

    def list_by_domain(self, domain: str) -> List[SourceConfig]:
        """Return sources filtered by domain (obra_publica, evento_climatico, ...)."""

        return [cfg for cfg in self._sources.values() if cfg.dominio == domain]

    def list_by_cadence(self, cadence: str) -> List[SourceConfig]:
        """Return sources filtered by cadence (realtime, hourly, daily, ...)."""

        return [cfg for cfg in self._sources.values() if cfg.cadencia == cadence]

    def export_snapshot(self, output_path: Path) -> None:
        """Export current registry state as JSON for gate evidence."""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [cfg.to_payload() for cfg in self.list_all()]
        output_path.write_text(_json_dumps(payload), encoding="utf-8")


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


DEFAULT_REGISTRY = SourceRegistry()
"""Global registry instance used by scheduler/run_connector during Wave 1."""
