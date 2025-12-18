from __future__ import annotations

from fastapi.testclient import TestClient

from inspectah.api import build_app


def _client() -> TestClient:
    app = build_app()
    assert app is not None, "FastAPI app não criado"
    return TestClient(app)


def test_list_sources_and_detail():
    client = _client()
    resp = client.get("/admin/sources")
    assert resp.status_code == 200
    payload = resp.json()
    assert "sources" in payload
    assert isinstance(payload["sources"], list)

    # Skip detail test if no sources (CI environment may have empty DB)
    if not payload["sources"]:
        return

    first_id = payload["sources"][0]["id"]
    detail = client.get(f"/admin/sources/{first_id}")
    assert detail.status_code == 200
    data = detail.json()
    assert data.get("source", {}).get("id") == first_id
    assert "status" in data.get("source", {})


def test_list_cases_and_detail():
    client = _client()
    resp = client.get("/admin/cases")
    assert resp.status_code == 200
    payload = resp.json()
    assert "cases" in payload
    assert isinstance(payload["cases"], list)

    if payload["cases"]:
        first_id = payload["cases"][0]["id"]
        detail = client.get(f"/admin/cases/{first_id}")
        assert detail.status_code == 200
        data = detail.json()
        assert data.get("case", {}).get("id") == first_id
    else:
        # still ensure 404 path works
        missing = client.get("/admin/cases/nonexistent-case")
        assert missing.status_code == 404


def test_health_endpoint():
    client = _client()
    resp = client.get("/admin/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert "health" in payload
    health = payload["health"]
    for key in [
        "sources_total",
        "sources_healthy",
        "sources_degraded",
        "cases_total",
        "cases_attention",
        "cases_stable",
    ]:
        assert key in health


def test_sources_404():
    client = _client()
    resp = client.get("/admin/sources/nonexistent-source")
    assert resp.status_code == 404
