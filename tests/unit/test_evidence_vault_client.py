from __future__ import annotations
from pathlib import Path

import pytest

from inspectah import config as inspectah_config
from inspectah.evidence_vault.client import (
    EvidenceStoreError,
    LocalEvidenceStoreClient,
    get_evidence_store_client,
)
from inspectah.evidence_vault.settings import EvidenceStoreConfig


def _build_config(tmp_path: Path, *, region: str = "sa-east-1") -> EvidenceStoreConfig:
    return EvidenceStoreConfig(
        backend="local_stub",
        bucket="unit-test-bucket",
        region=region,
        kms_key_alias="alias/unit-test",
        endpoint_url=None,
        default_ttl_seconds=900,
        local_root=tmp_path,
    )


def test_local_client_stores_and_recovers_bytes_without_leaking_payload(tmp_path, caplog):
    client = LocalEvidenceStoreClient(_build_config(tmp_path))
    payload = b"<secret-payload>"

    caplog.set_level("INFO")
    handle = client.put_object("foo/bar.bin", payload, metadata={"hash": "abc"})
    stored = (tmp_path / "foo" / "bar.bin").read_bytes()

    assert stored == payload
    assert "foo/bar.bin" in caplog.text
    assert "<secret-payload>" not in caplog.text

    fetched = client.get_object(handle.key)
    assert fetched == payload
    assert handle.bucket == "unit-test-bucket"
    assert handle.region == "sa-east-1"


def test_local_client_rejects_path_traversal(tmp_path):
    client = LocalEvidenceStoreClient(_build_config(tmp_path))
    with pytest.raises(EvidenceStoreError):
        client.put_object("../evil.bin", b"x")


def test_local_client_requires_sa_east_region(tmp_path):
    config = _build_config(tmp_path, region="us-east-1")
    with pytest.raises(EvidenceStoreError):
        LocalEvidenceStoreClient(config)


def test_load_settings_honors_env_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("INSPECTAH_VAULT_BUCKET", "override-bucket")
    monkeypatch.setenv("INSPECTAH_VAULT_KMS_KEY", "alias/override")
    monkeypatch.setenv("INSPECTAH_VAULT_LOCAL_ROOT", str(tmp_path))
    settings = inspectah_config.load_evidence_vault_settings()
    assert settings.bucket == "override-bucket"
    assert settings.kms_key_alias == "alias/override"
    assert settings.local_root == tmp_path


def test_get_evidence_store_client_uses_global_settings():
    client = get_evidence_store_client()
    assert isinstance(client, LocalEvidenceStoreClient)
