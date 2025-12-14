"""
Tests for Guardian Service — S37

Tests for GuardianService orchestration.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from app.guardian.service import GuardianService, get_guardian_service, _utcnow
from app.guardian.models import (
    Decision,
    DecisionStatus,
    Committee,
    CommitteeMember,
    Vote,
    VoteType,
)
from app.guardian.flow import FlowState, FlowContext


def run_async(coro):
    """Helper to run async functions in sync tests."""
    return asyncio.run(coro)


class TestGuardianServiceInit:
    """Tests for GuardianService initialization."""

    def test_init_default(self):
        """Initialize with default dependencies."""
        with patch("app.guardian.service.get_policy_engine") as mock_get_engine:
            mock_get_engine.return_value = MagicMock()
            service = GuardianService()
            assert service is not None
            assert service.timeout_seconds == 20

    def test_init_custom_timeout(self):
        """Initialize with custom timeout."""
        with patch("app.guardian.service.get_policy_engine") as mock_get_engine:
            mock_get_engine.return_value = MagicMock()
            service = GuardianService(timeout_seconds=30)
            assert service.timeout_seconds == 30

    def test_init_with_policy_engine(self):
        """Initialize with injected policy engine."""
        mock_engine = MagicMock()
        service = GuardianService(policy_engine=mock_engine)
        assert service.policy_engine == mock_engine

    def test_init_empty_stores(self):
        """Initialize with empty stores."""
        mock_engine = MagicMock()
        service = GuardianService(policy_engine=mock_engine)
        assert len(service._decisions) == 0
        assert len(service._committees) == 0
        assert len(service._blocks) == 0

    def test_init_metrics(self):
        """Initialize with default metrics."""
        mock_engine = MagicMock()
        service = GuardianService(policy_engine=mock_engine)
        assert service._metrics["decisions_submitted"] == 0
        assert service._metrics["decisions_approved"] == 0


class TestSubmitDecision:
    """Tests for submit_decision method."""

    @pytest.fixture
    def service(self):
        """Create service with mock engine."""
        return GuardianService(policy_engine=MagicMock())

    def test_submit_decision_basic(self, service):
        """Submit a basic decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={"evidence_count": 5},
        ))

        assert decision is not None
        assert decision.claim_id == "claim_123"
        assert decision.domain == "politics"
        assert decision.gate == "G1"

    def test_submit_decision_stored(self, service):
        """Submitted decision is stored."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        assert decision.id in service._decisions
        assert service._decisions[decision.id] == decision

    def test_submit_decision_increments_counter(self, service):
        """Submit increments counter."""
        run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        run_async(service.submit_decision(
            claim_id="claim_2",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        assert service._metrics["decisions_submitted"] == 2

    def test_submit_decision_with_policy(self, service):
        """Submit with specific policy."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
            policy_name="strict_policy",
        ))

        assert decision.policy_name == "strict_policy"


