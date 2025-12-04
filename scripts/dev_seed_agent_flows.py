"""
Seeds five sample agent flows for admin console sanity (Sprint 30).

Run with:
    PYTHONPATH=. python scripts/dev_seed_agent_flows.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowStepIn
from app.agents.flows.service import AgentFlowService
from app.agents.models import AgentRole


@dataclass
class SeedStep:
    position: int
    agent_role: AgentRole
    params: dict
    required: bool = True
    can_fail_soft: bool = False


@dataclass
class SeedFlow:
    domain_key: str
    name: str
    description: str
    change_reason: str
    is_active: bool
    steps: List[SeedStep]


SEED_FLOWS: List[SeedFlow] = [
    SeedFlow(
        domain_key="news_basic_fact_check",
        name="News basic fact check",
        description="Interpreta notícia, classifica tema e decide encaminhamento padrão",
        change_reason="seed S30 sanity",
        is_active=True,
        steps=[
            SeedStep(1, AgentRole.INTERPRETER, {"agent_id": "ag_news_interpreter_v1", "strict_mode": True}),
            SeedStep(2, AgentRole.CLASSIFIER, {"agent_id": "ag_news_classifier_v1", "committee_id": "ct_news_triage"}),
            SeedStep(3, AgentRole.DECISION_MAKER, {"agent_id": "ag_news_decider_v1", "threshold": 0.65}),
        ],
    ),
    SeedFlow(
        domain_key="news_committee_three_agents",
        name="News committee triage",
        description="Committee de três agentes para decidir bandeira de notícia",
        change_reason="seed S30 sanity",
        is_active=False,
        steps=[
            SeedStep(1, AgentRole.INTERPRETER, {"agent_id": "ag_interp_news_committee", "strict_mode": True}),
            SeedStep(
                2,
                AgentRole.CLASSIFIER,
                {
                    "agent_id": "ag_classifier_committee_driver",
                    "committee_id": "ct_news_committee_v1",
                    "allow_retry": True,
                },
            ),
            SeedStep(3, AgentRole.ANALYST, {"agent_id": "ag_news_analyst_v1", "max_depth": 2}, can_fail_soft=True),
            SeedStep(4, AgentRole.DECISION_MAKER, {"agent_id": "ag_decider_committee", "threshold": 0.7}),
        ],
    ),
    SeedFlow(
        domain_key="sources_healthcheck_router",
        name="Sources healthcheck router",
        description="Roteia checagem de fontes e envia para decision maker com nota de saúde",
        change_reason="seed S30 sanity",
        is_active=False,
        steps=[
            SeedStep(1, AgentRole.INTERPRETER, {"agent_id": "ag_sources_interpreter", "notes": "healthcheck"}),
            SeedStep(2, AgentRole.CLASSIFIER, {"agent_id": "ag_router_classifier", "threshold": 0.5}),
            SeedStep(3, AgentRole.DECISION_MAKER, {"agent_id": "ag_router_decider", "threshold": 0.6}),
        ],
    ),
    SeedFlow(
        domain_key="case_timeline_xray",
        name="Case timeline + xray",
        description="Interpreta caso, classifica e abre xray/timeline com agente especializado",
        change_reason="seed S30 sanity",
        is_active=False,
        steps=[
            SeedStep(1, AgentRole.INTERPRETER, {"agent_id": "ag_case_interpreter"}),
            SeedStep(2, AgentRole.CLASSIFIER, {"agent_id": "ag_case_classifier", "strict_mode": True}),
            SeedStep(3, AgentRole.ANALYST, {"agent_id": "ag_case_xray", "notes": "timeline+xray"}),
            SeedStep(4, AgentRole.DECISION_MAKER, {"agent_id": "ag_case_decider", "threshold": 0.8}),
        ],
    ),
    SeedFlow(
        domain_key="low_confidence_escalation",
        name="Low confidence escalation",
        description="Fluxo de fallback para confiança baixa, com debunker opcional",
        change_reason="seed S30 sanity",
        is_active=False,
        steps=[
            SeedStep(1, AgentRole.INTERPRETER, {"agent_id": "ag_lowconf_interpreter"}),
            SeedStep(2, AgentRole.CLASSIFIER, {"agent_id": "ag_lowconf_classifier", "threshold": 0.4}),
            SeedStep(3, AgentRole.DEBUNKER, {"agent_id": "ag_debunker_manual", "allow_retry": True}, can_fail_soft=True),
            SeedStep(4, AgentRole.DECISION_MAKER, {"agent_id": "ag_escalation_decider", "threshold": 0.55}),
        ],
    ),
]


def _to_config(seed: SeedFlow) -> AgentFlowConfigIn:
    return AgentFlowConfigIn(
        domain_key=seed.domain_key,
        name=seed.name,
        description=seed.description,
        change_reason=seed.change_reason,
        is_active=seed.is_active,
        steps=[
            AgentFlowStepIn(
                position=s.position,
                agent_role=s.agent_role,
                params=s.params,
                required=s.required,
                can_fail_soft=s.can_fail_soft,
            )
            for s in seed.steps
        ],
    )


def upsert_seed_flows(service: AgentFlowService) -> list[tuple[str, Literal["created", "updated"]]]:
    results: list[tuple[str, Literal["created", "updated"]]] = []
    for seed in SEED_FLOWS:
        payload = _to_config(seed)
        existing = service.get_flow_by_domain(seed.domain_key)
        if existing:
            service.update_flow(existing.id, payload)
            results.append((seed.domain_key, "updated"))
        else:
            flow = service.create_flow(payload)
            results.append((seed.domain_key, "created"))
    return results


def main() -> None:
    service = AgentFlowService()
    results = upsert_seed_flows(service)
    for domain_key, status in results:
        print(f"[agent-flows] {domain_key}: {status}")


if __name__ == "__main__":
    main()
