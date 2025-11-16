from __future__ import annotations
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Sequence, Tuple


ALLOWED_LGPD_TAGS: Tuple[str, ...] = (
    "lgpd.anonymized",
    "lgpd.personal",
    "lgpd.personal_sensitive",
    "lgpd.public_interest",
)

HASH_ALGORITHM = "sha256"
CHECKSUM_OK = "ok"
STORAGE_SUFFIX = ".bin"
_SOURCE_SEGMENT_RE = re.compile(r"[^a-zA-Z0-9_-]+")


class EvidenceVaultError(RuntimeError):
    """Raised when evidence operations fail due to business constraints."""


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_id: str
    evidence_type: str
    collected_at: datetime
    ingested_at: datetime
    storage_key: str
    hash_alg: str
    hash_value: str
    lgpd_tags: Tuple[str, ...]
    size_bytes: int
    checksum_status: str
    item_id: int | None = None
    item_version_id: str | None = None


@dataclass(frozen=True)
class EvidenceFetchResult:
    record: EvidenceRecord
    payload: bytes | None


def normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def generate_evidence_id() -> str:
    if hasattr(uuid, "uuid7"):
        return str(uuid.uuid7())
    return str(uuid.uuid4())


def validate_lgpd_tags(tags: Sequence[str]) -> Tuple[str, ...]:
    if not tags:
        raise EvidenceVaultError("At least one LGPD tag is required.")
    normalized = tuple(sorted({tag.strip() for tag in tags}))
    for tag in normalized:
        if tag not in ALLOWED_LGPD_TAGS:
            raise EvidenceVaultError(f"LGPD tag '{tag}' is not allowed.")
    return normalized


def build_storage_key(source_id: str, evidence_id: str, collected_at: datetime) -> str:
    collected = normalize_timestamp(collected_at)
    safe_source = _SOURCE_SEGMENT_RE.sub("_", source_id).strip("_") or "source"
    return (
        f"{safe_source}/"
        f"{collected:%Y/%m/%d}/"
        f"{evidence_id.replace('-', '')}{STORAGE_SUFFIX}"
    )


def record_from_row(row: Mapping[str, object]) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=row["id"],
        source_id=row["source_id"],
        evidence_type=row["evidence_type"],
        collected_at=normalize_timestamp(datetime.fromisoformat(row["collected_at"])),
        ingested_at=normalize_timestamp(datetime.fromisoformat(row["ingested_at"])),
        storage_key=row["storage_key"],
        hash_alg=row["hash_alg"],
        hash_value=row["hash_value"],
        lgpd_tags=tuple(json.loads(row["lgpd_tags"])),
        size_bytes=int(row["size_bytes"]),
        checksum_status=row["checksum_status"],
        item_id=row.get("item_id"),
        item_version_id=row.get("item_version_id"),
    )


def serialize_lgpd_tags(tags: Tuple[str, ...]) -> str:
    return json.dumps(list(tags))
