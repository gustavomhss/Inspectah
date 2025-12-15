"""
S38: Tests for Policy Engine - 100% coverage
"""
import pytest

from app.policies.engine import evaluate_policy
from app.policies.context_builder import PolicyEvaluationContext
from app.policies.models import PromotionPolicyConfig
from app.truth.enums import TruthState


class TestEvaluatePolicy:
    """Tests for evaluate_policy function."""

    @pytest.fixture
    def basic_policy(self):
        """Basic non-sensitive policy."""
        return PromotionPolicyConfig(
            name="basic_policy",
            domain="general",
            min_confidence=0.7,
            min_sources=2,
            require_debunk=False,
            require_human=False,
            sensitive=False,
            default_decision="HOLD",
        )

    @pytest.fixture
    def sensitive_policy(self):
        """Sensitive domain policy requiring debunk."""
        return PromotionPolicyConfig(
            name="sensitive_policy",
            domain="health",
            min_confidence=0.9,
            min_sources=3,
            require_debunk=True,
            require_human=True,
            sensitive=True,
            default_decision="BLOCK",
        )

    def test_insufficient_sources_hold(self, basic_policy):
        """Test HOLD decision when sources are insufficient."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.UNKNOWN,
            sources_count=1,  # Less than min_sources=2
            confidence=0.9,
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"
        assert "Fontes insuficientes" in decision.reason
        assert "missing_sources" in decision.flags
        assert decision.flags["missing_sources"] == 1
        assert decision.target_state == TruthState.PROVISIONAL

    def test_insufficient_sources_already_provisional(self, basic_policy):
        """Test that PROVISIONAL state is preserved when already PROVISIONAL."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=1,
            confidence=0.9,
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"
        assert decision.target_state == TruthState.PROVISIONAL

    def test_sensitive_domain_requires_debunk(self, sensitive_policy):
        """Test BLOCK when sensitive domain lacks debunk."""
        ctx = PolicyEvaluationContext(
            domain="health",
            current_state=TruthState.UNKNOWN,
            sources_count=5,
            confidence=0.95,
            has_debunk=False,  # No debunk
        )

        decision = evaluate_policy(sensitive_policy, ctx)

        assert decision.decision == "BLOCK"
        assert "debunker" in decision.reason.lower()
        assert decision.flags.get("require_debunk") is True
        assert decision.target_state == TruthState.UNKNOWN

    def test_sensitive_domain_with_debunk_requires_human(self, sensitive_policy):
        """Test HOLD when sensitive domain needs human review."""
        ctx = PolicyEvaluationContext(
            domain="health",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.95,
            has_debunk=True,
            human_required=False,  # Policy requires human
        )

        decision = evaluate_policy(sensitive_policy, ctx)

        assert decision.decision == "HOLD"
        assert "humana" in decision.reason.lower()
        assert decision.flags.get("require_human") is True
        assert decision.target_state == TruthState.PROVISIONAL

    def test_sensitive_domain_context_requires_human(self):
        """Test HOLD when context itself marks human_required."""
        policy = PromotionPolicyConfig(
            name="sensitive_no_human_req",
            domain="health",
            min_confidence=0.9,
            min_sources=3,
            require_debunk=False,
            require_human=False,  # Policy doesn't require
            sensitive=True,
            default_decision="HOLD",
        )

        ctx = PolicyEvaluationContext(
            domain="health",
            current_state=TruthState.UNKNOWN,
            sources_count=5,
            confidence=0.95,
            has_debunk=True,
            human_required=True,  # Context requires human
        )

        decision = evaluate_policy(policy, ctx)

        assert decision.decision == "HOLD"
        assert decision.flags.get("require_human") is True

    def test_low_confidence_hold(self, basic_policy):
        """Test HOLD when confidence is below minimum."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.5,  # Below min_confidence=0.7
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"
        assert "Confiança abaixo" in decision.reason
        assert decision.flags.get("low_confidence") is True
        assert decision.target_state == TruthState.PROVISIONAL

    def test_low_confidence_unknown_becomes_provisional(self, basic_policy):
        """Test that UNKNOWN becomes PROVISIONAL on low confidence."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.UNKNOWN,
            sources_count=5,
            confidence=0.5,
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"
        assert decision.target_state == TruthState.PROVISIONAL

    def test_promote_recommendation_accepted(self, basic_policy):
        """Test PROMOTE when recommendation is PROMOTE."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            recommendation="PROMOTE",
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "PROMOTE"
        assert decision.target_state == TruthState.ESTABLISHED_FACT
        assert "aceita" in decision.reason.lower()

    def test_promote_recommendation_lowercase(self, basic_policy):
        """Test PROMOTE works with lowercase recommendation."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            recommendation="promote",  # lowercase
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "PROMOTE"

    def test_default_decision_fallback(self, basic_policy):
        """Test default decision when no conditions match."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            recommendation=None,  # No recommendation
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"  # default_decision
        assert "padrão" in decision.reason.lower()
        assert decision.flags.get("default") is True
        assert decision.target_state == TruthState.PROVISIONAL

    def test_confidence_none_skips_check(self, basic_policy):
        """Test that None confidence skips the confidence check."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=None,  # No confidence
        )

        decision = evaluate_policy(basic_policy, ctx)

        # Should reach default decision
        assert decision.decision == "HOLD"
        assert "low_confidence" not in decision.flags

    def test_sensitive_with_debunk_and_no_human_requirement(self):
        """Test sensitive domain with debunk but no human requirement."""
        policy = PromotionPolicyConfig(
            name="sensitive_no_human",
            domain="health",
            min_confidence=0.8,
            min_sources=2,
            require_debunk=True,
            require_human=False,
            sensitive=True,
            default_decision="HOLD",
        )

        ctx = PolicyEvaluationContext(
            domain="health",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            has_debunk=True,
            human_required=False,
        )

        decision = evaluate_policy(policy, ctx)

        # Should pass sensitive checks and reach default
        assert decision.decision == "HOLD"
        assert decision.flags.get("default") is True

    def test_non_promote_recommendation_ignored(self, basic_policy):
        """Test that non-PROMOTE recommendations don't promote."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            recommendation="HOLD",
        )

        decision = evaluate_policy(basic_policy, ctx)

        # Should not promote, should use default
        assert decision.decision == "HOLD"
        assert decision.flags.get("default") is True

    def test_empty_recommendation_ignored(self, basic_policy):
        """Test that empty recommendation is treated as no recommendation."""
        ctx = PolicyEvaluationContext(
            domain="general",
            current_state=TruthState.PROVISIONAL,
            sources_count=5,
            confidence=0.9,
            recommendation="",
        )

        decision = evaluate_policy(basic_policy, ctx)

        assert decision.decision == "HOLD"
        assert decision.flags.get("default") is True
