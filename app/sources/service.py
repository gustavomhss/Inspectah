from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import Source, SourceHealthCheck, SourceHealthStatus, SourceState
from .normalizer import is_lab_endpoint, normalize_source_model, normalize_source_payload
from app.ingestion.repository import IngestionRepository
from app.ingestion.models import IngestionConfig, IngestionMode, IngestionStatus, MIN_INTERVAL
from .status import assert_valid_transition
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate
from .validators import validate_source_config, validate_source_payload
from .audit import record_admin_action
import importlib
sources_schema = importlib.import_module("migrations.versions.0002_s21_sources_schema")

DB_ENV = "INSPECTAH_S21_DB_PATH"
DEFAULT_DB = Path("out/databases/s21_sources.sqlite")


def _db_path() -> Path:
    path = Path(os.environ.get(DB_ENV, DEFAULT_DB))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_connection():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        _ensure_schema(conn)
        yield conn
    finally:
        conn.close()


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(value) -> str:
    return json.dumps(value, ensure_ascii=False) if value is not None else json.dumps({})


def _deserialize(value: Optional[str], default):
    if value is None:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _ensure_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sources'")
    exists = cursor.fetchone()
    if not exists:
        sources_schema.apply_migration(_db_path())
    info = conn.execute("PRAGMA table_info('sources')").fetchall()
    columns = {row[1] for row in info}
    if "refresh_interval" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN refresh_interval INTEGER")
        conn.commit()


MIN_REFRESH_INTERVAL = 15
MAX_REFRESH_INTERVAL = 10080  # 7 dias em minutos


def _default_refresh_interval(source_type: str) -> int:
    defaults = {
        "news_rss": 180,
        "gossip_feed": 720,
        "sports_api": 120,
        "weather_api": 60,
        "gov_record": 1440,
        "legislation": 720,
        "science_dataset": 10080,
        "static_dataset": 10080,
        "official_open": 1440,
    }
    return defaults.get(source_type, 1440)


def _normalize_refresh_interval(refresh_interval: Optional[int], source_type: str) -> int:
    value = refresh_interval if refresh_interval is not None else _default_refresh_interval(source_type)
    if value is None:
        value = _default_refresh_interval(source_type)
    if not isinstance(value, int):
        raise ValueError("refresh_interval deve ser inteiro em minutos")
    if value < MIN_REFRESH_INTERVAL or value > MAX_REFRESH_INTERVAL:
        raise ValueError("refresh_interval fora do intervalo permitido")
    return value


def _ensure_lab_ingestion_config(source: Source, updated_by: str) -> None:
    if not is_lab_endpoint(source.endpoint):
        return
    repo = IngestionRepository()
    existing = repo.get_config(source.id)
    mode = IngestionMode.MANUAL_ONLY
    enabled = True
    if existing:
        existing.mode = mode
        existing.enabled = enabled
        existing.updated_by = updated_by
        existing.updated_at = datetime.now(timezone.utc)
        repo.save_config(existing)
        return
    cfg = IngestionConfig.create(
        id=_generate_id("ingcfg"),
        source_id=source.id,
        source_state=source.state,
        enabled=enabled,
        mode=mode,
        interval_minutes=source.refresh_interval if getattr(source, "refresh_interval", None) else MIN_INTERVAL,
        max_attempts=3,
        timeout_seconds=60,
        created_by=updated_by,
    )
    repo.save_config(cfg)


