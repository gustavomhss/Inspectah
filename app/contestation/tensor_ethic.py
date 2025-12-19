"""
Tensor Ético — S41

Calculates the ethical impact tensor for dispute cases.
Based on the MAC (Máquina Adiabática de Consenso) conceptual guide.

The Tensor Ético provides a multi-dimensional assessment of the ethical
implications of a dispute resolution, considering:
- Social impact (effect on society/community)
- Individual impact (effect on the specific individual)
- Precedent weight (how this affects future cases)
- Urgency factor (time sensitivity of the decision)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.contestation.models import (
    AppealType,
    DisputeCaseModel,
    DisputeGround,
    TensorEticoResult,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# Domain-specific ethical weights
DOMAIN_WEIGHTS: Dict[str, Dict[str, float]] = {
    "saude": {
        "social_impact": 1.2,
        "individual_impact": 1.5,
        "precedent_weight": 0.8,
        "urgency_factor": 1.3,
    },
    "governo": {
        "social_impact": 1.5,
        "individual_impact": 0.7,
        "precedent_weight": 1.2,
        "urgency_factor": 1.0,
    },
    "financeiro": {
        "social_impact": 0.9,
        "individual_impact": 1.3,
        "precedent_weight": 1.1,
        "urgency_factor": 1.2,
    },
    "educacao": {
        "social_impact": 1.3,
        "individual_impact": 1.1,
        "precedent_weight": 1.0,
        "urgency_factor": 0.8,
    },
    "default": {
        "social_impact": 1.0,
        "individual_impact": 1.0,
        "precedent_weight": 1.0,
        "urgency_factor": 1.0,
    },
}

# Risk level multipliers
RISK_MULTIPLIERS: Dict[str, float] = {
    "low": 0.5,
    "medium": 1.0,
    "high": 1.5,
    "critical": 2.0,
}

# Ground type impact on ethical tensor
GROUND_TYPE_IMPACTS: Dict[AppealType, Dict[str, float]] = {
    AppealType.FACTUAL: {
        "social_impact": 0.3,
        "individual_impact": 0.5,
        "precedent_weight": 0.2,
        "urgency_factor": 0.4,
    },
    AppealType.PROCEDURAL: {
        "social_impact": 0.4,
        "individual_impact": 0.3,
        "precedent_weight": 0.6,
        "urgency_factor": 0.3,
    },
    AppealType.ETHICAL: {
        "social_impact": 0.8,
        "individual_impact": 0.6,
        "precedent_weight": 0.5,
        "urgency_factor": 0.5,
    },
    AppealType.TECHNICAL: {
        "social_impact": 0.2,
        "individual_impact": 0.4,
        "precedent_weight": 0.3,
        "urgency_factor": 0.6,
    },
}


@dataclass
class TensorInput:
    """Input data for tensor calculation."""

    domain: str = "default"
    risk_level: str = "medium"
    grounds: List[DisputeGround] = field(default_factory=list)
    precedent_count: int = 0  # Number of similar previous cases
    days_since_filing: int = 0  # Days since the case was filed
    affected_parties: int = 1  # Number of affected parties
    public_interest: float = 0.5  # Public interest score (0.0 to 1.0)
    reversibility: float = 0.5  # How reversible is the decision (0.0 to 1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TensorEthicCalculator:
    """
    Calculator for the Ethical Tensor.

    The Tensor Ético is a multi-dimensional assessment of ethical implications.
    Each dimension is calculated as a value between -1.0 and 1.0, where:
    - Negative values indicate potential harm
    - Positive values indicate potential benefit
    - Zero indicates neutral impact

    The overall score is a weighted combination of all dimensions.
    """

    def __init__(
        self,
        domain_weights: Optional[Dict[str, Dict[str, float]]] = None,
        risk_multipliers: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Initialize the tensor calculator.

        Args:
            domain_weights: Custom domain weights (uses defaults if None).
            risk_multipliers: Custom risk multipliers (uses defaults if None).
        """
        self._domain_weights = domain_weights or DOMAIN_WEIGHTS
        self._risk_multipliers = risk_multipliers or RISK_MULTIPLIERS

    def calculate(self, tensor_input: TensorInput) -> TensorEticoResult:
        """
        Calculate the ethical tensor for a dispute case.

        Args:
            tensor_input: Input data for the calculation.

        Returns:
            TensorEticoResult with all calculated dimensions.
        """
        # Get domain-specific weights
        domain_weight = self._domain_weights.get(
            tensor_input.domain, self._domain_weights["default"]
        )

        # Get risk multiplier
        risk_mult = self._risk_multipliers.get(
            tensor_input.risk_level, RISK_MULTIPLIERS["medium"]
        )

        # Calculate individual dimensions
        social_impact = self._calculate_social_impact(tensor_input, domain_weight)
        individual_impact = self._calculate_individual_impact(
            tensor_input, domain_weight
        )
        precedent_weight = self._calculate_precedent_weight(tensor_input, domain_weight)
        urgency_factor = self._calculate_urgency_factor(tensor_input, domain_weight)

        # Apply risk multiplier
        social_impact *= risk_mult
        individual_impact *= risk_mult
        precedent_weight *= risk_mult
        urgency_factor *= risk_mult

        # Clamp values to [-1.0, 1.0] range
        social_impact = self._clamp(social_impact, -1.0, 1.0)
        individual_impact = self._clamp(individual_impact, -1.0, 1.0)
        precedent_weight = self._clamp(precedent_weight, 0.0, 1.0)
        urgency_factor = self._clamp(urgency_factor, 0.0, 1.0)

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            social_impact,
            individual_impact,
            precedent_weight,
            urgency_factor,
        )

        result = TensorEticoResult(
            social_impact=round(social_impact, 4),
            individual_impact=round(individual_impact, 4),
            precedent_weight=round(precedent_weight, 4),
            urgency_factor=round(urgency_factor, 4),
            overall_score=round(overall_score, 4),
            calculation_metadata={
                "domain": tensor_input.domain,
                "risk_level": tensor_input.risk_level,
                "risk_multiplier": risk_mult,
                "ground_count": len(tensor_input.grounds),
                "precedent_count": tensor_input.precedent_count,
                "days_since_filing": tensor_input.days_since_filing,
                "calculated_at": _utcnow().isoformat(),
            },
        )

        logger.debug(
            f"Tensor calculated for domain={tensor_input.domain}, "
            f"overall_score={overall_score:.4f}"
        )

        return result

    def _calculate_social_impact(
        self, tensor_input: TensorInput, domain_weight: Dict[str, float]
    ) -> float:
        """
        Calculate social impact dimension.

        Considers:
        - Number of affected parties
        - Public interest level
        - Ground types (ethical grounds have higher social impact)
        """
        base_score = 0.0

        # Contribution from affected parties (logarithmic scale)
        if tensor_input.affected_parties > 0:
            base_score += 0.2 * math.log(tensor_input.affected_parties + 1)

        # Contribution from public interest
        base_score += 0.3 * (tensor_input.public_interest - 0.5)

        # Contribution from grounds
        for ground in tensor_input.grounds:
            ground_impact = GROUND_TYPE_IMPACTS.get(
                ground.ground_type, GROUND_TYPE_IMPACTS[AppealType.FACTUAL]
            )
            base_score += ground_impact["social_impact"] * ground.weight

        # Apply domain weight
        base_score *= domain_weight.get("social_impact", 1.0)

        return base_score

    def _calculate_individual_impact(
        self, tensor_input: TensorInput, domain_weight: Dict[str, float]
    ) -> float:
        """
        Calculate individual impact dimension.

        Considers:
        - Reversibility of the decision
        - Ground types
        - Risk level
        """
        base_score = 0.0

        # Reversibility affects individual impact
        # Low reversibility = higher negative potential
        base_score += 0.4 * (0.5 - tensor_input.reversibility)

        # Contribution from grounds
        for ground in tensor_input.grounds:
            ground_impact = GROUND_TYPE_IMPACTS.get(
                ground.ground_type, GROUND_TYPE_IMPACTS[AppealType.FACTUAL]
            )
            base_score += ground_impact["individual_impact"] * ground.weight

        # Apply domain weight
        base_score *= domain_weight.get("individual_impact", 1.0)

        return base_score

    def _calculate_precedent_weight(
        self, tensor_input: TensorInput, domain_weight: Dict[str, float]
    ) -> float:
        """
        Calculate precedent weight dimension.

        Considers:
        - Number of similar previous cases
        - Ground types (procedural grounds affect precedent more)
        """
        base_score = 0.0

        # More precedents = more weight for consistency
        if tensor_input.precedent_count > 0:
            base_score += 0.3 * min(tensor_input.precedent_count / 10.0, 1.0)
        else:
            # No precedent = this could set precedent
            base_score += 0.5

        # Contribution from grounds
        for ground in tensor_input.grounds:
            ground_impact = GROUND_TYPE_IMPACTS.get(
                ground.ground_type, GROUND_TYPE_IMPACTS[AppealType.FACTUAL]
            )
            base_score += 0.2 * ground_impact["precedent_weight"] * ground.weight

        # Apply domain weight
        base_score *= domain_weight.get("precedent_weight", 1.0)

        return base_score

    def _calculate_urgency_factor(
        self, tensor_input: TensorInput, domain_weight: Dict[str, float]
    ) -> float:
        """
        Calculate urgency factor dimension.

        Considers:
        - Days since filing
        - Reversibility
        - Ground types
        """
        base_score = 0.5  # Start at neutral

        # Longer time = higher urgency
        if tensor_input.days_since_filing > 0:
            base_score += 0.1 * min(tensor_input.days_since_filing / 30.0, 0.4)

        # Lower reversibility = higher urgency
        base_score += 0.2 * (1.0 - tensor_input.reversibility)

        # Contribution from grounds
        for ground in tensor_input.grounds:
            ground_impact = GROUND_TYPE_IMPACTS.get(
                ground.ground_type, GROUND_TYPE_IMPACTS[AppealType.FACTUAL]
            )
            base_score += 0.1 * ground_impact["urgency_factor"] * ground.weight

        # Apply domain weight
        base_score *= domain_weight.get("urgency_factor", 1.0)

        return base_score

    def _calculate_overall_score(
        self,
        social_impact: float,
        individual_impact: float,
        precedent_weight: float,
        urgency_factor: float,
    ) -> float:
        """
        Calculate the overall ethical score.

        This is a weighted combination of all dimensions.
        """
        # Weights for each dimension
        weights = {
            "social": 0.30,
            "individual": 0.30,
            "precedent": 0.20,
            "urgency": 0.20,
        }

        # Normalize impact scores to [0, 1] for combination
        normalized_social = (social_impact + 1.0) / 2.0
        normalized_individual = (individual_impact + 1.0) / 2.0

        overall = (
            weights["social"] * normalized_social
            + weights["individual"] * normalized_individual
            + weights["precedent"] * precedent_weight
            + weights["urgency"] * urgency_factor
        )

        return overall

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp a value to a range."""
        return max(min_val, min(max_val, value))

    def calculate_from_case(self, case: DisputeCaseModel) -> TensorEticoResult:
        """
        Calculate the ethical tensor directly from a DisputeCaseModel.

        Args:
            case: The dispute case model.

        Returns:
            TensorEticoResult for the case.
        """
        # Calculate days since filing
        days_since_filing = 0
        if case.filed_at:
            delta = _utcnow() - case.filed_at
            days_since_filing = max(0, delta.days)

        tensor_input = TensorInput(
            domain=case.domain or "default",
            risk_level=case.risk_level or "medium",
            grounds=case.grounds,
            days_since_filing=days_since_filing,
            affected_parties=1,  # Default to 1, could be extracted from metadata
            public_interest=0.5,  # Default to neutral
            reversibility=0.5,  # Default to neutral
            metadata=case.metadata,
        )

        return self.calculate(tensor_input)


# Singleton instance
_calculator: Optional[TensorEthicCalculator] = None


def get_tensor_calculator() -> TensorEthicCalculator:
    """Get or create the default TensorEthicCalculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = TensorEthicCalculator()
    return _calculator


def calculate_tensor_etico(
    case: DisputeCaseModel,
) -> TensorEticoResult:
    """
    Convenience function to calculate tensor for a case.

    Args:
        case: The dispute case model.

    Returns:
        TensorEticoResult for the case.
    """
    return get_tensor_calculator().calculate_from_case(case)
