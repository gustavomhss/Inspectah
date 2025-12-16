from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from app.agents.flows.schemas import AgentFlowConfigOut, AgentFlowStepOut
from app.agents.flows.service import AgentFlowService
from app.agents.flows.validator import validate_agent_flow
from app.agents.models import AgentRole

if TYPE_CHECKING:
    from app.agents.trace_repository import AgentTrace, TraceRepository
    from app.truth.models import TraceLinkRefs

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
    now = datetime.now(timezone.utc)
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


def record_flow_trace(
    link_refs: "TraceLinkRefs",
    flow_plan: Dict[str, Any],
    *,
    steps_summaries: Optional[List[str]] = None,
    repo: Optional["TraceRepository"] = None,
) -> "AgentTrace":
    """
    Records an AgentTrace for a flow execution based on the flow plan and step summaries.

    Args:
        link_refs: TraceLinkRefs with context (truth_record_id, decision_record_id, claim_id, domain, risk_level)
        flow_plan: The executed flow plan dict with flow_id, domain_key, steps
        steps_summaries: Optional list of summary strings for each step executed
        repo: Optional TraceRepository instance

    Returns:
        The saved AgentTrace
    """
    from app.agents.trace_repository import AgentTrace, ReasoningStep, TraceRepository

    repo_used = repo or TraceRepository()
    now = datetime.now(timezone.utc)
    flow_id = flow_plan.get("flow_id", "unknown")

    # Build reasoning steps from flow_plan steps
    reasoning_steps: List[ReasoningStep] = []
    plan_steps = flow_plan.get("steps", [])
    summaries = steps_summaries or []

    for idx, step_data in enumerate(plan_steps):
        summary = summaries[idx] if idx < len(summaries) else f"Step {idx + 1}: {step_data.get('agent_role', 'unknown')}"
        reasoning_steps.append(
            ReasoningStep(
                order=idx + 1,
                actor_role=step_data.get("agent_role"),
                step_kind="flow_step",
                summary=summary,
                input_refs=[flow_id],
                created_at=now,
            )
        )

    # Use pilot_politics as default domain if empty
    domain = link_refs.domain or flow_plan.get("domain_key") or "pilot_politics"

    trace = AgentTrace(
        truth_record_id=link_refs.truth_record_id,
        decision_record_id=link_refs.decision_record_id,
        claim_id=link_refs.claim_id,
        domain=domain,
        risk_level=link_refs.risk_level,
        request_id=link_refs.request_id,
        started_at=now,
        finished_at=now,
        steps=reasoning_steps,
        created_at=now,
    )

    saved_trace = repo_used.save_agent_trace(trace)
    logger.info(
        "flow_trace_recorded",
        extra={
            "agent_trace_id": saved_trace.agent_trace_id,
            "flow_id": flow_id,
            "steps_count": len(reasoning_steps),
        },
    )
    return saved_trace
