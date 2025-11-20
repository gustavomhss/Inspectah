"""Sprint 12 source registry implementation for Wave 1."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class SourceConfig:
    """Structured description of a source handled by the S12 scheduler."""

    id_fonte: str
    dominio: str
    tipo: str
    url: str
    cadencia_minutos: int
    connector: str
    ativo: bool = True
    autenticacao: Optional[Dict[str, str]] = None
    flags: Dict[str, str] = field(default_factory=dict)
    descricao: Optional[str] = None

    def to_payload(self) -> Dict[str, object]:
        """Return a serializable payload for scorecards/evidence exports."""

        payload = asdict(self)
        payload["flags"] = payload.get("flags", {}) or {}
        return {key: value for key, value in payload.items() if value is not None}


class SourceRegistry:
    """In-memory registry populated with the S12 pilot sources."""

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

    def list_due(self, now: Optional[datetime] = None) -> List[SourceConfig]:
        """Return sources that must run in the current window (simplified for G1)."""

        _ = now  # Placeholder for Wave 2 cadence tracking.
        return [cfg for cfg in self._sources.values() if cfg.ativo]

    def export_snapshot(self, output_path: Path) -> None:
        """Export current registry state as JSON for gate evidence."""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [cfg.to_payload() for cfg in self.list_all()]
        output_path.write_text(_json_dumps(payload), encoding="utf-8")


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


PILOT_SOURCES: List[SourceConfig] = [
    SourceConfig(
        id_fonte="s12_obras_diario_niteroi",
        dominio="obra_publica",
        tipo="diario_oficial",
        url="https://dados.niteroi.gov.br/diario-oficial/obras",
        cadencia_minutos=1440,
        connector="obra_publica_diario_oficial",
        flags={"municipio": "Niterói", "prioridade": "alta"},
        descricao="Diário oficial municipal monitorando contratos de obras críticas.",
    ),
    SourceConfig(
        id_fonte="s12_obras_transparencia_rj",
        dominio="obra_publica",
        tipo="portal_transparencia",
        url="https://transparencia.rj.gov.br/obras/contratos",
        cadencia_minutos=720,
        connector="obra_publica_portal_transparencia",
        flags={"uf": "RJ", "cadencia": "12h"},
        descricao="Portal estadual com atualizações de empenhos e pagamentos.",
    ),
    SourceConfig(
        id_fonte="s12_eventos_climaticos_inmet",
        dominio="evento_climatico",
        tipo="feed_nacional",
        url="https://clima.inmet.gov.br/eventos-criticos",
        cadencia_minutos=180,
        connector="evento_climatico_feed_nacional",
        flags={"abrangencia": "nacional"},
        descricao="Boletins do INMET com alertas meteorológicos relevantes.",
    ),
]

DEFAULT_REGISTRY = SourceRegistry(entries=PILOT_SOURCES)
"""Global registry instance used by scheduler/run_connector during Wave 1."""


def list_all_sources(registry: Optional[SourceRegistry] = None) -> List[SourceConfig]:
    """Return all configured sources."""

    return (registry or DEFAULT_REGISTRY).list_all()


def list_sources_by_domain(domain: str, registry: Optional[SourceRegistry] = None) -> List[SourceConfig]:
    """Return sources filtered by domain."""

    return (registry or DEFAULT_REGISTRY).list_by_domain(domain)


def list_sources_due(now: Optional[datetime] = None, registry: Optional[SourceRegistry] = None) -> List[SourceConfig]:
    """Return sources that must run during the provided window."""

    return (registry or DEFAULT_REGISTRY).list_due(now)


def export_sources_snapshot(path: Path | str, registry: Optional[SourceRegistry] = None) -> None:
    """Persist a JSON snapshot for gate evidence."""

    output_path = Path(path)
    (registry or DEFAULT_REGISTRY).export_snapshot(output_path)
