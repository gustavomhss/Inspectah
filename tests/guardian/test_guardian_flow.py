"""
Tests for Guardian Flow — S37

Tests for FlowState, FlowEvent, FlowTransition, FlowContext, GuardianFlow.
"""

import asyncio
import pytest
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from app.guardian.flow import (
    FlowState,
    FlowEvent,
    FlowTransition,
    FlowContext,
    GuardianFlow,
    TRANSITIONS,
    TERMINAL_STATES,
    can_transition,
    get_next_state,
)
from app.guardian.models import (
    Decision,
    DecisionStatus,
    Committee,
    Vote,
    VoteType,
)
from app.truth.policy_dsl import PolicyAction


def run_async(coro):
    """Helper to run async functions in sync tests."""
    return asyncio.run(coro)


class TestFlowState:
    """Tests for FlowState enum."""

    def test_all_states_defined(self):
        """All expected states are defined."""
        expected = [
            "init", "policy_check", "invariant_check", "auto_approve",
            "awaiting_review", "awaiting_quorum", "escalated",
            "completed", "timed_out", "failed",
            # S40: New states
            "blocked", "degraded"
        ]
        actual = [s.value for s in FlowState]
        assert set(actual) == set(expected)


class TestFlowEvent:
    """Tests for FlowEvent enum."""

    def test_all_events_defined(self):
        """All expected events are defined."""
        expected = [
            "start", "policy_passed", "policy_requires_review",
            "policy_requires_quorum", "invariants_passed", "invariants_failed",
            "review_approved", "review_rejected", "quorum_reached",
            "quorum_approved", "quorum_rejected", "quorum_tie",
            "timeout", "escalate", "error",
            # S40: New events
            "e40_5_blocked", "nogo_blocked", "enter_degraded", "exit_degraded", "unblock"
        ]
        actual = [e.value for e in FlowEvent]
        assert set(actual) == set(expected)


class TestTerminalStates:
    """Tests for TERMINAL_STATES."""

    def test_terminal_states(self):
        """Terminal states are correct."""
        assert FlowState.COMPLETED in TERMINAL_STATES
        assert FlowState.TIMED_OUT in TERMINAL_STATES
        assert FlowState.FAILED in TERMINAL_STATES
        assert FlowState.INIT not in TERMINAL_STATES
        assert FlowState.AWAITING_REVIEW not in TERMINAL_STATES


class TestTransitions:
    """Tests for state transition table."""

    def test_init_transitions(self):
        """Init state transitions."""
        assert TRANSITIONS[FlowState.INIT][FlowEvent.START] == FlowState.POLICY_CHECK
        assert TRANSITIONS[FlowState.INIT][FlowEvent.ERROR] == FlowState.FAILED

    def test_policy_check_transitions(self):
        """Policy check state transitions."""
        assert TRANSITIONS[FlowState.POLICY_CHECK][FlowEvent.POLICY_PASSED] == FlowState.INVARIANT_CHECK
        assert TRANSITIONS[FlowState.POLICY_CHECK][FlowEvent.POLICY_REQUIRES_REVIEW] == FlowState.AWAITING_REVIEW
        assert TRANSITIONS[FlowState.POLICY_CHECK][FlowEvent.POLICY_REQUIRES_QUORUM] == FlowState.AWAITING_QUORUM

    def test_invariant_check_transitions(self):
        """Invariant check state transitions."""
        assert TRANSITIONS[FlowState.INVARIANT_CHECK][FlowEvent.INVARIANTS_PASSED] == FlowState.AUTO_APPROVE
        assert TRANSITIONS[FlowState.INVARIANT_CHECK][FlowEvent.INVARIANTS_FAILED] == FlowState.AWAITING_REVIEW

    def test_awaiting_review_transitions(self):
        """Awaiting review state transitions."""
        assert TRANSITIONS[FlowState.AWAITING_REVIEW][FlowEvent.REVIEW_APPROVED] == FlowState.COMPLETED
        assert TRANSITIONS[FlowState.AWAITING_REVIEW][FlowEvent.REVIEW_REJECTED] == FlowState.COMPLETED
        assert TRANSITIONS[FlowState.AWAITING_REVIEW][FlowEvent.ESCALATE] == FlowState.ESCALATED

    def test_awaiting_quorum_transitions(self):
        """Awaiting quorum state transitions."""
        assert TRANSITIONS[FlowState.AWAITING_QUORUM][FlowEvent.QUORUM_APPROVED] == FlowState.COMPLETED
        assert TRANSITIONS[FlowState.AWAITING_QUORUM][FlowEvent.QUORUM_REJECTED] == FlowState.COMPLETED
        assert TRANSITIONS[FlowState.AWAITING_QUORUM][FlowEvent.QUORUM_TIE] == FlowState.ESCALATED


