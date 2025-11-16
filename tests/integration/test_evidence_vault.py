from __future__ import annotations
from datetime import datetime, timezone

import pytest

from inspectah import config as inspectah_config
from inspectah.evidence_vault.client import (
    EvidenceStoreConfig,
)
from inspectah.evidence_vault import metadata
from inspectah.evidence_vault.reader import fetch_evidence
from inspectah.evidence_vault.writer import store_evidence
from inspectah.models import (
    fetch_evidence_record,
    get_connection,
    init_db,
    reset_db,
)


@pytest.fixture(autouse=True)
def isolated_vault(monkeypatch, tmp_path):
    reset_db()
    init_db()
    cfg = EvidenceStoreConfig(
        backend="local_stub",
        bucket="integration-bucket",
        region="sa-east-1",
        kms_key_alias="alias/integration",
        endpoint_url=None,
        default_ttl_seconds=600,
        local_root=tmp_path / "vault",
    )
    from inspectah.evidence_vault import client as client_module

    monkeypatch.setattr(inspectah_config, "EVIDENCE_VAULT_SETTINGS", cfg)
    monkeypatch.setattr(client_module, "EVIDENCE_VAULT_SETTINGS", cfg)
    cfg.local_root.mkdir(parents=True, exist_ok=True)
    yield cfg
    reset_db()


def test_write_and_read_metadata():
    payload = b"integration-payload"
    collected = datetime(2024, 2, 20, 14, 5, tzinfo=timezone.utc)
    record = store_evidence(
        source_id="rss_news_minimal",
        evidence_type="http_snapshot",
        collected_at=collected,
        lgpd_tags=["lgpd.personal"],
        payload_bytes=payload,
    )

    with get_connection() as conn:
        stored = fetch_evidence_record(conn, record.evidence_id)
    assert stored is not None
    assert stored.hash_value == record.hash_value
    assert stored.lgpd_tags == ("lgpd.personal",)
    assert stored.storage_key.endswith(".bin")

    result = fetch_evidence(record.evidence_id)
    assert result.payload is None
    assert result.record.hash_value == record.hash_value


def test_fetch_with_payload_returns_bytes():
    payload = b"binary-data-v1"
    record = store_evidence(
        source_id="rss_news_minimal",
        evidence_type="json_blob",
        collected_at=datetime(2024, 2, 20, tzinfo=timezone.utc),
        lgpd_tags=["lgpd.personal"],
        payload_bytes=payload,
    )

    result = fetch_evidence(record.evidence_id, with_payload=True)
    assert result.payload == payload
    assert result.record.size_bytes == len(payload)
    assert result.record.checksum_status == metadata.CHECKSUM_OK
