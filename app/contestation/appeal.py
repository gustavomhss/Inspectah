"""
Appeal Service — S41

Service for managing appeals in the contestation module.
Handles the process of challenging an acordao decision.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _generate_id(prefix: str = "apl") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


class AppealStatus(str, Enum):
    """Status of an appeal."""

    DRAFT = "draft"
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"


class AppealBasis(str, Enum):
    """Basis for an appeal."""

    NEW_EVIDENCE = "new_evidence"  # New evidence discovered
    PROCEDURAL_ERROR = "procedural_error"  # Error in process
    BIAS = "bias"  # Allegation of bias
    LEGAL_ERROR = "legal_error"  # Error in applying rules
    FACTUAL_ERROR = "factual_error"  # Error in fact determination


@dataclass
class AppealModel:
    """Model representing an appeal of an acordao."""

    id: str = field(default_factory=lambda: _generate_id("apl"))
    acordao_id: str = ""
    dispute_case_id: str = ""
    appellant_id: str = ""
    appellant_name: Optional[str] = None
    status: AppealStatus = AppealStatus.DRAFT
    basis: AppealBasis = AppealBasis.NEW_EVIDENCE
    grounds: str = ""
    new_evidence_ids: List[str] = field(default_factory=list)
    response: Optional[str] = None
    decision: Optional[str] = None
    decision_by: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    filed_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "acordao_id": self.acordao_id,
            "dispute_case_id": self.dispute_case_id,
            "appellant_id": self.appellant_id,
            "appellant_name": self.appellant_name,
            "status": self.status.value,
            "basis": self.basis.value,
            "grounds": self.grounds,
            "new_evidence_ids": self.new_evidence_ids,
            "response": self.response,
            "decision": self.decision,
            "decision_by": self.decision_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "filed_at": self.filed_at.isoformat() if self.filed_at else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "metadata": self.metadata,
        }


class AppealService:
    """
    Service for managing appeals.

    Appeals are challenges to acordao decisions. They follow a simplified
    lifecycle: DRAFT -> FILED -> UNDER_REVIEW -> ACCEPTED/REJECTED -> CLOSED

    If an appeal is accepted, it may trigger a new dispute case or
    modify the original acordao.
    """

    def __init__(self) -> None:
        """Initialize the appeal service."""
        # In-memory storage (replace with repository in production)
        self._appeals: Dict[str, AppealModel] = {}

    def create_appeal(
        self,
        acordao_id: str,
        dispute_case_id: str,
        appellant_id: str,
        basis: AppealBasis,
        grounds: str,
        appellant_name: Optional[str] = None,
        new_evidence_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AppealModel:
        """
        Create a new appeal.

        Args:
            acordao_id: ID of the acordao being appealed.
            dispute_case_id: ID of the original dispute case.
            appellant_id: ID of the appellant.
            basis: Basis for the appeal.
            grounds: Textual grounds for the appeal.
            appellant_name: Name of the appellant.
            new_evidence_ids: IDs of new evidence being submitted.
            metadata: Additional metadata.

        Returns:
            The created AppealModel.
        """
        appeal = AppealModel(
            acordao_id=acordao_id,
            dispute_case_id=dispute_case_id,
            appellant_id=appellant_id,
            appellant_name=appellant_name,
            basis=basis,
            grounds=grounds,
            new_evidence_ids=new_evidence_ids or [],
            metadata=metadata or {},
        )

        self._appeals[appeal.id] = appeal

        logger.info(
            f"Created appeal {appeal.id} for acordao {acordao_id} "
            f"by appellant {appellant_id}"
        )

        return appeal

    def file_appeal(
        self,
        appeal_id: str,
        actor_id: str,
    ) -> AppealModel:
        """
        File an appeal (transition from DRAFT to FILED).

        Args:
            appeal_id: The appeal ID.
            actor_id: ID of the actor filing.

        Returns:
            The updated appeal.

        Raises:
            ValueError: If appeal not found or not in DRAFT status.
        """
        appeal = self._appeals.get(appeal_id)
        if appeal is None:
            raise ValueError(f"Appeal not found: {appeal_id}")

        if appeal.status != AppealStatus.DRAFT:
            raise ValueError(
                f"Cannot file appeal in status {appeal.status.value}"
            )

        if not appeal.grounds:
            raise ValueError("Cannot file appeal without grounds")

        appeal.status = AppealStatus.FILED
        appeal.filed_at = _utcnow()
        appeal.updated_at = _utcnow()

        logger.info(f"Appeal {appeal_id} filed by {actor_id}")

        return appeal

    def start_review(
        self,
        appeal_id: str,
        actor_id: str,
    ) -> AppealModel:
        """
        Start reviewing an appeal.

        Args:
            appeal_id: The appeal ID.
            actor_id: ID of the reviewer.

        Returns:
            The updated appeal.
        """
        appeal = self._appeals.get(appeal_id)
        if appeal is None:
            raise ValueError(f"Appeal not found: {appeal_id}")

        if appeal.status != AppealStatus.FILED:
            raise ValueError(
                f"Cannot start review for appeal in status {appeal.status.value}"
            )

        appeal.status = AppealStatus.UNDER_REVIEW
        appeal.updated_at = _utcnow()

        logger.info(f"Appeal {appeal_id} under review by {actor_id}")

        return appeal

    def accept_appeal(
        self,
        appeal_id: str,
        decision: str,
        decision_by: str,
    ) -> AppealModel:
        """
        Accept an appeal.

        Args:
            appeal_id: The appeal ID.
            decision: Decision text explaining the acceptance.
            decision_by: ID of the decision maker.

        Returns:
            The updated appeal.
        """
        appeal = self._appeals.get(appeal_id)
        if appeal is None:
            raise ValueError(f"Appeal not found: {appeal_id}")

        if appeal.status != AppealStatus.UNDER_REVIEW:
            raise ValueError(
                f"Cannot accept appeal in status {appeal.status.value}"
            )

        appeal.status = AppealStatus.ACCEPTED
        appeal.decision = decision
        appeal.decision_by = decision_by
        appeal.decided_at = _utcnow()
        appeal.updated_at = _utcnow()

        logger.info(f"Appeal {appeal_id} accepted by {decision_by}")

        return appeal

    def reject_appeal(
        self,
        appeal_id: str,
        decision: str,
        decision_by: str,
    ) -> AppealModel:
        """
        Reject an appeal.

        Args:
            appeal_id: The appeal ID.
            decision: Decision text explaining the rejection.
            decision_by: ID of the decision maker.

        Returns:
            The updated appeal.
        """
        appeal = self._appeals.get(appeal_id)
        if appeal is None:
            raise ValueError(f"Appeal not found: {appeal_id}")

        if appeal.status != AppealStatus.UNDER_REVIEW:
            raise ValueError(
                f"Cannot reject appeal in status {appeal.status.value}"
            )

        appeal.status = AppealStatus.REJECTED
        appeal.decision = decision
        appeal.decision_by = decision_by
        appeal.decided_at = _utcnow()
        appeal.updated_at = _utcnow()

        logger.info(f"Appeal {appeal_id} rejected by {decision_by}")

        return appeal

    def close_appeal(
        self,
        appeal_id: str,
        actor_id: str,
    ) -> AppealModel:
        """
        Close an appeal.

        Args:
            appeal_id: The appeal ID.
            actor_id: ID of the actor closing.

        Returns:
            The updated appeal.
        """
        appeal = self._appeals.get(appeal_id)
        if appeal is None:
            raise ValueError(f"Appeal not found: {appeal_id}")

        if appeal.status not in (AppealStatus.ACCEPTED, AppealStatus.REJECTED):
            raise ValueError(
                f"Cannot close appeal in status {appeal.status.value}"
            )

        appeal.status = AppealStatus.CLOSED
        appeal.updated_at = _utcnow()

        logger.info(f"Appeal {appeal_id} closed by {actor_id}")

        return appeal

    def get_appeal(self, appeal_id: str) -> Optional[AppealModel]:
        """Get an appeal by ID."""
        return self._appeals.get(appeal_id)

    def list_appeals(
        self,
        acordao_id: Optional[str] = None,
        appellant_id: Optional[str] = None,
        status: Optional[AppealStatus] = None,
        limit: int = 100,
    ) -> List[AppealModel]:
        """
        List appeals with optional filters.

        Args:
            acordao_id: Filter by acordao ID.
            appellant_id: Filter by appellant ID.
            status: Filter by status.
            limit: Maximum number to return.

        Returns:
            List of appeals.
        """
        results = []
        for appeal in self._appeals.values():
            if acordao_id and appeal.acordao_id != acordao_id:
                continue
            if appellant_id and appeal.appellant_id != appellant_id:
                continue
            if status and appeal.status != status:
                continue
            results.append(appeal)
            if len(results) >= limit:
                break

        # Sort by created_at descending
        results.sort(key=lambda a: a.created_at, reverse=True)
        return results

    def clear(self) -> None:
        """Clear all stored appeals (for testing)."""
        self._appeals.clear()


# Singleton instance
_appeal_service: Optional[AppealService] = None


def get_appeal_service() -> AppealService:
    """Get or create the default AppealService instance."""
    global _appeal_service
    if _appeal_service is None:
        _appeal_service = AppealService()
    return _appeal_service


def reset_appeal_service() -> None:
    """Reset the global AppealService instance (for testing)."""
    global _appeal_service
    _appeal_service = None
