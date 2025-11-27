import json
from pathlib import Path

from fastapi.testclient import TestClient

from inspectah.api import app


def test_cases_list_and_details():
    client = TestClient(app)
    resp = client.get("/api/cases")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    slugs = {case["case_id"] for case in data}
    assert "inflacao_br_2024" in slugs
    detail = client.get("/api/cases/inflacao_br_2024")
    assert detail.status_code == 200
    body = detail.json()
    assert body["case_id"] == "inflacao_br_2024"
    assert body["claims"]
    assert "debunk_summary" in body


def test_collections_list_and_detail():
    client = TestClient(app)
    resp = client.get("/api/cases/collections")
    assert resp.status_code == 200
    data = resp.json()
    assert any(c["collection_id"] == "economia_2024" for c in data)
    detail = client.get("/api/cases/collections/economia_2024")
    assert detail.status_code == 200
    body = detail.json()
    assert "inflacao_br_2024" in body["case_ids"]
