"""
Tests for Sprint 40 flow enhancements: E40.5 enforcement and degraded mode.

Tasks: S40-BE-005, S40-BE-029
"""

import pytest

from app.guardian.flow import (
    CRITICAL_INVARIANTS,
    E40_5CheckResult,
    FlowContext,
    FlowEvent,
    FlowState,
    GuardianFlow,
    can_transition,
    get_next_state,
)
from app.guardian.models import Decision, DecisionStatus


class TestE40_5CheckResult:
    """Tests for E40_5CheckResult dataclass."""

    def test_from_invariants_all_pass(self):
        """Test creating result from all passing invariants."""
        invariants = {
            "evidence_exists": True,
            "source_plurality": True,
            "temporal_coherence": True,
            "non_contradiction": True,
            "confidence_bounds": True,
        }

        result = E40_5CheckResult.from_invariants(invariants)

        assert result.status == "PASS"
        assert len(result.invariants_checked) == 5
        assert len(result.violations) == 0

    def test_from_invariants_with_failures(self):
        """Test creating result with some failures."""
        invariants = {
            "evidence_exists": False,
            "source_plurality": True,
            "temporal_coherence": True,
            "non_contradiction": False,
            "confidence_bounds": True,
        }

        result = E40_5CheckResult.from_invariants(invariants)

        assert result.status == "FAIL"
        assert len(result.invariants_checked) == 5
        assert len(result.violations) == 2
        assert any(v["invariant"] == "evidence_exists" for v in result.violations)
        assert any(v["invariant"] == "non_contradiction" for v in result.violations)

    def test_from_invariants_empty(self):
        """Test creating result from empty invariants."""
        result = E40_5CheckResult.from_invariants({})

        assert result.status == "PASS"
        assert len(result.invariants_checked) == 0
        assert len(result.violations) == 0


class TestFlowContextS40:
    """Tests for S40 FlowContext enhancements."""

    def _create_decision(self) -> Decision:
        """Create a test decision."""
        return Decision(
            id="test-decision-1",
            claim_id="claim-1",
            domain="saude",
            gate="G23",
            proposed_state="verified",
            context={},
            status=DecisionStatus.PENDING,
        )

    def test_context_has_e40_5_fields(self):
        """Test that FlowContext has S40 E40.5 fields."""
        ctx = FlowContext(decision=self._create_decision())

        assert hasattr(ctx, "e40_5_result")
        assert hasattr(ctx, "e40_5_required")
        assert hasattr(ctx, "blocked_reason")
        assert ctx.e40_5_result is None
        assert ctx.e40_5_required is True
        assert ctx.blocked_reason is None

    def test_context_has_degraded_fields(self):
        """Test that FlowContext has S40 degraded mode fields."""
        ctx = FlowContext(decision=self._create_decision())

        assert hasattr(ctx, "degraded_mode")
        assert hasattr(ctx, "degraded_reason")
        assert ctx.degraded_mode is False
        assert ctx.degraded_reason is None

    def test_is_e40_5_passed_when_not_required(self):
        """Test is_e40_5_passed when E40.5 is not required."""
        ctx = FlowContext(decision=self._create_decision())
        ctx.e40_5_required = False

        assert ctx.is_e40_5_passed() is True

    def test_is_e40_5_passed_when_no_result(self):
        """Test is_e40_5_passed when no result exists."""
        ctx = FlowContext(decision=self._create_decision())

        assert ctx.is_e40_5_passed() is False

    def test_is_e40_5_passed_with_pass_status(self):
        """Test is_e40_5_passed with PASS status."""
        ctx = FlowContext(decision=self._create_decision())
        ctx.e40_5_result = E40_5CheckResult(status="PASS")

        assert ctx.is_e40_5_passed() is True

    def test_is_e40_5_passed_with_skip_status(self):
        """Test is_e40_5_passed with SKIP status."""
        ctx = FlowContext(decision=self._create_decision())
        ctx.e40_5_result = E40_5CheckResult(status="SKIP")

        assert ctx.is_e40_5_passed() is True

    def test_is_e40_5_passed_with_fail_status(self):
        """Test is_e40_5_passed with FAIL status."""
        ctx = FlowContext(decision=self._create_decision())
        ctx.e40_5_result = E40_5CheckResult(status="FAIL")

        assert ctx.is_e40_5_passed() is False

    def test_is_blocked(self):
        """Test is_blocked method."""
        ctx = FlowContext(decision=self._create_decision())

        assert ctx.is_blocked() is False

        ctx.current_state = FlowState.BLOCKED
        assert ctx.is_blocked() is True

    def test_enter_degraded_mode(self):
        """Test entering degraded mode."""
        ctx = FlowContext(decision=self._create_decision())

        ctx.enter_degraded_mode("External service unavailable")

        assert ctx.degraded_mode is True
        assert ctx.degraded_reason == "External service unavailable"

    def test_exit_degraded_mode(self):
        """Test exiting degraded mode."""
        ctx = FlowContext(decision=self._create_decision())
        ctx.enter_degraded_mode("Test reason")

        ctx.exit_degraded_mode()

        assert ctx.degraded_mode is False
        assert ctx.degraded_reason is None


