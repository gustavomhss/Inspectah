from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import Histogram

from app.ingestion.models import IngestionRun, IngestionStatus
from app.ingestion.repository import IngestionRepository
from metrics import ingestion_s22 as metrics  # legado
from metrics import ingest as ingest_metrics

logger = logging.getLogger(__name__)

LOG_PATH_DEFAULT = Path("out/evidence/S22_G6_observability/ingestion_runs.log")

# S40-BE-020: P1 Latency Metrics
# Pilot domains for SLA tracking
P1_PILOT_DOMAINS = {"saude", "politica"}

# P1 latency histogram: collected_to_ready (in seconds)
# Buckets optimized for sub-second to multi-second latencies
p1_latency_collected_to_ready = Histogram(
    "p1_latency_collected_to_ready_seconds",
    "Latency from document collection to ready state (P1 SLA)",
    ["domain", "source"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

# P1 end-to-end latency histogram
p1_latency_end_to_end = Histogram(
    "p1_latency_end_to_end_seconds",
    "End-to-end latency from collection to pipeline completion (P1 SLA)",
    ["domain", "source"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

# In-memory tracking for collected timestamps (thread-safe)
_collected_timestamps: Dict[str, float] = {}
_timestamps_lock = threading.Lock()


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
        metrics.mark_success(run.source_id, datetime.now(timezone.utc).timestamp())
    if run.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS}:
        metrics.mark_failure(run.source_id, datetime.now(timezone.utc).timestamp())
        ingest_metrics.record_error(error_type=run.error_code or "error", source=run.source_id)


def sources_without_recent_runs(repo: IngestionRepository, threshold_minutes: int = 1440) -> List[str]:
    stale: List[str] = []
    now = datetime.now(timezone.utc)
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


# =============================================================================
# S40-BE-020: P1 Latency Metrics Functions
# =============================================================================


def is_pilot_domain(domain: str) -> bool:
    """Check if domain is a P1 pilot domain."""
    return domain.lower() in P1_PILOT_DOMAINS


def mark_collected(document_id: str, domain: str, source: str) -> None:
    """
    Mark a document as collected (start P1 latency tracking).

    Args:
        document_id: Unique identifier for the document
        domain: Domain (saude, politica, etc.)
        source: Source identifier
    """
    if not is_pilot_domain(domain):
        return

    key = f"{domain.lower()}:{source}:{document_id}"
    with _timestamps_lock:
        _collected_timestamps[key] = time.time()
    logger.debug(f"[p1_latency] Marked collected: {key}")


def mark_ready(
    document_id: str,
    domain: str,
    source: str,
    ready_at: Optional[float] = None,
) -> Optional[float]:
    """
    Mark a document as ready and record P1 latency.

    Args:
        document_id: Unique identifier for the document
        domain: Domain (saude, politica, etc.)
        source: Source identifier
        ready_at: Optional timestamp (defaults to now)

    Returns:
        Latency in seconds, or None if not tracked
    """
    if not is_pilot_domain(domain):
        return None

    key = f"{domain.lower()}:{source}:{document_id}"
    with _timestamps_lock:
        collected_at = _collected_timestamps.pop(key, None)

    if collected_at is None:
        logger.debug(f"[p1_latency] mark_ready called but no collected timestamp: {key}")
        return None

    ready_timestamp = ready_at or time.time()
    latency_seconds = ready_timestamp - collected_at

    # Record to Prometheus histogram
    p1_latency_collected_to_ready.labels(
        domain=domain.lower(),
        source=source,
    ).observe(latency_seconds)

    logger.debug(f"[p1_latency] Marked ready: {key}, latency={latency_seconds:.3f}s")
    return latency_seconds


def mark_pipeline_complete(
    document_id: str,
    domain: str,
    source: str,
    collected_at: float,
    completed_at: Optional[float] = None,
) -> Optional[float]:
    """
    Record end-to-end P1 latency (collection to pipeline completion).

    Args:
        document_id: Unique identifier for the document
        domain: Domain (saude, politica, etc.)
        source: Source identifier
        collected_at: Timestamp when document was collected
        completed_at: Optional completion timestamp (defaults to now)

    Returns:
        Latency in seconds, or None if not a pilot domain
    """
    if not is_pilot_domain(domain):
        return None

    completed_timestamp = completed_at or time.time()
    latency_seconds = completed_timestamp - collected_at

    # Record to Prometheus histogram
    p1_latency_end_to_end.labels(
        domain=domain.lower(),
        source=source,
    ).observe(latency_seconds)

    return latency_seconds


def get_p1_latency_stats(domain: str, source: str) -> Dict[str, Any]:
    """
    Get P1 latency statistics for a domain/source combination.

    Args:
        domain: Domain (saude, politica, etc.)
        source: Source identifier

    Returns:
        Dict with latency statistics
    """
    if not is_pilot_domain(domain):
        return {"error": f"Domain '{domain}' is not a P1 pilot domain"}

    # Get histogram data
    collected_to_ready = p1_latency_collected_to_ready.labels(
        domain=domain.lower(),
        source=source,
    )
    end_to_end = p1_latency_end_to_end.labels(
        domain=domain.lower(),
        source=source,
    )

    return {
        "domain": domain.lower(),
        "source": source,
        "collected_to_ready": {
            "count": collected_to_ready._sum._value if hasattr(collected_to_ready, "_sum") else 0,
            "buckets": list(p1_latency_collected_to_ready._upper_bounds),
        },
        "end_to_end": {
            "count": end_to_end._sum._value if hasattr(end_to_end, "_sum") else 0,
            "buckets": list(p1_latency_end_to_end._upper_bounds),
        },
        "pending_documents": sum(
            1 for k in _collected_timestamps if k.startswith(f"{domain.lower()}:{source}:")
        ),
    }


def clear_stale_timestamps(max_age_seconds: float = 3600) -> int:
    """
    Clear stale collected timestamps (documents that never became ready).

    Args:
        max_age_seconds: Maximum age before considering stale

    Returns:
        Number of cleared entries
    """
    now = time.time()
    with _timestamps_lock:
        stale_keys = [
            key for key, ts in _collected_timestamps.items()
            if now - ts > max_age_seconds
        ]

        for key in stale_keys:
            del _collected_timestamps[key]

    if stale_keys:
        logger.info(f"[p1_latency] Cleared {len(stale_keys)} stale timestamps")

    return len(stale_keys)


def get_pending_count() -> int:
    """Get count of documents pending ready state."""
    with _timestamps_lock:
        return len(_collected_timestamps)


def get_pending_documents(domain: Optional[str] = None) -> List[Tuple[str, str, str, float]]:
    """
    Get list of pending documents (collected but not ready).

    Args:
        domain: Optional domain filter

    Returns:
        List of (domain, source, document_id, collected_at) tuples
    """
    now = time.time()
    results = []

    with _timestamps_lock:
        for key, collected_at in _collected_timestamps.items():
            parts = key.split(":", 2)
            if len(parts) == 3:
                doc_domain, source, doc_id = parts
                if domain is None or doc_domain == domain.lower():
                    results.append((doc_domain, source, doc_id, now - collected_at))

    return sorted(results, key=lambda x: x[3], reverse=True)  # Oldest first


def get_p1_summary() -> Dict[str, Any]:
    """
    Get a summary of P1 latency tracking state.

    Returns:
        Dict with summary statistics
    """
    with _timestamps_lock:
        pending_count = len(_collected_timestamps)
        if pending_count == 0:
            oldest_pending = None
        else:
            now = time.time()
            oldest_pending = max(now - ts for ts in _collected_timestamps.values())

    return {
        "pilot_domains": list(P1_PILOT_DOMAINS),
        "pending_documents": pending_count,
        "oldest_pending_seconds": oldest_pending,
        "histograms": {
            "collected_to_ready": {
                "name": p1_latency_collected_to_ready._name,
                "buckets": list(p1_latency_collected_to_ready._upper_bounds),
            },
            "end_to_end": {
                "name": p1_latency_end_to_end._name,
                "buckets": list(p1_latency_end_to_end._upper_bounds),
            },
        },
    }