class TestCanTransition:
    """Tests for can_transition function."""

    def test_valid_transition(self):
        """Valid transition returns True."""
        assert can_transition(FlowState.INIT, FlowEvent.START)
        assert can_transition(FlowState.POLICY_CHECK, FlowEvent.POLICY_PASSED)

    def test_invalid_transition(self):
        """Invalid transition returns False."""
        assert not can_transition(FlowState.INIT, FlowEvent.REVIEW_APPROVED)
        assert not can_transition(FlowState.COMPLETED, FlowEvent.START)


class TestGetNextState:
    """Tests for get_next_state function."""

    def test_valid_next_state(self):
        """Get next state for valid transition."""
        assert get_next_state(FlowState.INIT, FlowEvent.START) == FlowState.POLICY_CHECK
        assert get_next_state(FlowState.INVARIANT_CHECK, FlowEvent.INVARIANTS_PASSED) == FlowState.AUTO_APPROVE

    def test_invalid_next_state(self):
        """Get next state for invalid transition returns None."""
        assert get_next_state(FlowState.INIT, FlowEvent.REVIEW_APPROVED) is None
        assert get_next_state(FlowState.COMPLETED, FlowEvent.START) is None


class TestFlowTransition:
    """Tests for FlowTransition dataclass."""

    def test_create_transition(self):
        """Create transition record."""
        transition = FlowTransition(
            from_state=FlowState.INIT,
            to_state=FlowState.POLICY_CHECK,
            event=FlowEvent.START,
        )
        assert transition.from_state == FlowState.INIT
        assert transition.to_state == FlowState.POLICY_CHECK
        assert transition.event == FlowEvent.START
        assert isinstance(transition.timestamp, datetime)
        assert transition.metadata == {}

    def test_transition_with_metadata(self):
        """Create transition with metadata."""
        transition = FlowTransition(
            from_state=FlowState.POLICY_CHECK,
            to_state=FlowState.INVARIANT_CHECK,
            event=FlowEvent.POLICY_PASSED,
            metadata={"action": "auto_approve"},
        )
        assert transition.metadata == {"action": "auto_approve"}


