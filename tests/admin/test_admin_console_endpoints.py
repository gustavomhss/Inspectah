from __future__ import annotations

from fastapi.testclient import TestClient

from inspectah.api import build_app


def _client():
    app = build_app()
    return TestClient(app)


def test_admin_sources_list_returns_200():
    client = _client()
    resp = client.get("/admin/sources")
    assert resp.status_code == 200
    data = resp.json()
    # legacy contract: payload possui chave "sources"
    assert isinstance(data, dict)
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_admin_agents_list_returns_200():
    client = _client()
    resp = client.get("/admin/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
