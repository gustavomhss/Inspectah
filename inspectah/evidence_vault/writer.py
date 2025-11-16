from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

from ..models import get_connection, insert_evidence_record
from .client import EvidenceStoreClient, get_evidence_store_client
from .metadata import (
    CHECKSUM_OK,
    HASH_ALGORITHM,
    EvidenceRecord,
    EvidenceVaultError,
    build_storage_key,
    generate_evidence_id,
    normalize_timestamp,
    validate_lgpd_tags,
)


def _resolve_payload(*, payload_bytes: Optional[bytes], payload_path: Optional[Path]) -> bytes:
    if payload_bytes and payload_path:
        raise EvidenceVaultError("Provide either payload_bytes or payload_path, not both.")
    if payload_bytes is None and payload_path is None:
        raise EvidenceVaultError("Payload is required to store evidence.")
    if payload_path is not None:
        if not payload_path.exists():
            raise EvidenceVaultError(f"Payload path {payload_path} does not exist.")
        return payload_path.read_bytes()
    return payload_bytes  # type: ignore[return-value]


def store_evidence(
    *,
    source_id: str,
    evidence_type: str,
    collected_at: datetime,
    lgpd_tags: Sequence[str],
    payload_bytes: Optional[bytes] = None,
    payload_path: Optional[Path] = None,
    item_id: Optional[int] = None,
    item_version_id: Optional[str] = None,
    client: Optional[EvidenceStoreClient] = None,
) -> EvidenceRecord:
    collected = normalize_timestamp(collected_at)
    ingested = normalize_timestamp(datetime.now(timezone.utc))
    tags = validate_lgpd_tags(lgpd_tags)
    payload = _resolve_payload(payload_bytes=payload_bytes, payload_path=payload_path)
    evidence_id = generate_evidence_id()
    storage_key = build_storage_key(source_id, evidence_id, collected)
    digest = hashlib.new(HASH_ALGORITHM)
    digest.update(payload)
    hash_value = digest.hexdigest()
    client_to_use = client or get_evidence_store_client()
    client_to_use.put_object(
        storage_key,
        payload,
        metadata={
            "evidence_id": evidence_id,
            "hash_alg": HASH_ALGORITHM,
            "hash_value": hash_value,
        },
    )
    record = EvidenceRecord(
        evidence_id=evidence_id,
        source_id=source_id,
        evidence_type=evidence_type,
        collected_at=collected,
        ingested_at=ingested,
        storage_key=storage_key,
        hash_alg=HASH_ALGORITHM,
        hash_value=hash_value,
        lgpd_tags=tags,
        size_bytes=len(payload),
        checksum_status=CHECKSUM_OK,
        item_id=item_id,
        item_version_id=item_version_id,
    )
    with get_connection() as conn:
        insert_evidence_record(conn, record)
    return record


__all__ = ["store_evidence"]