class TestFlowContext:
    """Tests for FlowContext dataclass."""

    def test_create_context(self):
        """Create flow context."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        ctx = FlowContext(decision=decision)

        assert ctx.decision == decision
        assert ctx.committee is None
        assert ctx.policy_result is None
        assert ctx.invariants is None
        assert ctx.current_state == FlowState.INIT
        assert ctx.transitions == []
        assert ctx.error is None

    def test_elapsed_ms(self):
        """Calculate elapsed time."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        ctx = FlowContext(decision=decision)
        time.sleep(0.01)  # 10ms
        elapsed = ctx.elapsed_ms()
        assert elapsed >= 10

    def test_add_transition(self):
        """Add state transition."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        ctx = FlowContext(decision=decision)

        ctx.add_transition(
            to_state=FlowState.POLICY_CHECK,
            event=FlowEvent.START,
            metadata={"test": True},
        )

        assert ctx.current_state == FlowState.POLICY_CHECK
        assert len(ctx.transitions) == 1
        assert ctx.transitions[0].from_state == FlowState.INIT
        assert ctx.transitions[0].to_state == FlowState.POLICY_CHECK
        assert ctx.transitions[0].event == FlowEvent.START
        assert ctx.transitions[0].metadata == {"test": True}

    def test_multiple_transitions(self):
        """Track multiple transitions."""
        decision = Decision.create("c1", "d1", "G1", "verified")
        ctx = FlowContext(decision=decision)

        ctx.add_transition(FlowState.POLICY_CHECK, FlowEvent.START)
        ctx.add_transition(FlowState.INVARIANT_CHECK, FlowEvent.POLICY_PASSED)
        ctx.add_transition(FlowState.AUTO_APPROVE, FlowEvent.INVARIANTS_PASSED)

        assert len(ctx.transitions) == 3
        assert ctx.current_state == FlowState.AUTO_APPROVE


class TestGuardianFlow:
    """Tests for GuardianFlow class."""

    def test_init_default(self):
        """Initialize with defaults."""
        flow = GuardianFlow()
        assert flow.timeout_seconds == 20

    def test_init_custom_timeout(self):
        """Initialize with custom timeout."""
        flow = GuardianFlow(timeout_seconds=60)
        assert flow.timeout_seconds == 60

    def test_set_state_change_callback(self):
        """Set state change callback."""
        flow = GuardianFlow()
        callback = MagicMock()
        flow.set_state_change_callback(callback)
        assert flow._on_state_change == callback

    def _make_policy_result(self, action, params=None):
        """Helper to create mock PolicyExecutionResult."""
        mock_result = MagicMock()
        mock_result.final_action = action
        mock_result.final_action_params = params or {}
        mock_result.policy_version = "v1"
        return mock_result

    def test_execute_auto_approve(self):
        """Execute flow with auto-approve policy."""
        mock_engine = MagicMock()
        mock_result = self._make_policy_result(PolicyAction.AUTO_APPROVE)
        mock_engine.execute.return_value = mock_result
        mock_engine.check_e40_5_invariants.return_value = {"inv1": True}

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.COMPLETED
        assert decision.status == DecisionStatus.APPROVED
        assert len(ctx.transitions) >= 3

    def test_execute_requires_review(self):
        """Execute flow that requires human review."""
        mock_engine = MagicMock()
        mock_result = self._make_policy_result(PolicyAction.HUMAN_REVIEW)
        mock_engine.execute.return_value = mock_result

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.AWAITING_REVIEW
        assert not decision.is_terminal()

    def test_execute_requires_quorum(self):
        """Execute flow that requires committee quorum."""
        mock_engine = MagicMock()
        mock_result = self._make_policy_result(
            PolicyAction.COMMITTEE_QUORUM,
            {"quorum": 3}
        )
        mock_engine.execute.return_value = mock_result

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.AWAITING_QUORUM
        assert ctx.committee is not None
        assert ctx.committee.quorum_required == 3

    def test_execute_invariants_failed(self):
        """Execute flow when invariants fail."""
        mock_engine = MagicMock()
        mock_result = self._make_policy_result(PolicyAction.AUTO_APPROVE)
        mock_engine.execute.return_value = mock_result
        mock_engine.check_e40_5_invariants.return_value = {
            "inv1": True,
            "inv2": False,
        }

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.AWAITING_REVIEW
        assert ctx.invariants == {"inv1": True, "inv2": False}

    def test_execute_no_policy(self):
        """Execute flow when no policy found."""
        mock_engine = MagicMock()
        mock_engine.execute.side_effect = ValueError("No policy found")

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        # Should fallback to human review
        assert ctx.current_state == FlowState.AWAITING_REVIEW

    def test_process_review_approved(self):
        """Process approved review decision."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.AWAITING_REVIEW

        ctx = run_async(flow.process_review_decision(
            ctx=ctx,
            approved=True,
            reviewer_id="reviewer_123",
            reason="Evidence is valid",
        ))

        assert ctx.current_state == FlowState.COMPLETED
        assert decision.status == DecisionStatus.APPROVED
        assert decision.final_state == "verified"
        assert decision.final_reason == "Evidence is valid"

    def test_process_review_rejected(self):
        """Process rejected review decision."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.AWAITING_REVIEW

        ctx = run_async(flow.process_review_decision(
            ctx=ctx,
            approved=False,
            reviewer_id="reviewer_123",
            reason="Insufficient evidence",
        ))

        assert ctx.current_state == FlowState.COMPLETED
        assert decision.status == DecisionStatus.REJECTED
        assert decision.final_state == "rejected"

    def test_process_review_wrong_state(self):
        """Process review in wrong state does nothing."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.INIT

        ctx = run_async(flow.process_review_decision(
            ctx=ctx,
            approved=True,
            reviewer_id="reviewer_123",
        ))

        assert ctx.current_state == FlowState.INIT  # Unchanged

    def test_process_vote_approve_quorum(self):
        """Process votes reaching approve quorum."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        committee = Committee.create(decision.id, quorum_required=3)
        ctx = FlowContext(decision=decision, committee=committee)
        ctx.current_state = FlowState.AWAITING_QUORUM

        # Add votes
        for i in range(3):
            vote = Vote.create(f"member_{i}", VoteType.APPROVE)
            ctx = run_async(flow.process_vote(ctx, vote))

        assert ctx.current_state == FlowState.COMPLETED
        assert decision.status == DecisionStatus.APPROVED

    def test_process_vote_reject_quorum(self):
        """Process votes reaching reject quorum."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        committee = Committee.create(decision.id, quorum_required=3)
        ctx = FlowContext(decision=decision, committee=committee)
        ctx.current_state = FlowState.AWAITING_QUORUM

        # Add reject votes
        for i in range(3):
            vote = Vote.create(f"member_{i}", VoteType.REJECT)
            ctx = run_async(flow.process_vote(ctx, vote))

        assert ctx.current_state == FlowState.COMPLETED
        assert decision.status == DecisionStatus.REJECTED

    def test_process_vote_tie_escalates(self):
        """Process votes resulting in tie escalates."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        committee = Committee.create(decision.id, quorum_required=2)
        ctx = FlowContext(decision=decision, committee=committee)
        ctx.current_state = FlowState.AWAITING_QUORUM

        ctx = run_async(flow.process_vote(ctx, Vote.create("m1", VoteType.APPROVE)))
        ctx = run_async(flow.process_vote(ctx, Vote.create("m2", VoteType.REJECT)))

        assert ctx.current_state == FlowState.ESCALATED
        assert decision.status == DecisionStatus.ESCALATED

    def test_process_vote_wrong_state(self):
        """Process vote in wrong state does nothing."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.INIT

        vote = Vote.create("m1", VoteType.APPROVE)
        ctx = run_async(flow.process_vote(ctx, vote))

        assert ctx.current_state == FlowState.INIT

    def test_create_decision_block_completed(self):
        """Create decision block for completed flow."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        decision.complete(DecisionStatus.APPROVED, "verified", "auto")

        ctx = FlowContext(
            decision=decision,
            invariants={"inv1": True},
        )
        ctx.current_state = FlowState.COMPLETED

        block = flow.create_decision_block(ctx)

        assert block is not None
        assert block.decision_id == decision.id
        assert block.final_state == "verified"
        assert block.invariants_checked == {"inv1": True}

    def test_create_decision_block_not_completed(self):
        """Create decision block for non-completed flow returns None."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.AWAITING_REVIEW

        block = flow.create_decision_block(ctx)

        assert block is None

    def test_create_decision_block_with_committee(self):
        """Create decision block with committee summary."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        decision.complete(DecisionStatus.APPROVED, "verified", "committee")

        committee = Committee.create(decision.id, quorum_required=3)
        committee.add_vote(Vote.create("m1", VoteType.APPROVE))
        committee.add_vote(Vote.create("m2", VoteType.APPROVE))
        committee.add_vote(Vote.create("m3", VoteType.REJECT))

        ctx = FlowContext(decision=decision, committee=committee)
        ctx.current_state = FlowState.COMPLETED

        block = flow.create_decision_block(ctx)

        assert block.committee_summary is not None
        assert block.committee_summary["quorum_reached"] is True


class TestStateChangeCallback:
    """Tests for state change callback notification."""

    def test_callback_exception_handled(self):
        """State change callback exception is handled gracefully."""
        flow = GuardianFlow()

        def failing_callback(ctx):
            raise RuntimeError("Callback error")

        flow.set_state_change_callback(failing_callback)

        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)

        # Should not raise, just log warning
        flow._notify_state_change(ctx)


class TestCheckTimeout:
    """Tests for timeout checking."""

    def test_check_timeout_true(self):
        """Timeout returns True when exceeded."""
        flow = GuardianFlow(timeout_seconds=0)  # 0 seconds means immediate timeout
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)

        time.sleep(0.01)  # Wait a bit
        assert flow._check_timeout(ctx) is True

    def test_check_timeout_false(self):
        """Timeout returns False when not exceeded."""
        flow = GuardianFlow(timeout_seconds=60)
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)

        assert flow._check_timeout(ctx) is False


class TestTransitionErrors:
    """Tests for invalid transition handling."""

    def test_invalid_transition_returns_false(self):
        """Invalid transition returns False and doesn't change state."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.COMPLETED  # Terminal state

        result = flow._transition(ctx, FlowEvent.START)

        assert result is False
        assert ctx.current_state == FlowState.COMPLETED

    def test_next_state_none_returns_false(self):
        """When next state is None, transition returns False."""
        flow = GuardianFlow()
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)

        # Try an invalid transition
        result = flow._transition(ctx, FlowEvent.REVIEW_APPROVED)

        assert result is False


