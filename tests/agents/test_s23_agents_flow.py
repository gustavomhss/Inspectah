from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents.models import AgentLayer, AgentRole, AgentStatus, FlowLayerType, AgentFlowLayer
from app.agents.repository import AgentsRepository
from app.agents.service import create_agent_profile
from app.api.agents.routes_admin import router as agents_router, get_repo as default_get_repo


def _make_repo(tmp_path: Path) -> AgentsRepository:
    return AgentsRepository(db_path=tmp_path / "flow.sqlite")


def _seed(repo: AgentsRepository, name: str, role: AgentRole, layer: AgentLayer):
    from app.agents.models import AgentProfile

    agent = AgentProfile(
        id=name,
        name=name,
        description="",
        instructions="",
        role=role,
        layer=layer,
        model_name=None,
        recommended_model_name="gpt-4.1",
        temperature=0.2,
        max_tokens=2000,
        top_p=1.0,
        status=AgentStatus.ACTIVE,
    )
    create_agent_profile(repo, agent)
    return agent


def test_flow_happy_path(tmp_path: Path):
    repo = _make_repo(tmp_path)
    interp_agents = [_seed(repo, f"interp{i}", AgentRole.INTERPRETER, AgentLayer.INTERPRETATION).id for i in range(3)]
    class_agents = [_seed(repo, f"class{i}", AgentRole.CLASSIFIER, AgentLayer.CLASSIFICATION).id for i in range(3)]
    dec = _seed(repo, "decider", AgentRole.DECISION_MAKER, AgentLayer.CLASSIFICATION).id
    lib = _seed(repo, "librarian", AgentRole.LIBRARIAN, AgentLayer.CLASSIFICATION).id
    mid_agents = [_seed(repo, f"deb{i}", AgentRole.DEBUNKER, AgentLayer.INTERPRETATION).id for i in range(3)]

    app = FastAPI()

    def override_repo():
        return repo

    app.dependency_overrides[default_get_repo] = override_repo
    app.include_router(agents_router)
    client = TestClient(app)

    payload = [
        {
            "name": "Interpretação",
            "description": "",
            "layer_type": FlowLayerType.INTERPRETATION.value,
            "layer_index": 1,
            "agent_ids": interp_agents,
            "mediator_agent_id": interp_agents[0],
        },
        {
            "name": "Classificação",
            "description": "",
            "layer_type": FlowLayerType.CLASSIFICATION.value,
            "layer_index": 2,
            "agent_ids": class_agents,
            "mediator_agent_id": class_agents[0],
        },
        {
            "name": "Intermediária",
            "description": "",
            "layer_type": FlowLayerType.INTERMEDIATE.value,
            "layer_index": 3,
            "agent_ids": mid_agents,
            "mediator_agent_id": mid_agents[0],
        },
        {
            "name": "Decision",
            "description": "",
            "layer_type": FlowLayerType.DECISION_MAKER.value,
            "layer_index": 4,
            "agent_ids": [dec, dec, dec],
            "mediator_agent_id": dec,
        },
        {
            "name": "Librarian",
            "description": "",
            "layer_type": FlowLayerType.LIBRARIAN.value,
            "layer_index": 5,
            "agent_ids": [lib, lib, lib],
            "mediator_agent_id": lib,
        },
    ]

    res = client.put("/admin/agents/flow", json=payload)
    assert res.status_code == 200, res.json()
    get_res = client.get("/admin/agents/flow")
    assert get_res.status_code == 200
    flow = get_res.json()
    assert len(flow) == 5
    assert flow[0]["layer_type"] == FlowLayerType.INTERPRETATION.value
    assert flow[-1]["layer_type"] == FlowLayerType.LIBRARIAN.value


@pytest.mark.parametrize(
    "mutator",
    [
        lambda p: p[:-1],
        lambda p: [{**p[0], "agent_ids": p[0]["agent_ids"][:2]}] + p[1:],
        lambda p: [{**p[0], "mediator_agent_id": "x"}] + p[1:],
    ],
)
def test_flow_invalid_rules(tmp_path: Path, mutator):
    repo = _make_repo(tmp_path)
    interp_agents = [_seed(repo, f"interp{i}", AgentRole.INTERPRETER, AgentLayer.INTERPRETATION).id for i in range(3)]
    class_agents = [_seed(repo, f"class{i}", AgentRole.CLASSIFIER, AgentLayer.CLASSIFICATION).id for i in range(3)]
    dec = _seed(repo, "decider", AgentRole.DECISION_MAKER, AgentLayer.CLASSIFICATION).id
    lib = _seed(repo, "librarian", AgentRole.LIBRARIAN, AgentLayer.CLASSIFICATION).id
    mid_agents = [_seed(repo, f"deb{i}", AgentRole.DEBUNKER, AgentLayer.INTERPRETATION).id for i in range(3)]

    base_payload = [
        {
            "name": "Interpretação",
            "description": "",
            "layer_type": FlowLayerType.INTERPRETATION.value,
            "layer_index": 1,
            "agent_ids": interp_agents,
            "mediator_agent_id": interp_agents[0],
        },
        {
            "name": "Classificação",
            "description": "",
            "layer_type": FlowLayerType.CLASSIFICATION.value,
            "layer_index": 2,
            "agent_ids": class_agents,
            "mediator_agent_id": class_agents[0],
        },
        {
            "name": "Intermediária",
            "description": "",
            "layer_type": FlowLayerType.INTERMEDIATE.value,
            "layer_index": 3,
            "agent_ids": mid_agents,
            "mediator_agent_id": mid_agents[0],
        },
        {
            "name": "Decision",
            "description": "",
            "layer_type": FlowLayerType.DECISION_MAKER.value,
            "layer_index": 4,
            "agent_ids": [dec, dec, dec],
            "mediator_agent_id": dec,
        },
        {
            "name": "Librarian",
            "description": "",
            "layer_type": FlowLayerType.LIBRARIAN.value,
            "layer_index": 5,
            "agent_ids": [lib, lib, lib],
            "mediator_agent_id": lib,
        },
    ]
    payload = mutator(base_payload)

    app = FastAPI()

    def override_repo():
        return repo

    app.dependency_overrides[default_get_repo] = override_repo
    app.include_router(agents_router)
    client = TestClient(app)

    res = client.put("/admin/agents/flow", json=payload)
    assert res.status_code == 400
