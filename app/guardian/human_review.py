"""
Guardian Human Review — S37

Human review queue and workflow management.
Handles reviewer assignment, review submission, and audit trail.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

from app.guardian.models import (
    CommitteeMember,
    Decision,
    DecisionStatus,
    Vote,
    VoteType,
)
from app.guardian.roles import GuardianRole

logger = logging.getLogger(__name__)


def _generate_id(prefix: str = "rev") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ReviewPriority(str, Enum):
    """Priority levels for human reviews."""

    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ReviewStatus(str, Enum):
    """Status of a review item."""

    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class ReviewItem:
    """An item in the human review queue."""

    id: str
    decision_id: str
    claim_id: str
    domain: str
    gate: str
    proposed_state: str
    priority: ReviewPriority = ReviewPriority.NORMAL
    status: ReviewStatus = ReviewStatus.QUEUED
    reason: Optional[str] = None
    context_summary: Dict[str, Any] = field(default_factory=dict)
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    review_result: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    expires_at: Optional[datetime] = None

    @classmethod
    def from_decision(
        cls,
        decision: Decision,
        priority: ReviewPriority = ReviewPriority.NORMAL,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> "ReviewItem":
        """Create a review item from a decision."""
        return cls(
            id=_generate_id("rev"),
            decision_id=decision.id,
            claim_id=decision.claim_id,
            domain=decision.domain,
            gate=decision.gate,
            proposed_state=decision.proposed_state,
            priority=priority,
            reason=reason,
            context_summary={
                k: v
                for k, v in decision.context.items()
                if k in ("evidence_count", "sources", "confidence_score", "entity_name")
            },
            expires_at=expires_at or decision.timeout_at,
        )

    def is_expired(self) -> bool:
        """Check if review has expired."""
        if self.expires_at is None:
            return False
        return _utcnow() > self.expires_at


@dataclass
class ReviewerInfo:
    """Information about a reviewer."""

    user_id: str
    name: str
    email: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    max_concurrent_reviews: int = 5
    active_reviews: int = 0
    total_reviews: int = 0
    avg_review_time_seconds: float = 0.0

    def can_accept_review(self) -> bool:
        """Check if reviewer can accept more reviews."""
        return self.active_reviews < self.max_concurrent_reviews


@dataclass
class ReviewSubmission:
    """A submitted review decision."""

    id: str
    review_item_id: str
    reviewer_id: str
    approved: bool
    notes: Optional[str] = None
    confidence: float = 1.0
    evidence_refs: List[str] = field(default_factory=list)
    submitted_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        review_item_id: str,
        reviewer_id: str,
        approved: bool,
        notes: Optional[str] = None,
        confidence: float = 1.0,
        evidence_refs: Optional[List[str]] = None,
    ) -> "ReviewSubmission":
        return cls(
            id=_generate_id("sub"),
            review_item_id=review_item_id,
            reviewer_id=reviewer_id,
            approved=approved,
            notes=notes,
            confidence=confidence,
            evidence_refs=evidence_refs or [],
        )


class ReviewQueue:
    """
    Human review queue manager.

    Manages the queue of decisions awaiting human review,
    reviewer assignments, and review submissions.
    """

    def __init__(self):
        self._queue: Dict[str, ReviewItem] = {}
        self._reviewers: Dict[str, ReviewerInfo] = {}
        self._submissions: Dict[str, ReviewSubmission] = {}
        self._decision_to_review: Dict[str, str] = {}  # decision_id -> review_id

    def add_to_queue(
        self,
        decision: Decision,
        priority: ReviewPriority = ReviewPriority.NORMAL,
        reason: Optional[str] = None,
    ) -> ReviewItem:
        """
        Add a decision to the review queue.

        Args:
            decision: Decision awaiting review
            priority: Review priority
            reason: Reason for human review

        Returns:
            Created ReviewItem
        """
        item = ReviewItem.from_decision(
            decision=decision,
            priority=priority,
            reason=reason,
        )
        self._queue[item.id] = item
        self._decision_to_review[decision.id] = item.id

        logger.info(
            f"Added to review queue: {item.id} "
            f"(decision={decision.id}, priority={priority.value})"
        )

        return item

    def get_queue(
        self,
        status: Optional[ReviewStatus] = None,
        domain: Optional[str] = None,
        priority: Optional[ReviewPriority] = None,
        assigned_to: Optional[str] = None,
    ) -> List[ReviewItem]:
        """
        Get review items from the queue.

        Args:
            status: Filter by status
            domain: Filter by domain
            priority: Filter by priority
            assigned_to: Filter by assigned reviewer

        Returns:
            List of matching ReviewItems
        """
        items = list(self._queue.values())

        if status:
            items = [i for i in items if i.status == status]
        if domain:
            items = [i for i in items if i.domain == domain]
        if priority:
            items = [i for i in items if i.priority == priority]
        if assigned_to:
            items = [i for i in items if i.assigned_to == assigned_to]

        # Sort by priority and creation time
        priority_order = {
            ReviewPriority.URGENT: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.NORMAL: 2,
            ReviewPriority.LOW: 3,
        }
        items.sort(key=lambda x: (priority_order[x.priority], x.created_at))

        return items

    def get_pending_reviews(self) -> List[ReviewItem]:
        """Get all reviews awaiting assignment."""
        return self.get_queue(status=ReviewStatus.QUEUED)

    def get_my_reviews(self, user_id: str) -> List[ReviewItem]:
        """Get reviews assigned to a specific user."""
        return self.get_queue(assigned_to=user_id)

    def get_review_item(self, item_id: str) -> Optional[ReviewItem]:
        """Get a specific review item."""
        return self._queue.get(item_id)

    def get_review_for_decision(self, decision_id: str) -> Optional[ReviewItem]:
        """Get the review item for a decision."""
        review_id = self._decision_to_review.get(decision_id)
        if review_id:
            return self._queue.get(review_id)
        return None

    def register_reviewer(
        self,
        user_id: str,
        name: str,
        email: Optional[str] = None,
        domains: Optional[List[str]] = None,
        max_concurrent: int = 5,
    ) -> ReviewerInfo:
        """Register a reviewer."""
        reviewer = ReviewerInfo(
            user_id=user_id,
            name=name,
            email=email,
            domains=domains or [],
            max_concurrent_reviews=max_concurrent,
        )
        self._reviewers[user_id] = reviewer
        logger.info(f"Registered reviewer: {user_id} ({name})")
        return reviewer

    def get_reviewer(self, user_id: str) -> Optional[ReviewerInfo]:
        """Get reviewer info."""
        return self._reviewers.get(user_id)

    def assign_review(
        self,
        item_id: str,
        user_id: str,
    ) -> ReviewItem:
        """
        Assign a review to a reviewer.

        Args:
            item_id: Review item ID
            user_id: Reviewer user ID

        Returns:
            Updated ReviewItem

        Raises:
            ValueError: If item not found or reviewer cannot accept
        """
        item = self._queue.get(item_id)
        if not item:
            raise ValueError(f"Review item not found: {item_id}")

        if item.status != ReviewStatus.QUEUED:
            raise ValueError(f"Review not available for assignment: {item_id}")

        reviewer = self._reviewers.get(user_id)
        if reviewer and not reviewer.can_accept_review():
            raise ValueError(f"Reviewer at capacity: {user_id}")

        # Update item
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = user_id
        item.assigned_at = _utcnow()

        # Update reviewer stats
        if reviewer:
            reviewer.active_reviews += 1

        logger.info(f"Review assigned: {item_id} -> {user_id}")

        return item

    def start_review(self, item_id: str) -> ReviewItem:
        """Mark a review as in progress."""
        item = self._queue.get(item_id)
        if not item:
            raise ValueError(f"Review item not found: {item_id}")

        if item.status != ReviewStatus.ASSIGNED:
            raise ValueError(f"Review not in assigned state: {item_id}")

        item.status = ReviewStatus.IN_PROGRESS

        logger.info(f"Review started: {item_id}")

        return item

    def submit_review(
        self,
        item_id: str,
        reviewer_id: str,
        approved: bool,
        notes: Optional[str] = None,
        confidence: float = 1.0,
        evidence_refs: Optional[List[str]] = None,
    ) -> ReviewSubmission:
        """
        Submit a review decision.

        Args:
            item_id: Review item ID
            reviewer_id: Reviewer user ID
            approved: Whether to approve
            notes: Review notes
            confidence: Confidence in decision
            evidence_refs: References to evidence

        Returns:
            ReviewSubmission record

        Raises:
            ValueError: If item not found or reviewer not assigned
        """
        item = self._queue.get(item_id)
        if not item:
            raise ValueError(f"Review item not found: {item_id}")

        if item.assigned_to != reviewer_id:
            raise ValueError(f"Review not assigned to this reviewer: {reviewer_id}")

        if item.status not in (ReviewStatus.ASSIGNED, ReviewStatus.IN_PROGRESS):
            raise ValueError(f"Review not in reviewable state: {item_id}")

        # Create submission
        submission = ReviewSubmission.create(
            review_item_id=item_id,
            reviewer_id=reviewer_id,
            approved=approved,
            notes=notes,
            confidence=confidence,
            evidence_refs=evidence_refs,
        )
        self._submissions[submission.id] = submission

        # Update item
        item.status = ReviewStatus.COMPLETED
        item.reviewed_at = _utcnow()
        item.review_result = "approved" if approved else "rejected"
        item.review_notes = notes

        # Update reviewer stats
        reviewer = self._reviewers.get(reviewer_id)
        if reviewer:
            reviewer.active_reviews = max(0, reviewer.active_reviews - 1)
            reviewer.total_reviews += 1
            # Update avg time
            if item.assigned_at:
                review_time = (
                    _utcnow() - item.assigned_at
                ).total_seconds()
                total = reviewer.total_reviews
                reviewer.avg_review_time_seconds = (
                    (reviewer.avg_review_time_seconds * (total - 1) + review_time)
                    / total
                )

        logger.info(
            f"Review submitted: {item_id} "
            f"(approved={approved}, reviewer={reviewer_id})"
        )

        return submission

    def cancel_review(self, item_id: str, reason: str = "cancelled") -> ReviewItem:
        """Cancel a review item."""
        item = self._queue.get(item_id)
        if not item:
            raise ValueError(f"Review item not found: {item_id}")

        old_status = item.status
        item.status = ReviewStatus.CANCELLED
        item.review_notes = reason

        # Update reviewer stats if was assigned
        if item.assigned_to:
            reviewer = self._reviewers.get(item.assigned_to)
            if reviewer and old_status in (
                ReviewStatus.ASSIGNED,
                ReviewStatus.IN_PROGRESS,
            ):
                reviewer.active_reviews = max(0, reviewer.active_reviews - 1)

        logger.info(f"Review cancelled: {item_id} ({reason})")

        return item

    def check_expired(self) -> List[ReviewItem]:
        """Check for and mark expired reviews."""
        expired = []
        for item in self._queue.values():
            if item.status in (
                ReviewStatus.QUEUED,
                ReviewStatus.ASSIGNED,
                ReviewStatus.IN_PROGRESS,
            ):
                if item.is_expired():
                    item.status = ReviewStatus.EXPIRED
                    expired.append(item)

                    # Update reviewer stats
                    if item.assigned_to:
                        reviewer = self._reviewers.get(item.assigned_to)
                        if reviewer:
                            reviewer.active_reviews = max(
                                0, reviewer.active_reviews - 1
                            )

                    logger.warning(f"Review expired: {item.id}")

        return expired

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        status_counts = {s.value: 0 for s in ReviewStatus}
        priority_counts = {p.value: 0 for p in ReviewPriority}
        domain_counts: Dict[str, int] = {}

        for item in self._queue.values():
            status_counts[item.status.value] += 1
            priority_counts[item.priority.value] += 1
            domain_counts[item.domain] = domain_counts.get(item.domain, 0) + 1

        return {
            "total_items": len(self._queue),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "by_domain": domain_counts,
            "total_reviewers": len(self._reviewers),
            "total_submissions": len(self._submissions),
        }


# Singleton instance
_queue: Optional[ReviewQueue] = None


def get_review_queue() -> ReviewQueue:
    """Get or create the default review queue instance."""
    global _queue
    if _queue is None:
        _queue = ReviewQueue()
    return _queue