class TestFlowStateTransitionsS40:
    """Tests for S40 state transitions."""

    def test_blocked_state_exists(self):
        """Test that BLOCKED state exists."""
        assert FlowState.BLOCKED == "blocked"

    def test_degraded_state_exists(self):
        """Test that DEGRADED state exists."""
        assert FlowState.DEGRADED == "degraded"

    def test_e40_5_blocked_event_exists(self):
        """Test that E40_5_BLOCKED event exists."""
        assert FlowEvent.E40_5_BLOCKED == "e40_5_blocked"

    def test_enter_degraded_event_exists(self):
        """Test that ENTER_DEGRADED event exists."""
        assert FlowEvent.ENTER_DEGRADED == "enter_degraded"

    def test_exit_degraded_event_exists(self):
        """Test that EXIT_DEGRADED event exists."""
        assert FlowEvent.EXIT_DEGRADED == "exit_degraded"

    def test_unblock_event_exists(self):
        """Test that UNBLOCK event exists."""
        assert FlowEvent.UNBLOCK == "unblock"

    def test_can_transition_to_blocked_from_invariant_check(self):
        """Test transition from INVARIANT_CHECK to BLOCKED."""
        assert can_transition(FlowState.INVARIANT_CHECK, FlowEvent.E40_5_BLOCKED)
        assert get_next_state(FlowState.INVARIANT_CHECK, FlowEvent.E40_5_BLOCKED) == FlowState.BLOCKED

    def test_can_transition_to_blocked_from_auto_approve(self):
        """Test transition from AUTO_APPROVE to BLOCKED."""
        assert can_transition(FlowState.AUTO_APPROVE, FlowEvent.E40_5_BLOCKED)
        assert get_next_state(FlowState.AUTO_APPROVE, FlowEvent.E40_5_BLOCKED) == FlowState.BLOCKED

    def test_can_transition_to_blocked_from_awaiting_review(self):
        """Test transition from AWAITING_REVIEW to BLOCKED."""
        assert can_transition(FlowState.AWAITING_REVIEW, FlowEvent.E40_5_BLOCKED)
        assert get_next_state(FlowState.AWAITING_REVIEW, FlowEvent.E40_5_BLOCKED) == FlowState.BLOCKED

    def test_can_unblock_from_blocked(self):
        """Test transition from BLOCKED to AWAITING_REVIEW via UNBLOCK."""
        assert can_transition(FlowState.BLOCKED, FlowEvent.UNBLOCK)
        assert get_next_state(FlowState.BLOCKED, FlowEvent.UNBLOCK) == FlowState.AWAITING_REVIEW

    def test_can_enter_degraded_from_init(self):
        """Test transition from INIT to DEGRADED."""
        assert can_transition(FlowState.INIT, FlowEvent.ENTER_DEGRADED)
        assert get_next_state(FlowState.INIT, FlowEvent.ENTER_DEGRADED) == FlowState.DEGRADED

    def test_can_exit_degraded(self):
        """Test transition from DEGRADED to INIT."""
        assert can_transition(FlowState.DEGRADED, FlowEvent.EXIT_DEGRADED)
        assert get_next_state(FlowState.DEGRADED, FlowEvent.EXIT_DEGRADED) == FlowState.INIT

    def test_can_start_from_degraded(self):
        """Test transition from DEGRADED to POLICY_CHECK via START."""
        assert can_transition(FlowState.DEGRADED, FlowEvent.START)
        assert get_next_state(FlowState.DEGRADED, FlowEvent.START) == FlowState.POLICY_CHECK


