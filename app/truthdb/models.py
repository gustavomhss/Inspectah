from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class TruthState(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    PROVISIONAL = "PROVISIONAL"
    ESTABLISHED_FACT = "ESTABLISHED_FACT"
    UNDER_DISPUTE = "UNDER_DISPUTE"
    RETRACTED = "RETRACTED"


def utcnow() -> datetime:
    return datetime.utcnow()


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
