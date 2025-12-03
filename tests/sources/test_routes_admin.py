from fastapi.testclient import TestClient

from inspectah.api import build_app


def test_sources_crud_api():
    client = TestClient(build_app())
    payload = {
        "slug": "api-source",
        "name": "Fonte API",
        "description": "",
        "type": "news_rss",
        "category": "official",
        "themes": ["politica"],
        "info_types": ["news"],
        "protocol": "https",
        "format": "rss",
        "endpoint": "https://example.com/rss",
        "auth_type": "none",
        "auth_config": {},
        "request_params": {},
        "headers": {},
        "frequency": "daily",
        "timeout_ms": 5000,
        "retry_policy": {},
        "parsing_config": {},
        "redundancy_group": None,
        "redundancy_role": None,
        "meta": {},
        "created_by": "tester",
    }
    resp = client.post("/admin/sources", json=payload)
    assert resp.status_code == 201
    source_id = resp.json()["source"]["id"]

    resp_list = client.get("/admin/sources")
    assert resp_list.status_code == 200
    assert any(src["id"] == source_id for src in resp_list.json()["sources"])

    resp_detail = client.get(f"/admin/sources/{source_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["source"]["id"] == source_id

    resp_hc = client.post(f"/admin/sources/{source_id}/healthcheck")
    assert resp_hc.status_code in (200, 500, 502, 504)


def test_manual_ingestion_endpoint_runs_and_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("INSPECTAH_S21_DB_PATH", str(tmp_path / "sources.sqlite"))
    monkeypatch.setenv("INSPECTAH_S22_DB_PATH", str(tmp_path / "ingestion.sqlite"))
    monkeypatch.setenv("INSPECTAH_AUDIT_LOG_BASE", str(tmp_path / "audit"))
    client = TestClient(build_app())

    payload = {
        "slug": "api-source-manual",
        "name": "Fonte Manual",
        "description": "",
        "type": "news_rss",
        "category": "official",
        "themes": ["politica"],
        "info_types": ["news"],
        "protocol": "https",
        "format": "rss",
        "endpoint": "https://example.com/rss",
        "auth_type": "none",
        "auth_config": {},
        "request_params": {},
        "headers": {},
        "frequency": "daily",
        "timeout_ms": 5000,
        "retry_policy": {},
        "parsing_config": {},
        "redundancy_group": None,
        "redundancy_role": None,
        "meta": {},
        "created_by": "tester",
    }
    resp = client.post("/admin/sources", json=payload)
    assert resp.status_code == 201
    source_id = resp.json()["source"]["id"]

    run_resp = client.post(f"/admin/sources/{source_id}/ingestion/run")
    assert run_resp.status_code == 200
    data = run_resp.json()
    assert data["run_id"]
    assert data["status"] in ("RUNNING", "SUCCESS")

    audit_log = tmp_path / "audit" / "sources_admin_actions.log"
    assert audit_log.exists()
    content = audit_log.read_text(encoding="utf-8")
    assert "manual_run" in content
