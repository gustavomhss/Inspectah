from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.debunk import service
from app.debunk.models import DebunkIssueStatus
from app.debunk.repository import DebunkRepository
from app.debunk.schemas import (
    DebunkDecisionCreate,
    DebunkDecisionResponse,
    DebunkIssueCreate,
    DebunkIssueOverview,
    DebunkIssueResponse,
    DebunkTaskCreate,
    DebunkTaskResponse,
)

router = APIRouter(prefix="/debunk", tags=["debunk"])


def get_repo() -> DebunkRepository:
    return DebunkRepository()


@router.post("/issues", response_model=DebunkIssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(payload: DebunkIssueCreate, repo: DebunkRepository = Depends(get_repo)):
    try:
        issue = service.open_issue(
            repo,
            target_type=payload.target_type,
            target_id=payload.target_id,
            question=payload.question,
            reason=payload.reason,
            risk_level=payload.risk_level,
            priority=payload.priority,
            origin=payload.origin,
            opened_by=payload.opened_by,
        )
    except service.DebunkDomainError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return issue


@router.get("/issues", response_model=List[DebunkIssueResponse])
def list_issues(statuses: str | None = None, repo: DebunkRepository = Depends(get_repo)):
    parsed = None
    if statuses:
        parsed = [DebunkIssueStatus(s) for s in statuses.split(",")]
    return repo.list_issues(parsed)


@router.get("/issues/{issue_id}", response_model=DebunkIssueOverview)
def get_issue(issue_id: str, repo: DebunkRepository = Depends(get_repo)):
    issue = repo.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue não encontrada")
    overview = service.issue_overview(repo, issue_id)
    return {
        "issue": overview["issue"],
        "tasks": overview["tasks"],
        "decisions": overview["decisions"],
    }


@router.post("/issues/{issue_id}/tasks", response_model=DebunkTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(issue_id: str, payload: DebunkTaskCreate, repo: DebunkRepository = Depends(get_repo)):
    try:
        task = service.add_task(
            repo,
            issue_id=issue_id,
            task_type=payload.task_type,
            instructions=payload.instructions,
            assigned_to=payload.assigned_to,
            due_at=payload.due_at,
        )
    except service.DebunkDomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return task


@router.post("/issues/{issue_id}/decisions", response_model=DebunkDecisionResponse, status_code=status.HTTP_201_CREATED)
def add_decision(issue_id: str, payload: DebunkDecisionCreate, repo: DebunkRepository = Depends(get_repo)):
    try:
        service.move_issue_status(
            repo,
            issue_id=issue_id,
            new_status=DebunkIssueStatus.READY_FOR_DECISION,
            actor=payload.created_by,
        )
        decision = service.record_decision(
            repo,
            issue_id=issue_id,
            decision_type=payload.decision_type,
            rationale=payload.rationale,
            recommended_truth_action=payload.recommended_truth_action,
            created_by=payload.created_by,
            confidence=payload.confidence,
            evidence_refs=payload.evidence_refs,
            residual_uncertainties=payload.residual_uncertainties,
        )
    except service.DebunkDomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return decision


@router.post("/issues/{issue_id}/status/{new_status}", response_model=DebunkIssueResponse)
def transition_issue(issue_id: str, new_status: DebunkIssueStatus, actor: str, repo: DebunkRepository = Depends(get_repo)):
    try:
        updated = service.move_issue_status(repo, issue_id=issue_id, new_status=new_status, actor=actor)
    except service.DebunkDomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return updated
