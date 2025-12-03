from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from app.agents.flows.schemas import AgentFlowConfigOut, AgentFlowStepOut
from app.agents.flows.service import AgentFlowService
from app.agents.flows.validator import validate_agent_flow
from app.agents.models import AgentRole

logger = logging.getLogger("agent_flows_runtime")

DEFAULT_FALLBACK_STEPS: List[Dict[str, object]] = [
    {"position": 1, "agent_role": AgentRole.INTERPRETER.value, "params": {"strict_mode": True}},
    {"position": 2, "agent_role": AgentRole.CLASSIFIER.value, "params": {"committee_id": "default"}},
    {"position": 3, "agent_role": AgentRole.DECISION_MAKER.value, "params": {"threshold": 0.5}},
]


def _normalize_step(step: AgentFlowStepOut | Dict[str, object]) -> Dict[str, object]:
    if isinstance(step, AgentFlowStepOut):
        return step.model_dump()
    return step


def _build_plan(flow: AgentFlowConfigOut, used_fallback: bool = False) -> Dict[str, object]:
    steps = [_normalize_step(s) for s in flow.steps]
    return {
        "flow_id": flow.id,
        "domain_key": flow.domain_key,
        "used_fallback": used_fallback,
        "steps": steps,
    }


def get_agent_flow_for_domain(domain_key: str, service: Optional[AgentFlowService] = None) -> Tuple[Optional[AgentFlowConfigOut], bool]:
    svc = service or AgentFlowService()
    flow = svc.get_flow_by_domain(domain_key)
    if not flow:
        logger.info("agent_flow_fallback_no_config", extra={"domain_key": domain_key})
        return None, True
    as_schema = AgentFlowConfigOut.model_validate(flow.__dict__ | {"steps": [s.__dict__ for s in flow.steps]})
    errors = validate_agent_flow(as_schema)
    if errors:
        logger.error(
            "agent_flow_invalid_runtime",
            extra={"domain_key": domain_key, "flow_id": flow.id, "errors": errors},
        )
        return None, True
    logger.info(
        "agent_flow_loaded",
        extra={"domain_key": domain_key, "flow_id": flow.id, "steps": len(flow.steps)},
    )
    return as_schema, False


def get_executable_flow_plan(domain_key: str, service: Optional[AgentFlowService] = None) -> Dict[str, object]:
    flow, fallback = get_agent_flow_for_domain(domain_key, service=service)
    if flow and not fallback:
        return _build_plan(flow, used_fallback=False)
    # fallback plan
    from datetime import datetime

    now = datetime.utcnow()
    fallback_flow = AgentFlowConfigOut(
        id="fallback",
        domain_key=domain_key,
        name="Fallback flow",
        description="Fallback linear agent flow",
        is_active=True,
        change_reason="fallback",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
        steps=[
            AgentFlowStepOut(
                id=f"fallback-{s['position']}",
                flow_id="fallback",
                position=s["position"],
                agent_role=s["agent_role"],
                params=s.get("params", {}),
                required=s.get("required", True),
                can_fail_soft=s.get("can_fail_soft", False),
                created_at=now,
                updated_at=now,
            )
            for s in DEFAULT_FALLBACK_STEPS
        ],
    )
    logger.info("agent_flow_fallback_used", extra={"domain_key": domain_key})
    return _build_plan(fallback_flow, used_fallback=True)
