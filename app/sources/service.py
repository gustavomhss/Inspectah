from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import Source, SourceHealthCheck, SourceHealthStatus, SourceState
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate
from .validators import validate_source_config, validate_source_payload

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
        yield conn
    finally:
        conn.close()


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _serialize(value) -> str:
    return json.dumps(value, ensure_ascii=False) if value is not None else json.dumps({})


def _deserialize(value: Optional[str], default):
    if value is None:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _row_to_source(row: sqlite3.Row) -> Source:
    return Source(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        description=row["description"] or "",
        type=row["type"],
        category=row["category"] or "",
        themes=_deserialize(row["themes"], []),
        info_types=_deserialize(row["info_types"], []),
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


def _allowed_transitions() -> Dict[SourceState, set[SourceState]]:
    return {
        SourceState.PROPOSED: {SourceState.TESTING},
        SourceState.TESTING: {SourceState.ACTIVE, SourceState.UNDER_REVIEW},
        SourceState.ACTIVE: {SourceState.UNDER_REVIEW, SourceState.SUSPECT, SourceState.DISABLED_TEMP},
        SourceState.UNDER_REVIEW: {
            SourceState.ACTIVE,
            SourceState.SUSPECT,
            SourceState.DISABLED_TEMP,
            SourceState.DISABLED_PERM,
        },
        SourceState.SUSPECT: {SourceState.UNDER_REVIEW, SourceState.DISABLED_TEMP, SourceState.DISABLED_PERM},
        SourceState.DISABLED_TEMP: {SourceState.UNDER_REVIEW, SourceState.ACTIVE},
    }


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
    validate_source_payload(payload)
    validate_source_config(payload.type, payload.model_dump())
    source_id = _generate_id("src")
    now = _now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sources (
                id, slug, name, description, type, category, themes, info_types, protocol, format, endpoint,
                auth_type, auth_config, request_params, headers, frequency, timeout_ms, retry_policy, parsing_config,
                redundancy_group, redundancy_role, state, state_reason, state_updated_at, created_at, updated_at,
                created_by, updated_by, last_reviewed_by, meta, conflict_flags, conflict_with_sources,
                has_open_contestation, last_conflict_at, evidence_refs, trust_severity
            ) VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
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
    result = get_source_detail(source_id)
    assert result is not None
    return result


def _update_source_record(conn: sqlite3.Connection, source: Source) -> None:
    conn.execute(
        """
        UPDATE sources SET
            slug=?, name=?, description=?, type=?, category=?, themes=?, info_types=?, protocol=?, format=?, endpoint=?,
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
    existing = get_source_detail(source_id)
    if not existing:
        return None
    validate_source_payload(SourceCreate(**payload.model_dump(exclude_none=True), created_by=existing.created_by))
    validate_source_config(payload.type or existing.type, payload.model_dump())

    updated = existing.__dict__.copy()
    updated.update(payload.model_dump(exclude_none=True, by_alias=True))
    updated["updated_by"] = payload.updated_by
    updated.pop("url_base", None)
    source = Source(**updated)  # type: ignore[arg-type]
    # não muda estado diretamente aqui; usar change_source_state para transições
    with get_connection() as conn:
        _update_source_record(conn, source)
        conn.commit()
    return get_source_detail(source_id)


def _apply_state_transition(conn: sqlite3.Connection, source: Source, target_state: SourceState, reason: str, changed_by: str) -> Source:
    if source.state == SourceState.DISABLED_PERM:
        raise ValueError("Fonte está desativada permanentemente")
    allowed = _allowed_transitions().get(source.state, set())
    if target_state not in allowed and target_state != SourceState.DISABLED_PERM:
        raise ValueError(f"Transição inválida: {source.state.value} -> {target_state.value}")
    prev = source.state
    source.state = target_state
    source.state_reason = reason
    source.state_updated_at = datetime.utcnow()
    source.updated_at = datetime.utcnow()
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
            checked_at=datetime.utcnow(),
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
    return SourceRead(
        **source.__dict__,
        last_health_status=last_health.status.value if last_health else None,
        last_health_error=last_health.error if last_health else None,
        last_health_at=last_health.checked_at if last_health else None,
        recent_items_count=0,
    )
