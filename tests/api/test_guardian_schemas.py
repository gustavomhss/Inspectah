"""
Tests for Guardian API Schemas — S37

Tests for Guardian Pydantic schemas.
"""

import pytest
from datetime import datetime, timezone

from app.api.guardian.schemas import (
    AddReviewerRequest,
    AddValidatorRequest,
    CommitteeResponse,
    DecisionBlockResponse,
    DecisionResponse,
    FlowContextResponse,
    GuardianMetricsResponse,
    PolicyListResponse,
    ReviewQueueItemResponse,
    ReviewQueueStatsResponse,
    SubmitDecisionRequest,
    SubmitReviewRequest,
    SubmitVoteRequest,
)


class TestSubmitDecisionRequest:
    """Tests for SubmitDecisionRequest schema."""

    def test_create_minimal(self):
        """Create with minimal required fields."""
        request = SubmitDecisionRequest(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
        )

        assert request.claim_id == "claim_123"
        assert request.domain == "politics"
        assert request.gate == "G1"
        assert request.proposed_state == "verified"
        assert request.context == {}
        assert request.policy_name is None

    def test_create_full(self):
        """Create with all fields."""
        request = SubmitDecisionRequest(
            claim_id="claim_123",
            domain="health",
            gate="G2",
            proposed_state="false",
            context={"evidence_count": 5, "sources": 3},
            policy_name="strict_health_policy",
        )

        assert request.context["evidence_count"] == 5
        assert request.policy_name == "strict_health_policy"

    def test_from_dict(self):
        """Create from dictionary."""
        data = {
            "claim_id": "c1",
            "domain": "test",
            "gate": "G1",
            "proposed_state": "pending",
        }
        request = SubmitDecisionRequest(**data)
        assert request.claim_id == "c1"


class TestDecisionResponse:
    """Tests for DecisionResponse schema."""

    def test_create_full(self):
        """Create with all fields."""
        now = datetime.now(timezone.utc)
        response = DecisionResponse(
            id="dec_123",
            claim_id="claim_456",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            status="approved",
            policy_name="standard_policy",
            committee_id="comm_789",
            final_state="verified",
            final_reason="High confidence",
            created_at=now,
            updated_at=now,
            completed_at=now,
        )

        assert response.id == "dec_123"
        assert response.status == "approved"
        assert response.final_state == "verified"

    def test_create_minimal(self):
        """Create with optional fields as None."""
        now = datetime.now(timezone.utc)
        response = DecisionResponse(
            id="dec_123",
            claim_id="claim_456",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            status="pending",
            policy_name=None,
            committee_id=None,
            final_state=None,
            final_reason=None,
            created_at=now,
            updated_at=now,
            completed_at=None,
        )

        assert response.policy_name is None
        assert response.completed_at is None


class TestFlowContextResponse:
    """Tests for FlowContextResponse schema."""

    def test_create_full(self):
        """Create with all fields."""
        now = datetime.now(timezone.utc)
        decision = DecisionResponse(
            id="dec_1",
            claim_id="c1",
            domain="test",
            gate="G1",
            proposed_state="v",
            status="pending",
            policy_name=None,
            committee_id=None,
            final_state=None,
            final_reason=None,
            created_at=now,
            updated_at=now,
            completed_at=None,
        )

        response = FlowContextResponse(
            decision=decision,
            current_state="awaiting_review",
            transitions=[{"from": "pending", "to": "awaiting_review"}],
            elapsed_ms=150,
            policy_result={"action": "human_review"},
            invariants={"no_self_vote": True},
            error=None,
        )

        assert response.current_state == "awaiting_review"
        assert response.elapsed_ms == 150


class TestSubmitReviewRequest:
    """Tests for SubmitReviewRequest schema."""

    def test_create_approve(self):
        """Create approval review."""
        request = SubmitReviewRequest(
            reviewer_id="user_123",
            approved=True,
            reason="Evidence is solid",
        )

        assert request.reviewer_id == "user_123"
        assert request.approved is True
        assert request.reason == "Evidence is solid"

    def test_create_reject(self):
        """Create rejection review."""
        request = SubmitReviewRequest(
            reviewer_id="user_456",
            approved=False,
            reason="Insufficient evidence",
        )

        assert request.approved is False

    def test_create_no_reason(self):
        """Create without reason."""
        request = SubmitReviewRequest(
            reviewer_id="user_123",
            approved=True,
        )

        assert request.reason is None


