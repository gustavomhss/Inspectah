from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.core.models import UserResponse


@dataclass
class UserQueryRequest:
    query: str
    demo_scenario: Optional[str] = None


@dataclass
class UserQueryResponse:
    query_id: str
    answer_text: str
    summary: Dict[str, Any]
    confidence: Dict[str, Any]
    limitations: List[str]
    evidence: Dict[str, Any]
    status: str
    evidence_bundle_id: Optional[str] = None

    @classmethod
    def from_user_response(cls, response: UserResponse) -> "UserQueryResponse":
        return cls(
            query_id=response.query_id,
            answer_text=response.answer_text,
            summary=response.summary,
            confidence=response.confidence,
            limitations=response.limitations,
            evidence=response.evidence,
            status=response.status,
            evidence_bundle_id=response.evidence_bundle_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
