from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from inspectah.api import app


FLOW_PATH = Path("out/runtime/console_agents_flow.json")


@pytest.fixture(autouse=True)
def clean_flow_file():
    if FLOW_PATH.exists():
        FLOW_PATH.unlink()
    yield
    if FLOW_PATH.exists():
        FLOW_PATH.unlink()


def test_console_flow_returns_empty_when_absent():
    client = TestClient(app)
    resp = client.get("/api/console/agents/flow")
    assert resp.status_code == 200
    assert resp.json() == []


def test_console_flow_persists_and_reads_payload():
    client = TestClient(app)
    payload = [{"agent_id": "debunker_v1"}, {"agent_id": "classifier_v1"}]

    put_resp = client.put("/api/console/agents/flow", json=payload)
    assert put_resp.status_code == 200
    assert put_resp.json() == payload

    get_resp = client.get("/api/console/agents/flow")
    assert get_resp.status_code == 200
    assert get_resp.json() == payload


def test_invalid_json_returns_empty_list():
    FLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
    FLOW_PATH.write_text("{{ lixo nao-json", encoding="utf-8")

    client = TestClient(app)
    resp = client.get("/api/console/agents/flow")
    assert resp.status_code == 200
    assert resp.json() == []
