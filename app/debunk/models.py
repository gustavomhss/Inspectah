from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class DebunkIssueTarget(str, Enum):
    CLAIM = "CLAIM"
    COMMITTEE_DECISION = "COMMITTEE_DECISION"
    TRUTH_RECORD = "TRUTH_RECORD"


class DebunkIssueStatus(str, Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_REVIEW = "IN_REVIEW"
    PENDING_ADDITIONAL_EVIDENCE = "PENDING_ADDITIONAL_EVIDENCE"
    READY_FOR_DECISION = "READY_FOR_DECISION"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    CLOSED_WITH_DOUBT = "CLOSED_WITH_DOUBT"


class DebunkRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DebunkTaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class DebunkTaskType(str, Enum):
    FACT_CHECK = "FACT_CHECK"
    SOURCE_COMPARE = "SOURCE_COMPARE"
    CONSISTENCY_CHECK = "CONSISTENCY_CHECK"
    HUMAN_SUMMARY = "HUMAN_SUMMARY"
    AGENT_REVIEW = "AGENT_REVIEW"


class DebunkDecisionType(str, Enum):
    CLAIM_NAO_SUPORTADO = "CLAIM_NAO_SUPORTADO"
    CLAIM_POUCO_SUPORTADO = "CLAIM_POUCO_SUPORTADO"
    CLAIM_PLAUSIVEL_MAS_INCOMPLETO = "CLAIM_PLAUSIVEL_MAS_INCOMPLETO"
    CLAIM_BEM_SUPORTADO = "CLAIM_BEM_SUPORTADO"
    DADOS_INCONCLUSIVOS = "DADOS_INCONCLUSIVOS"


class RecommendedTruthAction(str, Enum):
    SUGERE_REBAIXAR = "SUGERE_REBAIXAR"
    SUGERE_PROMOVER = "SUGERE_PROMOVER"
    MANTER_ESTADO_ATUAL = "MANTER_ESTADO_ATUAL"
    MARCAR_EM_DISPUTA = "MARCAR_EM_DISPUTA"


def utcnow() -> datetime:
    return datetime.utcnow()


@dataclass
class DebunkIssue:
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
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    metadata: Dict = field(default_factory=dict)

    def can_transition_to(self, new_status: DebunkIssueStatus) -> bool:
        if self.status == DebunkIssueStatus.RESOLVED and new_status != DebunkIssueStatus.ESCALATED:
            return False
        allowed: Dict[DebunkIssueStatus, List[DebunkIssueStatus]] = {
            DebunkIssueStatus.OPEN: [
                DebunkIssueStatus.TRIAGED,
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
            ],
            DebunkIssueStatus.TRIAGED: [
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
                DebunkIssueStatus.READY_FOR_DECISION,
            ],
            DebunkIssueStatus.IN_REVIEW: [
                DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
                DebunkIssueStatus.READY_FOR_DECISION,
                DebunkIssueStatus.RESOLVED,
                DebunkIssueStatus.ESCALATED,
            ],
            DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE: [
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.READY_FOR_DECISION,
                DebunkIssueStatus.ESCALATED,
            ],
            DebunkIssueStatus.READY_FOR_DECISION: [
                DebunkIssueStatus.RESOLVED,
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.ESCALATED,
            ],
            DebunkIssueStatus.RESOLVED: [DebunkIssueStatus.ESCALATED, DebunkIssueStatus.CLOSED_WITH_DOUBT],
            DebunkIssueStatus.ESCALATED: [
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.READY_FOR_DECISION,
                DebunkIssueStatus.RESOLVED,
            ],
            DebunkIssueStatus.CLOSED_WITH_DOUBT: [],
        }
        return new_status in allowed[self.status]


@dataclass
class DebunkTask:
    id: str
    issue_id: str
    task_type: DebunkTaskType
    instructions: str
    status: DebunkTaskStatus
    assigned_to: Optional[str] = None
    result: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    due_at: Optional[datetime] = None


@dataclass
class DebunkDecision:
    id: str
    issue_id: str
    decision_type: DebunkDecisionType
    confidence: Optional[float]
    rationale: str
    recommended_truth_action: RecommendedTruthAction
    evidence_refs: List[str] = field(default_factory=list)
    residual_uncertainties: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class DebunkOutcome:
    decision_id: str
    issue_id: str
    target_id: str
    recommended_truth_action: RecommendedTruthAction
    decision_type: DebunkDecisionType
    rationale: str
    confidence: Optional[float]


@dataclass
class DebunkIssueEvent:
    id: str
    issue_id: str
    event_type: str
    payload: Dict
    created_by: Optional[str]
    created_at: datetime = field(default_factory=utcnow)