class TestProcessDecision:
    """Tests for process_decision method."""

    @pytest.fixture
    def service(self):
        """Create service with mock flow."""
        svc = GuardianService(policy_engine=MagicMock())
        svc.flow = MagicMock()
        return svc

    def _make_flow_context(self, state=FlowState.COMPLETED, committee=None):
        """Helper to create mock FlowContext."""
        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = state
        ctx.committee = committee
        ctx.elapsed_ms.return_value = 100
        ctx.started_at = datetime.now(timezone.utc)
        return ctx

    def test_process_decision_not_found(self, service):
        """Process raises for unknown decision."""
        with pytest.raises(ValueError, match="Decision not found"):
            run_async(service.process_decision("unknown_id"))

    def test_process_decision_already_complete(self, service):
        """Process raises for completed decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.APPROVED

        with pytest.raises(ValueError, match="already completed"):
            run_async(service.process_decision(decision.id))

    def test_process_decision_updates_status(self, service):
        """Process updates decision status."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        ctx = self._make_flow_context(FlowState.AWAITING_REVIEW)
        service.flow.execute = AsyncMock(return_value=ctx)

        run_async(service.process_decision(decision.id))

        assert decision.status == DecisionStatus.AWAITING_REVIEW

    def test_process_decision_stores_committee(self, service):
        """Process stores committee from flow."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        mock_committee = MagicMock(spec=Committee)
        mock_committee.id = "comm_123"
        ctx = self._make_flow_context(FlowState.AWAITING_QUORUM, committee=mock_committee)
        service.flow.execute = AsyncMock(return_value=ctx)

        run_async(service.process_decision(decision.id))

        assert mock_committee.id in service._committees


class TestAddReviewer:
    """Tests for add_reviewer method."""

    @pytest.fixture
    def service(self):
        """Create service with decision awaiting review."""
        svc = GuardianService(policy_engine=MagicMock())
        return svc

    def test_add_reviewer_not_found(self, service):
        """Add reviewer raises for unknown decision."""
        with pytest.raises(ValueError, match="Decision not found"):
            run_async(service.add_reviewer("unknown_id", "user_123"))

    def test_add_reviewer_wrong_status(self, service):
        """Add reviewer raises if not awaiting review."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        with pytest.raises(ValueError, match="not awaiting review"):
            run_async(service.add_reviewer(decision.id, "user_123"))

    def test_add_reviewer_success(self, service):
        """Add reviewer creates member."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.AWAITING_REVIEW

        # Create flow context
        ctx = MagicMock(spec=FlowContext)
        ctx.committee = None
        service._flow_contexts[decision.id] = ctx

        member = run_async(service.add_reviewer(decision.id, "user_123"))

        assert member is not None
        assert member.user_id == "user_123"


class TestSubmitReview:
    """Tests for submit_review method."""

    @pytest.fixture
    def service(self):
        """Create service with mock flow."""
        svc = GuardianService(policy_engine=MagicMock())
        svc.flow = MagicMock()
        return svc

    def test_submit_review_no_context(self, service):
        """Submit review raises if no context."""
        with pytest.raises(ValueError, match="No flow context"):
            run_async(service.submit_review(
                decision_id="unknown",
                reviewer_id="user_123",
                approved=True,
            ))

    def test_submit_review_decision_not_found(self, service):
        """Submit review raises if decision not found."""
        service._flow_contexts["ctx_123"] = MagicMock()

        with pytest.raises(ValueError, match="Decision not found"):
            run_async(service.submit_review(
                decision_id="ctx_123",
                reviewer_id="user_123",
                approved=True,
            ))


class TestAddValidator:
    """Tests for add_validator method."""

    @pytest.fixture
    def service(self):
        """Create service."""
        return GuardianService(policy_engine=MagicMock())

    def test_add_validator_not_found(self, service):
        """Add validator raises for unknown decision."""
        with pytest.raises(ValueError, match="Decision not found"):
            run_async(service.add_validator("unknown_id", "agent_123"))

    def test_add_validator_wrong_status(self, service):
        """Add validator raises if not awaiting quorum."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        with pytest.raises(ValueError, match="not awaiting quorum"):
            run_async(service.add_validator(decision.id, "agent_123"))


class TestSubmitVote:
    """Tests for submit_vote method."""

    @pytest.fixture
    def service(self):
        """Create service with mock flow."""
        svc = GuardianService(policy_engine=MagicMock())
        svc.flow = MagicMock()
        return svc

    def test_submit_vote_no_context(self, service):
        """Submit vote raises if no context."""
        with pytest.raises(ValueError, match="No flow context"):
            run_async(service.submit_vote(
                decision_id="unknown",
                member_id="member_123",
                vote_type=VoteType.APPROVE,
            ))


