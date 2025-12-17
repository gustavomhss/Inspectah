"""
Tests for NO-GO Signal Integration in Guardian Flow (S40-BE-015).

Tests for FlowEvent.NOGO_BLOCKED and related functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.guardian.flow import (
    FlowState,
    FlowEvent,
    FlowContext,
    GuardianFlow,
    TRANSITIONS,
)
from app.guardian.models import Decision, DecisionStatus


def _create_decision() -> Decision:
    """Create a test decision."""
    return Decision.create(
        claim_id="claim-nogo-test",
        domain="test",
        gate="G22",
        proposed_state="VERIFIED",
        claim_summary="Test claim for NO-GO signals",
    )


class TestNOGOBlockedEvent:
    """Tests for NOGO_BLOCKED event."""

    def test_nogo_blocked_event_exists(self):
        """NOGO_BLOCKED event is defined."""
        assert FlowEvent.NOGO_BLOCKED == "nogo_blocked"

    def test_nogo_blocked_in_transitions(self):
        """NOGO_BLOCKED leads to BLOCKED state in all applicable states."""
        states_with_nogo = [
            FlowState.POLICY_CHECK,
            FlowState.INVARIANT_CHECK,
            FlowState.AUTO_APPROVE,
            FlowState.AWAITING_REVIEW,
            FlowState.AWAITING_QUORUM,
            FlowState.ESCALATED,
        ]
        for state in states_with_nogo:
            assert FlowEvent.NOGO_BLOCKED in TRANSITIONS[state]
            assert TRANSITIONS[state][FlowEvent.NOGO_BLOCKED] == FlowState.BLOCKED


class TestFlowContextNOGO:
    """Tests for FlowContext NO-GO signal fields."""

    def test_context_has_signal_refs(self):
        """FlowContext has signal_refs field."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)

        assert hasattr(ctx, "signal_refs")
        assert ctx.signal_refs == []

    def test_context_has_nogo_blocked(self):
        """FlowContext has nogo_blocked field."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)

        assert hasattr(ctx, "nogo_blocked")
        assert ctx.nogo_blocked is False

    def test_has_nogo_signals_empty(self):
        """has_nogo_signals returns False when no signals."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)

        assert ctx.has_nogo_signals() is False

    def test_has_nogo_signals_with_refs(self):
        """has_nogo_signals returns True when signal_refs present."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)
        ctx.signal_refs = ["sig_123"]

        assert ctx.has_nogo_signals() is True

    def test_has_nogo_signals_when_blocked(self):
        """has_nogo_signals returns True when nogo_blocked is True."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)
        ctx.nogo_blocked = True

        assert ctx.has_nogo_signals() is True

    def test_add_nogo_signal(self):
        """add_nogo_signal adds signal ID."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)

        ctx.add_nogo_signal("sig_001")
        ctx.add_nogo_signal("sig_002")

        assert len(ctx.signal_refs) == 2
        assert "sig_001" in ctx.signal_refs
        assert "sig_002" in ctx.signal_refs

    def test_add_nogo_signal_no_duplicates(self):
        """add_nogo_signal doesn't add duplicates."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)

        ctx.add_nogo_signal("sig_001")
        ctx.add_nogo_signal("sig_001")

        assert len(ctx.signal_refs) == 1

    def test_clear_nogo_signals(self):
        """clear_nogo_signals clears all signals."""
        decision = _create_decision()
        ctx = FlowContext(decision=decision)
        ctx.signal_refs = ["sig_001", "sig_002"]
        ctx.nogo_blocked = True

        ctx.clear_nogo_signals()

        assert ctx.signal_refs == []
        assert ctx.nogo_blocked is False


class TestGuardianFlowNOGO:
    """Tests for GuardianFlow NO-GO signal methods."""

    def test_check_nogo_signals_no_signals(self):
        """check_nogo_signals with no signals doesn't block."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.POLICY_CHECK)

        # Evidence that doesn't trigger signals (all supports)
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "supports"},
        ]

        result = flow.check_nogo_signals(ctx, claim_id="claim-1", evidence_trail=evidence)

        assert result.current_state == FlowState.POLICY_CHECK
        assert not result.nogo_blocked
        assert len(result.signal_refs) == 0

    def test_check_nogo_signals_blocks_on_inconsistency(self):
        """check_nogo_signals blocks when inconsistency detected."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.POLICY_CHECK)

        # Evidence with high conflict ratio (triggers inconsistency)
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
            {"evidence_id": "e3", "stance": "refutes"},
        ]

        result = flow.check_nogo_signals(ctx, claim_id="claim-2", evidence_trail=evidence)

        assert result.current_state == FlowState.BLOCKED
        assert result.nogo_blocked is True
        assert len(result.signal_refs) > 0
        assert "INCONSISTENCY" in result.blocked_reason

    def test_check_nogo_signals_blocks_on_abuse(self):
        """check_nogo_signals blocks when abuse detected."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.AWAITING_REVIEW)

        result = flow.check_nogo_signals(
            ctx,
            claim_id="claim-3",
            source_id="bad-source",
            retracted_count=5,  # Above threshold
        )

        assert result.current_state == FlowState.BLOCKED
        assert result.nogo_blocked is True
        assert "ABUSE" in result.blocked_reason

    def test_clear_nogo_block(self):
        """clear_nogo_block resolves signals and unblocks."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.BLOCKED)
        ctx.nogo_blocked = True
        ctx.signal_refs = ["sig_001"]
        ctx.blocked_reason = "NO-GO signals detected"

        with patch("app.claims.signals.get_signal_repository") as mock_get_repo:
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            result = flow.clear_nogo_block(ctx, resolver_id="admin", reason="False positive")

        assert result.nogo_blocked is False
        assert result.signal_refs == []
        assert result.blocked_reason is None
        assert result.current_state == FlowState.AWAITING_REVIEW  # Unblocked
        mock_repo.resolve.assert_called_once_with("sig_001", "admin", "False positive")

    def test_clear_nogo_block_no_signals(self):
        """clear_nogo_block does nothing when no signals."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.AWAITING_REVIEW)

        result = flow.clear_nogo_block(ctx, resolver_id="admin", reason="Test")

        # Should return context unchanged
        assert result.current_state == FlowState.AWAITING_REVIEW
        assert not result.nogo_blocked


class TestNOGOTransitions:
    """Tests for NO-GO related state transitions."""

    def test_policy_check_to_blocked_via_nogo(self):
        """POLICY_CHECK can transition to BLOCKED via NOGO_BLOCKED."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.POLICY_CHECK)

        flow._transition(ctx, FlowEvent.NOGO_BLOCKED, {"reason": "test"})

        assert ctx.current_state == FlowState.BLOCKED
        assert len(ctx.transitions) == 1
        assert ctx.transitions[0].event == FlowEvent.NOGO_BLOCKED

    def test_blocked_to_awaiting_review_via_unblock(self):
        """BLOCKED can transition to AWAITING_REVIEW via UNBLOCK."""
        flow = GuardianFlow()
        decision = _create_decision()
        ctx = FlowContext(decision=decision, current_state=FlowState.BLOCKED)

        flow._transition(ctx, FlowEvent.UNBLOCK, {"resolver_id": "admin"})

        assert ctx.current_state == FlowState.AWAITING_REVIEW
