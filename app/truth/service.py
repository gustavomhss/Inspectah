from __future__ import annotations

from typing import List, Optional
from pathlib import Path

from .enums import TruthEventType, TruthState
from .models import (
    DecisionRecord,
    TruthChangeEvent,
    TruthRecord,
    gen_decision_id,
    gen_event_id,
    gen_truth_record_id,
    utcnow,
)
from .repository import TruthRepository
from app.policies.engine import evaluate_policy
from app.policies.schema import load_policies_from_dir
from app.policies.context_builder import build_basic_context
from app.policies.models import PolicyDecision, PromotionPolicyConfig


def get_or_create_truth_record_for_claim(
    claim_id: str,
    domain: str,
    slug: Optional[str] = None,
    repo: Optional[TruthRepository] = None,
    initial_state: TruthState = TruthState.UNKNOWN,
) -> TruthRecord:
    """Fetches an existing truth record by slug or creates a new one with state UNKNOWN/CLAIMED."""
    repository = repo or TruthRepository()
    resolved_slug = slug or f"{domain}:{claim_id}"
    existing = repository.get_record_by_slug(resolved_slug)
    if existing:
        return existing
    record = TruthRecord(
        id=gen_truth_record_id(),
        slug=resolved_slug,
        claim_id=claim_id,
        domain=domain,
        current_state=initial_state,
    )
    return repository.upsert_truth_record(record)


class InvalidTruthTransition(Exception):
    """Raised when a transition between states is not allowed."""


def apply_transition(
    truth_record: TruthRecord,
    new_state: TruthState,
    reason: str,
    source: str,
    repo: Optional[TruthRepository] = None,
    event_type: Optional[TruthEventType] = None,
    metadata: Optional[dict] = None,
    policy_decision: Optional[PolicyDecision] = None,
) -> TruthChangeEvent:
    """
    Applies a simple state transition, records a DecisionRecord + TruthChangeEvent,
    and updates the TruthRecord in storage.
    """

    repository = repo or TruthRepository()

    if policy_decision is not None:
        if policy_decision.decision == "BLOCK":
            raise InvalidTruthTransition(f"Policy bloqueou a transição: {policy_decision.reason}")
        if policy_decision.decision == "HOLD":
            new_state = policy_decision.target_state or truth_record.current_state

    if truth_record.current_state == new_state:
        raise InvalidTruthTransition("Transição redundante para o mesmo estado.")
    if truth_record.current_state == TruthState.RETRACTED and new_state != TruthState.RETRACTED:
        raise InvalidTruthTransition("Registros retraídos não podem voltar a estados ativos.")

    decision = DecisionRecord(
        id=gen_decision_id(),
        truth_record_id=truth_record.id,
        rationale=reason,
        decided_by=source,
        metadata=metadata or {},
    )
    repository.insert_decision(decision)

    event = TruthChangeEvent(
        id=gen_event_id(),
        truth_record_id=truth_record.id,
        previous_state=truth_record.current_state,
        new_state=new_state,
        event_type=event_type,
        reason=reason,
        source=source,
        decision_id=decision.id,
        metadata=metadata or {},
    )
    repository.insert_event(event)

    truth_record.current_state = new_state
    truth_record.last_decision_id = decision.id
    truth_record.updated_at = utcnow()
    repository.upsert_truth_record(truth_record)
    return event


def get_timeline(truth_record_id: str, repo: Optional[TruthRepository] = None) -> List[TruthChangeEvent]:
    repository = repo or TruthRepository()
    return repository.list_events(truth_record_id)


def apply_transition_with_policy(
    truth_record: TruthRecord,
    target_state: TruthState,
    reason: str,
    source: str,
    repo: Optional[TruthRepository] = None,
    policies_dir: str = "configs/promotion_policies",
    recommendation: Optional[str] = None,
    confidence: Optional[float] = None,
    sources_count: int = 0,
    has_debunk: bool = False,
    human_required: bool = False,
    event_type: Optional[TruthEventType] = None,
    metadata: Optional[dict] = None,
) -> TruthChangeEvent:
    """
    Constrói contexto básico, avalia a policy do domínio e aplica a transição se permitido.
    """
    repo_used = repo or TruthRepository()
    policies = load_policies_from_dir(Path(policies_dir))
    policy: PromotionPolicyConfig = policies.get(truth_record.domain) or policies.get("general") or list(policies.values())[0]
    ctx = build_basic_context(
        domain=truth_record.domain,
        current_state=truth_record.current_state,
        recommendation=recommendation,
        confidence=confidence,
        sources_count=sources_count,
        has_debunk=has_debunk,
        human_required=human_required,
    )
    decision = evaluate_policy(policy, ctx)
    meta = metadata.copy() if metadata else {}
    meta.setdefault("policy_name", policy.name)
    meta.setdefault("policy_domain", policy.domain)
    return apply_transition(
        truth_record=truth_record,
        new_state=decision.target_state or target_state,
        reason=decision.reason or reason,
        source=source,
        repo=repo_used,
        event_type=event_type,
        metadata=meta,
        policy_decision=decision,
    )
