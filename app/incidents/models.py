from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Incident:
    id: str
    title: str
    summary: str
    domain: str
    severity: str
    status: str = "OPEN"
    related_claims: List[str] = field(default_factory=list)
    threat_signals: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)
    updated_at: str = field(default_factory=utcnow)
    ref_truth_record_id: str | None = None
    ref_case_id: str | None = None
    type: str = "threat_signal"
