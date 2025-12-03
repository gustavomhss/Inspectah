from __future__ import annotations
from types import SimpleNamespace

import pytest

from inspectah.ingest.pipeline import run_ingest_pipeline


def test_run_ingest_pipeline_calls_watcher(monkeypatch):
    captured = {}
    plan_seen = {}

    def fake_get_source_config(source_id: str):
        return SimpleNamespace(id=source_id, type="rss")

    def fake_run_once(source_id: str, use_fixture: bool, fixture_path: str | None):
        captured["source_id"] = source_id
        captured["use_fixture"] = use_fixture
        captured["fixture_path"] = fixture_path
        return 3

    def fake_plan(domain_key: str):
        plan_seen["domain_key"] = domain_key
        return {"flow_id": "f1", "domain_key": domain_key, "used_fallback": False, "steps": []}

    monkeypatch.setattr("inspectah.ingest.pipeline.get_source_config", fake_get_source_config)
    monkeypatch.setattr("inspectah.ingest.pipeline.run_once_for_source", fake_run_once)
    monkeypatch.setattr("inspectah.ingest.pipeline.get_executable_flow_plan", fake_plan)

    result = run_ingest_pipeline(
        "rss_news_minimal",
        use_fixture=True,
        fixture_path="tests/fixtures/rss_sample.xml",
    )

    assert result.items_ingested == 3
    assert plan_seen == {"domain_key": "rss_news_minimal"}
    assert captured == {
        "source_id": "rss_news_minimal",
        "use_fixture": True,
        "fixture_path": "tests/fixtures/rss_sample.xml",
    }


def test_run_ingest_pipeline_rejects_unknown_type(monkeypatch):
    def fake_get_source_config(source_id: str):
        return SimpleNamespace(id=source_id, type="sql")

    monkeypatch.setattr("inspectah.ingest.pipeline.get_source_config", fake_get_source_config)
    with pytest.raises(ValueError):
        run_ingest_pipeline("sql_source")
