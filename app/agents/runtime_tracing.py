from __future__ import annotations

"""
Helpers centralizados de tracing para S36 (AgentTrace/CommitteeTrace) no runtime real.

Uso esperado:
- Construir TraceLinkRefs (truth_record_id, decision_record_id, claim_id, domain, risk_level, request_id).
- Chamar record_flow_trace(...) para registrar passos de flow ContentItem→Claim/Entidade.
- Chamar record_committee_trace(...) após deliberação/IEL com os agent_trace_ids relacionados.
"""

from typing import List, Optional

from app.agents.flows.runtime_adapter import record_flow_trace
from app.agents.service import record_committee_trace
from app.agents.trace_repository import TraceRepository
from app.truth.models import TraceLinkRefs


def trace_flow_execution(
    link_refs: TraceLinkRefs,
    flow_plan: dict,
    *,
    steps_summaries: Optional[List[str]] = None,
    repo: Optional[TraceRepository] = None,
):
    """
    Registra AgentTrace para a execução do flow ContentItem→Claim/Entidade com base no plano de steps.
    """
    repo_used = repo or TraceRepository()
    return record_flow_trace(link_refs, flow_plan, steps_summaries=steps_summaries, repo=repo_used)


def trace_committee_decision(
    link_refs: TraceLinkRefs,
    agent_trace_ids: List[str],
    summary: str,
    *,
    committee_id: str = "pilot_committee",
    committee_version: str = "v1",
    repo: Optional[TraceRepository] = None,
):
    """
    Registra CommitteeTrace para uma decisão, ligando DecisionRecord/TR/Claim a AgentTraces.
    """
    repo_used = repo or TraceRepository()
    return record_committee_trace(
        link_refs=link_refs,
        agent_trace_ids=agent_trace_ids,
        summary=summary,
        committee_id=committee_id,
        committee_version=committee_version,
        repo=repo_used,
    )
