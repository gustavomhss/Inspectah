from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents.models import AgentLayer, AgentProfile, AgentRole, AgentStatus, CommitteePolicy, AgentRunStatus
from app.agents.repository import AgentsRepository
from app.agents.service import create_agent_profile
from app.api.agents.routes_admin import router as agents_router, get_repo as default_get_repo


def _make_repo(tmp_path: Path) -> AgentsRepository:
    db_path = tmp_path / "agents.sqlite"
    return AgentsRepository(db_path=db_path)


def _seed_agent(repo: AgentsRepository, name: str, role: AgentRole, layer: AgentLayer) -> AgentProfile:
    agent = AgentProfile(
        id=f"agent_{name}",
        name=f"Agent {name}",
        description="desc",
        instructions="Be cautious",
        role=role,
        layer=layer,
        model_name=None,
        recommended_model_name="gpt-plus-latest",
        temperature=0.2,
        max_tokens=2000,
        top_p=1.0,
        status=AgentStatus.ACTIVE,
        created_by="tester",
    )
    create_agent_profile(repo, agent)
    return agent


def test_repository_creates_agents_and_versions(tmp_path):
    repo = _make_repo(tmp_path)
    agent = _seed_agent(repo, "a", AgentRole.DEBUNKER, AgentLayer.CLASSIFICATION)
    fetched = repo.get_agent(agent.id)
    assert fetched is not None
    versions = repo.list_instruction_versions(agent.id)
    assert versions and versions[0].version_number == 1


def test_committee_requires_three_distinct_agents(tmp_path):
    repo = _make_repo(tmp_path)
    a1 = _seed_agent(repo, "d1", AgentRole.DEBUNKER, AgentLayer.INTERPRETATION)
    a2 = _seed_agent(repo, "d2", AgentRole.DEBUNKER, AgentLayer.INTERPRETATION)
    mediator = _seed_agent(repo, "med", AgentRole.MEDIATOR, AgentLayer.INTERPRETATION)
    from app.agents.models import AgentCommittee
    from app.agents.service import create_committee

    committee = AgentCommittee(
        id="committee_1",
        name="Interp Committee",
        description="",
        layer=AgentLayer.INTERPRETATION,
        primary_agents=[a1.id, a2.id],
        mediator_agent=mediator.id,
        policy=CommitteePolicy(),
    )
    created = create_committee(repo, committee)
    assert created.id == committee.id


def test_admin_api_endpoints(tmp_path):
    repo = _make_repo(tmp_path)

    app = FastAPI()

    def get_repo_override():
        return repo

    app.dependency_overrides[default_get_repo] = get_repo_override
    app.include_router(agents_router)

    client = TestClient(app)

    # create agents
    payload_a = {
        "name": "Debunker A",
        "description": "cético A",
        "instructions": "debunk firmly",
        "role": "debunker",
        "layer": "interpretation",
        "status": "active",
    }
    res_a = client.post("/admin/agents", json=payload_a)
    assert res_a.status_code == 201
    agent_a_id = res_a.json()["id"]

    res_list = client.get("/admin/agents")
    assert res_list.status_code == 200
    assert any(item["id"] == agent_a_id for item in res_list.json())

    # add version
    res_ver = client.post(f"/admin/agents/{agent_a_id}/instructions", json={"changelog": "ajuste", "created_by": "tester"})
    assert res_ver.status_code == 201

    # create second and mediator
    payload_b = {**payload_a, "name": "Debunker B"}
    agent_b_id = client.post("/admin/agents", json=payload_b).json()["id"]
    mediator_id = client.post(
        "/admin/agents",
        json={
            "name": "Mediator",
            "description": "",
            "instructions": "",
            "role": "mediator",
            "layer": "interpretation",
            "status": "active",
        },
    ).json()["id"]

    # create committee
    res_committee = client.post(
        "/admin/agents/committees",
        json={
            "name": "Interp Committee",
            "description": "",
            "layer": "interpretation",
            "primary_agents": [agent_a_id, agent_b_id],
            "mediator_agent": mediator_id,
            "policy": {},
            "status": "active",
        },
    )
    assert res_committee.status_code == 201
    committee_id = res_committee.json()["id"]

    # dry run
    res_run = client.post(f"/admin/agents/committees/{committee_id}/dry-run", json={"input_ref": "case-1", "payload": {"foo": "bar"}})
    assert res_run.status_code == 201
    run_body = res_run.json()
    assert run_body["status"] == AgentRunStatus.SUCCESS.value
    assert run_body["result_bundle_ref"]

    # policy
    res_policy = client.get("/admin/agents/policies/model-upgrades")
    assert res_policy.status_code == 200
    policy = res_policy.json()
    assert policy["global_default_model"]
    assert policy["adoption_delay_days"] >= 0
