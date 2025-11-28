from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .enums import TruthEventType, TruthState


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def gen_truth_record_id() -> str:
    return f"tr_{uuid4().hex[:12]}"


def gen_decision_id() -> str:
    return f"td_{uuid4().hex[:12]}"


def gen_event_id() -> str:
    return f"tce_{uuid4().hex[:12]}"


@dataclass
class TruthRecord:
    id: str
    slug: str
    domain: str
    current_state: TruthState
    claim_id: Optional[str] = None
    last_decision_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class DecisionRecord:
    id: str
    truth_record_id: str
    rationale: str
    decided_by: str
    policy_version: Optional[str] = None
    threat_snapshot: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class TruthChangeEvent:
    id: str
    truth_record_id: str
    previous_state: Optional[TruthState]
    new_state: TruthState
    event_type: Optional[TruthEventType] = None
    reason: str = ""
    source: str = ""
    decision_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
