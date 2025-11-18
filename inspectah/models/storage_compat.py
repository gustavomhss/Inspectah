from __future__ import annotations

"""Sprint 3 compatibility shim built on top of ``app.core.storage``.

The historical Sprint 3 automation depends on helpers such as ``init_db`` and
``get_connection``. Rather than resurrecting the SQLite backend, this adapter
persists everything inside ``out/evidence/s3_legacy`` using the same data-dir
resolution as ``app.core.storage`` so the newer pipeline keeps its layout.
"""

import json
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from app.core import storage as core_storage

from inspectah.config import DB_PATH
from inspectah.evidence_vault.metadata import EvidenceRecord, normalize_timestamp

_LEGACY_NAMESPACE = "s3_legacy"
_ITEM_PREFIX = "legacy_item"
_EVIDENCE_PREFIX = "evidence"


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _legacy_root() -> Path:
    data_dir = core_storage.bundles_dir().parent
    return _ensure_dir(data_dir / _LEGACY_NAMESPACE)


LEGACY_ROOT = _legacy_root()
ITEMS_DIR = _ensure_dir(LEGACY_ROOT / "items")
EVIDENCE_DIR = _ensure_dir(LEGACY_ROOT / "evidence_records")
STATE_PATH = LEGACY_ROOT / "state.json"


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {"next_item_id": 1}
    return _read_json(STATE_PATH)


def _save_state(state: Dict[str, Any]) -> None:
    _write_json(STATE_PATH, state)


def _next_item_id() -> int:
    state = _load_state()
    next_id = int(state.get("next_item_id", 1))
    state["next_item_id"] = next_id + 1
    _save_state(state)
    return next_id


def _item_filename(item_id: int) -> str:
    return f"{_ITEM_PREFIX}_{item_id:09d}.json"


def _item_path(item_id: int) -> Path:
    return ITEMS_DIR / _item_filename(item_id)


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass
class LegacyItemRecord:
    item_id: int
    source_id: str
    canonical_url: str
    content_hash: str
    manifest_path: str
    collected_at: datetime
    fields: Dict[str, Any]

    def to_storage_dict(self) -> Dict[str, Any]:
        return {
            "id": self.item_id,
            "source_id": self.source_id,
            "canonical_url": self.canonical_url,
            "content_hash": self.content_hash,
            "manifest_path": self.manifest_path,
            "collected_at": self.collected_at.isoformat(),
            "fields": self.fields,
        }


def _item_from_data(data: Dict[str, Any]) -> LegacyItemRecord:
    return LegacyItemRecord(
        item_id=int(data["id"]),
        source_id=data["source_id"],
        canonical_url=data["canonical_url"],
        content_hash=data["content_hash"],
        manifest_path=data["manifest_path"],
        collected_at=_parse_datetime(data["collected_at"]),
        fields=dict(data.get("fields", {})),
    )


class LegacyConnection:
    def close(self) -> None:  # pragma: no cover - placeholder for API parity
        return None


@contextmanager
def get_connection() -> Iterable[LegacyConnection]:
    conn = LegacyConnection()
    try:
        yield conn
    finally:
        conn.close()


def _ensure_db_placeholder() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.touch()


def init_db() -> None:
    _ensure_dir(ITEMS_DIR)
    _ensure_dir(EVIDENCE_DIR)
    if not STATE_PATH.exists():
        _save_state({"next_item_id": 1})
    _ensure_db_placeholder()


def reset_db() -> None:
    if LEGACY_ROOT.exists():
        shutil.rmtree(LEGACY_ROOT)
    _ensure_dir(ITEMS_DIR)
    _ensure_dir(EVIDENCE_DIR)
    _save_state({"next_item_id": 1})
    if DB_PATH.exists():
        DB_PATH.unlink()


def _iter_items(source_id: Optional[str] = None) -> Iterator[LegacyItemRecord]:
    for path in sorted(ITEMS_DIR.glob("*.json")):
        record = _item_from_data(_read_json(path))
        if source_id and record.source_id != source_id:
            continue
        yield record


def item_exists(conn: LegacyConnection, source_id: str, content_hash: str) -> bool:
    return any(
        record.content_hash == content_hash
        for record in _iter_items(source_id=source_id)
    )


