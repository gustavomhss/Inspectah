from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Optional

from app.debunk.models import (
    DebunkDecision,
    DebunkDecisionType,
    DebunkIssue,
    DebunkIssueEvent,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTask,
    DebunkTaskStatus,
    DebunkTaskType,
    DebunkOutcome,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository, gen_id
from app.integration.s25_adapter import DebunkOutcomeResult, deliver_outcome


class DebunkDomainError(ValueError):
    pass


def _now() -> datetime:
    from app.debunk.models import utcnow

    return utcnow()


def open_issue(
    repo: Optional[DebunkRepository],
    *,
    target_type: DebunkIssueTarget,
    target_id: str,
    question: str,
    reason: str,
    risk_level: DebunkRiskLevel,
    priority: int,
    origin: str,
    opened_by: str,
    metadata: Optional[Dict] = None,
) -> DebunkIssue:
    repo = repo or DebunkRepository()
    existing = repo.find_open_issue_for_target(target_type, target_id)
    if existing:
        raise DebunkDomainError("Já existe issue aberta para este alvo.")
    issue = DebunkIssue(
        id=gen_id("dbi"),
        target_type=target_type,
        target_id=target_id,
        question=question.strip(),
        reason=reason.strip(),
        risk_level=risk_level,
        priority=priority,
        status=DebunkIssueStatus.OPEN,
        origin=origin,
        opened_by=opened_by,
        metadata=metadata or {},
    )
    repo.create_issue(issue)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="ISSUE_OPENED",
            payload={"reason": issue.reason, "risk_level": issue.risk_level.value, "priority": issue.priority},
            created_by=opened_by,
        )
    )
    return issue


def add_task(
    repo: Optional[DebunkRepository],
    *,
    issue_id: str,
    task_type: DebunkTaskType,
    instructions: str,
    assigned_to: Optional[str],
    due_at: Optional[datetime] = None,
) -> DebunkTask:
    repo = repo or DebunkRepository()
    issue = repo.get_issue(issue_id)
    if not issue:
        raise DebunkDomainError("Issue não encontrada para criação de tarefa.")
    task = DebunkTask(
        id=gen_id("dbt"),
        issue_id=issue_id,
        task_type=task_type,
        instructions=instructions.strip(),
        status=DebunkTaskStatus.PENDING,
        assigned_to=assigned_to,
        due_at=due_at,
    )
    repo.create_task(task)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="TASK_CREATED",
            payload={"task_id": task.id, "task_type": task.task_type.value},
            created_by=assigned_to,
        )
    )
    _maybe_transition(issue, repo, DebunkIssueStatus.TRIAGED)
    return task


def update_task_status(
    repo: Optional[DebunkRepository], *, task_id: str, new_status: DebunkTaskStatus, result: Optional[str], actor: Optional[str]
) -> DebunkTask:
    repo = repo or DebunkRepository()
    tasks_issue = _get_task_and_issue(repo, task_id)
    task, issue = tasks_issue
    task.status = new_status
    if result is not None:
        task.result = result
    task.updated_at = _now()
    repo.update_task(task)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="TASK_STATUS_CHANGED",
            payload={"task_id": task.id, "status": task.status.value},
            created_by=actor,
        )
    )
    _reevaluate_issue_status(repo, issue)
    return task


def record_decision(
    repo: Optional[DebunkRepository],
    *,
    issue_id: str,
    decision_type: DebunkDecisionType,
    rationale: str,
    recommended_truth_action: RecommendedTruthAction,
    created_by: str,
    confidence: Optional[float] = None,
    evidence_refs: Optional[List[str]] = None,
    residual_uncertainties: Optional[List[str]] = None,
) -> DebunkDecision:
    repo = repo or DebunkRepository()
    issue = repo.get_issue(issue_id)
    if not issue:
        raise DebunkDomainError("Issue não encontrada para decisão.")
    if issue.status not in {
        DebunkIssueStatus.READY_FOR_DECISION,
        DebunkIssueStatus.IN_REVIEW,
        DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
    }:
        raise DebunkDomainError(f"Issue em estado {issue.status.value} não aceita decisão.")
    decision = DebunkDecision(
        id=gen_id("dbd"),
        issue_id=issue_id,
        decision_type=decision_type,
        confidence=confidence,
        rationale=rationale.strip(),
        recommended_truth_action=recommended_truth_action,
        evidence_refs=evidence_refs or [],
        residual_uncertainties=residual_uncertainties or [],
        created_by=created_by,
    )
    repo.record_decision(decision)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="DECISION_RECORDED",
            payload={"decision_type": decision.decision_type.value, "recommended_truth_action": decision.recommended_truth_action.value},
            created_by=created_by,
        )
    )
    issue.status = DebunkIssueStatus.RESOLVED
    issue.updated_at = _now()
    repo.update_issue(issue)
    outcome_result = _emit_truth_change(issue, decision)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="OUTCOME_READY",
            payload={
                "decision_id": decision.id,
                "target_id": issue.target_id,
                "recommended_truth_action": decision.recommended_truth_action.value,
                "decision_type": decision.decision_type.value,
                "truth_change_event_id": outcome_result.event.id,
                "truth_state": outcome_result.record.state.value,
            },
            created_by=created_by,
        )
    )
    return decision


