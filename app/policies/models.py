from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.truth.enums import TruthState


@dataclass
class PromotionPolicyConfig:
    """
    Configuração declarativa de política de promoção/rebaixamento por domínio.
    """

    name: str
    domain: str
    min_confidence: float
    min_sources: int
    require_debunk: bool = False
    require_human: bool = False
    sensitive: bool = False
    default_decision: str = "HOLD"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    decision: str  # PROMOTE | HOLD | BLOCK
    reason: str
    policy_name: str
    flags: Dict[str, Any] = field(default_factory=dict)
    target_state: Optional[TruthState] = None
