from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from inspectah.evidence_vault import metadata
from inspectah.evidence_vault.cli import main as cli_main
from inspectah.evidence_vault.metadata import EvidenceRecord, EvidenceFetchResult


class DummyRecord(EvidenceRecord):
    def __init__(self):
        super().__init__(
            evidence_id="ev_123",
            source_id="source_x",
            evidence_type="http_snapshot",
            collected_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ingested_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            storage_key="source_x/2024/01/01/ev_123.bin",
            hash_alg=metadata.HASH_ALGORITHM,
            hash_value="abcd",
            lgpd_tags=("lgpd.personal",),
            size_bytes=4,
            checksum_status=metadata.CHECKSUM_OK,
        )


def test_cli_write_prints_json(monkeypatch, tmp_path, capsys):
    payload = tmp_path / "payload.bin"
    payload.write_text("data", encoding="utf-8")
    dummy_record = DummyRecord()

    def fake_store(**kwargs):
        assert kwargs["source_id"] == "src"
        return dummy_record

    monkeypatch.setattr("inspectah.evidence_vault.cli.store_evidence", fake_store)
    exit_code = cli_main(
        [
            "write",
            "--file",
            str(payload),
            "--source-id",
            "src",
            "--evidence-type",
            "http_snapshot",
            "--lgpd-tag",
            "lgpd.personal",
        ]
    )
    assert exit_code == 0
    stdout = capsys.readouterr().out.strip()
    parsed = json.loads(stdout)
    assert parsed["evidence_id"] == "ev_123"
    assert parsed["hash_value"] == "abcd"


def test_cli_read_prints_metadata(monkeypatch, capsys):
    dummy_record = DummyRecord()

    def fake_fetch(evidence_id: str, with_payload: bool = False):
        assert evidence_id == "ev_123"
        return EvidenceFetchResult(record=dummy_record, payload=None)

    monkeypatch.setattr("inspectah.evidence_vault.cli.fetch_evidence", fake_fetch)
    exit_code = cli_main(["read", "--id", "ev_123"])
    assert exit_code == 0
    stdout = capsys.readouterr().out.strip()
    parsed = json.loads(stdout)
    assert parsed["payload_loaded"] is False
    assert parsed["evidence_type"] == "http_snapshot"