class TestSubmitVoteRequest:
    """Tests for SubmitVoteRequest schema."""

    def test_create_approve(self):
        """Create approve vote."""
        request = SubmitVoteRequest(
            member_id="member_123",
            vote_type="approve",
            reason="Agree with assessment",
            confidence=0.9,
        )

        assert request.vote_type == "approve"
        assert request.confidence == 0.9

    def test_create_reject(self):
        """Create reject vote."""
        request = SubmitVoteRequest(
            member_id="member_123",
            vote_type="reject",
        )

        assert request.vote_type == "reject"
        assert request.confidence == 1.0  # Default

    def test_create_abstain(self):
        """Create abstain vote."""
        request = SubmitVoteRequest(
            member_id="member_123",
            vote_type="abstain",
            reason="Not enough expertise",
            confidence=0.5,
        )

        assert request.vote_type == "abstain"

    def test_confidence_bounds(self):
        """Confidence is bounded 0-1."""
        request = SubmitVoteRequest(
            member_id="m1",
            vote_type="approve",
            confidence=0.0,
        )
        assert request.confidence == 0.0

        request = SubmitVoteRequest(
            member_id="m1",
            vote_type="approve",
            confidence=1.0,
        )
        assert request.confidence == 1.0


class TestAddReviewerRequest:
    """Tests for AddReviewerRequest schema."""

    def test_create(self):
        """Create add reviewer request."""
        request = AddReviewerRequest(user_id="user_123")
        assert request.user_id == "user_123"


class TestAddValidatorRequest:
    """Tests for AddValidatorRequest schema."""

    def test_create(self):
        """Create add validator request."""
        request = AddValidatorRequest(agent_id="agent_123")
        assert request.agent_id == "agent_123"


class TestCommitteeResponse:
    """Tests for CommitteeResponse schema."""

    def test_create(self):
        """Create committee response."""
        response = CommitteeResponse(
            id="comm_123",
            decision_id="dec_456",
            member_count=5,
            vote_count=3,
            quorum_required=3,
            has_quorum=True,
            vote_counts={"approve": 2, "reject": 1, "abstain": 0},
        )

        assert response.id == "comm_123"
        assert response.has_quorum is True
        assert response.vote_counts["approve"] == 2


class TestDecisionBlockResponse:
    """Tests for DecisionBlockResponse schema."""

    def test_create(self):
        """Create decision block response."""
        now = datetime.now(timezone.utc)
        response = DecisionBlockResponse(
            id="block_123",
            decision_id="dec_456",
            claim_id="claim_789",
            domain="politics",
            gate="G1",
            initial_state="pending",
            final_state="verified",
            decision_type="auto",
            policy_name="standard",
            policy_version="1.0.0",
            committee_summary={"votes": 3, "approved": True},
            invariants_checked={"no_self_vote": True, "quorum_reached": True},
            evidence_refs=["ev_1", "ev_2"],
            created_at=now,
            latency_ms=150,
        )

        assert response.id == "block_123"
        assert response.final_state == "verified"
        assert len(response.evidence_refs) == 2


class TestReviewQueueItemResponse:
    """Tests for ReviewQueueItemResponse schema."""

    def test_create(self):
        """Create review queue item response."""
        now = datetime.now(timezone.utc)
        response = ReviewQueueItemResponse(
            id="rev_123",
            decision_id="dec_456",
            claim_id="claim_789",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            priority="high",
            status="queued",
            reason="Low confidence",
            context_summary={"sources": 2},
            assigned_to=None,
            assigned_at=None,
            created_at=now,
            expires_at=now,
        )

        assert response.id == "rev_123"
        assert response.priority == "high"
        assert response.assigned_to is None


class TestReviewQueueStatsResponse:
    """Tests for ReviewQueueStatsResponse schema."""

    def test_create(self):
        """Create review queue stats response."""
        response = ReviewQueueStatsResponse(
            total_items=100,
            by_status={"queued": 50, "assigned": 30, "completed": 20},
            by_priority={"urgent": 10, "high": 30, "normal": 50, "low": 10},
            by_domain={"politics": 60, "health": 40},
            total_reviewers=15,
            total_submissions=80,
        )

        assert response.total_items == 100
        assert response.by_status["queued"] == 50


class TestGuardianMetricsResponse:
    """Tests for GuardianMetricsResponse schema."""

    def test_create(self):
        """Create guardian metrics response."""
        response = GuardianMetricsResponse(
            decisions_submitted=1000,
            decisions_approved=800,
            decisions_rejected=150,
            decisions_timed_out=50,
            avg_latency_ms=250.5,
            pending_decisions=20,
            awaiting_review=10,
            awaiting_quorum=5,
        )

        assert response.decisions_submitted == 1000
        assert response.decisions_approved == 800
        assert response.avg_latency_ms == 250.5


class TestPolicyListResponse:
    """Tests for PolicyListResponse schema."""

    def test_create(self):
        """Create policy list response."""
        response = PolicyListResponse(
            name="standard_politics",
            domain="politics",
            gate="G1",
            version="2.0.0",
            requirements=5,
            rules=3,
        )

        assert response.name == "standard_politics"
        assert response.requirements == 5
        assert response.rules == 3
