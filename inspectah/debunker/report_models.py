"""Modelos estruturados usados pelo Debunker v1 da Sprint 15.

Os relatórios precisam ser legíveis por humanos e por outras camadas
da pipeline (comitês V2/V3 e scripts de gates), por isso mantemos
dataclasses simples com conversão para dicionários.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Sequence


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(str, Enum):
    KEEP_STATE = "keep_state"
    QUESTIONED = "questioned"
    OPEN_DISPUTE = "open_dispute"
    ESCALATE = "escalate_committee"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    stance: str
    summary: str
    weight: float = 1.0
    source: str | None = None

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Contradiction:
    description: str
    evidence_ids: Sequence[str] = field(default_factory=tuple)
    severity: str = "medium"

    def to_dict(self) -> Dict[str, object]:
        return {
            "description": self.description,
            "evidence_ids": list(self.evidence_ids),
            "severity": self.severity,
        }


@dataclass(slots=True)
class DebunkerReport:
    claim_id: str
    domain: str
    risk: RiskLevel
    evidence_for: List[EvidenceItem] = field(default_factory=list)
    evidence_against: List[EvidenceItem] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)
    recommendation: Recommendation = Recommendation.QUESTIONED
    rationale: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "domain": self.domain,
            "risk": self.risk.value,
            "evidence_for": [item.to_dict() for item in self.evidence_for],
            "evidence_against": [item.to_dict() for item in self.evidence_against],
            "contradictions": [item.to_dict() for item in self.contradictions],
            "recommendation": self.recommendation.value,
            "rationale": self.rationale,
            "generated_at": self.generated_at.isoformat().replace("+00:00", "Z"),
            "meta": self.meta,
        }


__all__ = [
    "Contradiction",
    "DebunkerReport",
    "EvidenceItem",
    "Recommendation",
    "RiskLevel",
]
