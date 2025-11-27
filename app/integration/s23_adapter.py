from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.debunk import service
from app.debunk.models import DebunkIssueTarget, DebunkRiskLevel
from app.debunk.repository import DebunkRepository


class ConflictLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ClaimConflictSignal:
    claim_id: str
    conflict_level: ConflictLevel
    summary: str
    source: str = "s23"


def process_conflict_signal(repo: DebunkRepository, signal: ClaimConflictSignal) -> str | None:
    """Open a debunk issue for conflicting claims coming from S23."""
    if signal.conflict_level not in {ConflictLevel.HIGH, ConflictLevel.CRITICAL}:
        return None
    issue = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.CLAIM,
        target_id=signal.claim_id,
        question=f"Resolver conflito do claim {signal.claim_id}",
        reason=f"Signal de conflito ({signal.conflict_level.value}): {signal.summary}",
        risk_level=DebunkRiskLevel.HIGH,
        priority=9,
        origin=signal.source,
        opened_by="s23_pipeline",
    )
    return issue.id
