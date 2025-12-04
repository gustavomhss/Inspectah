from __future__ import annotations

from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowStepIn
from app.agents.flows.validator import validate_agent_flow
from app.agents.models import AgentRole


def _base_steps():
    return [
        AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER, params={"strict_mode": True}),
        AgentFlowStepIn(position=2, agent_role=AgentRole.CLASSIFIER, params={"committee_id": "c1"}),
        AgentFlowStepIn(position=3, agent_role=AgentRole.DECISION_MAKER, params={"threshold": 0.6}),
    ]


def test_validate_happy_path():
    cfg = AgentFlowConfigIn(domain_key="politics_news", steps=_base_steps())
    errors = validate_agent_flow(cfg)
    assert errors == []


def test_missing_required_roles():
    cfg = AgentFlowConfigIn(
        domain_key="economy_news",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER),
            AgentFlowStepIn(position=2, agent_role=AgentRole.ANALYST),
        ],
    )
    errors = validate_agent_flow(cfg)
    assert any("Missing required roles" in err for err in errors)


def test_decision_maker_not_last():
    cfg = AgentFlowConfigIn(
        domain_key="health_news",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.DECISION_MAKER),
            AgentFlowStepIn(position=2, agent_role=AgentRole.INTERPRETER),
            AgentFlowStepIn(position=3, agent_role=AgentRole.CLASSIFIER),
        ],
    )
    errors = validate_agent_flow(cfg)
    assert any("Decision maker must be the last step" in err for err in errors)


def test_positions_gaps_and_duplicates():
    cfg = AgentFlowConfigIn(
        domain_key="finance_news",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER),
            AgentFlowStepIn(position=1, agent_role=AgentRole.CLASSIFIER),
            AgentFlowStepIn(position=3, agent_role=AgentRole.DECISION_MAKER),
        ],
    )
    errors = validate_agent_flow(cfg)
    assert any("duplicate" in err.lower() for err in errors)

    cfg_gap = AgentFlowConfigIn(
        domain_key="finance_news",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER),
            AgentFlowStepIn(position=3, agent_role=AgentRole.CLASSIFIER),
            AgentFlowStepIn(position=4, agent_role=AgentRole.DECISION_MAKER),
        ],
    )
    errors_gap = validate_agent_flow(cfg_gap)
    assert any("contiguous" in err for err in errors_gap)


def test_unknown_param_keys_blocked():
    cfg = AgentFlowConfigIn(
        domain_key="science_news",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER),
            AgentFlowStepIn(position=2, agent_role=AgentRole.CLASSIFIER),
            AgentFlowStepIn(position=3, agent_role=AgentRole.DECISION_MAKER, params={"secret_switch": True}),
        ],
    )
    errors = validate_agent_flow(cfg)
    assert any("unsupported params keys" in err for err in errors)
