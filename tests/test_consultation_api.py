from fastapi.testclient import TestClient

from inspectah.api import build_app


def test_post_consultation_returns_payload():
    app = build_app()
    client = TestClient(app)
    response = client.post("/api/consultation", json={"question": "Há risco climático hoje?"})
    assert response.status_code == 200
    data = response.json()
    assert data.get("answer")
    assert data.get("risk_level")
    assert isinstance(data.get("evidences"), list)
    assert data.get("request_id")


def test_post_consultation_handles_bad_domain():
    app = build_app()
    client = TestClient(app)
    response = client.post("/api/consultation", json={"question": "???"})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("risk_level") == "unknown"
    assert payload.get("insufficient_data") is True
    assert isinstance(payload.get("evidences"), list)
    assert payload.get("evidences") == [] or all(
        "???" not in (item.get("description") or "") for item in payload.get("evidences", [])
    )
