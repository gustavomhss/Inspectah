"""Validador mecânico (V1) para decisões de disputa e atualização de fatos."""
from __future__ import annotations

from typing import Dict, Iterable, List

from inspectah.truthdb.state_machine import FactState, InvalidStateTransition, StateMachine

from .common import CommitteeDecision, DecisionStatus, Reason, Vote, VoteOutcome


def _ensure_fields(payload: Dict[str, object], required: Iterable[str]) -> List[str]:
    missing = []
    for field in required:
        if field not in payload or payload.get(field) in (None, ""):
            missing.append(field)
    return missing


def validate_submission(submission: Dict[str, object], *, state_machine: StateMachine | None = None) -> CommitteeDecision:
    sm = state_machine or StateMachine()
    errors: List[str] = []
    missing = _ensure_fields(
        submission,
        ("case_id", "fact_id", "proposed_state", "current_state", "evidence_count"),
    )
    if missing:
        errors.extend([f"campo_obrigatorio:{field}" for field in missing])
    try:
        desired = FactState(str(submission.get("proposed_state")))
        current = FactState(str(submission.get("current_state")))
        sm.validate_transition(current, desired)
    except (ValueError, InvalidStateTransition) as exc:
        errors.append(f"transicao_invalida:{exc}")

    ev_count = int(submission.get("evidence_count", 0) or 0)
    if ev_count <= 0:
        errors.append("sem_evidencias")

    if errors:
        votes = [Vote(voter="validator", outcome=VoteOutcome.DISAGREE, reason=Reason(code=e, description=e)) for e in errors]
        return CommitteeDecision(
            layer="V1",
            status=DecisionStatus.REJECTED,
            rationale="; ".join(errors),
            votes=votes,
            metadata={"errors": errors},
        )
    return CommitteeDecision(
        layer="V1",
        status=DecisionStatus.APPROVED,
        rationale="Estrutura válida e transições permitidas.",
        votes=[Vote(voter="validator", outcome=VoteOutcome.AGREE, reason=Reason(code="ok", description="válido"))],
        metadata={"checked": True},
    )


__all__ = ["validate_submission"]
