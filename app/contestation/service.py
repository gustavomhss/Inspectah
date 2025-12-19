"""
Contestation Service — S41

Main orchestration service for the contestation module.
Manages the complete lifecycle of dispute cases from filing to resolution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.contestation.models import (
    AcordaoOutcome,
    AppealType,
    DisputeCaseModel,
    DisputeGround,
    DisputeStatus,
    EvidenceRef,
    EvidenceType,
    VoteRecord,
)
from app.contestation.dispute_case import DisputeCase, TransitionResult
from app.contestation.acordao import (
    AcordaoModel,
    AcordaoRequest,
    AcordaoService,
    get_acordao_service,
)
from app.contestation.tensor_ethic import TensorEthicCalculator, get_tensor_calculator

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass
class ContestationStats:
    """Statistics about contestation cases."""

    total_cases: int = 0
    draft_cases: int = 0
    filed_cases: int = 0
    under_triage_cases: int = 0
    instruction_cases: int = 0
    ready_for_decision_cases: int = 0
    decided_cases: int = 0
    closed_cases: int = 0
    rejected_cases: int = 0
    upheld_count: int = 0
    overturned_count: int = 0
    modified_count: int = 0
    average_resolution_days: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_cases": self.total_cases,
            "draft_cases": self.draft_cases,
            "filed_cases": self.filed_cases,
            "under_triage_cases": self.under_triage_cases,
            "instruction_cases": self.instruction_cases,
            "ready_for_decision_cases": self.ready_for_decision_cases,
            "decided_cases": self.decided_cases,
            "closed_cases": self.closed_cases,
            "rejected_cases": self.rejected_cases,
            "upheld_count": self.upheld_count,
            "overturned_count": self.overturned_count,
            "modified_count": self.modified_count,
            "average_resolution_days": self.average_resolution_days,
        }


class ContestationService:
    """
    Main service for managing contestation workflows.

    This service orchestrates:
    - Creating and managing dispute cases
    - Transitioning cases through the FSM
    - Calculating ethical tensors
    - Creating acordaos
    - Tracking statistics

    Usage:
        service = ContestationService()

        # Create a new dispute
        case = service.create_dispute(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            grounds=[...],
        )

        # File the dispute
        service.file_dispute(case.id, actor_id="user_789")

        # Add evidence
        service.add_evidence(case.id, evidence_type=EvidenceType.DOCUMENT, ...)

        # Decide the dispute
        acordao = service.decide_dispute(case.id, votes=[...], actor_id="arbiter_001")
    """

    def __init__(
        self,
        acordao_service: Optional[AcordaoService] = None,
        tensor_calculator: Optional[TensorEthicCalculator] = None,
    ) -> None:
        """
        Initialize the contestation service.

        Args:
            acordao_service: Service for managing acordaos.
            tensor_calculator: Calculator for ethical tensors.
        """
        self._acordao_service = acordao_service or get_acordao_service()
        self._tensor_calculator = tensor_calculator or get_tensor_calculator()

        # In-memory storage (replace with repository in production)
        self._cases: Dict[str, DisputeCase] = {}

    def create_dispute(
        self,
        claim_id: str,
        original_decision_id: str,
        petitioner_id: str,
        petitioner_name: Optional[str] = None,
        domain: Optional[str] = None,
        risk_level: Optional[str] = None,
        priority: int = 0,
        grounds: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DisputeCase:
        """
        Create a new dispute case.

        Args:
            claim_id: ID of the claim being disputed.
            original_decision_id: ID of the original decision.
            petitioner_id: ID of the petitioner.
            petitioner_name: Name of the petitioner.
            domain: Domain of the dispute (e.g., "saude", "governo").
            risk_level: Risk level (e.g., "low", "medium", "high").
            priority: Priority level (higher = more urgent).
            grounds: Initial grounds for the dispute.
            metadata: Additional metadata.

        Returns:
            The created DisputeCase.
        """
        case = DisputeCase.create(
            claim_id=claim_id,
            original_decision_id=original_decision_id,
            petitioner_id=petitioner_id,
            petitioner_name=petitioner_name,
            domain=domain,
            risk_level=risk_level,
            priority=priority,
        )

        if metadata:
            case.model.metadata = metadata

        # Add initial grounds if provided
        if grounds:
            for ground_data in grounds:
                ground_type = ground_data.get("ground_type", AppealType.FACTUAL)
                if isinstance(ground_type, str):
                    ground_type = AppealType(ground_type)
                case.add_ground(
                    ground_type=ground_type,
                    description=ground_data.get("description", ""),
                    supporting_evidence=ground_data.get("supporting_evidence", []),
                    weight=ground_data.get("weight", 1.0),
                )

        # Store
        self._cases[case.id] = case

        logger.info(
            f"Created dispute case {case.id} for claim {claim_id} "
            f"by petitioner {petitioner_id}"
        )

        return case

    def get_dispute(self, case_id: str) -> Optional[DisputeCase]:
        """
        Get a dispute case by ID.

        Args:
            case_id: The case ID.

        Returns:
            The dispute case or None if not found.
        """
        return self._cases.get(case_id)

    def file_dispute(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        File a dispute case.

        Args:
            case_id: The case ID.
            actor_id: ID of the actor filing the case.
            reason: Reason for filing.

        Returns:
            TransitionResult indicating success or failure.

        Raises:
            ValueError: If case not found.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        result = case.file(actor_id, reason)

        if result.success:
            logger.info(f"Dispute case {case_id} filed by {actor_id}")

        return result

    def start_triage(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        Start triaging a dispute case.

        Args:
            case_id: The case ID.
            actor_id: ID of the actor starting triage.
            reason: Reason for starting triage.

        Returns:
            TransitionResult indicating success or failure.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        return case.start_triage(actor_id, reason)

    def start_instruction(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        Start the instruction phase for a case.

        Args:
            case_id: The case ID.
            actor_id: ID of the actor starting instruction.
            reason: Reason for starting instruction.

        Returns:
            TransitionResult indicating success or failure.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        return case.start_instruction(actor_id, reason)

    def add_ground(
        self,
        case_id: str,
        ground_type: AppealType,
        description: str,
        supporting_evidence: Optional[List[str]] = None,
        weight: float = 1.0,
    ) -> DisputeGround:
        """
        Add a ground to a dispute case.

        Args:
            case_id: The case ID.
            ground_type: Type of the ground.
            description: Description of the ground.
            supporting_evidence: IDs of supporting evidence.
            weight: Importance weight.

        Returns:
            The created ground.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        return case.add_ground(
            ground_type=ground_type,
            description=description,
            supporting_evidence=supporting_evidence,
            weight=weight,
        )

    def add_evidence(
        self,
        case_id: str,
        evidence_type: EvidenceType,
        description: str,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        submitted_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRef:
        """
        Add evidence to a dispute case.

        Args:
            case_id: The case ID.
            evidence_type: Type of the evidence.
            description: Description of the evidence.
            url: URL of the evidence.
            content_hash: Hash of the evidence content.
            submitted_by: ID of the submitter.
            metadata: Additional metadata.

        Returns:
            The created evidence reference.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        return case.add_evidence(
            evidence_type=evidence_type,
            description=description,
            url=url,
            content_hash=content_hash,
            submitted_by=submitted_by,
            metadata=metadata,
        )

    def mark_ready_for_decision(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        Mark a case as ready for decision.

        Args:
            case_id: The case ID.
            actor_id: ID of the actor.
            reason: Reason for marking ready.

        Returns:
            TransitionResult indicating success or failure.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        return case.mark_ready_for_decision(actor_id, reason)

    def decide_dispute(
        self,
        case_id: str,
        votes: List[VoteRecord],
        actor_id: str,
        precedents_cited: Optional[List[str]] = None,
        custom_reasoning: Optional[str] = None,
    ) -> AcordaoModel:
        """
        Decide a dispute case by creating an acordao.

        This is the culmination of the contestation process. It:
        1. Calculates the ethical tensor for the case
        2. Creates an acordao from the votes
        3. Transitions the case to DECIDED status
        4. Returns the acordao

        Args:
            case_id: The case ID.
            votes: List of vote records from the committee.
            actor_id: ID of the actor (typically the committee lead).
            precedents_cited: IDs of precedent cases.
            custom_reasoning: Custom reasoning text (optional).

        Returns:
            The created AcordaoModel.

        Raises:
            ValueError: If case not found or not ready for decision.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        if case.status != DisputeStatus.READY_FOR_DECISION:
            raise ValueError(
                f"Case {case_id} is not ready for decision "
                f"(current status: {case.status.value})"
            )

        # Calculate ethical tensor
        tensor = self._tensor_calculator.calculate_from_case(case.model)

        # Create acordao request
        request = AcordaoRequest(
            dispute_case_id=case_id,
            original_decision_id=case.model.original_decision_id,
            votes=votes,
            tensor_etico=tensor,
            precedents_cited=precedents_cited or [],
            issued_by=actor_id,
            custom_reasoning=custom_reasoning,
        )

        # Create acordao
        acordao = self._acordao_service.create_acordao(request, case.model)

        # Transition case to decided
        result = case.decide(actor_id, acordao.id, f"Acordao issued: {acordao.id}")
        if not result.success:
            logger.error(f"Failed to transition case {case_id} to decided: {result.reason}")

        logger.info(
            f"Decided dispute case {case_id} with acordao {acordao.id}: "
            f"outcome={acordao.outcome.value}"
        )

        return acordao

    def reject_dispute(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        Reject a dispute case (dismiss without decision).

        Args:
            case_id: The case ID.
            actor_id: ID of the actor rejecting.
            reason: Reason for rejection.

        Returns:
            TransitionResult indicating success or failure.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        result = case.reject(actor_id, reason)

        if result.success:
            logger.info(f"Dispute case {case_id} rejected by {actor_id}: {reason}")

        return result

    def close_dispute(
        self,
        case_id: str,
        actor_id: str,
        reason: str = "",
    ) -> TransitionResult:
        """
        Close a dispute case (final state).

        Args:
            case_id: The case ID.
            actor_id: ID of the actor closing.
            reason: Reason for closing.

        Returns:
            TransitionResult indicating success or failure.
        """
        case = self._cases.get(case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        result = case.close(actor_id, reason)

        if result.success:
            logger.info(f"Dispute case {case_id} closed by {actor_id}")

        return result

    def list_disputes(
        self,
        status: Optional[DisputeStatus] = None,
        petitioner_id: Optional[str] = None,
        domain: Optional[str] = None,
        claim_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[DisputeCase]:
        """
        List dispute cases with optional filters.

        Args:
            status: Filter by status.
            petitioner_id: Filter by petitioner.
            domain: Filter by domain.
            claim_id: Filter by claim ID.
            limit: Maximum number to return.

        Returns:
            List of dispute cases.
        """
        results = []
        for case in self._cases.values():
            if status and case.status != status:
                continue
            if petitioner_id and case.model.petitioner_id != petitioner_id:
                continue
            if domain and case.model.domain != domain:
                continue
            if claim_id and case.model.claim_id != claim_id:
                continue
            results.append(case)
            if len(results) >= limit:
                break

        # Sort by created_at descending
        results.sort(key=lambda c: c.model.created_at, reverse=True)
        return results

    def get_statistics(self) -> ContestationStats:
        """
        Get statistics about contestation cases.

        Returns:
            ContestationStats with current statistics.
        """
        stats = ContestationStats()
        total_resolution_days = 0.0
        decided_count = 0

        for case in self._cases.values():
            stats.total_cases += 1

            if case.status == DisputeStatus.DRAFT:
                stats.draft_cases += 1
            elif case.status == DisputeStatus.FILED:
                stats.filed_cases += 1
            elif case.status == DisputeStatus.UNDER_TRIAGE:
                stats.under_triage_cases += 1
            elif case.status == DisputeStatus.INSTRUCTION:
                stats.instruction_cases += 1
            elif case.status == DisputeStatus.READY_FOR_DECISION:
                stats.ready_for_decision_cases += 1
            elif case.status == DisputeStatus.DECIDED:
                stats.decided_cases += 1
            elif case.status == DisputeStatus.CLOSED:
                stats.closed_cases += 1
            elif case.status == DisputeStatus.REJECTED:
                stats.rejected_cases += 1

            # Calculate resolution time for decided/closed cases
            if case.model.decided_at and case.model.filed_at:
                delta = case.model.decided_at - case.model.filed_at
                total_resolution_days += delta.days
                decided_count += 1

            # Count acordao outcomes
            if case.model.acordao_id:
                acordao = self._acordao_service.get_acordao(case.model.acordao_id)
                if acordao:
                    if acordao.outcome == AcordaoOutcome.UPHELD:
                        stats.upheld_count += 1
                    elif acordao.outcome == AcordaoOutcome.OVERTURNED:
                        stats.overturned_count += 1
                    elif acordao.outcome == AcordaoOutcome.MODIFIED:
                        stats.modified_count += 1

        if decided_count > 0:
            stats.average_resolution_days = round(total_resolution_days / decided_count, 2)

        return stats

    def clear(self) -> None:
        """Clear all stored cases (for testing)."""
        self._cases.clear()


# Singleton instance
_contestation_service: Optional[ContestationService] = None


def get_contestation_service() -> ContestationService:
    """Get or create the default ContestationService instance."""
    global _contestation_service
    if _contestation_service is None:
        _contestation_service = ContestationService()
    return _contestation_service


def reset_contestation_service() -> None:
    """Reset the global ContestationService instance (for testing)."""
    global _contestation_service
    _contestation_service = None
