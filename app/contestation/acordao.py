"""
Acordao Service — S41

Service for creating and managing Acordaos (final decisions) in the contestation module.
Implements the MAC (Máquina Adiabática de Consenso) decision process.

The Acordao is the authoritative resolution of a dispute, produced by:
1. Collecting votes from committee members (arbiters/validators)
2. Calculating the ethical tensor
3. Computing delta-crença (belief change) and lambda-factor (confidence)
4. Issuing the final reasoned decision
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.contestation.models import (
    AcordaoModel,
    AcordaoOutcome,
    DisputeCaseModel,
    TensorEticoResult,
    VoteRecord,
)
from app.contestation.tensor_ethic import TensorEthicCalculator, get_tensor_calculator

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _generate_id(prefix: str = "acrd") -> str:
    """Generate a unique ID with prefix."""
    from uuid import uuid4
    return f"{prefix}_{uuid4().hex[:12]}"


# Vote type mappings
VOTE_OUTCOMES = {
    "uphold": AcordaoOutcome.UPHELD,
    "overturn": AcordaoOutcome.OVERTURNED,
    "modify": AcordaoOutcome.MODIFIED,
    "remand": AcordaoOutcome.REMANDED,
}


@dataclass
class ConsensusMetrics:
    """Metrics about the consensus process."""

    total_votes: int = 0
    uphold_votes: int = 0
    overturn_votes: int = 0
    modify_votes: int = 0
    remand_votes: int = 0
    consensus_level: float = 0.0  # 0.0 to 1.0
    average_confidence: float = 0.0
    has_majority: bool = False
    majority_outcome: Optional[AcordaoOutcome] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_votes": self.total_votes,
            "uphold_votes": self.uphold_votes,
            "overturn_votes": self.overturn_votes,
            "modify_votes": self.modify_votes,
            "remand_votes": self.remand_votes,
            "consensus_level": self.consensus_level,
            "average_confidence": self.average_confidence,
            "has_majority": self.has_majority,
            "majority_outcome": self.majority_outcome.value if self.majority_outcome else None,
        }


@dataclass
class AcordaoRequest:
    """Request to create an acordao."""

    dispute_case_id: str
    original_decision_id: str
    votes: List[VoteRecord] = field(default_factory=list)
    tensor_etico: Optional[TensorEticoResult] = None
    precedents_cited: List[str] = field(default_factory=list)
    issued_by: str = ""
    custom_reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AcordaoService:
    """
    Service for creating and managing Acordaos.

    The AcordaoService implements the MAC decision process:
    1. Collect votes from committee members
    2. Calculate consensus metrics
    3. Compute delta-crença (belief change)
    4. Compute lambda-factor (confidence)
    5. Calculate ethical tensor
    6. Generate reasoned decision
    7. Issue the acordao
    """

    def __init__(
        self,
        tensor_calculator: Optional[TensorEthicCalculator] = None,
        min_votes_required: int = 1,
        majority_threshold: float = 0.5,
    ) -> None:
        """
        Initialize the acordao service.

        Args:
            tensor_calculator: Calculator for ethical tensor.
            min_votes_required: Minimum votes required for a decision.
            majority_threshold: Threshold for majority (0.0 to 1.0).
        """
        self._tensor_calculator = tensor_calculator or get_tensor_calculator()
        self._min_votes_required = min_votes_required
        self._majority_threshold = majority_threshold

        # In-memory storage (replace with repository in production)
        self._acordaos: Dict[str, AcordaoModel] = {}

    def create_acordao(
        self,
        request: AcordaoRequest,
        case: Optional[DisputeCaseModel] = None,
    ) -> AcordaoModel:
        """
        Create a new acordao from the request.

        Args:
            request: The acordao request with votes and metadata.
            case: Optional dispute case for tensor calculation.

        Returns:
            The created AcordaoModel.

        Raises:
            ValueError: If insufficient votes or no majority.
        """
        # Validate votes
        if len(request.votes) < self._min_votes_required:
            raise ValueError(
                f"Insufficient votes: {len(request.votes)} < {self._min_votes_required}"
            )

        # Calculate consensus metrics
        consensus = self._calculate_consensus(request.votes)

        if not consensus.has_majority:
            logger.warning(
                f"No majority reached for dispute {request.dispute_case_id}. "
                f"Consensus level: {consensus.consensus_level:.2%}"
            )
            # For MAC, we still proceed but note the lack of consensus

        # Determine outcome
        outcome = consensus.majority_outcome or AcordaoOutcome.UPHELD

        # Calculate delta-crença (belief change)
        delta_crenca = self._calculate_delta_crenca(consensus, request.votes)

        # Calculate lambda-factor (confidence)
        lambda_factor = self._calculate_lambda_factor(consensus, request.votes)

        # Calculate or use provided tensor
        tensor_etico = request.tensor_etico
        if tensor_etico is None and case is not None:
            tensor_etico = self._tensor_calculator.calculate_from_case(case)

        # Generate reasoning
        reasoning = request.custom_reasoning or self._generate_reasoning(
            outcome, consensus, delta_crenca, lambda_factor
        )

        # Generate summary
        summary = self._generate_summary(outcome, consensus)

        # Create the acordao
        acordao = AcordaoModel(
            id=_generate_id("acrd"),
            dispute_case_id=request.dispute_case_id,
            outcome=outcome,
            original_decision_id=request.original_decision_id,
            new_decision_id=None,  # Set later if overturned/modified
            votes=request.votes,
            delta_crenca=round(delta_crenca, 4),
            lambda_factor=round(lambda_factor, 4),
            tensor_etico=tensor_etico,
            reasoning=reasoning,
            summary=summary,
            precedents_cited=request.precedents_cited,
            dissenting_opinions=self._extract_dissenting_opinions(
                request.votes, outcome
            ),
            issued_at=_utcnow(),
            issued_by=request.issued_by,
            finalized=False,
            metadata={
                **request.metadata,
                "consensus_metrics": consensus.to_dict(),
            },
        )

        # Store
        self._acordaos[acordao.id] = acordao

        logger.info(
            f"Created acordao {acordao.id} for dispute {request.dispute_case_id}: "
            f"outcome={outcome.value}, delta_crenca={delta_crenca:.4f}, "
            f"lambda={lambda_factor:.4f}"
        )

        return acordao

    def _calculate_consensus(self, votes: List[VoteRecord]) -> ConsensusMetrics:
        """
        Calculate consensus metrics from votes.

        Args:
            votes: List of vote records.

        Returns:
            ConsensusMetrics with calculated values.
        """
        if not votes:
            return ConsensusMetrics()

        # Count votes by type
        uphold_count = sum(1 for v in votes if v.vote == "uphold")
        overturn_count = sum(1 for v in votes if v.vote == "overturn")
        modify_count = sum(1 for v in votes if v.vote == "modify")
        remand_count = sum(1 for v in votes if v.vote == "remand")

        total = len(votes)

        # Determine majority
        vote_counts = {
            AcordaoOutcome.UPHELD: uphold_count,
            AcordaoOutcome.OVERTURNED: overturn_count,
            AcordaoOutcome.MODIFIED: modify_count,
            AcordaoOutcome.REMANDED: remand_count,
        }

        max_count = max(vote_counts.values())
        majority_outcome = None
        has_majority = False

        if max_count > 0:
            for outcome, count in vote_counts.items():
                if count == max_count:
                    majority_outcome = outcome
                    break
            has_majority = (max_count / total) > self._majority_threshold

        # Calculate consensus level (how unified the votes are)
        consensus_level = max_count / total if total > 0 else 0.0

        # Calculate average confidence
        avg_confidence = sum(v.confidence for v in votes) / total if total > 0 else 0.0

        return ConsensusMetrics(
            total_votes=total,
            uphold_votes=uphold_count,
            overturn_votes=overturn_count,
            modify_votes=modify_count,
            remand_votes=remand_count,
            consensus_level=round(consensus_level, 4),
            average_confidence=round(avg_confidence, 4),
            has_majority=has_majority,
            majority_outcome=majority_outcome,
        )

    def _calculate_delta_crenca(
        self, consensus: ConsensusMetrics, votes: List[VoteRecord]
    ) -> float:
        """
        Calculate delta-crença (belief change).

        This measures how much the decision changes the belief state.
        A higher delta indicates a more significant shift from the original decision.

        Formula based on MAC guide:
        Δcrença = (1 - P(original)) × confidence_weighted_votes

        Args:
            consensus: Consensus metrics.
            votes: List of votes.

        Returns:
            Delta-crença value (-1.0 to 1.0).
        """
        if not votes:
            return 0.0

        # Calculate confidence-weighted change
        # Uphold = no change (0), Overturn = full change (1), Modify = partial (0.5)
        change_weights = {
            "uphold": 0.0,
            "overturn": 1.0,
            "modify": 0.5,
            "remand": 0.3,
        }

        total_weighted_change = 0.0
        total_confidence = 0.0

        for vote in votes:
            change = change_weights.get(vote.vote, 0.0)
            total_weighted_change += change * vote.confidence
            total_confidence += vote.confidence

        if total_confidence == 0:
            return 0.0

        # Normalize by total confidence
        delta = total_weighted_change / total_confidence

        # Apply consensus factor (higher consensus = stronger delta)
        delta *= consensus.consensus_level

        return delta

    def _calculate_lambda_factor(
        self, consensus: ConsensusMetrics, votes: List[VoteRecord]
    ) -> float:
        """
        Calculate lambda-factor (confidence factor).

        This measures the overall confidence in the decision.
        Combines:
        - Average vote confidence
        - Consensus level
        - Number of votes (more votes = higher confidence)

        Args:
            consensus: Consensus metrics.
            votes: List of votes.

        Returns:
            Lambda-factor value (0.0 to 1.0).
        """
        if not votes:
            return 0.0

        # Base from average confidence
        base_lambda = consensus.average_confidence

        # Boost from consensus level
        consensus_boost = consensus.consensus_level * 0.3

        # Boost from number of votes (logarithmic, caps at ~0.2 for many votes)
        vote_boost = 0.2 * math.log(len(votes) + 1) / math.log(10)
        vote_boost = min(0.2, vote_boost)

        # Combine
        lambda_factor = base_lambda * 0.5 + consensus_boost + vote_boost

        # Clamp to [0, 1]
        return max(0.0, min(1.0, lambda_factor))

    def _generate_reasoning(
        self,
        outcome: AcordaoOutcome,
        consensus: ConsensusMetrics,
        delta_crenca: float,
        lambda_factor: float,
    ) -> str:
        """
        Generate the reasoning text for the acordao.

        Args:
            outcome: The final outcome.
            consensus: Consensus metrics.
            delta_crenca: Delta-crença value.
            lambda_factor: Lambda-factor value.

        Returns:
            Reasoning text.
        """
        outcome_descriptions = {
            AcordaoOutcome.UPHELD: "A decisão original foi mantida",
            AcordaoOutcome.OVERTURNED: "A decisão original foi revertida",
            AcordaoOutcome.MODIFIED: "A decisão original foi modificada",
            AcordaoOutcome.REMANDED: "O caso foi devolvido para reavaliação",
        }

        reasoning_parts = [
            outcome_descriptions.get(outcome, "Decisão proferida"),
            f" com base em {consensus.total_votes} voto(s).",
        ]

        if consensus.consensus_level >= 0.8:
            reasoning_parts.append(
                f" O comitê alcançou alto nível de consenso ({consensus.consensus_level:.0%})."
            )
        elif consensus.consensus_level >= 0.6:
            reasoning_parts.append(
                f" O comitê alcançou consenso moderado ({consensus.consensus_level:.0%})."
            )
        else:
            reasoning_parts.append(
                f" O nível de consenso foi baixo ({consensus.consensus_level:.0%})."
            )

        if delta_crenca > 0.5:
            reasoning_parts.append(
                " Esta decisão representa uma mudança significativa em relação à posição original."
            )
        elif delta_crenca > 0.2:
            reasoning_parts.append(
                " Esta decisão representa uma mudança moderada em relação à posição original."
            )

        reasoning_parts.append(
            f" Fator de confiança: {lambda_factor:.0%}."
        )

        return "".join(reasoning_parts)

    def _generate_summary(
        self, outcome: AcordaoOutcome, consensus: ConsensusMetrics
    ) -> str:
        """
        Generate a brief summary of the acordao.

        Args:
            outcome: The final outcome.
            consensus: Consensus metrics.

        Returns:
            Summary text.
        """
        outcome_labels = {
            AcordaoOutcome.UPHELD: "MANTIDA",
            AcordaoOutcome.OVERTURNED: "REVERTIDA",
            AcordaoOutcome.MODIFIED: "MODIFICADA",
            AcordaoOutcome.REMANDED: "DEVOLVIDA",
        }

        label = outcome_labels.get(outcome, "DECIDIDA")
        return f"Decisão {label} ({consensus.total_votes} votos, {consensus.consensus_level:.0%} consenso)"

    def _extract_dissenting_opinions(
        self, votes: List[VoteRecord], majority_outcome: AcordaoOutcome
    ) -> List[str]:
        """
        Extract dissenting opinions from votes.

        Args:
            votes: List of votes.
            majority_outcome: The majority outcome.

        Returns:
            List of dissenting opinion strings.
        """
        majority_vote_str = {
            AcordaoOutcome.UPHELD: "uphold",
            AcordaoOutcome.OVERTURNED: "overturn",
            AcordaoOutcome.MODIFIED: "modify",
            AcordaoOutcome.REMANDED: "remand",
        }.get(majority_outcome, "uphold")

        dissenting = []
        for vote in votes:
            if vote.vote != majority_vote_str and vote.reasoning:
                dissenting.append(
                    f"[{vote.voter_id}]: {vote.reasoning}"
                )

        return dissenting

    def get_acordao(self, acordao_id: str) -> Optional[AcordaoModel]:
        """
        Get an acordao by ID.

        Args:
            acordao_id: The acordao ID.

        Returns:
            The acordao model or None if not found.
        """
        return self._acordaos.get(acordao_id)

    def finalize_acordao(self, acordao_id: str) -> AcordaoModel:
        """
        Finalize an acordao (make it immutable).

        Args:
            acordao_id: The acordao ID.

        Returns:
            The finalized acordao.

        Raises:
            ValueError: If acordao not found or already finalized.
        """
        acordao = self._acordaos.get(acordao_id)
        if acordao is None:
            raise ValueError(f"Acordao not found: {acordao_id}")

        if acordao.finalized:
            raise ValueError(f"Acordao already finalized: {acordao_id}")

        acordao.finalize()

        logger.info(f"Finalized acordao {acordao_id}")
        return acordao

    def list_acordaos(
        self,
        dispute_case_id: Optional[str] = None,
        finalized_only: bool = False,
        limit: int = 100,
    ) -> List[AcordaoModel]:
        """
        List acordaos with optional filters.

        Args:
            dispute_case_id: Filter by dispute case ID.
            finalized_only: Only return finalized acordaos.
            limit: Maximum number to return.

        Returns:
            List of acordao models.
        """
        results = []
        for acordao in self._acordaos.values():
            if dispute_case_id and acordao.dispute_case_id != dispute_case_id:
                continue
            if finalized_only and not acordao.finalized:
                continue
            results.append(acordao)
            if len(results) >= limit:
                break

        # Sort by issued_at descending
        results.sort(key=lambda a: a.issued_at, reverse=True)
        return results

    def clear(self) -> None:
        """Clear all stored acordaos (for testing)."""
        self._acordaos.clear()


# Singleton instance
_acordao_service: Optional[AcordaoService] = None


def get_acordao_service() -> AcordaoService:
    """Get or create the default AcordaoService instance."""
    global _acordao_service
    if _acordao_service is None:
        _acordao_service = AcordaoService()
    return _acordao_service


def reset_acordao_service() -> None:
    """Reset the global AcordaoService instance (for testing)."""
    global _acordao_service
    _acordao_service = None
