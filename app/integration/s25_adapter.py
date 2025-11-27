from __future__ import annotations

from dataclasses import dataclass

from app.debunk.models import DebunkOutcome, RecommendedTruthAction
from app.truthdb.models import TruthChangeEvent, TruthRecord, TruthState
from app.truthdb.repository import TruthRepository, gen_event_id


@dataclass
class DebunkOutcomeResult:
    outcome: DebunkOutcome
    event: TruthChangeEvent
    record: TruthRecord


def _map_action_to_state(action: RecommendedTruthAction) -> TruthState:
    mapping = {
        RecommendedTruthAction.SUGERE_PROMOVER: TruthState.ESTABLISHED_FACT,
        RecommendedTruthAction.SUGERE_REBAIXAR: TruthState.UNDER_DISPUTE,
        RecommendedTruthAction.MANTER_ESTADO_ATUAL: TruthState.PROVISIONAL,
        RecommendedTruthAction.MARCAR_EM_DISPUTA: TruthState.UNDER_DISPUTE,
    }
    return mapping.get(action, TruthState.UNDER_REVIEW)


def deliver_outcome(outcome: DebunkOutcome, truth_repo: TruthRepository | None = None) -> DebunkOutcomeResult:
    """
    S24→S25 bridge.

    Takes a DebunkOutcome produced by the Debunker and materializes the corresponding TruthChangeEvent
    plus the latest TruthRecord state that S25 would keep.
    """
    repo = truth_repo or TruthRepository()
    previous = repo.latest_record(outcome.target_id)
    new_state = _map_action_to_state(outcome.recommended_truth_action)
    record = repo.upsert_truth_record(
        TruthRecord(
            claim_id=outcome.target_id,
            state=new_state,
            version=previous.version + 1 if previous else 1,
            metadata={"decision_id": outcome.decision_id, "issue_id": outcome.issue_id},
        )
    )
    event = repo.append_event(
        TruthChangeEvent(
            id=gen_event_id(),
            claim_id=outcome.target_id,
            previous_state=previous.state if previous else None,
            new_state=new_state,
            rationale=outcome.rationale,
            source="debunk_v0",
            debunk_issue_id=outcome.issue_id,
            decision_id=outcome.decision_id,
            metadata={"recommended_action": outcome.recommended_truth_action.value},
        )
    )
    return DebunkOutcomeResult(outcome=outcome, event=event, record=record)
