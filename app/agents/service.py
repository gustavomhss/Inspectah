from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from app.agents.trace_repository import CommitteeTrace, TraceRepository
    from app.truth.models import TraceLinkRefs

from app.agents.models import (
    AgentCommittee,
    AgentInstructionVersion,
    AgentKBRef,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentRun,
    AgentRunStatus,
    AgentStatus,
    FlowLayerType,
    CommitteePolicy,
    ModelUpgradePolicy,
)
from app.agents.repository import AgentsRepository

FLOW_PATH = Path("out/runtime/console_agents_flow.json")


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def get_flow(repo: Optional[AgentsRepository] = None) -> List[Any]:
    """Weak, file-based flow shared between admin and console."""
    _ = repo
    try:
        if not FLOW_PATH.exists():
            return []
        text = FLOW_PATH.read_text(encoding="utf-8")
        if not text.strip():
            return []
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_flow(flow: Any, repo: Optional[AgentsRepository] = None) -> List[Any]:
    """Persists the agents flow to the shared file and returns a list."""
    _ = repo
    try:
        FLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
        _validate_flow(flow)
        if not isinstance(flow, list):
            flow = []
        FLOW_PATH.write_text(json.dumps(flow, ensure_ascii=False, indent=2), encoding="utf-8")
        return flow
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        return []


def create_agent_profile(repo: Optional[AgentsRepository], payload: AgentProfile) -> AgentProfile:
    repo = repo or AgentsRepository()
    _validate_agent(payload)
    repo.create_agent(payload)
    initial_version = payload.to_version_snapshot(version_number=1, changelog="Versão inicial", author=payload.created_by or "system")
    repo.create_instruction_version(initial_version)
    return payload


def update_agent_profile(repo: Optional[AgentsRepository], agent_id: str, updates: Dict) -> Optional[AgentProfile]:
    repo = repo or AgentsRepository()
    current = repo.get_agent(agent_id)
    if not current:
        return None
    for field_name, value in updates.items():
        if hasattr(current, field_name) and value is not None:
            setattr(current, field_name, value)
    current.updated_at = datetime.now(timezone.utc)
    _validate_agent(current)
    repo.update_agent(current)
    return current


def add_instruction_version(
    repo: Optional[AgentsRepository],
    agent_id: str,
    instructions: Optional[str],
    changelog: str,
    model_name: Optional[str],
    temperature: Optional[float],
    max_tokens: Optional[int],
    top_p: Optional[float],
    kb_snapshot: Optional[List[AgentKBRef]],
    author: Optional[str],
) -> Optional[AgentInstructionVersion]:
    repo = repo or AgentsRepository()
    agent = repo.get_agent(agent_id)
    if not agent:
        return None
    versions = repo.list_instruction_versions(agent_id)
    next_version_number = versions[0].version_number + 1 if versions else 1
    version = AgentInstructionVersion(
        id=_gen_id("agver"),
        agent_id=agent_id,
        version_number=next_version_number,
        instructions=instructions or agent.instructions,
        model_name=model_name or agent.model_name,
        temperature=temperature if temperature is not None else agent.temperature,
        max_tokens=max_tokens if max_tokens is not None else agent.max_tokens,
        top_p=top_p if top_p is not None else agent.top_p,
        kb_snapshot=kb_snapshot if kb_snapshot is not None else agent.kb_refs,
        changelog=changelog or "Atualização de instruções",
        created_by=author,
    )
    repo.create_instruction_version(version)
    agent.instructions = version.instructions
    agent.model_name = version.model_name
    agent.temperature = version.temperature
    agent.max_tokens = version.max_tokens
    agent.top_p = version.top_p
    agent.kb_refs = version.kb_snapshot
    agent.updated_at = datetime.now(timezone.utc)
    repo.update_agent(agent)
    return version


def create_committee(repo: Optional[AgentsRepository], committee: AgentCommittee) -> AgentCommittee:
    repo = repo or AgentsRepository()
    _validate_committee(repo, committee)
    repo.create_committee(committee)
    return committee


def update_committee(repo: Optional[AgentsRepository], committee_id: str, updates: Dict) -> Optional[AgentCommittee]:
    repo = repo or AgentsRepository()
    current = repo.get_committee(committee_id)
    if not current:
        return None
    for field_name, value in updates.items():
        if hasattr(current, field_name) and value is not None:
            setattr(current, field_name, value)
    current.updated_at = datetime.now(timezone.utc)
    _validate_committee(repo, current)
    repo.update_committee(current)
    return current


def get_or_create_model_policy(repo: Optional[AgentsRepository]) -> ModelUpgradePolicy:
    repo = repo or AgentsRepository()
    return repo.get_model_policy()


def update_model_policy(
    repo: Optional[AgentsRepository],
    global_default_model: Optional[str],
    auto_upgrade_enabled: Optional[bool],
    adoption_delay_days: Optional[int],
    allowed_models: Optional[List[str]],
    next_upgrade_at: Optional[datetime] = None,
) -> ModelUpgradePolicy:
    repo = repo or AgentsRepository()
    policy = repo.get_model_policy()
    if global_default_model:
        policy.global_default_model = global_default_model
    if auto_upgrade_enabled is not None:
        policy.auto_upgrade_enabled = auto_upgrade_enabled
    if adoption_delay_days is not None:
        policy.adoption_delay_days = adoption_delay_days
    if allowed_models is not None:
        policy.allowed_models = allowed_models
    if next_upgrade_at is not None:
        policy.next_upgrade_at = next_upgrade_at
    policy.updated_at = datetime.now(timezone.utc)
    repo.save_model_policy(policy)
    return policy


