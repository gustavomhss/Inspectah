from pathlib import Path
import os

from app.debunk import service
from app.debunk.models import (
    DebunkDecisionType,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository
from app.integration.s23_adapter import ClaimConflictSignal, ConflictLevel, process_conflict_signal
from app.truthdb.repository import TruthRepository


def test_s23_conflict_opens_debunk_issue_and_truth_event():
    debunk_db = Path("out/databases/contract_debunk.sqlite")
    truth_db = Path("out/databases/contract_truth.sqlite")
    if debunk_db.exists():
        debunk_db.unlink()
    if truth_db.exists():
        truth_db.unlink()
    os.environ["INSPECTAH_S24_TRUTH_DB_PATH"] = str(truth_db)
    repo = DebunkRepository(debunk_db)
    truth_repo = TruthRepository(truth_db)
    # S23 conflict signal
    signal = ClaimConflictSignal(claim_id="claim-contract-test", conflict_level=ConflictLevel.HIGH, summary="Comitês discordam")
    issue_id = process_conflict_signal(repo, signal)
    assert issue_id is not None
    issue = repo.get_issue(issue_id)
    assert issue is not None
    assert issue.status == DebunkIssueStatus.OPEN

    # Move to decision and emit truth change
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.TRIAGED, actor="tester")
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.IN_REVIEW, actor="tester")
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.READY_FOR_DECISION, actor="tester")
    decision = service.record_decision(
        repo,
        issue_id=issue.id,
        decision_type=DebunkDecisionType.CLAIM_BEM_SUPORTADO,
        rationale="Contratos ok",
        recommended_truth_action=RecommendedTruthAction.SUGERE_PROMOVER,
        created_by="tester",
        confidence=0.9,
    )
    assert decision.issue_id == issue.id
    refreshed_issue = repo.get_issue(issue.id)
    assert refreshed_issue is not None
    assert refreshed_issue.status == DebunkIssueStatus.RESOLVED
    outcome = service.build_outcome(refreshed_issue, decision)
    assert outcome.recommended_truth_action == RecommendedTruthAction.SUGERE_PROMOVER
    assert outcome.decision_type == DebunkDecisionType.CLAIM_BEM_SUPORTADO

    record = truth_repo.latest_record(issue.target_id)
    assert record is not None
    assert record.state.value == "ESTABLISHED_FACT"
    events = truth_repo.list_events(issue.target_id)
    assert events
    last_event = events[-1]
    assert last_event.new_state.value == "ESTABLISHED_FACT"
    assert last_event.debunk_issue_id == issue.id
    assert last_event.metadata.get("recommended_action") == RecommendedTruthAction.SUGERE_PROMOVER.value

    debunk_events = repo.list_events(issue.id)
    outcome_events = [evt for evt in debunk_events if evt.event_type == "OUTCOME_READY"]
    assert outcome_events, "DebunkOutcome deve gerar evento OUTCOME_READY para S25"
    assert outcome_events[-1].payload.get("truth_change_event_id") == last_event.id
    assert outcome_events[-1].payload.get("truth_state") == record.state.value
