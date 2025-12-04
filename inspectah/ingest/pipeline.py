from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

from ..registry.loader import get_source_config
from ..watchers import run_once_for_source
try:  # pragma: no cover
    from app.agents.flows.runtime_adapter import get_executable_flow_plan  # type: ignore
except Exception:  # pragma: no cover
    def get_executable_flow_plan(domain_key: str):
        return {"flow_id": None, "domain_key": domain_key, "used_fallback": True, "steps": []}

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestResult:
    source_id: str
    items_ingested: int


def run_ingest_pipeline(
    source_id: str,
    *,
    use_fixture: bool = False,
    fixture_path: Optional[str] = None,
) -> IngestResult:
    source_cfg = get_source_config(source_id)
    if source_cfg.type != "rss":
        raise ValueError(f"Unsupported source type '{source_cfg.type}' for source {source_id}")
    # Plan is primarily for observabilidade/controle; ignored if not present
    try:
        plan = get_executable_flow_plan(source_cfg.id)
        logger.info("ingest_plan_resolved", extra={"source_id": source_id, "plan": plan})
    except Exception:  # pragma: no cover - do not block ingest if plan resolver fails
        plan = None
    try:
        created = run_once_for_source(
            source_cfg.id,
            use_fixture=use_fixture,
            fixture_path=fixture_path,
        )
        logger.info(
            "ingest_completed",
            extra={
                "source_id": source_id,
                "items_ingested": created,
                "use_fixture": use_fixture,
            },
        )
        return IngestResult(source_id=source_id, items_ingested=created)
    except Exception as exc:  # pragma: no cover - logged and re-raised for visibility
        logger.error(
            "ingest_failed",
            extra={
                "source_id": source_id,
                "use_fixture": use_fixture,
                "fixture_path": fixture_path or "",
                "error": str(exc),
            },
        )
        raise


__all__ = ["run_ingest_pipeline", "IngestResult"]
