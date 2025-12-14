"""
Tests for Guardian API Routes — S37

Tests for Guardian REST API endpoints.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, AsyncMock

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.guardian.routes import (
    router,
    _decision_to_response,
    _flow_context_to_response,
    get_service,
    get_queue,
)
from app.api.guardian.schemas import DecisionResponse
from app.guardian.models import Decision, DecisionStatus, VoteType


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def mock_service():
    """Create mock guardian service."""
    return MagicMock()


@pytest.fixture
def mock_queue():
    """Create mock review queue."""
    return MagicMock()


@pytest.fixture
def client(mock_service, mock_queue):
    """Create test client with dependency overrides."""
    app.dependency_overrides[get_service] = lambda: mock_service
    app.dependency_overrides[get_queue] = lambda: mock_queue
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_decision():
    """Create mock decision."""
    now = datetime.now(timezone.utc)
    decision = MagicMock()
    decision.id = "dec_123"
    decision.claim_id = "claim_456"
    decision.claim_summary = "Test claim summary"
    decision.evidence_summary = ["Evidence 1", "Evidence 2"]
    decision.domain = "politics"
    decision.gate = "G1"
    decision.proposed_state = "verified"
    decision.status = DecisionStatus.PENDING
    decision.policy_name = "standard"
    decision.committee_id = None
    decision.final_state = None
    decision.final_reason = None
    decision.created_at = now
    decision.updated_at = now
    decision.completed_at = None
    return decision


class TestDecisionToResponse:
    """Tests for _decision_to_response helper."""

    def test_convert_decision(self, mock_decision):
        """Convert decision to response."""
        response = _decision_to_response(mock_decision)

        assert isinstance(response, DecisionResponse)
        assert response.id == "dec_123"
        assert response.claim_id == "claim_456"
        assert response.domain == "politics"
        assert response.status == "pending"


class TestFlowContextToResponse:
    """Tests for _flow_context_to_response helper."""

    def test_convert_flow_context(self, mock_decision):
        """Convert flow context to response."""
        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "awaiting_review"
        mock_ctx.transitions = []
        mock_ctx.elapsed_ms.return_value = 150
        mock_ctx.policy_result = None
        mock_ctx.invariants = {"test": True}
        mock_ctx.error = None

        response = _flow_context_to_response(mock_ctx)

        assert response.current_state == "awaiting_review"
        assert response.elapsed_ms == 150
        assert response.invariants == {"test": True}

    def test_convert_with_policy_result(self, mock_decision):
        """Convert with policy result."""
        from app.truth.policy_dsl.executor import PolicyAction

        mock_policy_result = MagicMock()
        mock_policy_result.policy_name = "strict"
        mock_policy_result.final_action = PolicyAction.AUTO_APPROVE
        mock_policy_result.all_requirements_met = True

        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "approved"
        mock_ctx.transitions = []
        mock_ctx.elapsed_ms.return_value = 100
        mock_ctx.policy_result = mock_policy_result
        mock_ctx.invariants = {}
        mock_ctx.error = None

        response = _flow_context_to_response(mock_ctx)

        assert response.policy_result is not None
        assert response.policy_result["policy_name"] == "strict"
        assert response.policy_result["final_action"] == "auto_approve"

    def test_convert_with_transitions(self, mock_decision):
        """Convert with transitions."""
        mock_transition = MagicMock()
        mock_transition.from_state.value = "pending"
        mock_transition.to_state.value = "approved"
        mock_transition.event.value = "policy_approved"
        mock_transition.timestamp.isoformat.return_value = "2024-01-01T00:00:00"
        mock_transition.metadata = {"policy": "auto"}

        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "approved"
        mock_ctx.transitions = [mock_transition]
        mock_ctx.elapsed_ms.return_value = 50
        mock_ctx.policy_result = None
        mock_ctx.invariants = {}
        mock_ctx.error = None

        response = _flow_context_to_response(mock_ctx)

        assert len(response.transitions) == 1
        assert response.transitions[0]["from_state"] == "pending"
        assert response.transitions[0]["to_state"] == "approved"


class TestSubmitDecision:
    """Tests for POST /decisions endpoint."""

    def test_submit_decision(self, client, mock_decision, mock_service):
        """Submit decision successfully."""
        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "pending"
        mock_ctx.transitions = []
        mock_ctx.elapsed_ms.return_value = 100
        mock_ctx.policy_result = None
        mock_ctx.invariants = {}
        mock_ctx.error = None

        mock_service.submit_and_process = AsyncMock(return_value=mock_ctx)

        response = client.post(
            "/api/guardian/decisions",
            json={
                "claim_id": "claim_456",
                "domain": "politics",
                "gate": "G1",
                "proposed_state": "verified",
            },
        )

        assert response.status_code == 200


class TestListDecisions:
    """Tests for GET /decisions endpoint."""

    def test_list_decisions(self, client, mock_decision, mock_service):
        """List all decisions."""
        mock_service.list_all_decisions.return_value = [mock_decision]

        response = client.get("/api/guardian/decisions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "dec_123"

    def test_list_decisions_filtered(self, client, mock_decision, mock_service):
        """List decisions with status filter."""
        mock_service.list_all_decisions.return_value = [mock_decision]

        response = client.get("/api/guardian/decisions?status_filter=pending")

        assert response.status_code == 200


class TestGetDecision:
    """Tests for GET /decisions/{id} endpoint."""

    def test_get_decision(self, client, mock_decision, mock_service):
        """Get single decision."""
        mock_service.get_decision.return_value = mock_decision

        response = client.get("/api/guardian/decisions/dec_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "dec_123"

    def test_get_decision_not_found(self, client, mock_service):
        """Get non-existent decision."""
        mock_service.get_decision.return_value = None

        response = client.get("/api/guardian/decisions/unknown")

        assert response.status_code == 404


class TestAwaitingReviewAndQuorum:
    """Tests for awaiting review/quorum endpoints."""

    def test_list_awaiting_review(self, client, mock_decision, mock_service):
        """List decisions awaiting review."""
        mock_service.list_awaiting_review.return_value = [mock_decision]

        response = client.get("/api/guardian/decisions/awaiting-review")

        assert response.status_code == 200

    def test_list_awaiting_quorum(self, client, mock_decision, mock_service):
        """List decisions awaiting quorum."""
        mock_service.list_awaiting_quorum.return_value = [mock_decision]

        response = client.get("/api/guardian/decisions/awaiting-quorum")

        assert response.status_code == 200


class TestAddReviewer:
    """Tests for POST /decisions/{id}/reviewer endpoint."""

    def test_add_reviewer(self, client, mock_service):
        """Add reviewer to decision."""
        mock_member = MagicMock()
        mock_member.id = "member_123"
        mock_member.user_id = "user_456"

        mock_service.add_reviewer = AsyncMock(return_value=mock_member)

        response = client.post(
            "/api/guardian/decisions/dec_123/reviewer",
            json={"user_id": "user_456"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == "member_123"

    def test_add_reviewer_error(self, client, mock_service):
        """Add reviewer with error."""
        mock_service.add_reviewer = AsyncMock(side_effect=ValueError("Invalid decision"))

        response = client.post(
            "/api/guardian/decisions/dec_123/reviewer",
            json={"user_id": "user_456"},
        )

        assert response.status_code == 400


class TestSubmitReview:
    """Tests for POST /decisions/{id}/review endpoint."""

    def test_submit_review(self, client, mock_decision, mock_service):
        """Submit review."""
        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "approved"
        mock_ctx.transitions = []
        mock_ctx.elapsed_ms.return_value = 200
        mock_ctx.policy_result = None
        mock_ctx.invariants = {}
        mock_ctx.error = None

        mock_service.submit_review = AsyncMock(return_value=mock_ctx)

        response = client.post(
            "/api/guardian/decisions/dec_123/review",
            json={"reviewer_id": "rev_456", "approved": True, "reason": "Valid evidence"},
        )

        assert response.status_code == 200

    def test_submit_review_error(self, client, mock_service):
        """Submit review with error."""
        mock_service.submit_review = AsyncMock(side_effect=ValueError("Invalid decision state"))

        response = client.post(
            "/api/guardian/decisions/dec_123/review",
            json={"reviewer_id": "rev_456", "approved": True},
        )

        assert response.status_code == 400


class TestAddValidator:
    """Tests for POST /decisions/{id}/validator endpoint."""

    def test_add_validator(self, client, mock_service):
        """Add validator to decision."""
        mock_member = MagicMock()
        mock_member.id = "member_123"
        mock_member.agent_id = "agent_456"

        mock_service.add_validator = AsyncMock(return_value=mock_member)

        response = client.post(
            "/api/guardian/decisions/dec_123/validator",
            json={"agent_id": "agent_456"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == "member_123"
        assert data["agent_id"] == "agent_456"

    def test_add_validator_error(self, client, mock_service):
        """Add validator with error."""
        mock_service.add_validator = AsyncMock(side_effect=ValueError("Not awaiting quorum"))

        response = client.post(
            "/api/guardian/decisions/dec_123/validator",
            json={"agent_id": "agent_456"},
        )

        assert response.status_code == 400


class TestSubmitVote:
    """Tests for POST /decisions/{id}/vote endpoint."""

    def test_submit_vote(self, client, mock_decision, mock_service):
        """Submit committee vote."""
        mock_ctx = MagicMock()
        mock_ctx.decision = mock_decision
        mock_ctx.current_state.value = "approved"
        mock_ctx.transitions = []
        mock_ctx.elapsed_ms.return_value = 300
        mock_ctx.policy_result = None
        mock_ctx.invariants = {}
        mock_ctx.error = None

        mock_service.submit_vote = AsyncMock(return_value=mock_ctx)

        response = client.post(
            "/api/guardian/decisions/dec_123/vote",
            json={"member_id": "m1", "vote_type": "approve", "confidence": 0.9},
        )

        assert response.status_code == 200

    def test_submit_vote_invalid_type(self, client, mock_service):
        """Submit vote with invalid type."""
        response = client.post(
            "/api/guardian/decisions/dec_123/vote",
            json={"member_id": "m1", "vote_type": "invalid"},
        )

        assert response.status_code == 400

    def test_submit_vote_error(self, client, mock_service):
        """Submit vote with service error."""
        mock_service.submit_vote = AsyncMock(side_effect=ValueError("Invalid member"))

        response = client.post(
            "/api/guardian/decisions/dec_123/vote",
            json={"member_id": "m1", "vote_type": "approve"},
        )

        assert response.status_code == 400


class TestGetCommittee:
    """Tests for GET /decisions/{id}/committee endpoint."""

    def test_get_committee(self, client, mock_decision, mock_service):
        """Get committee for decision."""
        mock_decision.committee_id = "comm_123"

        mock_committee = MagicMock()
        mock_committee.id = "comm_123"
        mock_committee.decision_id = "dec_123"
        mock_committee.members = [MagicMock()]
        mock_committee.votes = []
        mock_committee.quorum_required = 3
        mock_committee.has_quorum.return_value = False
        mock_committee.count_votes.return_value = {VoteType.APPROVE: 1}

        mock_service.get_decision.return_value = mock_decision
        mock_service.get_committee.return_value = mock_committee

        response = client.get("/api/guardian/decisions/dec_123/committee")

        assert response.status_code == 200

    def test_get_committee_no_committee(self, client, mock_decision, mock_service):
        """Get committee when none exists."""
        mock_decision.committee_id = None

        mock_service.get_decision.return_value = mock_decision

        response = client.get("/api/guardian/decisions/dec_123/committee")

        assert response.status_code == 404

    def test_get_committee_decision_not_found(self, client, mock_service):
        """Get committee for non-existent decision."""
        mock_service.get_decision.return_value = None

        response = client.get("/api/guardian/decisions/unknown/committee")

        assert response.status_code == 404

    def test_get_committee_committee_not_found(self, client, mock_decision, mock_service):
        """Get committee when committee_id is set but committee doesn't exist."""
        mock_decision.committee_id = "comm_missing"
        mock_service.get_decision.return_value = mock_decision
        mock_service.get_committee.return_value = None

        response = client.get("/api/guardian/decisions/dec_123/committee")

        assert response.status_code == 404


