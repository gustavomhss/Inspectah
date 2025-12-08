from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from app.ingestion.models import IngestionRun, IngestionStatus
from app.ingestion.repository import IngestionRepository
from metrics import ingestion_s22 as metrics  # legado
from metrics import ingest as ingest_metrics

LOG_PATH_DEFAULT = Path("out/evidence/S22_G6_observability/ingestion_runs.log")


def _append_log(entry: dict, log_path: Path = LOG_PATH_DEFAULT) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.open("a", encoding="utf-8").write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_run_start(run: IngestionRun, log_path: Path = LOG_PATH_DEFAULT) -> None:
    _append_log(
        {
            "event": "start",
            "run_id": run.id,
            "source_id": run.source_id,
            "status": run.status.value,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "trigger": run.trigger.value,
        },
        log_path=log_path,
    )
    metrics.record_run(run.source_id, run.status.value, run.trigger.value)
    ingest_metrics.record_request(status=run.status.value, source=run.source_id)


def log_run_end(run: IngestionRun, log_path: Path = LOG_PATH_DEFAULT) -> None:
    latency_ms = _compute_latency_ms(run)
    _append_log(
        {
            "event": "end",
            "run_id": run.id,
            "source_id": run.source_id,
            "status": run.status.value,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "items_processed": run.items_processed,
            "error_code": run.error_code,
            "error_message": run.error_message,
            "payload_ref": run.payload_ref,
            "latency_ms": latency_ms,
        },
        log_path=log_path,
    )
    metrics.record_run(run.source_id, run.status.value, run.trigger.value)
    if latency_ms is not None:
        metrics.record_latency(run.source_id, latency_ms)
        ingest_metrics.record_request(status=run.status.value, source=run.source_id, duration_seconds=latency_ms / 1000.0)
    if run.items_processed:
        ingest_metrics.record_items(run.source_id, run.items_processed)
    if run.status == IngestionStatus.SUCCESS:
        metrics.mark_success(run.source_id, datetime.utcnow().timestamp())
    if run.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS}:
        metrics.mark_failure(run.source_id, datetime.utcnow().timestamp())
        ingest_metrics.record_error(error_type=run.error_code or "error", source=run.source_id)


def sources_without_recent_runs(repo: IngestionRepository, threshold_minutes: int = 1440) -> List[str]:
    stale: List[str] = []
    now = datetime.utcnow()
    for cfg in repo.list_configs():
        runs = repo.list_runs_by_source(cfg.source_id, limit=1)
        if not runs:
            stale.append(cfg.source_id)
            continue
        last = runs[0]
        delta = now - (last.finished_at or last.started_at)
        if delta.total_seconds() > threshold_minutes * 60:
            stale.append(cfg.source_id)
    return stale


def _compute_latency_ms(run: IngestionRun):
    if not run.started_at or not run.finished_at:
        return None
    delta = run.finished_at - run.started_at
    return int(delta.total_seconds() * 1000)