def _emit_truth_change(issue: DebunkIssue, decision: DebunkDecision) -> DebunkOutcomeResult:
    """Bridge DebunkOutcome into the TruthChangeEvent contract."""
    outcome = build_outcome(issue, decision)
    return deliver_outcome(outcome)


def build_outcome(issue: DebunkIssue, decision: DebunkDecision) -> DebunkOutcome:
    return DebunkOutcome(
        decision_id=decision.id,
        issue_id=issue.id,
        target_id=issue.target_id,
        recommended_truth_action=decision.recommended_truth_action,
        decision_type=decision.decision_type,
        rationale=decision.rationale,
        confidence=decision.confidence,
    )


def move_issue_status(repo: Optional[DebunkRepository], *, issue_id: str, new_status: DebunkIssueStatus, actor: str) -> DebunkIssue:
    repo = repo or DebunkRepository()
    issue = repo.get_issue(issue_id)
    if not issue:
        raise DebunkDomainError("Issue não encontrada.")
    if new_status == issue.status or getattr(issue.status, "value", None) == getattr(new_status, "value", None):
        return issue
    if not issue.can_transition_to(new_status):
        raise DebunkDomainError(f"Transição {issue.status.value} -> {new_status.value} inválida.")
    previous_status = issue.status
    issue.status = new_status
    issue.updated_at = _now()
    repo.update_issue(issue)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="ISSUE_STATUS_CHANGED",
            payload={"from": previous_status.value, "to": new_status.value},
            created_by=actor,
        )
    )
    return issue


def _get_task_and_issue(repo: DebunkRepository, task_id: str) -> tuple[DebunkTask, DebunkIssue]:
    with repo._conn() as conn:
        task_row = conn.execute(
            """
            SELECT t.*, i.status as issue_status, i.id as issue_id, i.target_type, i.target_id, i.question, i.reason,
                   i.risk_level, i.priority, i.origin, i.opened_by, i.created_at as issue_created_at,
                   i.updated_at as issue_updated_at, i.metadata as issue_metadata
            FROM debunk_tasks t JOIN debunk_issues i ON i.id = t.issue_id WHERE t.id=?
            """,
            (task_id,),
        ).fetchone()
    if not task_row:
        raise DebunkDomainError("Task não encontrada.")
    issue = repo._row_to_issue(
        {
            "id": task_row["issue_id"],
            "target_type": task_row["target_type"],
            "target_id": task_row["target_id"],
            "question": task_row["question"],
            "reason": task_row["reason"],
            "risk_level": task_row["risk_level"],
            "priority": task_row["priority"],
            "status": task_row["issue_status"],
            "origin": task_row["origin"],
            "opened_by": task_row["opened_by"],
            "created_at": task_row["issue_created_at"],
            "updated_at": task_row["issue_updated_at"],
            "metadata": task_row["issue_metadata"],
        }  # type: ignore[arg-type]
    )
    task = repo._row_to_task(task_row)
    return task, issue


def _maybe_transition(issue: DebunkIssue, repo: DebunkRepository, target_status: DebunkIssueStatus) -> None:
    if issue.can_transition_to(target_status):
        issue.status = target_status
        issue.updated_at = _now()
        repo.update_issue(issue)


def _reevaluate_issue_status(repo: DebunkRepository, issue: DebunkIssue) -> None:
    tasks = repo.list_tasks(issue.id)
    if tasks and all(t.status in {DebunkTaskStatus.DONE, DebunkTaskStatus.CANCELLED} for t in tasks):
        _maybe_transition(issue, repo, DebunkIssueStatus.READY_FOR_DECISION)
    elif any(t.status == DebunkTaskStatus.NEEDS_HUMAN_REVIEW for t in tasks):
        _maybe_transition(issue, repo, DebunkIssueStatus.IN_REVIEW)
    else:
        _maybe_transition(issue, repo, DebunkIssueStatus.TRIAGED)


def issue_overview(repo: Optional[DebunkRepository], issue_id: str) -> Dict:
    repo = repo or DebunkRepository()
    issue = repo.get_issue(issue_id)
    if not issue:
        raise DebunkDomainError("Issue não encontrada.")
    tasks = repo.list_tasks(issue_id)
    decisions = repo.list_decisions(issue_id)
    events = repo.list_events(issue_id)
    return {
        "issue": asdict(issue),
        "tasks": [asdict(t) for t in tasks],
        "decisions": [asdict(d) for d in decisions],
        "events": [asdict(e) for e in events],
    }
