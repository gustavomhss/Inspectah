from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import (
    EvidenceBundle,
    EvidenceItemRef,
    Item,
    QueryLog,
    Source,
    SourceConfig,
    SourceStatus,
    UserResponse,
)

DATA_DIR_ENV = "INSPECTAH_DATA_DIR"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _data_dir() -> Path:
    override = os.getenv(DATA_DIR_ENV)
    if override:
        base = Path(override)
    else:
        base = _repo_root() / "out" / "evidence"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sources_dir() -> Path:
    return _ensure_dir(_data_dir() / "s8_sources")


def _items_dir() -> Path:
    return _ensure_dir(_data_dir() / "s8_items")


def bundles_dir() -> Path:
    return _ensure_dir(_data_dir() / "s8_bundles")


def queries_dir() -> Path:
    return _ensure_dir(_data_dir() / "s8_queries")


def responses_dir() -> Path:
    return _ensure_dir(_data_dir() / "s8_responses")


def _to_serializable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {k: _to_serializable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_serializable(v) for v in value]
    return value


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_source(source: Source) -> Path:
    path = _sources_dir() / f"{source.id}.json"
    _write_json(path, _to_serializable(source))
    return path


def _source_from_data(data: Dict[str, Any]) -> Source:
    config = data.get("config", {})
    status = data.get("status", {})
    return Source(
        id=data["id"],
        name=data["name"],
        type=data["type"],
        config=SourceConfig(
            url_base=config.get("url_base", ""),
            auth_token=config.get("auth_token"),
            params=config.get("params", {}),
            selected_fields=config.get("selected_fields", []),
        ),
        status=SourceStatus(
            last_fetch_at=_parse_datetime(status.get("last_fetch_at")),
            last_fetch_status=status.get("last_fetch_status", "ok"),
            last_fetch_error=status.get("last_fetch_error"),
            recent_items_count=status.get("recent_items_count", 0),
        ),
    )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def get_source(source_id: str) -> Optional[Source]:
    path = _sources_dir() / f"{source_id}.json"
    if not path.exists():
        return None
    return _source_from_data(_read_json(path))


def list_sources() -> List[Source]:
    return [
        _source_from_data(_read_json(path))
        for path in sorted(_sources_dir().glob("*.json"))
    ]


def save_item(item: Item) -> Path:
    path = _items_dir() / f"{item.id}.json"
    _write_json(path, _to_serializable(item))
    return path


def get_item(item_id: str) -> Optional[Item]:
    path = _items_dir() / f"{item_id}.json"
    if not path.exists():
        return None
    data = _read_json(path)
    return Item(
        id=data["id"],
        source_id=data["source_id"],
        payload=data.get("payload", {}),
        created_at=_parse_datetime(data.get("created_at")) or datetime.utcnow(),
    )


def get_item_path(item_id: str) -> Path:
    return _items_dir() / f"{item_id}.json"


def list_items_by_filter(
    filters: Optional[Dict[str, Any]] = None,
    limit_per_source: int = 10,
) -> List[Item]:
    filters = filters or {}
    produto = _normalize(filters.get("produto"))
    cidade = _normalize(filters.get("cidade"))
    pessoa = _normalize(filters.get("pessoa"))
    caso = _normalize(filters.get("caso"))
    info_type = _normalize(filters.get("info_type"))
    source_ids_filter = set(filters.get("source_ids", []))
    source_types = {_normalize(s) for s in filters.get("source_types", []) if s}

    sources_map = {source.id: source for source in list_sources()}
    per_source_count: Dict[str, int] = {}
    results: List[Item] = []

    for path in sorted(_items_dir().glob("*.json")):
        data = _read_json(path)
        item = Item(
            id=data["id"],
            source_id=data["source_id"],
            payload=data.get("payload", {}),
            created_at=_parse_datetime(data.get("created_at")) or datetime.utcnow(),
        )
        source = sources_map.get(item.source_id)
        if not source:
            continue
        if source_ids_filter and item.source_id not in source_ids_filter:
            continue
        if source_types and _normalize(source.type) not in source_types:
            continue
        if per_source_count.get(item.source_id, 0) >= limit_per_source:
            continue
        payload = item.payload
        if produto and _normalize(payload.get("produto")) != produto:
            continue
        if cidade and _normalize(payload.get("cidade")) != cidade:
            continue
        if pessoa and _normalize(payload.get("pessoa")) != pessoa:
            continue
        if caso and _normalize(payload.get("caso")) != caso:
            continue
        payload_info = _normalize(payload.get("info_type"))
        if info_type and payload_info != info_type:
            continue
        per_source_count[item.source_id] = per_source_count.get(item.source_id, 0) + 1
        results.append(item)
    results.sort(key=lambda it: it.created_at, reverse=True)
    return results


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def save_evidence_bundle(bundle: EvidenceBundle) -> Path:
    path = bundles_dir() / f"{bundle.id}.json"
    payload = _to_serializable(bundle)
    payload.setdefault("storage_path", str(path))
    _write_json(path, payload)
    return path


def load_evidence_bundle(bundle_id: str) -> Optional[EvidenceBundle]:
    path = bundles_dir() / f"{bundle_id}.json"
    if not path.exists():
        return None
    data = _read_json(path)
    items_by_source: Dict[str, List[EvidenceItemRef]] = {}
    for source_id, items in data.get("items_by_source", {}).items():
        refs = [
            EvidenceItemRef(
                item_id=ref["item_id"],
                source_id=ref["source_id"],
                key_fields=ref.get("key_fields", {}),
            )
            for ref in items
        ]
        items_by_source[source_id] = refs
    return EvidenceBundle(
        id=data["id"],
        query_type=data["query_type"],
        query_filters=data.get("query_filters", {}),
        items_by_source=items_by_source,
        manifest_paths=data.get("manifest_paths", {}),
        created_at=_parse_datetime(data.get("created_at")) or datetime.utcnow(),
        meta=data.get("meta", {}),
    )


def save_query_log(log: QueryLog) -> Path:
    path = queries_dir() / f"{log.query_id}.json"
    payload = _to_serializable(log)
    payload.setdefault("storage_path", str(path))
    _write_json(path, payload)
    return path


def load_query_log(query_id: str) -> Optional[QueryLog]:
    path = queries_dir() / f"{query_id}.json"
    if not path.exists():
        return None
    data = _read_json(path)
    return QueryLog(
        query_id=data["query_id"],
        user_query=data["user_query"],
        query_type=data.get("query_type"),
        evidence_bundle_id=data.get("evidence_bundle_id"),
        sources=data.get("sources", []),
        items_used=data.get("items_used", []),
        gpt_response_ref=data.get("gpt_response_ref"),
        timestamp=_parse_datetime(data.get("timestamp")) or datetime.utcnow(),
        status=data.get("status", "ok"),
        error_code=data.get("error_code"),
    )


def save_user_response(response: UserResponse | Dict[str, Any], response_id: Optional[str] = None) -> str:
    response_id = response_id or generate_entity_id("resp")
    path = responses_dir() / f"{response_id}.json"
    if isinstance(response, UserResponse):
        payload = _to_serializable(response)
    else:
        payload = dict(response)
    payload.setdefault("id", response_id)
    payload.setdefault("created_at", datetime.utcnow().isoformat())
    _write_json(path, payload)
    return response_id


def generate_entity_id(prefix: str) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    suffix = uuid.uuid4().hex[:6]
    return f"{prefix}_{stamp}_{suffix}"


def ensure_fixture_sources(sources: Iterable[Source]) -> None:
    for source in sources:
        save_source(source)