def _row_to_source(row: sqlite3.Row) -> Source:
    refresh_from_row = row["refresh_interval"] if "refresh_interval" in row.keys() else None
    return Source(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        description=row["description"] or "",
        type=row["type"],
        category=row["category"] or "",
        themes=_deserialize(row["themes"], []),
        info_types=_deserialize(row["info_types"], []),
        refresh_interval=_normalize_refresh_interval(refresh_from_row, row["type"]),
        protocol=row["protocol"] or "https",
        format=row["format"] or "json",
        endpoint=row["endpoint"] or "",
        auth_type=row["auth_type"] or "none",
        auth_config=_deserialize(row["auth_config"], {}),
        request_params=_deserialize(row["request_params"], {}),
        headers=_deserialize(row["headers"], {}),
        frequency=row["frequency"] or "manual",
        timeout_ms=int(row["timeout_ms"]) if row["timeout_ms"] is not None else 10000,
        retry_policy=_deserialize(row["retry_policy"], {}),
        parsing_config=_deserialize(row["parsing_config"], {}),
        redundancy_group=row["redundancy_group"],
        redundancy_role=row["redundancy_role"],
        state=SourceState(row["state"]),
        state_reason=row["state_reason"],
        state_updated_at=datetime.fromisoformat(row["state_updated_at"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        created_by=row["created_by"] or "system",
        updated_by=row["updated_by"] or "system",
        last_reviewed_by=row["last_reviewed_by"],
        meta=_deserialize(row["meta"], {}),
        conflict_flags=_deserialize(row["conflict_flags"], []),
        conflict_with_sources=_deserialize(row["conflict_with_sources"], []),
        has_open_contestation=bool(row["has_open_contestation"]),
        last_conflict_at=datetime.fromisoformat(row["last_conflict_at"]) if row["last_conflict_at"] else None,
        evidence_refs=_deserialize(row["evidence_refs"], []),
        trust_severity=row["trust_severity"],
    )


def _fetch_latest_health(conn: sqlite3.Connection, source_id: str) -> Optional[SourceHealthCheck]:
    cursor = conn.execute(
        "SELECT * FROM source_health_checks WHERE source_id=? ORDER BY datetime(checked_at) DESC LIMIT 1",
        (source_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return SourceHealthCheck(
        id=row["id"],
        source_id=row["source_id"],
        status=SourceHealthStatus(row["status"]),
        latency_ms=int(row["latency_ms"]),
        checked_at=datetime.fromisoformat(row["checked_at"]),
        error=row["error"],
        meta=_deserialize(row["meta"], {}),
    )


def list_sources(filters: Optional[SourceFilter] = None) -> List[Source]:
    filters = filters or SourceFilter()
    clauses = []
    params: List = []
    if filters.type:
        clauses.append("type = ?")
        params.append(filters.type)
    if filters.category:
        clauses.append("category = ?")
        params.append(filters.category)
    if filters.state:
        clauses.append("state = ?")
        params.append(filters.state.value)
    if filters.theme:
        clauses.append("themes LIKE ?")
        params.append(f"%{filters.theme}%")
    if filters.redundancy_group:
        clauses.append("redundancy_group = ?")
        params.append(filters.redundancy_group)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT * FROM sources {where} ORDER BY updated_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_source(row) for row in rows]


def get_source_detail(source_id: str) -> Optional[Source]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
        if not row:
            return None
        return _row_to_source(row)


def _insert_state_history(conn: sqlite3.Connection, source_id: str, from_state: Optional[SourceState], to_state: SourceState, reason: str, changed_by: str) -> None:
    conn.execute(
        """
        INSERT INTO source_state_history (id, source_id, from_state, to_state, reason, changed_by, created_at, conflict_flag, conflict_types, conflict_with_sources, contestations, evidence_refs)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
        """,
        (
            _generate_id("state"),
            source_id,
            from_state.value if from_state else None,
            to_state.value,
            reason,
            changed_by,
            _now_iso(),
            json.dumps([]),
            json.dumps([]),
            json.dumps({}),
            json.dumps([]),
        ),
    )


def create_source(payload: SourceCreate) -> Source:
    payload = normalize_source_payload(payload)  # aplica regras de normalização antes de persistir
    validate_source_payload(payload)
    validate_source_config(payload.type, payload.model_dump())
    source_id = _generate_id("src")
    now = _now_iso()
    refresh_interval = _normalize_refresh_interval(payload.refresh_interval, payload.type)
    with get_connection() as conn:
        placeholders = ",".join(["?"] * 37)
        conn.execute(
            f"""
            INSERT INTO sources (
                id, slug, name, description, type, category, themes, info_types, refresh_interval, protocol, format, endpoint,
                auth_type, auth_config, request_params, headers, frequency, timeout_ms, retry_policy, parsing_config,
                redundancy_group, redundancy_role, state, state_reason, state_updated_at, created_at, updated_at,
                created_by, updated_by, last_reviewed_by, meta, conflict_flags, conflict_with_sources,
                has_open_contestation, last_conflict_at, evidence_refs, trust_severity
            ) VALUES (
                {placeholders}
            )
            """,
            (
                source_id,
                payload.slug or source_id,
                payload.name,
                payload.description,
                payload.type,
                payload.category,
                _serialize(payload.themes),
                _serialize(payload.info_types),
                refresh_interval,
                payload.protocol,
                payload.format,
                payload.endpoint,
                payload.auth_type,
                _serialize(payload.auth_config),
                _serialize(payload.request_params),
                _serialize(payload.headers),
                payload.frequency,
                payload.timeout_ms,
                _serialize(payload.retry_policy),
                _serialize(payload.parsing_config),
                payload.redundancy_group,
                payload.redundancy_role,
                SourceState.PROPOSED.value,
                None,
                now,
                now,
                now,
                payload.created_by,
                payload.created_by,
                None,
                _serialize(payload.meta),
                json.dumps([]),
                json.dumps([]),
                0,
                None,
                json.dumps([]),
                None,
            ),
        )
        _insert_state_history(conn, source_id, None, SourceState.PROPOSED, "Fonte criada", payload.created_by)
        conn.commit()
    created = get_source_detail(source_id)
    assert created is not None
    normalized = normalize_source_model(created)
    if normalized != created:
        with get_connection() as conn:
            _update_source_record(conn, normalized)
            conn.commit()
        created = get_source_detail(source_id) or normalized
    _ensure_lab_ingestion_config(created, payload.created_by)
    record_admin_action("create_source", source_id, payload.created_by, {"slug": payload.slug or source_id, "type": payload.type})
    return created


def _update_source_record(conn: sqlite3.Connection, source: Source) -> None:
    conn.execute(
        """
        UPDATE sources SET
            slug=?, name=?, description=?, type=?, category=?, themes=?, info_types=?, refresh_interval=?, protocol=?, format=?, endpoint=?,
            auth_type=?, auth_config=?, request_params=?, headers=?, frequency=?, timeout_ms=?, retry_policy=?, parsing_config=?,
            redundancy_group=?, redundancy_role=?, state=?, state_reason=?, state_updated_at=?, updated_at=?, updated_by=?,
            last_reviewed_by=?, meta=?, conflict_flags=?, conflict_with_sources=?, has_open_contestation=?, last_conflict_at=?,
            evidence_refs=?, trust_severity=?
        WHERE id=?
        """,
        (
            source.slug,
            source.name,
            source.description,
            source.type,
            source.category,
            _serialize(source.themes),
            _serialize(source.info_types),
            source.refresh_interval,
            source.protocol,
            source.format,
            source.endpoint,
            source.auth_type,
            _serialize(source.auth_config),
            _serialize(source.request_params),
            _serialize(source.headers),
            source.frequency,
            source.timeout_ms,
            _serialize(source.retry_policy),
            _serialize(source.parsing_config),
            source.redundancy_group,
            source.redundancy_role,
            source.state.value,
            source.state_reason,
            source.state_updated_at.isoformat(),
            _now_iso(),
            source.updated_by,
            source.last_reviewed_by,
            _serialize(source.meta),
            _serialize(source.conflict_flags),
            _serialize(source.conflict_with_sources),
            int(source.has_open_contestation),
            source.last_conflict_at.isoformat() if source.last_conflict_at else None,
            _serialize(source.evidence_refs),
            source.trust_severity,
            source.id,
        ),
    )


def update_source(source_id: str, payload: SourceUpdate) -> Optional[Source]:
    payload = normalize_source_payload(payload)
    existing = get_source_detail(source_id)
    if not existing:
        return None
    incoming = payload.model_dump(exclude_none=True, by_alias=True)
    merged = existing.__dict__.copy()
    merged.update(incoming)
    merged["slug"] = existing.slug
    merged["type"] = merged.get("type") or existing.type
    merged["category"] = merged.get("category") or existing.category
    merged["updated_by"] = payload.updated_by or existing.updated_by
    merged.pop("url_base", None)
    merged["refresh_interval"] = _normalize_refresh_interval(
        merged.get("refresh_interval"), merged.get("type", existing.type)
    )
    validate_source_payload(SourceCreate(**{**merged, "created_by": existing.created_by}))
    validate_source_config(merged["type"], merged)

    source = Source(**merged)  # type: ignore[arg-type]
    state_before = source.state
    source = normalize_source_model(source)
    if source.state != state_before:
        source.state_updated_at = datetime.now(timezone.utc)
    # não muda estado diretamente aqui; usar change_source_state para transições
    with get_connection() as conn:
        _update_source_record(conn, source)
        conn.commit()
    _ensure_lab_ingestion_config(source, payload.updated_by)
    record_admin_action("update_source", source_id, payload.updated_by, {"fields": list(payload.model_dump(exclude_none=True).keys())})
    return get_source_detail(source_id)


def _apply_state_transition(conn: sqlite3.Connection, source: Source, target_state: SourceState, reason: str, changed_by: str) -> Source:
    if source.state == SourceState.DISABLED_PERM:
        raise ValueError("Fonte está desativada permanentemente")
    assert_valid_transition(source.state, target_state)
    prev = source.state
    source.state = target_state
    source.state_reason = reason
    source.state_updated_at = datetime.now(timezone.utc)
    source.updated_at = datetime.now(timezone.utc)
    source.updated_by = changed_by
    _update_source_record(conn, source)
    _insert_state_history(conn, source.id, prev, target_state, reason, changed_by)
    return source


def change_source_state(source_id: str, target_state: SourceState, reason: str, changed_by: str) -> Optional[Source]:
    source = get_source_detail(source_id)
    if not source:
        return None
    with get_connection() as conn:
        _apply_state_transition(conn, source, target_state, reason, changed_by)
        conn.commit()
    record_admin_action("change_source_state", source_id, changed_by, {"target_state": target_state.value, "reason": reason})
    return get_source_detail(source_id)


def register_healthcheck(
    source_id: str,
    status: SourceHealthStatus,
    latency_ms: int,
    error: Optional[str] = None,
    meta: Optional[Dict] = None,
) -> SourceHealthCheck:
    with get_connection() as conn:
        check = SourceHealthCheck(
            id=_generate_id("hc"),
            source_id=source_id,
            status=status,
            latency_ms=latency_ms,
            checked_at=datetime.now(timezone.utc),
            error=error,
            meta=meta or {},
        )
        conn.execute(
            """
            INSERT INTO source_health_checks (id, source_id, status, latency_ms, checked_at, error, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                check.id,
                check.source_id,
                check.status.value,
                check.latency_ms,
                check.checked_at.isoformat(),
                check.error,
                json.dumps(check.meta),
            ),
        )
        conn.commit()
    return check


def list_healthchecks(source_id: str) -> List[SourceHealthCheck]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM source_health_checks WHERE source_id=? ORDER BY datetime(checked_at) DESC",
            (source_id,),
        ).fetchall()
        return [
            SourceHealthCheck(
                id=row["id"],
                source_id=row["source_id"],
                status=SourceHealthStatus(row["status"]),
                latency_ms=int(row["latency_ms"]),
                checked_at=datetime.fromisoformat(row["checked_at"]),
                error=row["error"],
                meta=_deserialize(row["meta"], {}),
            )
            for row in rows
        ]


def list_state_history(source_id: str) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM source_state_history WHERE source_id=? ORDER BY datetime(created_at) DESC",
            (source_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def enrich_source_read(source: Source) -> SourceRead:
    with get_connection() as conn:
        last_health = _fetch_latest_health(conn, source.id)
    health = _compute_health_from_runs(source.id)
    return SourceRead(
        **source.__dict__,
        last_health_status=last_health.status.value if last_health else None,
        last_health_error=last_health.error if last_health else None,
        last_health_at=last_health.checked_at if last_health else None,
        recent_items_count=health["recent_items_count"],
        ingestion_mode=_get_ingestion_mode(source.id),
        health_status=health["status"],
        health_reason=health["reason"],
        last_run_status=health["last_run_status"],
        last_run_finished_at=health["last_run_finished_at"],
        last_run_latency_ms=health["last_run_latency_ms"],
        last_run_items=health["last_run_items"],
        failure_streak=health["failure_streak"],
    )


def _get_ingestion_mode(source_id: str) -> str:
    try:
        cfg = IngestionRepository().get_config(source_id)
        if cfg:
            return cfg.mode.value
    except Exception:
        return IngestionMode.MANUAL_ONLY.value
    return IngestionMode.MANUAL_ONLY.value


def _compute_health_from_runs(source_id: str) -> Dict[str, Optional[object]]:
    repo = IngestionRepository()
    runs = repo.list_runs_by_source(source_id, limit=5)
    if not runs:
        return {
            "status": SourceHealthStatus.DEGRADED.value,
            "reason": "Sem execuções recentes",
            "last_run_status": None,
            "last_run_finished_at": None,
            "last_run_latency_ms": None,
            "last_run_items": None,
            "failure_streak": 0,
            "recent_items_count": 0,
        }
    last = runs[0]
    success_count = sum(1 for r in runs if r.status == IngestionStatus.SUCCESS)
    fail_count = sum(1 for r in runs if r.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS})
    latency_ms = _run_latency_ms(last)
    items_total = sum(r.items_processed for r in runs if r.items_processed is not None)
    status = SourceHealthStatus.OK
    reason = "Última execução bem-sucedida"
    if last.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS}:
        status = SourceHealthStatus.FAIL if last.status == IngestionStatus.FAIL else SourceHealthStatus.DEGRADED
        reason = last.error_message or "Falha recente de ingestão"
    elif fail_count > 0:
        status = SourceHealthStatus.DEGRADED
        reason = "Falhas recentes detectadas"
    if latency_ms is not None and latency_ms > 120000:
        status = SourceHealthStatus.DEGRADED
        reason = "Latência elevada na última execução"
    failure_streak = 0
    for run in runs:
        if run.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS}:
            failure_streak += 1
        else:
            break
    return {
        "status": status.value,
        "reason": reason,
        "last_run_status": last.status.value,
        "last_run_finished_at": last.finished_at or last.started_at,
        "last_run_latency_ms": latency_ms,
        "last_run_items": last.items_processed,
        "failure_streak": failure_streak,
        "recent_items_count": items_total,
    }


def _run_latency_ms(run) -> Optional[int]:
    if not run.started_at or not run.finished_at:
        return None
    delta = run.finished_at - run.started_at
    return int(delta.total_seconds() * 1000)