class TestGetters:
    """Tests for getter methods."""

    @pytest.fixture
    def service(self):
        """Create service with some data."""
        svc = GuardianService(policy_engine=MagicMock())
        return svc

    def test_get_decision_found(self, service):
        """Get existing decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        result = service.get_decision(decision.id)
        assert result == decision

    def test_get_decision_not_found(self, service):
        """Get unknown decision returns None."""
        result = service.get_decision("unknown_id")
        assert result is None

    def test_get_committee_not_found(self, service):
        """Get unknown committee returns None."""
        result = service.get_committee("unknown_id")
        assert result is None

    def test_get_block_not_found(self, service):
        """Get unknown block returns None."""
        result = service.get_block("unknown_id")
        assert result is None

    def test_get_decision_block(self, service):
        """Get block by decision ID."""
        # No blocks, should return None
        result = service.get_decision_block("decision_123")
        assert result is None


class TestListMethods:
    """Tests for list methods."""

    @pytest.fixture
    def service(self):
        """Create service with multiple decisions."""
        svc = GuardianService(policy_engine=MagicMock())
        return svc

    def test_list_pending_decisions(self, service):
        """List pending decisions."""
        d1 = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d2 = run_async(service.submit_decision(
            claim_id="claim_2",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d2.status = DecisionStatus.APPROVED

        pending = service.list_pending_decisions()
        assert len(pending) == 1
        assert d1 in pending

    def test_list_awaiting_review(self, service):
        """List decisions awaiting review."""
        d1 = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d1.status = DecisionStatus.AWAITING_REVIEW

        d2 = run_async(service.submit_decision(
            claim_id="claim_2",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        awaiting = service.list_awaiting_review()
        assert len(awaiting) == 1
        assert d1 in awaiting

    def test_list_awaiting_quorum(self, service):
        """List decisions awaiting quorum."""
        d1 = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d1.status = DecisionStatus.AWAITING_QUORUM

        awaiting = service.list_awaiting_quorum()
        assert len(awaiting) == 1
        assert d1 in awaiting

    def test_list_all_decisions(self, service):
        """List all decisions."""
        run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        run_async(service.submit_decision(
            claim_id="claim_2",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        all_decisions = service.list_all_decisions()
        assert len(all_decisions) == 2


class TestMetrics:
    """Tests for metrics."""

    @pytest.fixture
    def service(self):
        """Create service."""
        return GuardianService(policy_engine=MagicMock())

    def test_get_metrics_initial(self, service):
        """Get initial metrics."""
        metrics = service.get_metrics()

        assert metrics["decisions_submitted"] == 0
        assert metrics["decisions_approved"] == 0
        assert metrics["pending_decisions"] == 0

    def test_get_metrics_after_submit(self, service):
        """Get metrics after submission."""
        run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        metrics = service.get_metrics()
        assert metrics["decisions_submitted"] == 1
        assert metrics["pending_decisions"] == 1


class TestCheckTimeouts:
    """Tests for check_timeouts method."""

    @pytest.fixture
    def service(self):
        """Create service."""
        return GuardianService(policy_engine=MagicMock(), timeout_seconds=1)

    def test_check_timeouts_none(self, service):
        """Check timeouts with no expired decisions."""
        run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        timed_out = run_async(service.check_timeouts())
        assert len(timed_out) == 0

    def test_check_timeouts_expired(self, service):
        """Check timeouts with expired decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        # Force expiry
        decision.timeout_at = datetime.now(timezone.utc) - timedelta(hours=1)

        timed_out = run_async(service.check_timeouts())

        assert len(timed_out) == 1
        assert decision.status == DecisionStatus.TIMED_OUT


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_guardian_service(self):
        """Get singleton instance."""
        import app.guardian.service as svc_module

        # Reset singleton
        svc_module._service = None

        with patch.object(svc_module, "get_policy_engine") as mock_get_engine:
            mock_get_engine.return_value = MagicMock()

            s1 = get_guardian_service()
            s2 = get_guardian_service()

            assert s1 is s2


class TestUtcNow:
    """Tests for _utcnow helper."""

    def test_utcnow_returns_datetime(self):
        """_utcnow returns datetime."""
        result = _utcnow()
        assert isinstance(result, datetime)

    def test_utcnow_is_timezone_aware(self):
        """_utcnow returns timezone-aware datetime."""
        result = _utcnow()
        assert result.tzinfo is not None


