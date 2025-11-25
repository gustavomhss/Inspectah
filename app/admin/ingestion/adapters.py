from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from app.ingestion.models import IngestionConfig, IngestionRun, IngestionStatus


def _format_status(status: IngestionStatus) -> str:
    mapping = {
        IngestionStatus.PENDING: "Pendente",
        IngestionStatus.RUNNING: "Em execução",
        IngestionStatus.SUCCESS: "Sucesso",
        IngestionStatus.PARTIAL_SUCCESS: "Parcial",
        IngestionStatus.FAIL: "Falha",
    }
    return mapping.get(status, status.value)


def config_to_view(config: IngestionConfig, last_run: Optional[IngestionRun] = None, source_name: Optional[str] = None, source_type: Optional[str] = None) -> Dict:
    return {
        "source_id": config.source_id,
        "source_name": source_name or config.source_id,
        "source_type": source_type or "",
        "mode": config.mode.value,
        "enabled": config.enabled,
        "interval_minutes": config.interval_minutes,
        "last_run_id": config.last_run_id,
        "last_run_status": _format_status(last_run.status) if last_run else None,
        "last_run_started_at": _iso(last_run.started_at) if last_run else None,
        "last_run_finished_at": _iso(last_run.finished_at) if last_run and last_run.finished_at else None,
        "last_run_items": last_run.items_processed if last_run else None,
    }


def run_to_view(run: IngestionRun) -> Dict:
    return {
        "id": run.id,
        "status": _format_status(run.status),
        "trigger": run.trigger.value,
        "started_at": _iso(run.started_at),
        "finished_at": _iso(run.finished_at),
        "items_processed": run.items_processed,
        "error_code": run.error_code,
        "error_message": run.error_message,
    }


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None
