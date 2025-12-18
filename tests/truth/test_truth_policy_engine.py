"""
Tests for Truth Policy Engine — S37

Tests for central policy engine.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.truth.policy_engine import (
    PolicyEngine,
    get_policy_engine,
    DEFAULT_POLICIES_DIR,
)
from app.truth.policy_dsl.executor import PolicyAction, PolicyExecutionResult
from app.truth.policy_dsl.grammar import PolicyAST, RequireCondition


class TestPolicyEngine:
    """Tests for PolicyEngine class."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine with temp directory."""
        return PolicyEngine(policies_dir=tmp_path)

    def test_init_default(self):
        """Initialize with default directory."""
        engine = PolicyEngine()

        assert engine.policies_dir == DEFAULT_POLICIES_DIR
        assert engine._policy_cache == {}
        assert engine._loaded is False

    def test_init_custom(self, tmp_path):
        """Initialize with custom directory."""
        engine = PolicyEngine(policies_dir=tmp_path)

        assert engine.policies_dir == tmp_path

    def test_load_policies_no_dir(self, tmp_path):
        """Load policies when directory doesn't exist."""
        engine = PolicyEngine(policies_dir=tmp_path / "nonexistent")

        count = engine.load_policies()

        assert count == 0
        # _loaded stays False when directory doesn't exist (early return)

    def test_load_policies_from_files(self, tmp_path):
        """Load policies from files."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY test_policy
        DOMAIN politics
        GATE G1
        REQUIRE sources >= 1
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)
        count = engine.load_policies()

        assert count == 1
        assert "politics:G1" in engine._policy_cache
        assert "test_policy" in engine._policy_cache

    def test_load_policies_invalid_file(self, tmp_path):
        """Handle invalid policy file."""
        policy_file = tmp_path / "bad.policy"
        policy_file.write_text("INVALID SYNTAX", encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)
        count = engine.load_policies()

        assert count == 0  # Failed to load

    def test_load_policy_file(self, tmp_path):
        """Load single policy file."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY single
        DOMAIN test
        GATE G2
        REQUIRE sources >= 2
        VERSION "2.0.0"
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)
        policy = engine._load_policy_file(policy_file)

        assert policy.name == "single"
        assert policy.domain == "test"
        assert policy.gate == "G2"
        assert policy.version == "2.0.0"

    def test_load_policy_file_validation_error(self, tmp_path):
        """Load policy file with validation errors."""
        policy_file = tmp_path / "invalid.policy"
        policy_file.write_text("""
        POLICY invalid
        DOMAIN test
        GATE INVALID_GATE
        REQUIRE sources >= 1
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        with pytest.raises(ValueError, match="validation failed"):
            engine._load_policy_file(policy_file)

    def test_get_policy(self, tmp_path):
        """Get policy by domain and gate."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY test
        DOMAIN politics
        GATE G1
        REQUIRE sources >= 1
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        policy = engine.get_policy("politics", "G1")

        assert policy is not None
        assert policy.name == "test"
        assert engine._loaded is True

    def test_get_policy_not_found(self, tmp_path):
        """Get policy returns None when not found."""
        engine = PolicyEngine(policies_dir=tmp_path)

        policy = engine.get_policy("unknown", "G99")

        assert policy is None

    def test_get_policy_by_name(self, tmp_path):
        """Get policy by name."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY my_policy
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        policy = engine.get_policy_by_name("my_policy")

        assert policy is not None
        assert policy.name == "my_policy"

    def test_list_policies(self, tmp_path):
        """List all loaded policies."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY list_test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON high_confidence THEN auto_approve
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        policies = engine.list_policies()

        assert len(policies) == 1
        assert policies[0]["name"] == "list_test"
        assert policies[0]["requirements"] == 1
        assert policies[0]["rules"] == 1

    def test_execute_policy(self, tmp_path):
        """Execute policy against context."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY exec_test
        DOMAIN politics
        GATE G1
        REQUIRE sources >= 2
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        context = {"sources": 3}
        result = engine.execute("politics", "G1", context)

        assert isinstance(result, PolicyExecutionResult)
        assert result.all_requirements_met is True

    def test_execute_policy_not_found(self, tmp_path):
        """Execute raises when policy not found."""
        engine = PolicyEngine(policies_dir=tmp_path)

        with pytest.raises(ValueError, match="No policy found"):
            engine.execute("unknown", "G99", {})

    def test_execute_by_name(self, tmp_path):
        """Execute policy by name."""
        policy_file = tmp_path / "named.policy"
        policy_file.write_text("""
        POLICY specific_policy
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        result = engine.execute("test", "G1", {"sources": 2}, policy_name="specific_policy")

        assert result.policy_name == "specific_policy"


class TestE40_5Invariants:
    """Tests for E40.5 invariant checking."""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create engine."""
        return PolicyEngine(policies_dir=tmp_path)

    def test_check_invariants_all_pass(self, engine):
        """All invariants pass."""
        context = {
            "evidence_count": 3,
            "sources": 2,
            "gate": "G1",
            "temporal_consistent": True,
            "state": "pending",
            "confidence_score": 0.8,
        }

        invariants = engine.check_e40_5_invariants(context)

        assert all(invariants.values())
        assert invariants["evidence_exists"] is True
        assert invariants["source_plurality"] is True
        assert invariants["temporal_coherence"] is True
        assert invariants["non_contradiction"] is True
        assert invariants["confidence_bounds"] is True

    def test_invariant_evidence_exists_fail(self, engine):
        """Evidence exists invariant fails."""
        context = {"evidence_count": 0}

        invariants = engine.check_e40_5_invariants(context)

        assert invariants["evidence_exists"] is False

    def test_invariant_source_plurality_g2(self, engine):
        """Source plurality for G2+ gates."""
        # G2 requires 2+ sources
        context_fail = {"sources": 1, "gate": "G2"}
        invariants = engine.check_e40_5_invariants(context_fail)
        assert invariants["source_plurality"] is False

        context_pass = {"sources": 2, "gate": "G2"}
        invariants = engine.check_e40_5_invariants(context_pass)
        assert invariants["source_plurality"] is True

    def test_invariant_source_plurality_g1(self, engine):
        """Source plurality for G1 (no requirement)."""
        context = {"sources": 1, "gate": "G1"}

        invariants = engine.check_e40_5_invariants(context)

        assert invariants["source_plurality"] is True

    def test_invariant_temporal_coherence(self, engine):
        """Temporal coherence invariant."""
        context_pass = {"temporal_consistent": True}
        invariants = engine.check_e40_5_invariants(context_pass)
        assert invariants["temporal_coherence"] is True

        context_fail = {"temporal_consistent": False}
        invariants = engine.check_e40_5_invariants(context_fail)
        assert invariants["temporal_coherence"] is False

    def test_invariant_non_contradiction_verified(self, engine):
        """Non-contradiction for verified state."""
        # Verified with strong contradiction fails
        context_fail = {
            "state": "verified",
            "has_contradiction": True,
            "contradiction_strength": "strong",
        }
        invariants = engine.check_e40_5_invariants(context_fail)
        assert invariants["non_contradiction"] is False

        # Verified with weak contradiction passes
        context_pass = {
            "state": "verified",
            "has_contradiction": True,
            "contradiction_strength": "weak",
        }
        invariants = engine.check_e40_5_invariants(context_pass)
        assert invariants["non_contradiction"] is True

    def test_invariant_non_contradiction_pending(self, engine):
        """Non-contradiction for non-verified states."""
        context = {
            "state": "pending",
            "has_contradiction": True,
            "contradiction_strength": "strong",
        }

        invariants = engine.check_e40_5_invariants(context)

        assert invariants["non_contradiction"] is True  # Not applicable

    def test_invariant_confidence_bounds(self, engine):
        """Confidence bounds invariant."""
        context_pass = {"confidence_score": 0.75}
        invariants = engine.check_e40_5_invariants(context_pass)
        assert invariants["confidence_bounds"] is True

        context_fail_low = {"confidence_score": -0.1}
        invariants = engine.check_e40_5_invariants(context_fail_low)
        assert invariants["confidence_bounds"] is False

        context_fail_high = {"confidence_score": 1.5}
        invariants = engine.check_e40_5_invariants(context_fail_high)
        assert invariants["confidence_bounds"] is False


class TestExecuteWithInvariants:
    """Tests for execute_with_invariants method."""

    def test_execute_with_invariants_pass(self, tmp_path):
        """Execute with all invariants passing."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY inv_test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON high_confidence THEN auto_approve
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        context = {
            "sources": 2,
            "evidence_count": 1,
            "confidence": "high",
            "temporal_consistent": True,
            "confidence_score": 0.9,
        }

        result = engine.execute_with_invariants("test", "G1", context)

        assert result["all_invariants_pass"] is True
        assert isinstance(result["execution_result"], PolicyExecutionResult)
        assert "invariants" in result

    def test_execute_with_invariants_override_auto_approve(self, tmp_path):
        """Override auto_approve when invariants fail."""
        policy_file = tmp_path / "test.policy"
        policy_file.write_text("""
        POLICY inv_override
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON high_confidence THEN auto_approve
        """, encoding="utf-8")

        engine = PolicyEngine(policies_dir=tmp_path)

        context = {
            "sources": 2,
            "evidence_count": 0,  # Invariant violation
            "confidence": "high",
            "temporal_consistent": True,
            "confidence_score": 0.9,
        }

        result = engine.execute_with_invariants("test", "G1", context)

        assert result["all_invariants_pass"] is False
        # Action should be overridden to HUMAN_REVIEW
        assert result["execution_result"].final_action == PolicyAction.HUMAN_REVIEW
        assert result["execution_result"].final_action_params["reason"] == "invariant_violation"


class TestGetPolicyEngine:
    """Tests for get_policy_engine singleton."""

    def test_get_policy_engine_creates_instance(self):
        """Creates singleton instance."""
        import app.truth.policy_engine as module

        # Reset singleton
        module._engine = None

        engine = get_policy_engine()

        assert engine is not None
        assert isinstance(engine, PolicyEngine)

    def test_get_policy_engine_returns_same_instance(self):
        """Returns same instance on subsequent calls."""
        import app.truth.policy_engine as module

        # Reset singleton
        module._engine = None

        engine1 = get_policy_engine()
        engine2 = get_policy_engine()

        assert engine1 is engine2
