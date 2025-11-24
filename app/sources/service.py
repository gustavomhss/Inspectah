from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import (
    Source,
    SourceHealthCheck,
    SourceHealthStatus,
    SourceState,
    SourceStateHistory,
)
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate
from .validators import validate_source_config, validate_source_payload

DATA_DIR = Path(__file__).resolve().parents[2] / "out" / "data" / "s21_sources"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SOURCES_PATH = DATA_DIR / "sources.json"
HEALTH_PATH = DATA_DIR / "healthchecks.json"
STATE_PATH = DATA_DIR / "state_history.json"


def _load_json(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_json(path: Path, payload: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str, ensure_ascii=False)


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _serialize_source(source: Source) -> Dict:
    return {
        **source.__dict__,
        "state": source.state.value,
        "state_updated_at": source.state_updated_at.isoformat(),
        "created_at": source.created_at.isoformat(),
        "updated_at": source.updated_at.isoformat(),
        "last_conflict_at": source.last_conflict_at.isoformat() if source.last_conflict_at else None,
    }


def _deserialize_source(data: Dict) -> Source:
    return Source(
        id=data["id"],
        slug=data["slug"],
        name=data["name"],
        description=data.get("description", ""),
        type=data["type"],
        category=data.get("category", ""),
        themes=data.get("themes", []),
        info_types=data.get("info_types", []),
        protocol=data.get("protocol", "https"),
        format=data.get("format", "json"),
        endpoint=data.get("endpoint", data.get("url_base", "")),
        auth_type=data.get("auth_type", "none"),
        auth_config=data.get("auth_config", {}),
        request_params=data.get("request_params", {}),
        headers=data.get("headers", {}),
        frequency=data.get("frequency", "manual"),
        timeout_ms=int(data.get("timeout_ms", 10000)),
        retry_policy=data.get("retry_policy", {}),
        parsing_config=data.get("parsing_config", {}),
        redundancy_group=data.get("redundancy_group"),
        redundancy_role=data.get("redundancy_role"),
        state=SourceState(data.get("state", "PROPOSED")),
        state_reason=data.get("state_reason"),
        state_updated_at=datetime.fromisoformat(data["state_updated_at"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        created_by=data.get("created_by", "system"),
        updated_by=data.get("updated_by", "system"),
        last_reviewed_by=data.get("last_reviewed_by"),
        meta=data.get("meta", {}),
        conflict_flags=data.get("conflict_flags", []),
        conflict_with_sources=data.get("conflict_with_sources", []),
        has_open_contestation=data.get("has_open_contestation", False),
        last_conflict_at=datetime.fromisoformat(data["last_conflict_at"])
        if data.get("last_conflict_at")
        else None,
        evidence_refs=data.get("evidence_refs", []),
        trust_severity=data.get("trust_severity"),
    )


def _persist_sources(sources: List[Source]) -> None:
    _save_json(SOURCES_PATH, [_serialize_source(src) for src in sources])


def _load_sources() -> List[Source]:
    return [_deserialize_source(data) for data in _load_json(SOURCES_PATH)]


def _find_source(source_id: str) -> Tuple[Optional[Source], List[Source]]:
    sources = _load_sources()
    for src in sources:
        if src.id == source_id:
            return src, sources
    return None, sources


def list_sources(filters: Optional[SourceFilter] = None) -> List[Source]:
    filters = filters or SourceFilter()
    results: List[Source] = []
    for src in _load_sources():
        if filters.type and src.type != filters.type:
            continue
        if filters.category and src.category != filters.category:
            continue
        if filters.state and src.state != filters.state:
            continue
        if filters.theme and filters.theme not in src.themes:
            continue
        if filters.redundancy_group and src.redundancy_group != filters.redundancy_group:
            continue
        results.append(src)
    return results


def get_source_detail(source_id: str) -> Optional[Source]:
    src, _ = _find_source(source_id)
    return src


def create_source(payload: SourceCreate) -> Source:
    validate_source_payload(payload)
    validate_source_config(payload.type, payload.model_dump())
    source_id = _generate_id("src")
    slug = payload.slug or source_id
    source = Source.create(
        id=source_id,
        slug=slug,
        name=payload.name,
        description=payload.description,
        type=payload.type,
        category=payload.category,
        themes=payload.themes,
        info_types=payload.info_types,
        protocol=payload.protocol,
        format=payload.format,
        endpoint=payload.endpoint or getattr(payload, "url_base", payload.endpoint),
        auth_type=payload.auth_type,
        auth_config=payload.auth_config,
        request_params=payload.request_params,
        headers=payload.headers,
        frequency=payload.frequency,
        timeout_ms=payload.timeout_ms,
        retry_policy=payload.retry_policy,
        parsing_config=payload.parsing_config,
        redundancy_group=payload.redundancy_group,
        redundancy_role=payload.redundancy_role,
        created_by=payload.created_by,
        meta=payload.meta,
    )
    sources = _load_sources()
    sources.append(source)
    _persist_sources(sources)
    _append_state_history(source, None, source.state, payload.created_by, "Fonte criada")
    return source


def update_source(source_id: str, payload: SourceUpdate) -> Optional[Source]:
    source, sources = _find_source(source_id)
    if not source:
        return None
    validate_source_payload(SourceCreate(**payload.dict(exclude_none=True, exclude={"updated_by"}), created_by=source.created_by))
    validate_source_config(payload.type or source.type, payload.dict())
    updated = source.__dict__.copy()
    updated.update(payload.dict(exclude_unset=True, by_alias=True))
    updated["updated_at"] = datetime.utcnow()
    updated["updated_by"] = payload.updated_by
    if payload.state:
        _apply_state_transition(source, payload.state, payload.state_reason or "Atualização de estado", payload.updated_by)
    new_source = Source(**updated)  # type: ignore[arg-type]
    new_source.state = source.state
    new_source.state_reason = source.state_reason
    new_source.state_updated_at = source.state_updated_at
    idx = [i for i, s in enumerate(sources) if s.id == source_id][0]
    sources[idx] = new_source
    _persist_sources(sources)
    return new_source


def _append_state_history(source: Source, from_state: Optional[SourceState], to_state: SourceState, changed_by: str, reason: str) -> None:
    entries = _load_json(STATE_PATH)
    entries.append(
        {
            "id": _generate_id("state"),
            "source_id": source.id,
            "from_state": from_state.value if from_state else None,
            "to_state": to_state.value,
            "reason": reason,
            "changed_by": changed_by,
            "created_at": datetime.utcnow().isoformat(),
            "conflict_flag": False,
            "conflict_types": [],
            "conflict_with_sources": [],
            "contestations": {},
            "evidence_refs": [],
        }
    )
    _save_json(STATE_PATH, entries)


def _apply_state_transition(source: Source, target_state: SourceState, reason: str, changed_by: str) -> None:
    if source.state == SourceState.DISABLED_PERM:
        raise ValueError("Fonte está desativada permanentemente")
    valid = {
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
    allowed = valid.get(source.state, set())
    if target_state not in allowed and target_state != SourceState.DISABLED_PERM:
        raise ValueError(f"Transição inválida: {source.state.value} -> {target_state.value}")
    from_state = source.state
    source.state = target_state
    source.state_reason = reason
    source.state_updated_at = datetime.utcnow()
    _append_state_history(source, from_state, target_state, changed_by, reason)


def change_source_state(source_id: str, target_state: SourceState, reason: str, changed_by: str) -> Optional[Source]:
    source, sources = _find_source(source_id)
    if not source:
        return None
    _apply_state_transition(source, target_state, reason, changed_by)
    source.updated_at = datetime.utcnow()
    source.updated_by = changed_by
    idx = [i for i, s in enumerate(sources) if s.id == source_id][0]
    sources[idx] = source
    _persist_sources(sources)
    return source


def register_healthcheck(source_id: str, status: SourceHealthStatus, latency_ms: int, error: Optional[str] = None, meta: Optional[Dict] = None) -> SourceHealthCheck:
    check = SourceHealthCheck(
        id=_generate_id("hc"),
        source_id=source_id,
        status=status,
        latency_ms=latency_ms,
        checked_at=datetime.utcnow(),
        error=error,
        meta=meta or {},
    )
    entries = _load_json(HEALTH_PATH)
    entries.append(
        {
            "id": check.id,
            "source_id": check.source_id,
            "status": check.status.value,
            "latency_ms": check.latency_ms,
            "checked_at": check.checked_at.isoformat(),
            "error": check.error,
            "meta": check.meta,
        }
    )
    _save_json(HEALTH_PATH, entries)
    return check


def list_healthchecks(source_id: str) -> List[SourceHealthCheck]:
    return [
        SourceHealthCheck(
            id=entry["id"],
            source_id=entry["source_id"],
            status=SourceHealthStatus(entry["status"]),
            latency_ms=int(entry["latency_ms"]),
            checked_at=datetime.fromisoformat(entry["checked_at"]),
            error=entry.get("error"),
            meta=entry.get("meta", {}),
        )
        for entry in _load_json(HEALTH_PATH)
        if entry.get("source_id") == source_id
    ]
