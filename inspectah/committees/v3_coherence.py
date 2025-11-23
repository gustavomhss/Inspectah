"""Verificador de coerência global (V3)."""
from __future__ import annotations

from typing import Iterable, Mapping

from inspectah.truthdb.state_machine import FactState

from .common import CommitteeDecision, DecisionStatus, Reason, Vote, VoteOutcome


def check_coherence(
    submission: Mapping[str, object],
    related_facts: Iterable[Mapping[str, object]],
) -> CommitteeDecision:
    raw_state = submission.get("proposed_state", FactState.INCERTO)
    if isinstance(raw_state, FactState):
        desired_state = raw_state
    else:
        try:
            desired_state = FactState(str(raw_state))
        except ValueError:
            desired_state = FactState.INCERTO
    conflicts: list[str] = []
    scope = submission.get("scope") or submission.get("domain") or "generic"
    for fact in related_facts:
        fact_state = FactState(str(fact.get("current_state", FactState.INCERTO)))
        if fact.get("fact_id") == submission.get("fact_id"):
            continue
        if fact.get("scope", scope) != scope:
            continue
        if fact_state in {FactState.CONCLUIDO, FactState.CONFIRMADO} and desired_state in {
            FactState.CONCLUIDO,
            FactState.CONFIRMADO,
        }:
            conflicts.append(f"conflito_com:{fact.get('fact_id')}")

    if conflicts:
        votes = [
            Vote(
                voter="coherence_guard",
                outcome=VoteOutcome.DISAGREE,
                reason=Reason(code="conflito_global", description=";".join(conflicts)),
            )
        ]
        return CommitteeDecision(
            layer="V3",
            status=DecisionStatus.BLOCKED,
            rationale="; ".join(conflicts),
            votes=votes,
            metadata={"conflicts": conflicts},
        )

    votes = [
        Vote(
            voter="coherence_guard",
            outcome=VoteOutcome.AGREE,
            reason=Reason(code="coerente", description="sem conflitos aparentes"),
        )
    ]
    return CommitteeDecision(
        layer="V3",
        status=DecisionStatus.APPROVED,
        rationale="sem conflito global",
        votes=votes,
        metadata={"checked": True},
    )


__all__ = ["check_coherence"]
