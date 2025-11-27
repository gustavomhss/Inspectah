from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.debunk.models import (
    DebunkDecisionType,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTaskStatus,
    DebunkTaskType,
    RecommendedTruthAction,
)


class DebunkIssueCreate(BaseModel):
    target_type: DebunkIssueTarget
    target_id: str
    question: str
    reason: str
    risk_level: DebunkRiskLevel = DebunkRiskLevel.MEDIUM
    priority: int = Field(ge=0, le=100)
    origin: str
    opened_by: str

    @validator("question", "reason", pre=True)
    def _strip(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("Campo obrigatório vazio.")
        return value


class DebunkIssueResponse(BaseModel):
    id: str
    target_type: DebunkIssueTarget
    target_id: str
    question: str
    reason: str
    risk_level: DebunkRiskLevel
    priority: int
    status: DebunkIssueStatus
    origin: str
    opened_by: str
    created_at: datetime
    updated_at: datetime


class DebunkTaskCreate(BaseModel):
    task_type: DebunkTaskType
    instructions: str
    assigned_to: Optional[str] = None
    due_at: Optional[datetime] = None


class DebunkTaskResponse(BaseModel):
    id: str
    issue_id: str
    task_type: DebunkTaskType
    instructions: str
    status: DebunkTaskStatus
    assigned_to: Optional[str]
    result: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime]


class DebunkDecisionCreate(BaseModel):
    decision_type: DebunkDecisionType
    rationale: str
    recommended_truth_action: RecommendedTruthAction
    created_by: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence_refs: List[str] = Field(default_factory=list)
    residual_uncertainties: List[str] = Field(default_factory=list)


class DebunkDecisionResponse(BaseModel):
    id: str
    issue_id: str
    decision_type: DebunkDecisionType
    confidence: Optional[float]
    rationale: str
    recommended_truth_action: RecommendedTruthAction
    evidence_refs: List[str]
    residual_uncertainties: List[str]
    created_by: str
    created_at: datetime


class DebunkIssueOverview(BaseModel):
    issue: DebunkIssueResponse
    tasks: List[DebunkTaskResponse]
    decisions: List[DebunkDecisionResponse]
