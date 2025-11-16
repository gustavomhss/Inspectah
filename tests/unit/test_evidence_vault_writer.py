from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import pytest

from inspectah.evidence_vault.metadata import EvidenceVaultError
from inspectah.evidence_vault.writer import store_evidence
from inspectah.evidence_vault.client import (
    EvidenceObjectHandle,
    EvidenceStoreClient,
    EvidenceStoreConfig,
)
from inspectah.models import (
    get_connection,
    init_db,
    reset_db,
    fetch_evidence_record,
)


class FakeEvidenceClient(EvidenceStoreClient):
    def __init__(self, root: Path):
        super().__init__(
            EvidenceStoreConfig(
                backend="fake",
                bucket="unit-fake",
                region="sa-east-1",
                kms_key_alias="alias/unit-test",
                endpoint_url=None,
                default_ttl_seconds=900,
                local_root=root,
            )
        )
        self.objects: Dict[str, bytes] = {}

    def put_object(self, key: str, data: bytes, *, metadata: Dict[str, str] | None = None) -> EvidenceObjectHandle:
        self.objects[key] = data
        return EvidenceObjectHandle(
            bucket=self.config.bucket,
            key=key,
            region=self.config.region,
            size_bytes=len(data),
            kms_key_alias=self.config.kms_key_alias,
        )

    def get_object(self, key: str) -> bytes:
        return self.objects[key]


@pytest.fixture(autouse=True)
def _clean_db():
    reset_db()
    init_db()
    yield
    reset_db()


def test_store_evidence_persists_metadata_and_hash(tmp_path):
    client = FakeEvidenceClient(tmp_path)
    payload = b"evidence payload"
    collected = datetime(2024, 1, 5, tzinfo=timezone.utc)

    record = store_evidence(
        source_id="rss_news_minimal",
        evidence_type="http_snapshot",
        collected_at=collected,
        lgpd_tags=["lgpd.personal"],
        payload_bytes=payload,
        client=client,
    )

    assert record.hash_value == hashlib.sha256(payload).hexdigest()
    assert record.size_bytes == len(payload)
    assert record.lgpd_tags == ("lgpd.personal",)
    assert record.storage_key in client.objects

    with get_connection() as conn:
        stored = fetch_evidence_record(conn, record.evidence_id)
    assert stored is not None
    assert stored.hash_value == record.hash_value


def test_store_evidence_rejects_invalid_tags(tmp_path):
    client = FakeEvidenceClient(tmp_path)
    with pytest.raises(EvidenceVaultError):
        store_evidence(
            source_id="rss_news_minimal",
            evidence_type="http_snapshot",
            collected_at=datetime.now(timezone.utc),
            lgpd_tags=["invalid.tag"],
            payload_bytes=b"x",
            client=client,
        )
