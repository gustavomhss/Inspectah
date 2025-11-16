from __future__ import annotations
from typing import Optional

from ..models import get_connection, fetch_evidence_record
from .client import EvidenceStoreClient, get_evidence_store_client
from .metadata import EvidenceFetchResult, EvidenceVaultError


def fetch_evidence(
    evidence_id: str,
    *,
    with_payload: bool = False,
    client: Optional[EvidenceStoreClient] = None,
) -> EvidenceFetchResult:
    if not evidence_id:
        raise EvidenceVaultError("evidence_id is required.")
    with get_connection() as conn:
        record = fetch_evidence_record(conn, evidence_id)
    if record is None:
        raise EvidenceVaultError(f"Evidence {evidence_id} not found.")
    payload: bytes | None = None
    if with_payload:
        client_to_use = client or get_evidence_store_client()
        payload = client_to_use.get_object(record.storage_key)
    return EvidenceFetchResult(record=record, payload=payload)


__all__ = ["fetch_evidence"]
