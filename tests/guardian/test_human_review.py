"""
Tests for Guardian Human Review — S37

Tests for human review queue and workflow management.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from app.guardian.human_review import (
    ReviewPriority,
    ReviewStatus,
    ReviewItem,
    ReviewerInfo,
    ReviewSubmission,
    ReviewQueue,
    get_review_queue,
    _generate_id,
    _utcnow,
)
from app.guardian.models import Decision, DecisionStatus


class TestReviewPriority:
    """Tests for ReviewPriority enum."""

    def test_priority_values(self):
        """Priority enum has expected values."""
        assert ReviewPriority.URGENT.value == "urgent"
        assert ReviewPriority.HIGH.value == "high"
        assert ReviewPriority.NORMAL.value == "normal"
        assert ReviewPriority.LOW.value == "low"

    def test_priority_count(self):
        """Priority enum has 4 values."""
        assert len(ReviewPriority) == 4


class TestReviewStatus:
    """Tests for ReviewStatus enum."""

    def test_status_values(self):
        """Status enum has expected values."""
        assert ReviewStatus.QUEUED.value == "queued"
        assert ReviewStatus.ASSIGNED.value == "assigned"
        assert ReviewStatus.IN_PROGRESS.value == "in_progress"
        assert ReviewStatus.COMPLETED.value == "completed"
        assert ReviewStatus.EXPIRED.value == "expired"
        assert ReviewStatus.CANCELLED.value == "cancelled"


class TestReviewItem:
    """Tests for ReviewItem dataclass."""

    @pytest.fixture
    def mock_decision(self):
        """Create mock decision."""
        decision = MagicMock(spec=Decision)
        decision.id = "dec_123"
        decision.claim_id = "claim_456"
        decision.domain = "politics"
        decision.gate = "G1"
        decision.proposed_state = "verified"
        decision.context = {"evidence_count": 5, "sources": ["s1"]}
        decision.timeout_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return decision

    def test_from_decision(self, mock_decision):
        """Create ReviewItem from decision."""
        item = ReviewItem.from_decision(mock_decision)

        assert item.decision_id == "dec_123"
        assert item.claim_id == "claim_456"
        assert item.domain == "politics"
        assert item.gate == "G1"
        assert item.status == ReviewStatus.QUEUED

    def test_from_decision_with_priority(self, mock_decision):
        """Create ReviewItem with priority."""
        item = ReviewItem.from_decision(
            mock_decision, priority=ReviewPriority.URGENT
        )
        assert item.priority == ReviewPriority.URGENT

    def test_from_decision_with_reason(self, mock_decision):
        """Create ReviewItem with reason."""
        item = ReviewItem.from_decision(
            mock_decision, reason="Needs human verification"
        )
        assert item.reason == "Needs human verification"

    def test_from_decision_context_summary(self, mock_decision):
        """Context summary filters relevant keys."""
        item = ReviewItem.from_decision(mock_decision)

        assert "evidence_count" in item.context_summary
        assert "sources" in item.context_summary

    def test_is_expired_false(self):
        """Not expired when expires_at is in future."""
        item = ReviewItem(
            id="rev_123",
            decision_id="dec_123",
            claim_id="claim_123",
            domain="test",
            gate="G1",
            proposed_state="verified",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        assert item.is_expired() is False

    def test_is_expired_true(self):
        """Expired when expires_at is in past."""
        item = ReviewItem(
            id="rev_123",
            decision_id="dec_123",
            claim_id="claim_123",
            domain="test",
            gate="G1",
            proposed_state="verified",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        assert item.is_expired() is True

    def test_is_expired_no_expiry(self):
        """Not expired when no expires_at."""
        item = ReviewItem(
            id="rev_123",
            decision_id="dec_123",
            claim_id="claim_123",
            domain="test",
            gate="G1",
            proposed_state="verified",
            expires_at=None,
        )
        assert item.is_expired() is False


class TestReviewerInfo:
    """Tests for ReviewerInfo dataclass."""

    def test_can_accept_review_true(self):
        """Can accept when under capacity."""
        reviewer = ReviewerInfo(
            user_id="user_123",
            name="Test User",
            max_concurrent_reviews=5,
            active_reviews=3,
        )
        assert reviewer.can_accept_review() is True

    def test_can_accept_review_false(self):
        """Cannot accept when at capacity."""
        reviewer = ReviewerInfo(
            user_id="user_123",
            name="Test User",
            max_concurrent_reviews=5,
            active_reviews=5,
        )
        assert reviewer.can_accept_review() is False

    def test_default_max_concurrent(self):
        """Default max concurrent is 5."""
        reviewer = ReviewerInfo(user_id="user_123", name="Test")
        assert reviewer.max_concurrent_reviews == 5

    def test_default_domains(self):
        """Default domains is empty."""
        reviewer = ReviewerInfo(user_id="user_123", name="Test")
        assert reviewer.domains == []


class TestReviewSubmission:
    """Tests for ReviewSubmission dataclass."""

    def test_create_submission(self):
        """Create submission."""
        submission = ReviewSubmission.create(
            review_item_id="rev_123",
            reviewer_id="user_456",
            approved=True,
            notes="Looks good",
        )

        assert submission.review_item_id == "rev_123"
        assert submission.reviewer_id == "user_456"
        assert submission.approved is True
        assert submission.notes == "Looks good"

    def test_create_with_confidence(self):
        """Create with confidence."""
        submission = ReviewSubmission.create(
            review_item_id="rev_123",
            reviewer_id="user_456",
            approved=False,
            confidence=0.8,
        )
        assert submission.confidence == 0.8

    def test_create_with_evidence_refs(self):
        """Create with evidence refs."""
        submission = ReviewSubmission.create(
            review_item_id="rev_123",
            reviewer_id="user_456",
            approved=True,
            evidence_refs=["ev1", "ev2"],
        )
        assert submission.evidence_refs == ["ev1", "ev2"]

    def test_create_generates_id(self):
        """Create generates unique ID."""
        s1 = ReviewSubmission.create("rev_1", "user_1", True)
        s2 = ReviewSubmission.create("rev_2", "user_1", True)
        assert s1.id != s2.id


class TestReviewQueue:
    """Tests for ReviewQueue class."""

    @pytest.fixture
    def queue(self):
        """Create empty queue."""
        return ReviewQueue()

    @pytest.fixture
    def mock_decision(self):
        """Create mock decision."""
        decision = MagicMock(spec=Decision)
        decision.id = "dec_123"
        decision.claim_id = "claim_456"
        decision.domain = "politics"
        decision.gate = "G1"
        decision.proposed_state = "verified"
        decision.context = {}
        decision.timeout_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return decision

    def test_add_to_queue(self, queue, mock_decision):
        """Add decision to queue."""
        item = queue.add_to_queue(mock_decision)

        assert item.decision_id == "dec_123"
        assert item in queue._queue.values()

    def test_add_to_queue_with_priority(self, queue, mock_decision):
        """Add with priority."""
        item = queue.add_to_queue(
            mock_decision, priority=ReviewPriority.HIGH
        )
        assert item.priority == ReviewPriority.HIGH

    def test_get_queue_all(self, queue, mock_decision):
        """Get all items from queue."""
        queue.add_to_queue(mock_decision)

        items = queue.get_queue()
        assert len(items) == 1

    def test_get_queue_by_status(self, queue, mock_decision):
        """Get items by status."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED

        queued = queue.get_queue(status=ReviewStatus.QUEUED)
        assigned = queue.get_queue(status=ReviewStatus.ASSIGNED)

        assert len(queued) == 0
        assert len(assigned) == 1

    def test_get_queue_by_domain(self, queue, mock_decision):
        """Get items by domain."""
        queue.add_to_queue(mock_decision)

        politics = queue.get_queue(domain="politics")
        other = queue.get_queue(domain="other")

        assert len(politics) == 1
        assert len(other) == 0

    def test_get_queue_by_priority(self, queue, mock_decision):
        """Get items by priority."""
        queue.add_to_queue(mock_decision, priority=ReviewPriority.URGENT)

        urgent = queue.get_queue(priority=ReviewPriority.URGENT)
        normal = queue.get_queue(priority=ReviewPriority.NORMAL)

        assert len(urgent) == 1
        assert len(normal) == 0

    def test_get_queue_sorted_by_priority(self, queue):
        """Queue sorted by priority then time."""
        d1 = MagicMock(spec=Decision)
        d1.id = "d1"
        d1.claim_id = "c1"
        d1.domain = "test"
        d1.gate = "G1"
        d1.proposed_state = "v"
        d1.context = {}
        d1.timeout_at = datetime.now(timezone.utc) + timedelta(hours=1)

        d2 = MagicMock(spec=Decision)
        d2.id = "d2"
        d2.claim_id = "c2"
        d2.domain = "test"
        d2.gate = "G1"
        d2.proposed_state = "v"
        d2.context = {}
        d2.timeout_at = datetime.now(timezone.utc) + timedelta(hours=1)

        queue.add_to_queue(d1, priority=ReviewPriority.LOW)
        queue.add_to_queue(d2, priority=ReviewPriority.URGENT)

        items = queue.get_queue()
        assert items[0].priority == ReviewPriority.URGENT

    def test_get_pending_reviews(self, queue, mock_decision):
        """Get pending reviews."""
        queue.add_to_queue(mock_decision)

        pending = queue.get_pending_reviews()
        assert len(pending) == 1

    def test_get_my_reviews(self, queue, mock_decision):
        """Get reviews assigned to user."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = "user_123"

        my = queue.get_my_reviews("user_123")
        other = queue.get_my_reviews("other_user")

        assert len(my) == 1
        assert len(other) == 0

    def test_get_review_item(self, queue, mock_decision):
        """Get specific review item."""
        item = queue.add_to_queue(mock_decision)

        found = queue.get_review_item(item.id)
        assert found == item

    def test_get_review_item_not_found(self, queue):
        """Get unknown review item returns None."""
        found = queue.get_review_item("unknown")
        assert found is None

    def test_get_review_for_decision(self, queue, mock_decision):
        """Get review item for decision."""
        item = queue.add_to_queue(mock_decision)

        found = queue.get_review_for_decision("dec_123")
        assert found == item

    def test_register_reviewer(self, queue):
        """Register a reviewer."""
        reviewer = queue.register_reviewer(
            user_id="user_123",
            name="Test User",
            email="test@test.com",
            domains=["politics"],
        )

        assert reviewer.user_id == "user_123"
        assert reviewer.name == "Test User"
        assert "user_123" in queue._reviewers

    def test_get_reviewer(self, queue):
        """Get registered reviewer."""
        queue.register_reviewer("user_123", "Test User")

        reviewer = queue.get_reviewer("user_123")
        assert reviewer is not None
        assert reviewer.name == "Test User"

    def test_assign_review(self, queue, mock_decision):
        """Assign review to user."""
        item = queue.add_to_queue(mock_decision)
        queue.register_reviewer("user_123", "Test User")

        assigned = queue.assign_review(item.id, "user_123")

        assert assigned.status == ReviewStatus.ASSIGNED
        assert assigned.assigned_to == "user_123"

    def test_assign_review_not_found(self, queue):
        """Assign raises for unknown item."""
        with pytest.raises(ValueError, match="not found"):
            queue.assign_review("unknown", "user_123")

    def test_assign_review_already_assigned(self, queue, mock_decision):
        """Assign raises for already assigned."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED

        with pytest.raises(ValueError, match="not available"):
            queue.assign_review(item.id, "user_123")

    def test_assign_review_reviewer_at_capacity(self, queue, mock_decision):
        """Assign raises if reviewer at capacity."""
        item = queue.add_to_queue(mock_decision)
        reviewer = queue.register_reviewer("user_123", "Test", max_concurrent=1)
        reviewer.active_reviews = 1

        with pytest.raises(ValueError, match="at capacity"):
            queue.assign_review(item.id, "user_123")

    def test_start_review(self, queue, mock_decision):
        """Start a review."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED

        started = queue.start_review(item.id)
        assert started.status == ReviewStatus.IN_PROGRESS

    def test_start_review_not_assigned(self, queue, mock_decision):
        """Start raises if not assigned."""
        item = queue.add_to_queue(mock_decision)

        with pytest.raises(ValueError, match="not in assigned"):
            queue.start_review(item.id)

    def test_submit_review(self, queue, mock_decision):
        """Submit a review."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = "user_123"
        item.assigned_at = datetime.now(timezone.utc)

        submission = queue.submit_review(
            item_id=item.id,
            reviewer_id="user_123",
            approved=True,
            notes="Good",
        )

        assert submission.approved is True
        assert item.status == ReviewStatus.COMPLETED

    def test_submit_review_wrong_reviewer(self, queue, mock_decision):
        """Submit raises if wrong reviewer."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = "user_123"

        with pytest.raises(ValueError, match="not assigned"):
            queue.submit_review(item.id, "wrong_user", True)

    def test_submit_review_updates_reviewer_stats(self, queue, mock_decision):
        """Submit updates reviewer stats."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = "user_123"
        item.assigned_at = datetime.now(timezone.utc)

        reviewer = queue.register_reviewer("user_123", "Test")
        reviewer.active_reviews = 1

        queue.submit_review(item.id, "user_123", True)

        assert reviewer.active_reviews == 0
        assert reviewer.total_reviews == 1

    def test_cancel_review(self, queue, mock_decision):
        """Cancel a review."""
        item = queue.add_to_queue(mock_decision)

        cancelled = queue.cancel_review(item.id, "test reason")

        assert cancelled.status == ReviewStatus.CANCELLED
        assert cancelled.review_notes == "test reason"

    def test_cancel_review_updates_reviewer(self, queue, mock_decision):
        """Cancel updates reviewer if assigned."""
        item = queue.add_to_queue(mock_decision)
        item.status = ReviewStatus.ASSIGNED
        item.assigned_to = "user_123"

        reviewer = queue.register_reviewer("user_123", "Test")
        reviewer.active_reviews = 1

        queue.cancel_review(item.id)

        assert reviewer.active_reviews == 0

    def test_check_expired(self, queue, mock_decision):
        """Check expired reviews."""
        mock_decision.timeout_at = datetime.now(timezone.utc) - timedelta(hours=1)
        item = queue.add_to_queue(mock_decision)
        item.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        expired = queue.check_expired()

        assert len(expired) == 1
        assert item.status == ReviewStatus.EXPIRED

    def test_get_stats(self, queue, mock_decision):
        """Get queue statistics."""
        queue.add_to_queue(mock_decision)
        queue.register_reviewer("user_123", "Test")

        stats = queue.get_stats()

        assert stats["total_items"] == 1
        assert stats["total_reviewers"] == 1
        assert "by_status" in stats
        assert "by_priority" in stats


class TestHelpers:
    """Tests for helper functions."""

    def test_generate_id(self):
        """Generate ID with prefix."""
        id1 = _generate_id("test")
        assert id1.startswith("test_")
        assert len(id1) == 17  # test_ + 12 chars

    def test_generate_id_unique(self):
        """Generated IDs are unique."""
        ids = [_generate_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_utcnow(self):
        """_utcnow returns timezone-aware datetime."""
        result = _utcnow()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_review_queue(self):
        """Get singleton instance."""
        import app.guardian.human_review as hr_module

        # Reset singleton
        hr_module._queue = None

        q1 = get_review_queue()
        q2 = get_review_queue()

        assert q1 is q2
