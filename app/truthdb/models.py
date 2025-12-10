from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


class TruthState(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    PROVISIONAL = "PROVISIONAL"
    ESTABLISHED_FACT = "ESTABLISHED_FACT"
    UNDER_DISPUTE = "UNDER_DISPUTE"
    RETRACTED = "RETRACTED"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TruthRecord:
    claim_id: str
    state: TruthState
    version: int = 1
    metadata: Dict = field(default_factory=dict)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class TruthChangeEvent:
    id: str
    claim_id: str
    previous_state: Optional[TruthState]
    new_state: TruthState
    rationale: str
    source: str
    created_at: datetime = field(default_factory=utcnow)
    debunk_issue_id: Optional[str] = None
    decision_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class TruthStatus(str, Enum):
    """Estados canônicos usados na S32 para TruthState persistido."""

    PENDING = "PENDING"
    PROVISIONAL = "PROVISIONAL"
    TRUE = "TRUE"
    REJECTED = "REJECTED"
    CONTESTED = "CONTESTED"


FINAL_STATUSES = {TruthStatus.TRUE.value, TruthStatus.REJECTED.value}


@dataclass
class FactBlock:
    id: str
    claim_id: str
    content_hash: str
    created_at: datetime = field(default_factory=utcnow)
    metadata: Dict = field(default_factory=dict)


@dataclass
class EvidenceBlock:
    id: str
    fact_block_id: str
    evidence_type: str
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class DecisionBlock:
    id: str
    fact_block_id: str
    decision_type: str
    reasoning_summary: str | None = None
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class TruthStateRecord:
    id: str
    claim_id: str
    fact_block_id: str
    status: TruthStatus
    current_decision_block_id: Optional[str]
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class ContestRecord:
    id: str
    truth_state_id: str
    reason: str | None = None
    status: str = "PENDING"
    processed_decision_block_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    processed_at: Optional[datetime] = None