def start_committee_run(repo: Optional[AgentsRepository], committee_id: str, input_ref: Optional[str], payload_snapshot: Dict[str, object]) -> Optional[AgentRun]:
    repo = repo or AgentsRepository()
    committee = repo.get_committee(committee_id)
    if not committee:
        return None
    run = AgentRun.create(id=_gen_id("agrun"), committee_id=committee_id, input_ref=input_ref, payload_snapshot=payload_snapshot)
    repo.create_run(run)
    return run


def finalize_committee_run_success(repo: Optional[AgentsRepository], run_id: str, result_bundle_ref: str) -> Optional[AgentRun]:
    repo = repo or AgentsRepository()
    matching = repo.get_run(run_id)
    if not matching:
        return None
    matching.status = AgentRunStatus.SUCCESS
    matching.result_bundle_ref = result_bundle_ref
    matching.finished_at = datetime.now(timezone.utc)
    repo.update_run(matching)
    return matching


def finalize_committee_run_fail(repo: Optional[AgentsRepository], run_id: str, error: str) -> Optional[AgentRun]:
    repo = repo or AgentsRepository()
    matching = repo.get_run(run_id)
    if not matching:
        return None
    matching.status = AgentRunStatus.FAIL
    matching.error = error
    matching.finished_at = datetime.now(timezone.utc)
    repo.update_run(matching)
    return matching


def _validate_agent(agent: AgentProfile) -> None:
    if not agent.name:
        raise ValueError("Agent name is required")
    if not agent.layer or not agent.role:
        raise ValueError("Agent layer and role are required")


def _validate_committee(repo: AgentsRepository, committee: AgentCommittee) -> None:
    if len(committee.primary_agents) != 2:
        raise ValueError("Comitê precisa de dois agentes primários (debunkers/classificadores)")
    if committee.mediator_agent in committee.primary_agents:
        raise ValueError("Mediador deve ser diferente dos agentes primários")
    for agent_id in committee.primary_agents + [committee.mediator_agent]:
        if not repo.get_agent(agent_id):
            raise ValueError(f"Agente {agent_id} não encontrado")


def _validate_flow(flow: Any) -> None:
    if not isinstance(flow, list) or not flow:
        raise ValueError("Fluxo de agentes deve ser uma lista não vazia")

    required_layers = {
        FlowLayerType.INTERPRETATION.value,
        FlowLayerType.CLASSIFICATION.value,
        FlowLayerType.INTERMEDIATE.value,
        FlowLayerType.DECISION_MAKER.value,
        FlowLayerType.LIBRARIAN.value,
    }
    seen_layers = set()
    for entry in flow:
        if not isinstance(entry, dict):
            raise ValueError("Cada camada do fluxo deve ser um objeto")
        layer_type = entry.get("layer_type")
        agent_ids = entry.get("agent_ids") or []
        mediator = entry.get("mediator_agent_id")
        if layer_type not in required_layers:
            raise ValueError(f"Camada inválida no fluxo: {layer_type}")
        if layer_type in seen_layers:
            raise ValueError(f"Camada duplicada no fluxo: {layer_type}")
        seen_layers.add(layer_type)
        if len(agent_ids) < 3:
            raise ValueError(f"Camada {layer_type} deve ter pelo menos 3 agentes")
        if mediator not in agent_ids:
            raise ValueError(f"Mediador deve fazer parte dos agentes da camada {layer_type}")
    if not required_layers.issubset(seen_layers):
        missing = required_layers - seen_layers
        raise ValueError(f"Fluxo incompleto; faltam camadas: {sorted(missing)}")


_logger = logging.getLogger(__name__)


def record_committee_trace(
    link_refs: "TraceLinkRefs",
    *,
    agent_trace_ids: List[str],
    summary: str,
    committee_id: str = "pilot_committee",
    committee_version: str = "v1",
    repo: Optional["TraceRepository"] = None,
) -> "CommitteeTrace":
    """
    Records a CommitteeTrace for a committee decision, linking DecisionRecord/TruthRecord/Claim to AgentTraces.

    Args:
        link_refs: TraceLinkRefs with context (truth_record_id, decision_record_id, claim_id, domain, risk_level)
        agent_trace_ids: List of agent trace IDs that contributed to this committee decision
        summary: Summary of the committee decision
        committee_id: ID of the committee
        committee_version: Version of the committee configuration
        repo: Optional TraceRepository instance

    Returns:
        The saved CommitteeTrace
    """
    from app.agents.trace_repository import CommitteeTrace, TraceRepository

    repo_used = repo or TraceRepository()
    now = datetime.now(timezone.utc)

    # Use pilot_politics as default domain if None or empty
    domain = link_refs.domain or "pilot_politics"

    trace = CommitteeTrace(
        committee_id=committee_id,
        committee_version=committee_version,
        truth_record_id=link_refs.truth_record_id,
        decision_record_id=link_refs.decision_record_id,
        claim_id=link_refs.claim_id,
        agent_trace_ids=agent_trace_ids,
        summary=summary,
        domain=domain,
        risk_level=link_refs.risk_level,
        request_id=link_refs.request_id,
        started_at=now,
        finished_at=now,
        created_at=now,
    )

    saved_trace = repo_used.save_committee_trace(trace)
    _logger.info(
        "committee_trace_recorded",
        extra={
            "committee_trace_id": saved_trace.committee_trace_id,
            "committee_id": committee_id,
            "agent_traces_count": len(agent_trace_ids),
        },
    )
    return saved_trace