class TestSubmitAndProcess:
    """Tests for submit_and_process method."""

    @pytest.fixture
    def service(self):
        """Create service with mock flow."""
        svc = GuardianService(policy_engine=MagicMock())
        svc.flow = MagicMock()
        return svc

    def test_submit_and_process(self, service):
        """Submit and process in one call."""
        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = FlowState.AWAITING_REVIEW
        ctx.committee = None
        ctx.elapsed_ms.return_value = 100
        service.flow.execute = AsyncMock(return_value=ctx)

        result = run_async(service.submit_and_process(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={"evidence_count": 5},
        ))

        assert result.current_state == FlowState.AWAITING_REVIEW
        assert service._metrics["decisions_submitted"] == 1


class TestFinalizeDecision:
    """Tests for _finalize_decision method."""

    @pytest.fixture
    def service(self):
        """Create service with mock flow."""
        svc = GuardianService(policy_engine=MagicMock())
        svc.flow = MagicMock()
        return svc

    def test_finalize_decision_with_block(self, service):
        """Finalize decision creates block."""
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.APPROVED

        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = FlowState.COMPLETED
        ctx.elapsed_ms.return_value = 150

        mock_block = MagicMock()
        mock_block.id = "block_123"
        mock_block.final_state = "approved"
        mock_block.decision_id = decision.id
        service.flow.create_decision_block = MagicMock(return_value=mock_block)

        run_async(service._finalize_decision(decision, ctx))

        assert "block_123" in service._blocks
        assert service._metrics["decisions_approved"] == 1


