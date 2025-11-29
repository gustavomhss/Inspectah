from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.truth.enums import TruthState


@dataclass
class PolicyEvaluationContext:
    domain: str
    current_state: TruthState
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    sources_count: int = 0
    has_debunk: bool = False
    human_required: bool = False


def build_basic_context(
    domain: str,
    current_state: TruthState,
    recommendation: Optional[str] = None,
    confidence: Optional[float] = None,
    sources_count: int = 0,
    has_debunk: bool = False,
    human_required: bool = False,
) -> PolicyEvaluationContext:
    return PolicyEvaluationContext(
        domain=domain,
        current_state=current_state,
        recommendation=recommendation,
        confidence=confidence,
        sources_count=sources_count,
        has_debunk=has_debunk,
        human_required=human_required,
    )
