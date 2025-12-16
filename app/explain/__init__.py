"""
S39: Explainability Service

Provides explanations and reasoning paths for system decisions.
"""

from app.explain.service import (
    ExplainabilityService,
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    Counterfactual,
    ExplanationType,
    get_service,
)

from app.explain.drilldown import (
    DrilldownService,
    DrilldownResult,
    EvidenceDetail,
)

__all__ = [
    # Service
    "ExplainabilityService",
    "Explanation",
    "ReasoningStep",
    "ExplanationFactor",
    "Counterfactual",
    "ExplanationType",
    "get_service",
    # Drilldown
    "DrilldownService",
    "DrilldownResult",
    "EvidenceDetail",
]
