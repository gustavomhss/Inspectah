from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.admin_agent_flows_routes import router as flows_router, get_service as default_get_service
from app.agents.flows.service import AgentFlowService
from scripts.dev_seed_agent_flows import SEED_FLOWS, upsert_seed_flows


def _service(tmp_path: Path) -> AgentFlowService:
    return AgentFlowService(db_path=tmp_path / "flows_api.sqlite")


def _app(service: AgentFlowService) -> TestClient:
    app = FastAPI()

    def override_service():
        return service

    app.dependency_overrides[default_get_service] = override_service
    app.include_router(flows_router)
    return TestClient(app)


def _payload():
    return {
        "domain_key": "politics_news",
        "name": "Politics flow",
        "description": "Base flow",
        "is_active": True,
        "change_reason": "initial setup",
        "created_by": "tester",
        "steps": [
            {"position": 1, "agent_role": "interpreter", "params": {"strict_mode": True, "agent_id": "ag_interp"}},
            {"position": 2, "agent_role": "classifier", "params": {"committee_id": "c1", "agent_id": "ag_classifier"}},
            {"position": 3, "agent_role": "decision_maker", "params": {"threshold": 0.7, "agent_id": "ag_decider"}},
        ],
    }


def test_create_and_fetch_flow(tmp_path: Path):
    service = _service(tmp_path)
    client = _app(service)

    res = client.post("/admin/agent-flows", json=_payload())
    assert res.status_code == 201, res.text
    flow_id = res.json()["id"]

    res_get = client.get(f"/admin/agent-flows/{flow_id}")
    assert res_get.status_code == 200
    assert res_get.json()["domain_key"] == "politics_news"

    res_domain = client.get("/admin/agent-flows/by-domain/politics_news")
    assert res_domain.status_code == 200
    assert res_domain.json()["id"] == flow_id

    res_list = client.get("/admin/agent-flows")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1


def test_validation_error_on_invalid_flow(tmp_path: Path):
    service = _service(tmp_path)
    client = _app(service)

    bad_payload = _payload()
    bad_payload["steps"] = [
        {"position": 1, "agent_role": "interpreter"},
        {"position": 2, "agent_role": "analyst"},
    ]
    res = client.post("/admin/agent-flows", json=bad_payload)
    assert res.status_code == 422
    detail = res.json().get("detail", {})
    assert "errors" in detail


def test_update_flow(tmp_path: Path):
    service = _service(tmp_path)
    client = _app(service)

    res = client.post("/admin/agent-flows", json=_payload())
    flow_id = res.json()["id"]

    update_payload = _payload()
    update_payload["name"] = "Updated flow"
    update_payload["change_reason"] = "tuning"
    update_payload["steps"][1]["params"] = {"committee_id": "c2"}

    res_put = client.put(f"/admin/agent-flows/{flow_id}", json=update_payload)
    assert res_put.status_code == 200, res_put.text
    assert res_put.json()["name"] == "Updated flow"
    assert res_put.json()["steps"][1]["params"]["committee_id"] == "c2"


def test_domain_uniqueness(tmp_path: Path):
    service = _service(tmp_path)
    client = _app(service)

    res = client.post("/admin/agent-flows", json=_payload())
    assert res.status_code == 201

    res_dup = client.post("/admin/agent-flows", json=_payload())
    assert res_dup.status_code == 400


def test_seed_flows_are_listed(tmp_path: Path):
    service = _service(tmp_path)
    upsert_seed_flows(service)
    client = _app(service)

    res = client.get("/admin/agent-flows")
    assert res.status_code == 200
    payloads = res.json()
    assert len(payloads) == len(SEED_FLOWS)
    returned_domains = {f["domain_key"] for f in payloads}
    assert {seed.domain_key for seed in SEED_FLOWS}.issubset(returned_domains)
