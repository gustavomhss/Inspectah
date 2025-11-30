import json
import os
from pathlib import Path

from app.sources.audit import record_admin_action
from app.sources import service
from app.sources.models import SourceState
from app.sources.schemas import SourceCreate


def test_record_admin_action_writes_json(tmp_path):
    base = tmp_path / "audit"
    path = record_admin_action("create", "src-1", "tester", {"foo": "bar"}, base_dir=base)
    assert path.exists()
    content = path.read_text(encoding="utf-8").strip().splitlines()
    assert content, "log deve ter ao menos uma linha"
    entry = json.loads(content[-1])
    assert entry["action"] == "create"
    assert entry["source_id"] == "src-1"
    assert entry["user"] == "tester"
    assert entry["meta"]["foo"] == "bar"
    assert entry["timestamp"]


def test_change_state_logs_admin_action(tmp_path, monkeypatch):
    monkeypatch.setenv("INSPECTAH_S21_DB_PATH", str(tmp_path / "db.sqlite"))
    monkeypatch.setenv("INSPECTAH_AUDIT_LOG_BASE", str(tmp_path / "audit_logs"))
    payload = SourceCreate(
        slug="audit-src",
        name="Audit Source",
        type="news_rss",
        category="general",
        created_by="tester",
        description="",
        endpoint="https://example",
        themes=[],
        info_types=[],
        refresh_interval=60,
    )
    src = service.create_source(payload)
    updated = service.change_source_state(src.id, SourceState.ACTIVE, "teste", "tester")
    assert updated is not None
    log_path = Path(os.environ["INSPECTAH_AUDIT_LOG_BASE"]) / "sources_admin_actions.log"
    assert log_path.exists()
    last_line = log_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    entry = json.loads(last_line)
    assert entry["action"] == "change_source_state"
    assert entry["source_id"] == src.id
    assert entry["user"] == "tester"
    assert entry["meta"]["target_state"] == "ACTIVE"
