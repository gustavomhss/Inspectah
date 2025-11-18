from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from app.core.models import UserResponse
from app.core.query_types import to_legacy_query_type


@dataclass
class UserQueryRequest:
    question: str
    scenario_id: Optional[str] = None
    info_type: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserQueryResponse:
    query_id: str
    response_id: str
    info_type: str
    query_type: str
    legacy_query_type: str
    answer_text: str
    summary: Dict[str, Any]
    summary_card: Dict[str, Any]
    evidence: Dict[str, Any]
    evidence_links: Dict[str, Any]
    status: str
    confidence: Dict[str, Any]
    limitations: List[str]
    scenario_id: Optional[str] = None

    @classmethod
    def from_core_response(
        cls,
        response: UserResponse,
        summary_card: Dict[str, Any],
        evidence_links: Dict[str, Any],
        scenario_id: Optional[str],
    ) -> "UserQueryResponse":
        summary = _public_summary(response.summary)
        return cls(
            query_id=response.query_id,
            response_id=response.id,
            info_type=response.info_type,
            query_type=response.query_type,
            legacy_query_type=to_legacy_query_type(response.query_type),
            answer_text=response.answer_text,
            summary=summary,
            summary_card=summary_card,
            evidence=response.evidence,
            evidence_links=evidence_links,
            status=response.status,
            confidence=response.confidence,
            limitations=response.limitations,
            scenario_id=scenario_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _public_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    filtered = {k: v for k, v in summary.items() if k not in {"info_type", "scenario_tag"}}
    return filtered
