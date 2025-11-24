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