class TestPolicyCheckTimeout:
    """Tests for policy check timeout handling."""

    def test_policy_check_timeout(self):
        """Policy check handles timeout."""
        mock_engine = MagicMock()
        flow = GuardianFlow(policy_engine=mock_engine, timeout_seconds=0)
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.POLICY_CHECK

        time.sleep(0.01)  # Exceed timeout

        run_async(flow._execute_policy_check(ctx, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.TIMED_OUT


class TestInvariantCheckTimeout:
    """Tests for invariant check timeout handling."""

    def test_invariant_check_timeout(self):
        """Invariant check handles timeout."""
        mock_engine = MagicMock()
        flow = GuardianFlow(policy_engine=mock_engine, timeout_seconds=0)
        decision = Decision.create("c1", "politics", "G7", "verified")
        ctx = FlowContext(decision=decision)
        ctx.current_state = FlowState.INVARIANT_CHECK

        time.sleep(0.01)  # Exceed timeout

        run_async(flow._execute_invariant_check(ctx, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.TIMED_OUT


class TestUnknownPolicyAction:
    """Tests for unknown policy action handling."""

    def test_unknown_action_fallback_to_review(self):
        """Unknown policy action falls back to human review."""
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.final_action = None  # Unknown action
        mock_result.final_action_params = {}
        mock_engine.execute.return_value = mock_result

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.AWAITING_REVIEW


class TestExecutionError:
    """Tests for flow execution error handling."""

    def test_execution_error_transitions_to_failed(self):
        """Flow execution error transitions to FAILED state."""
        mock_engine = MagicMock()
        mock_engine.execute.side_effect = RuntimeError("Unexpected error")

        flow = GuardianFlow(policy_engine=mock_engine)
        decision = Decision.create("c1", "politics", "G7", "verified")

        ctx = run_async(flow.execute(decision, {"claim_id": "c1"}))

        assert ctx.current_state == FlowState.FAILED
        assert ctx.error == "Unexpected error"
