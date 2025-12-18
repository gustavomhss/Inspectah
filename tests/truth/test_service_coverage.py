"""
Tests for Truth Service Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines 69, 76 in service.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from app.truth.service import apply_transition
from app.truth.repository import TruthRepository
from app.truth.models import TruthRecord
from app.truth.enums import TruthState, TruthEventType
from app.policies.models import PolicyDecision


class TestApplyTransitionPolicyDecision:
    """Tests for apply_transition with policy_decision."""

    def setup_method(self):
        """Setup temporary database for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_truth.sqlite"
        self.repo = TruthRepository(db_path=self.db_path)

    def teardown_method(self):
        """Cleanup temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_policy_decision_block_raises_error(self):
        """Line 69: Policy decision BLOCK should raise InvalidTruthTransition."""
        from app.truth.service import InvalidTruthTransition

        # Create a truth record
        record = TruthRecord(
            id="test-id",
            slug="test:claim",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Create policy decision with BLOCK
        policy_decision = PolicyDecision(
            decision="BLOCK",
            reason="Policy blocked this transition",
            policy_name="test_policy",
            target_state=None,
        )

        # Attempt transition with blocking policy
        with pytest.raises(InvalidTruthTransition, match="Policy bloqueou a transição"):
            apply_transition(
                truth_record=record,
                new_state=TruthState.CLAIMED,
                reason="Trying to transition",
                source="test_source",
                repo=self.repo,
                policy_decision=policy_decision,
            )

    def test_policy_decision_hold_changes_target_state(self):
        """Line 71: Policy decision HOLD should change target state."""
        # Create a truth record
        record = TruthRecord(
            id="test-id",
            slug="test:claim",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Create policy decision with HOLD
        policy_decision = PolicyDecision(
            decision="HOLD",
            reason="Policy holds this transition",
            policy_name="test_policy",
            target_state=TruthState.UNDER_REVIEW,
        )

        # Attempt transition with HOLD policy
        event = apply_transition(
            truth_record=record,
            new_state=TruthState.CLAIMED,  # This will be overridden by policy
            reason="Trying to transition",
            source="test_source",
            repo=self.repo,
            policy_decision=policy_decision,
        )

        # The new_state should be from policy_decision.target_state
        assert event.new_state == TruthState.UNDER_REVIEW

    def test_policy_decision_hold_with_none_target_keeps_current(self):
        """Line 71: Policy decision HOLD with None target_state keeps current state."""
        from app.truth.service import InvalidTruthTransition

        # Create a truth record
        record = TruthRecord(
            id="test-id",
            slug="test:claim",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Create policy decision with HOLD but no target_state
        policy_decision = PolicyDecision(
            decision="HOLD",
            reason="Policy holds this transition",
            policy_name="test_policy",
            target_state=None,  # No target state specified
        )

        # Attempt transition with HOLD policy with no target state
        # This should result in trying to transition to the same state (current_state)
        # which should raise InvalidTruthTransition for redundant transition
        with pytest.raises(InvalidTruthTransition, match="redundante"):
            apply_transition(
                truth_record=record,
                new_state=TruthState.CLAIMED,
                reason="Trying to transition",
                source="test_source",
                repo=self.repo,
                policy_decision=policy_decision,
            )

    def test_policy_decision_allow_proceeds_normally(self):
        """Policy decision ALLOW should proceed with normal transition."""
        # Create a truth record
        record = TruthRecord(
            id="test-id",
            slug="test:claim",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Create policy decision with ALLOW
        policy_decision = PolicyDecision(
            decision="ALLOW",
            reason="Policy allows this transition",
            policy_name="test_policy",
            target_state=None,
        )

        # Transition should proceed normally
        event = apply_transition(
            truth_record=record,
            new_state=TruthState.CLAIMED,
            reason="Normal transition",
            source="test_source",
            repo=self.repo,
            policy_decision=policy_decision,
        )

        assert event.new_state == TruthState.CLAIMED


class TestApplyTransitionWithoutPolicyDecision:
    """Tests for apply_transition without policy_decision (existing behavior)."""

    def setup_method(self):
        """Setup temporary database for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_truth.sqlite"
        self.repo = TruthRepository(db_path=self.db_path)

    def teardown_method(self):
        """Cleanup temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_transition_without_policy_decision(self):
        """Transition without policy_decision should work normally."""
        # Create a truth record
        record = TruthRecord(
            id="test-id",
            slug="test:claim",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Transition without policy_decision
        event = apply_transition(
            truth_record=record,
            new_state=TruthState.CLAIMED,
            reason="Normal transition",
            source="test_source",
            repo=self.repo,
            policy_decision=None,  # No policy decision
        )

        assert event.new_state == TruthState.CLAIMED
