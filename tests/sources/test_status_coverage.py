"""
Tests for Sources Status Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines in status.py
"""

import pytest

from app.sources.status import can_transition, assert_valid_transition
from app.sources.models import SourceState


class TestCanTransition:
    """Tests for can_transition function."""

    def test_from_disabled_perm_returns_false(self):
        """Line 26: Transition from DISABLED_PERM should always return False."""
        result = can_transition(
            SourceState.DISABLED_PERM,
            SourceState.ACTIVE
        )

        assert result is False

    def test_from_disabled_perm_to_any_state_returns_false(self):
        """Line 26: All transitions from DISABLED_PERM should return False."""
        # Test various target states
        for target_state in [
            SourceState.PROPOSED,
            SourceState.TESTING,
            SourceState.ACTIVE,
            SourceState.UNDER_REVIEW,
            SourceState.SUSPECT,
            SourceState.DISABLED_TEMP,
            SourceState.DISABLED_PERM,
        ]:
            result = can_transition(SourceState.DISABLED_PERM, target_state)
            assert result is False, f"Transition from DISABLED_PERM to {target_state} should be False"


class TestValidTransitions:
    """Additional tests for valid transition scenarios."""

    def test_any_state_to_disabled_perm_returns_true(self):
        """Any state can transition to DISABLED_PERM."""
        # Test from various states
        for from_state in [
            SourceState.PROPOSED,
            SourceState.TESTING,
            SourceState.ACTIVE,
            SourceState.UNDER_REVIEW,
            SourceState.SUSPECT,
            SourceState.DISABLED_TEMP,
        ]:
            result = can_transition(from_state, SourceState.DISABLED_PERM)
            assert result is True, f"Transition from {from_state} to DISABLED_PERM should be True"

    def test_proposed_to_testing(self):
        """PROPOSED can transition to TESTING."""
        result = can_transition(SourceState.PROPOSED, SourceState.TESTING)
        assert result is True

    def test_proposed_to_active(self):
        """PROPOSED can transition to ACTIVE."""
        result = can_transition(SourceState.PROPOSED, SourceState.ACTIVE)
        assert result is True

    def test_invalid_transition_returns_false(self):
        """Invalid transitions return False."""
        # PROPOSED cannot go to SUSPECT
        result = can_transition(SourceState.PROPOSED, SourceState.SUSPECT)
        assert result is False


class TestAssertValidTransition:
    """Tests for assert_valid_transition function."""

    def test_valid_transition_does_not_raise(self):
        """Valid transition should not raise."""
        # Should not raise
        assert_valid_transition(SourceState.PROPOSED, SourceState.ACTIVE)

    def test_invalid_transition_raises(self):
        """Invalid transition should raise ValueError."""
        with pytest.raises(ValueError, match="Transição inválida"):
            assert_valid_transition(SourceState.PROPOSED, SourceState.SUSPECT)

    def test_disabled_perm_transition_raises(self):
        """Transition from DISABLED_PERM should raise ValueError."""
        with pytest.raises(ValueError, match="Transição inválida"):
            assert_valid_transition(SourceState.DISABLED_PERM, SourceState.ACTIVE)