class TestCriticalInvariants:
    """Tests for critical invariants configuration."""

    def test_evidence_exists_is_critical(self):
        """Test that evidence_exists is a critical invariant."""
        assert "evidence_exists" in CRITICAL_INVARIANTS

    def test_non_contradiction_is_critical(self):
        """Test that non_contradiction is a critical invariant."""
        assert "non_contradiction" in CRITICAL_INVARIANTS


class TestGuardianFlowS40Methods:
    """Tests for S40 GuardianFlow methods."""

    def _create_decision(self) -> Decision:
        """Create a test decision."""
        return Decision(
            id="test-decision-1",
            claim_id="claim-1",
            domain="saude",
            gate="G23",
            proposed_state="verified",
            context={},
            status=DecisionStatus.PENDING,
        )

    @pytest.mark.asyncio
    async def test_unblock_decision(self):
        """Test unblocking a blocked decision."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())
        ctx.current_state = FlowState.BLOCKED
        ctx.blocked_reason = "Critical invariant failed"

        result = await flow.unblock_decision(ctx, "admin-1", "Issue resolved")

        assert result.current_state == FlowState.AWAITING_REVIEW
        assert result.blocked_reason is None
        assert len(result.transitions) == 1
        assert result.transitions[0].event == FlowEvent.UNBLOCK

    @pytest.mark.asyncio
    async def test_unblock_decision_wrong_state(self):
        """Test unblocking when not in BLOCKED state."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())
        ctx.current_state = FlowState.INIT

        result = await flow.unblock_decision(ctx, "admin-1", "Issue resolved")

        assert result.current_state == FlowState.INIT  # State unchanged
        assert len(result.transitions) == 0

    def test_enter_degraded_mode(self):
        """Test entering degraded mode."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())

        result = flow.enter_degraded_mode(ctx, "External service down")

        assert result.current_state == FlowState.DEGRADED
        assert result.degraded_mode is True
        assert result.degraded_reason == "External service down"
        assert result.e40_5_required is False  # E40.5 relaxed in degraded mode

    def test_enter_degraded_mode_wrong_state(self):
        """Test entering degraded mode from wrong state."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())
        ctx.current_state = FlowState.COMPLETED

        result = flow.enter_degraded_mode(ctx, "External service down")

        assert result.current_state == FlowState.COMPLETED  # State unchanged
        assert result.degraded_mode is False

    def test_exit_degraded_mode(self):
        """Test exiting degraded mode."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())
        ctx.current_state = FlowState.DEGRADED
        ctx.degraded_mode = True
        ctx.degraded_reason = "Test"
        ctx.e40_5_required = False

        result = flow.exit_degraded_mode(ctx)

        assert result.current_state == FlowState.INIT
        assert result.degraded_mode is False
        assert result.degraded_reason is None
        assert result.e40_5_required is True  # E40.5 restored

    def test_exit_degraded_mode_wrong_state(self):
        """Test exiting degraded mode from wrong state."""
        flow = GuardianFlow()
        ctx = FlowContext(decision=self._create_decision())
        ctx.current_state = FlowState.INIT

        result = flow.exit_degraded_mode(ctx)

        assert result.current_state == FlowState.INIT  # State unchanged