class TestGetDecisionBlock:
    """Tests for GET /decisions/{id}/block endpoint."""

    def test_get_decision_block(self, client, mock_service):
        """Get decision block."""
        now = datetime.now(timezone.utc)
        mock_block = MagicMock()
        mock_block.id = "block_123"
        mock_block.decision_id = "dec_123"
        mock_block.claim_id = "claim_456"
        mock_block.domain = "politics"
        mock_block.gate = "G1"
        mock_block.initial_state = "pending"
        mock_block.final_state = "verified"
        mock_block.decision_type = "auto"
        mock_block.policy_name = "standard"
        mock_block.policy_version = "1.0.0"
        mock_block.committee_summary = None
        mock_block.invariants_checked = {"test": True}
        mock_block.evidence_refs = ["ev_1"]
        mock_block.created_at = now
        mock_block.latency_ms = 150

        mock_service.get_decision_block.return_value = mock_block

        response = client.get("/api/guardian/decisions/dec_123/block")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "block_123"

    def test_get_decision_block_not_found(self, client, mock_service):
        """Get non-existent decision block."""
        mock_service.get_decision_block.return_value = None

        response = client.get("/api/guardian/decisions/dec_123/block")

        assert response.status_code == 404


class TestReviewQueue:
    """Tests for review queue endpoints."""

    def test_list_review_queue(self, client, mock_queue):
        """List review queue items."""
        now = datetime.now(timezone.utc)
        mock_item = MagicMock()
        mock_item.id = "rq_123"
        mock_item.decision_id = "dec_123"
        mock_item.claim_id = "claim_456"
        mock_item.domain = "politics"
        mock_item.gate = "G1"
        mock_item.proposed_state = "verified"
        mock_item.priority.value = "high"
        mock_item.status.value = "queued"
        mock_item.reason = "Low confidence"
        mock_item.context_summary = {}
        mock_item.assigned_to = None
        mock_item.assigned_at = None
        mock_item.created_at = now
        mock_item.expires_at = now

        mock_queue.get_queue.return_value = [mock_item]

        response = client.get("/api/guardian/review-queue")

        assert response.status_code == 200

    def test_get_review_queue_stats(self, client, mock_queue):
        """Get review queue stats."""
        mock_queue.get_stats.return_value = {
            "total_items": 100,
            "by_status": {"queued": 50},
            "by_priority": {"high": 30},
            "by_domain": {"politics": 60},
            "total_reviewers": 10,
            "total_submissions": 80,
        }

        response = client.get("/api/guardian/review-queue/stats")

        assert response.status_code == 200


