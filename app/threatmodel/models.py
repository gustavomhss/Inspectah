from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ThreatSignal:
    kind: str
    severity: str
    details: Dict[str, Any]
    domain: str
    created_at: str = field(default_factory=utcnow)


@dataclass
class ThreatMetricSnapshot:
    domain: str
    metrics: Dict[str, Any]
    signals: List[ThreatSignal] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)