class TestUpdateMetrics:
    """Tests for _update_metrics method."""

    @pytest.fixture
    def service(self):
        """Create service."""
        return GuardianService(policy_engine=MagicMock())

    def test_update_metrics_approved(self, service):
        """Update metrics for approved decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.APPROVED

        service._update_metrics(decision, 100)

        assert service._metrics["decisions_approved"] == 1
        assert service._metrics["avg_latency_ms"] == 100.0

    def test_update_metrics_rejected(self, service):
        """Update metrics for rejected decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.REJECTED

        service._update_metrics(decision, 200)

        assert service._metrics["decisions_rejected"] == 1

    def test_update_metrics_timed_out(self, service):
        """Update metrics for timed out decision."""
        decision = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.TIMED_OUT

        service._update_metrics(decision, 300)

        assert service._metrics["decisions_timed_out"] == 1

    def test_update_metrics_avg_latency(self, service):
        """Update average latency calculation."""
        # First decision
        d1 = run_async(service.submit_decision(
            claim_id="claim_1",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d1.status = DecisionStatus.APPROVED
        service._update_metrics(d1, 100)

        # Second decision
        d2 = run_async(service.submit_decision(
            claim_id="claim_2",
            domain="d1",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        d2.status = DecisionStatus.APPROVED
        service._update_metrics(d2, 200)

        # Average should be 150
        assert service._metrics["avg_latency_ms"] == 150.0


class TestAddReviewerNoContext:
    """Tests for add_reviewer with no context."""

    def test_add_reviewer_no_context(self):
        """Add reviewer raises if no flow context."""
        service = GuardianService(policy_engine=MagicMock())
        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.AWAITING_REVIEW

        with pytest.raises(ValueError, match="No flow context"):
            run_async(service.add_reviewer(decision.id, "user_123"))


class TestSubmitReviewFull:
    """Tests for submit_review full flow."""

    def test_submit_review_success(self):
        """Submit review with full flow."""
        service = GuardianService(policy_engine=MagicMock())
        service.flow = MagicMock()

        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.AWAITING_REVIEW

        # Create flow context
        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = FlowState.COMPLETED
        ctx.elapsed_ms.return_value = 100
        service._flow_contexts[decision.id] = ctx

        service.flow.process_review_decision = AsyncMock(return_value=ctx)
        service.flow.create_decision_block = MagicMock(return_value=None)

        result = run_async(service.submit_review(
            decision_id=decision.id,
            reviewer_id="user_123",
            approved=True,
            reason="Good evidence",
        ))

        service.flow.process_review_decision.assert_called_once()
        assert result.current_state == FlowState.COMPLETED


class TestAddValidatorFull:
    """Tests for add_validator full flow."""

    def test_add_validator_success(self):
        """Add validator successfully."""
        service = GuardianService(policy_engine=MagicMock())

        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.AWAITING_QUORUM

        # Create flow context with committee
        ctx = MagicMock(spec=FlowContext)
        mock_committee = MagicMock(spec=Committee)
        mock_committee.id = "comm_123"
        ctx.committee = mock_committee
        service._flow_contexts[decision.id] = ctx

        member = run_async(service.add_validator(decision.id, "agent_123"))

        assert member is not None
        assert member.agent_id == "agent_123"
        mock_committee.add_member.assert_called_once()

    def test_add_validator_no_context(self):
        """Add validator raises if no context."""
        service = GuardianService(policy_engine=MagicMock())

        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.AWAITING_QUORUM

        with pytest.raises(ValueError, match="No committee"):
            run_async(service.add_validator(decision.id, "agent_123"))


class TestSubmitVoteFull:
    """Tests for submit_vote full flow."""

    def test_submit_vote_success(self):
        """Submit vote successfully."""
        service = GuardianService(policy_engine=MagicMock())
        service.flow = MagicMock()

        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))

        # Create flow context
        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = FlowState.AWAITING_QUORUM
        ctx.elapsed_ms.return_value = 100
        service._flow_contexts[decision.id] = ctx

        result_ctx = MagicMock(spec=FlowContext)
        result_ctx.current_state = FlowState.AWAITING_QUORUM
        service.flow.process_vote = AsyncMock(return_value=result_ctx)

        result = run_async(service.submit_vote(
            decision_id=decision.id,
            member_id="member_123",
            vote_type=VoteType.APPROVE,
            reason="Valid claim",
            confidence=0.95,
        ))

        service.flow.process_vote.assert_called_once()

    def test_submit_vote_decision_not_found(self):
        """Submit vote raises if decision not found."""
        service = GuardianService(policy_engine=MagicMock())

        # Add context but no decision
        service._flow_contexts["ctx_123"] = MagicMock()

        with pytest.raises(ValueError, match="Decision not found"):
            run_async(service.submit_vote(
                decision_id="ctx_123",
                member_id="member_123",
                vote_type=VoteType.APPROVE,
            ))

    def test_submit_vote_finalize_on_terminal(self):
        """Submit vote finalizes on terminal state."""
        service = GuardianService(policy_engine=MagicMock())
        service.flow = MagicMock()

        decision = run_async(service.submit_decision(
            claim_id="claim_123",
            domain="politics",
            gate="G1",
            proposed_state="verified",
            context={},
        ))
        decision.status = DecisionStatus.APPROVED

        # Create flow context
        ctx = MagicMock(spec=FlowContext)
        ctx.current_state = FlowState.AWAITING_QUORUM
        service._flow_contexts[decision.id] = ctx

        result_ctx = MagicMock(spec=FlowContext)
        result_ctx.current_state = FlowState.COMPLETED
        result_ctx.elapsed_ms.return_value = 200
        service.flow.process_vote = AsyncMock(return_value=result_ctx)
        service.flow.create_decision_block = MagicMock(return_value=None)

        run_async(service.submit_vote(
            decision_id=decision.id,
            member_id="member_123",
            vote_type=VoteType.APPROVE,
        ))


class TestGetDecisionBlock:
    """Tests for get_decision_block with matching block."""

    def test_get_decision_block_found(self):
        """Get block when it exists."""
        service = GuardianService(policy_engine=MagicMock())

        mock_block = MagicMock()
        mock_block.id = "block_123"
        mock_block.decision_id = "decision_abc"
        service._blocks["block_123"] = mock_block

        result = service.get_decision_block("decision_abc")

        assert result is not None
        assert result.id == "block_123"