class TestMetricsAndPolicies:
    """Tests for metrics and policies endpoints."""

    def test_get_metrics(self, client, mock_service):
        """Get Guardian metrics."""
        mock_service.get_metrics.return_value = {
            "decisions_submitted": 1000,
            "decisions_approved": 800,
            "decisions_rejected": 150,
            "decisions_timed_out": 50,
            "avg_latency_ms": 200.0,
            "pending_decisions": 20,
            "awaiting_review": 10,
            "awaiting_quorum": 5,
        }

        response = client.get("/api/guardian/metrics")

        assert response.status_code == 200
        data = response.json()
        assert data["decisions_submitted"] == 1000

    def test_list_policies(self, client):
        """List available policies."""
        mock_engine = MagicMock()
        mock_engine.list_policies.return_value = [
            {
                "name": "standard",
                "domain": "politics",
                "gate": "G1",
                "version": "1.0.0",
                "requirements": 3,
                "rules": 2,
            }
        ]

        with patch("app.api.guardian.routes.get_policy_engine", return_value=mock_engine):
            response = client.get("/api/guardian/policies")

        assert response.status_code == 200

    def test_check_timeouts(self, client, mock_decision, mock_service):
        """Check for timed out decisions."""
        mock_service.check_timeouts = AsyncMock(return_value=[mock_decision])

        response = client.post("/api/guardian/check-timeouts")

        assert response.status_code == 200
        data = response.json()
        assert data["timed_out_count"] == 1

    def test_get_policy_details(self, client):
        """Get policy details."""
        mock_engine = MagicMock()
        mock_policy = MagicMock()
        mock_policy.to_dict.return_value = {
            "name": "pilot_politics_v1",
            "domain": "politics",
            "gate": "G7",
            "version": "1.0.0",
            "requirements": [
                {"field": "sources", "operator": ">=", "value": 2, "modifier": "independent"},
                {"field": "evidence_strength", "operator": ">=", "value": 0.6, "modifier": None},
            ],
            "rules": [
                {
                    "condition_field": "high_confidence",
                    "condition_operator": "=",
                    "condition_value": True,
                    "action": "auto_approve",
                    "action_params": {},
                },
            ],
            "metadata": {},
        }
        mock_engine.get_policy_by_name.return_value = mock_policy

        with patch("app.api.guardian.routes.get_policy_engine", return_value=mock_engine):
            response = client.get("/api/guardian/policies/pilot_politics_v1")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "pilot_politics_v1"
        assert len(data["requirements"]) == 2
        assert len(data["rules"]) == 1
        assert data["requirements"][0]["field"] == "sources"
        assert data["rules"][0]["action"] == "auto_approve"

    def test_get_policy_details_not_found(self, client):
        """Get non-existent policy details."""
        mock_engine = MagicMock()
        mock_engine.get_policy_by_name.return_value = None

        with patch("app.api.guardian.routes.get_policy_engine", return_value=mock_engine):
            response = client.get("/api/guardian/policies/unknown_policy")

        assert response.status_code == 404