def insert_item(
    conn: LegacyConnection,
    source_id: str,
    canonical_url: str,
    content_hash: str,
    collected_at: datetime,
    manifest_path: str,
) -> int:
    item_id = _next_item_id()
    record = LegacyItemRecord(
        item_id=item_id,
        source_id=source_id,
        canonical_url=canonical_url,
        content_hash=content_hash,
        manifest_path=manifest_path,
        collected_at=collected_at,
        fields={},
    )
    _write_json(_item_path(item_id), record.to_storage_dict())
    return item_id


def insert_item_kv(
    conn: LegacyConnection,
    item_id: int,
    field_name: str,
    field_type: str,
    value_string: Optional[str] = None,
    value_numeric: Optional[float] = None,
    value_timestamp: Optional[datetime] = None,
) -> None:
    path = _item_path(item_id)
    if not path.exists():
        raise FileNotFoundError(f"Item {item_id} not found for KV insertion")
    data = _read_json(path)
    fields = data.setdefault("fields", {})
    if value_timestamp is not None:
        value = value_timestamp.isoformat()
    elif value_numeric is not None:
        value = value_numeric
    else:
        value = value_string
    fields[field_name] = value
    _write_json(path, data)


def fetch_items_by_source(conn: LegacyConnection, source_id: str) -> List[Dict[str, Any]]:
    items = [
        {"id": record.item_id, "manifest_path": record.manifest_path}
        for record in _iter_items(source_id=source_id)
    ]
    items.sort(key=lambda entry: entry["id"])
    return items


def list_legacy_items(
    *,
    source_id: Optional[str] = None,
    collected_from: Optional[str] = None,
    collected_to: Optional[str] = None,
) -> List[LegacyItemRecord]:
    lower = _parse_datetime(collected_from) if collected_from else None
    upper = _parse_datetime(collected_to) if collected_to else None
    results: List[LegacyItemRecord] = []
    for record in _iter_items(source_id=source_id):
        if lower and record.collected_at < lower:
            continue
        if upper and record.collected_at > upper:
            continue
        results.append(record)
    results.sort(key=lambda rec: rec.collected_at, reverse=True)
    return results


def _as_int(item_id: Union[str, int]) -> int:
    if isinstance(item_id, int):
        return item_id
    return int(str(item_id))


def get_legacy_item(item_id: Union[str, int]) -> Optional[LegacyItemRecord]:
    numeric_id = _as_int(item_id)
    path = _item_path(numeric_id)
    if not path.exists():
        return None
    return _item_from_data(_read_json(path))


def _evidence_path(evidence_id: str) -> Path:
    safe_id = evidence_id.replace("/", "_")
    return EVIDENCE_DIR / f"{_EVIDENCE_PREFIX}_{safe_id}.json"


def insert_evidence_record(conn: LegacyConnection, record: EvidenceRecord) -> None:
    payload = {
        "evidence_id": record.evidence_id,
        "source_id": record.source_id,
        "item_id": record.item_id,
        "item_version_id": record.item_version_id,
        "evidence_type": record.evidence_type,
        "collected_at": normalize_timestamp(record.collected_at).isoformat(),
        "ingested_at": normalize_timestamp(record.ingested_at).isoformat(),
        "storage_key": record.storage_key,
        "hash_alg": record.hash_alg,
        "hash_value": record.hash_value,
        "lgpd_tags": list(record.lgpd_tags),
        "size_bytes": record.size_bytes,
        "checksum_status": record.checksum_status,
    }
    _write_json(_evidence_path(record.evidence_id), payload)


def fetch_evidence_record(conn: LegacyConnection, evidence_id: str) -> Optional[EvidenceRecord]:
    path = _evidence_path(evidence_id)
    if not path.exists():
        return None
    data = _read_json(path)
    return EvidenceRecord(
        evidence_id=data["evidence_id"],
        source_id=data["source_id"],
        evidence_type=data["evidence_type"],
        collected_at=_parse_datetime(data["collected_at"]),
        ingested_at=_parse_datetime(data["ingested_at"]),
        storage_key=data["storage_key"],
        hash_alg=data["hash_alg"],
        hash_value=data["hash_value"],
        lgpd_tags=tuple(data.get("lgpd_tags", ())),
        size_bytes=int(data["size_bytes"]),
        checksum_status=data["checksum_status"],
        item_id=data.get("item_id"),
        item_version_id=data.get("item_version_id"),
    )


__all__ = [
    "LegacyItemRecord",
    "fetch_evidence_record",
    "fetch_items_by_source",
    "get_connection",
    "get_legacy_item",
    "init_db",
    "insert_evidence_record",
    "insert_item",
    "insert_item_kv",
    "item_exists",
    "list_legacy_items",
    "reset_db",
]
