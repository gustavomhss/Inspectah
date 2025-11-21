"""Tipos compartilhados entre os comitês V1/V2/V3 da Sprint 15."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Sequence


class DecisionStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATE = "escalate"
    NEED_MORE_EVIDENCE = "need_more_evidence"
    BLOCKED = "blocked"


class VoteOutcome(str, Enum):
    AGREE = "agree"
    DISAGREE = "disagree"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class Reason:
    code: str
    description: str


@dataclass(slots=True)
class Vote:
    voter: str
    outcome: VoteOutcome
    reason: Reason
    weight: float = 1.0

    def to_dict(self) -> Dict[str, object]:
        return {
            "voter": self.voter,
            "outcome": self.outcome.value,
            "reason": {"code": self.reason.code, "description": self.reason.description},
            "weight": self.weight,
        }


@dataclass(slots=True)
class CommitteeDecision:
    layer: str
    status: DecisionStatus
    rationale: str
    votes: List[Vote] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)

    def approve_ratio(self) -> float:
        total = sum(v.weight for v in self.votes) or 1.0
        approvals = sum(v.weight for v in self.votes if v.outcome is VoteOutcome.AGREE)
        return approvals / total

    def to_dict(self) -> Dict[str, object]:
        return {
            "layer": self.layer,
            "status": self.status.value,
            "rationale": self.rationale,
            "votes": [v.to_dict() for v in self.votes],
            "metadata": self.metadata,
        }


def summarize_pipeline(decisions: Sequence[CommitteeDecision]) -> Dict[str, object]:
    return {
        "summary": {d.layer: d.status.value for d in decisions},
        "approvals": {d.layer: d.approve_ratio() for d in decisions},
    }


__all__ = [
    "CommitteeDecision",
    "DecisionStatus",
    "Reason",
    "Vote",
    "VoteOutcome",
    "summarize_pipeline",
]
