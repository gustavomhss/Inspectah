"""
Dispute Case FSM — S41

Finite State Machine for managing dispute cases in the contestation module.
Implements the lifecycle of a dispute from DRAFT to CLOSED.

Based on:
- P5-1: DisputeCase Appeal workflow
- MAC (Máquina Adiabática de Consenso) conceptual guide
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.contestation.models import (
    DisputeCaseModel,
    DisputeGround,
    DisputeStatus,
    EvidenceRef,
    EvidenceType,
    AppealType,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


# Valid state transitions
VALID_TRANSITIONS: Dict[DisputeStatus, List[DisputeStatus]] = {
    DisputeStatus.DRAFT: [DisputeStatus.FILED, DisputeStatus.REJECTED],
    DisputeStatus.FILED: [DisputeStatus.UNDER_TRIAGE, DisputeStatus.REJECTED],
    DisputeStatus.UNDER_TRIAGE: [
        DisputeStatus.INSTRUCTION,
        DisputeStatus.READY_FOR_DECISION,
        DisputeStatus.REJECTED,
    ],
    DisputeStatus.INSTRUCTION: [DisputeStatus.READY_FOR_DECISION],
    DisputeStatus.READY_FOR_DECISION: [DisputeStatus.DECIDED],
    DisputeStatus.DECIDED: [DisputeStatus.CLOSED],
    DisputeStatus.REJECTED: [DisputeStatus.CLOSED],
    DisputeStatus.CLOSED: [],  # Terminal state
}


@dataclass
class TransitionResult:
    """Result of a state transition attempt."""

    success: bool
    from_status: DisputeStatus
    to_status: DisputeStatus
    reason: str = ""
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitionRecord:
    """Record of a state transition."""

    from_status: DisputeStatus
    to_status: DisputeStatus
    actor_id: str
    reason: str = ""
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "actor_id": self.actor_id,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class DisputeCase:
    """
    Finite State Machine for managing a dispute case.

    This class wraps a DisputeCaseModel and provides state machine
    functionality for managing the lifecycle of a dispute.

    Lifecycle:
    DRAFT -> FILED -> UNDER_TRIAGE -> INSTRUCTION -> READY_FOR_DECISION -> DECIDED -> CLOSED
                  |                |
                  v                v
              REJECTED ---------> CLOSED

    Key invariants:
    - A case cannot transition to an invalid state
    - All transitions are recorded for audit
    - Certain transitions require preconditions (e.g., grounds for filing)
    """

    def __init__(self, model: Optional[DisputeCaseModel] = None) -> None:
        """
        Initialize the dispute case FSM.

        Args:
            model: Optional existing model. Creates new if None.
        """
        self.model = model or DisputeCaseModel()
        self._transitions: List[TransitionRecord] = []
        self._callbacks: Dict[str, List[Callable[[TransitionRecord], None]]] = {}

    @property
    def id(self) -> str:
        """Get the case ID."""
        return self.model.id

    @property
    def status(self) -> DisputeStatus:
        """Get the current status."""
        return self.model.status

    @property
    def claim_id(self) -> str:
        """Get the associated claim ID."""
        return self.model.claim_id

    @property
    def is_terminal(self) -> bool:
        """Check if the case is in a terminal state."""
        return self.model.status in (DisputeStatus.CLOSED, DisputeStatus.REJECTED)

    @property
    def is_active(self) -> bool:
        """Check if the case is actively being processed."""
        return self.model.status in (
            DisputeStatus.FILED,
            DisputeStatus.UNDER_TRIAGE,
            DisputeStatus.INSTRUCTION,
            DisputeStatus.READY_FOR_DECISION,
        )

    def can_transition_to(self, target_status: DisputeStatus) -> bool:
        """
        Check if a transition to the target status is valid.

        Args:
            target_status: The target status to transition to.

        Returns:
            True if the transition is valid, False otherwise.
        """
        valid_targets = VALID_TRANSITIONS.get(self.model.status, [])
        return target_status in valid_targets

    def transition(
        self,
        target_status: DisputeStatus,
        actor_id: str,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TransitionResult:
        """
        Attempt to transition to a new status.

        Args:
            target_status: The target status to transition to.
            actor_id: ID of the actor performing the transition.
            reason: Reason for the transition.
            metadata: Additional metadata for the transition.

        Returns:
            TransitionResult indicating success or failure.
        """
        current_status = self.model.status

        # Check if transition is valid
        if not self.can_transition_to(target_status):
            return TransitionResult(
                success=False,
                from_status=current_status,
                to_status=target_status,
                reason=f"Invalid transition from {current_status.value} to {target_status.value}",
            )

        # Check preconditions
        precondition_result = self._check_preconditions(target_status)
        if not precondition_result[0]:
            return TransitionResult(
                success=False,
                from_status=current_status,
                to_status=target_status,
                reason=precondition_result[1],
            )

        # Perform the transition
        self.model.status = target_status
        self.model.updated_at = _utcnow()

        # Update timestamps based on target status
        if target_status == DisputeStatus.FILED:
            self.model.filed_at = _utcnow()
        elif target_status == DisputeStatus.DECIDED:
            self.model.decided_at = _utcnow()
        elif target_status == DisputeStatus.CLOSED:
            self.model.closed_at = _utcnow()

        # Record the transition
        transition_record = TransitionRecord(
            from_status=current_status,
            to_status=target_status,
            actor_id=actor_id,
            reason=reason,
            metadata=metadata or {},
        )
        self._transitions.append(transition_record)

        # Fire callbacks
        self._fire_callbacks(target_status.value, transition_record)
        self._fire_callbacks("*", transition_record)  # Wildcard callbacks

        logger.info(
            f"Dispute case {self.id} transitioned from {current_status.value} "
            f"to {target_status.value} by {actor_id}"
        )

        return TransitionResult(
            success=True,
            from_status=current_status,
            to_status=target_status,
            reason=reason,
            metadata=metadata or {},
        )

    def _check_preconditions(self, target_status: DisputeStatus) -> Tuple[bool, str]:
        """
        Check preconditions for a transition.

        Args:
            target_status: The target status.

        Returns:
            Tuple of (success, error_message).
        """
        if target_status == DisputeStatus.FILED:
            # Must have at least one ground
            if not self.model.grounds:
                return False, "Cannot file case without grounds"
            # Must have claim_id
            if not self.model.claim_id:
                return False, "Cannot file case without claim_id"
            # Must have petitioner_id
            if not self.model.petitioner_id:
                return False, "Cannot file case without petitioner_id"

        elif target_status == DisputeStatus.READY_FOR_DECISION:
            # Must have evidence if coming from INSTRUCTION
            if self.model.status == DisputeStatus.INSTRUCTION:
                if not self.model.evidence:
                    return False, "Cannot proceed to decision without evidence"

        elif target_status == DisputeStatus.DECIDED:
            # Must have acordao_id
            if not self.model.acordao_id:
                return False, "Cannot mark as decided without acordao"

        return True, ""

    def file(self, actor_id: str, reason: str = "") -> TransitionResult:
        """
        File the dispute case.

        Args:
            actor_id: ID of the actor filing the case.
            reason: Reason for filing.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.FILED, actor_id, reason)

    def start_triage(self, actor_id: str, reason: str = "") -> TransitionResult:
        """
        Start triaging the case.

        Args:
            actor_id: ID of the actor starting triage.
            reason: Reason for starting triage.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.UNDER_TRIAGE, actor_id, reason)

    def start_instruction(self, actor_id: str, reason: str = "") -> TransitionResult:
        """
        Start the instruction phase (evidence gathering).

        Args:
            actor_id: ID of the actor starting instruction.
            reason: Reason for starting instruction.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.INSTRUCTION, actor_id, reason)

    def mark_ready_for_decision(
        self, actor_id: str, reason: str = ""
    ) -> TransitionResult:
        """
        Mark the case as ready for decision.

        Args:
            actor_id: ID of the actor marking ready.
            reason: Reason for marking ready.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.READY_FOR_DECISION, actor_id, reason)

    def decide(
        self, actor_id: str, acordao_id: str, reason: str = ""
    ) -> TransitionResult:
        """
        Mark the case as decided with an acordao.

        Args:
            actor_id: ID of the actor making the decision.
            acordao_id: ID of the acordao.
            reason: Reason for the decision.

        Returns:
            TransitionResult indicating success or failure.
        """
        self.model.acordao_id = acordao_id
        return self.transition(DisputeStatus.DECIDED, actor_id, reason)

    def close(self, actor_id: str, reason: str = "") -> TransitionResult:
        """
        Close the case.

        Args:
            actor_id: ID of the actor closing the case.
            reason: Reason for closing.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.CLOSED, actor_id, reason)

    def reject(self, actor_id: str, reason: str = "") -> TransitionResult:
        """
        Reject the case (dismiss without decision).

        Args:
            actor_id: ID of the actor rejecting the case.
            reason: Reason for rejection.

        Returns:
            TransitionResult indicating success or failure.
        """
        return self.transition(DisputeStatus.REJECTED, actor_id, reason)

    def add_ground(
        self,
        ground_type: AppealType,
        description: str,
        supporting_evidence: Optional[List[str]] = None,
        weight: float = 1.0,
    ) -> DisputeGround:
        """
        Add a ground for the dispute.

        Args:
            ground_type: Type of the ground.
            description: Description of the ground.
            supporting_evidence: IDs of supporting evidence.
            weight: Importance weight (0.0 to 1.0).

        Returns:
            The created ground.

        Raises:
            ValueError: If case is not in DRAFT status.
        """
        if self.model.status != DisputeStatus.DRAFT:
            raise ValueError(
                f"Cannot add grounds to case in status {self.model.status.value}"
            )

        ground = DisputeGround(
            ground_type=ground_type,
            description=description,
            supporting_evidence=supporting_evidence or [],
            weight=max(0.0, min(1.0, weight)),  # Clamp to [0.0, 1.0]
        )
        self.model.add_ground(ground)

        logger.debug(f"Added ground {ground.id} to case {self.id}")
        return ground

    def add_evidence(
        self,
        evidence_type: EvidenceType,
        description: str,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        submitted_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRef:
        """
        Add evidence to the dispute.

        Args:
            evidence_type: Type of the evidence.
            description: Description of the evidence.
            url: URL of the evidence (if applicable).
            content_hash: Hash of the evidence content.
            submitted_by: ID of the submitter.
            metadata: Additional metadata.

        Returns:
            The created evidence reference.

        Raises:
            ValueError: If case is in a terminal status.
        """
        if self.is_terminal:
            raise ValueError(
                f"Cannot add evidence to case in status {self.model.status.value}"
            )

        evidence = EvidenceRef(
            evidence_type=evidence_type,
            description=description,
            url=url,
            content_hash=content_hash,
            submitted_by=submitted_by,
            metadata=metadata or {},
        )
        self.model.add_evidence(evidence)

        logger.debug(f"Added evidence {evidence.id} to case {self.id}")
        return evidence

    def on_transition(
        self, status: str, callback: Callable[[TransitionRecord], None]
    ) -> None:
        """
        Register a callback for a specific status transition.

        Args:
            status: Status to trigger on, or "*" for all transitions.
            callback: Callback function to call.
        """
        if status not in self._callbacks:
            self._callbacks[status] = []
        self._callbacks[status].append(callback)

    def _fire_callbacks(self, status: str, record: TransitionRecord) -> None:
        """Fire callbacks for a status."""
        for callback in self._callbacks.get(status, []):
            try:
                callback(record)
            except Exception as e:
                logger.error(f"Callback error for status {status}: {e}")

    def get_transitions(self) -> List[TransitionRecord]:
        """Get all transition records."""
        return list(self._transitions)

    def get_valid_transitions(self) -> List[DisputeStatus]:
        """Get list of valid transitions from current status."""
        return VALID_TRANSITIONS.get(self.model.status, [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = self.model.to_dict()
        result["transitions"] = [t.to_dict() for t in self._transitions]
        result["valid_transitions"] = [s.value for s in self.get_valid_transitions()]
        return result

    @classmethod
    def create(
        cls,
        claim_id: str,
        original_decision_id: str,
        petitioner_id: str,
        petitioner_name: Optional[str] = None,
        domain: Optional[str] = None,
        risk_level: Optional[str] = None,
        priority: int = 0,
    ) -> "DisputeCase":
        """
        Create a new dispute case.

        Args:
            claim_id: ID of the claim being disputed.
            original_decision_id: ID of the original decision.
            petitioner_id: ID of the petitioner.
            petitioner_name: Name of the petitioner.
            domain: Domain of the dispute.
            risk_level: Risk level of the dispute.
            priority: Priority level (higher = more urgent).

        Returns:
            A new DisputeCase instance.
        """
        model = DisputeCaseModel(
            claim_id=claim_id,
            original_decision_id=original_decision_id,
            petitioner_id=petitioner_id,
            petitioner_name=petitioner_name,
            domain=domain,
            risk_level=risk_level,
            priority=priority,
        )
        return cls(model)
