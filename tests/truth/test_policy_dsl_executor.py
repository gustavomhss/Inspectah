"""
Tests for Truth Policy DSL Executor — S37

Tests for policy execution against contexts.
"""

import pytest

from app.truth.policy_dsl.executor import (
    PolicyAction,
    PolicyExecutionResult,
    PolicyExecutor,
    RequirementResult,
    RuleResult,
    execute_policy,
)
from app.truth.policy_dsl.grammar import OnThenRule, PolicyAST, RequireCondition


class TestPolicyAction:
    """Tests for PolicyAction enum."""

    def test_action_values(self):
        """PolicyAction has expected values."""
        assert PolicyAction.AUTO_APPROVE.value == "auto_approve"
        assert PolicyAction.AUTO_REJECT.value == "auto_reject"
        assert PolicyAction.HUMAN_REVIEW.value == "human_review"
        assert PolicyAction.COMMITTEE_QUORUM.value == "committee_quorum"
        assert PolicyAction.ESCALATE.value == "escalate"
        assert PolicyAction.DEFER.value == "defer"
        assert PolicyAction.FLAG_FOR_REVIEW.value == "flag_for_review"


class TestRequirementResult:
    """Tests for RequirementResult dataclass."""

    def test_create_passed(self):
        """Create passed requirement result."""
        req = RequireCondition("sources", ">=", 2)
        result = RequirementResult(
            requirement=req,
            passed=True,
            actual_value=3,
            message="sources >= 2: actual=3",
        )

        assert result.passed is True
        assert result.actual_value == 3

    def test_create_failed(self):
        """Create failed requirement result."""
        req = RequireCondition("evidence_count", ">=", 5)
        result = RequirementResult(
            requirement=req,
            passed=False,
            actual_value=2,
            message="evidence_count >= 5: actual=2",
        )

        assert result.passed is False


class TestRuleResult:
    """Tests for RuleResult dataclass."""

    def test_create_triggered(self):
        """Create triggered rule result."""
        rule = OnThenRule("high_confidence", "=", True, "auto_approve")
        result = RuleResult(
            rule=rule,
            triggered=True,
            action=PolicyAction.AUTO_APPROVE,
            action_params={"reason": "high confidence"},
        )

        assert result.triggered is True
        assert result.action == PolicyAction.AUTO_APPROVE

    def test_create_not_triggered(self):
        """Create not triggered rule result."""
        rule = OnThenRule("low_confidence", "=", True, "human_review")
        result = RuleResult(
            rule=rule,
            triggered=False,
        )

        assert result.triggered is False
        assert result.action is None


class TestPolicyExecutionResult:
    """Tests for PolicyExecutionResult dataclass."""

    def test_create_full(self):
        """Create full execution result."""
        result = PolicyExecutionResult(
            policy_name="test_policy",
            policy_version="1.0.0",
            domain="politics",
            gate="G1",
            all_requirements_met=True,
            requirement_results=[],
            triggered_rules=[],
            final_action=PolicyAction.AUTO_APPROVE,
            final_action_params={},
            context_used={"sources": 3},
        )

        assert result.policy_name == "test_policy"
        assert result.all_requirements_met is True
        assert result.final_action == PolicyAction.AUTO_APPROVE


class TestPolicyExecutor:
    """Tests for PolicyExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create executor."""
        return PolicyExecutor()

    @pytest.fixture
    def basic_policy(self):
        """Create basic policy."""
        return PolicyAST(
            name="basic_policy",
            domain="politics",
            gate="G1",
            requirements=[
                RequireCondition("sources", ">=", 2),
                RequireCondition("evidence_count", ">=", 1),
            ],
            rules=[
                OnThenRule("high_confidence", "=", True, "auto_approve"),
                OnThenRule("low_confidence", "=", True, "human_review"),
            ],
            version="1.0.0",
        )

    def test_execute_requirements_met(self, executor, basic_policy):
        """Execute with all requirements met."""
        context = {
            "sources": 3,
            "evidence_count": 2,
            "confidence": "high",
        }

        result = executor.execute(basic_policy, context)

        assert result.all_requirements_met is True
        assert result.final_action == PolicyAction.AUTO_APPROVE

    def test_execute_requirements_not_met(self, executor, basic_policy):
        """Execute with requirements not met."""
        context = {
            "sources": 1,  # Below required 2
            "evidence_count": 2,
            "confidence": "high",
        }

        result = executor.execute(basic_policy, context)

        assert result.all_requirements_met is False
        assert result.final_action == PolicyAction.HUMAN_REVIEW

    def test_execute_no_rules_triggered(self, executor):
        """Execute with no rules triggered defaults to auto_approve."""
        policy = PolicyAST(
            name="simple",
            domain="test",
            gate="G1",
            requirements=[RequireCondition("sources", ">=", 1)],
            rules=[],
        )
        context = {"sources": 2}

        result = executor.execute(policy, context)

        assert result.all_requirements_met is True
        assert result.final_action == PolicyAction.AUTO_APPROVE

    def test_execute_low_confidence_rule(self, executor, basic_policy):
        """Execute triggers low confidence rule."""
        context = {
            "sources": 3,
            "evidence_count": 2,
            "confidence": "low",
        }

        result = executor.execute(basic_policy, context)

        assert result.final_action == PolicyAction.HUMAN_REVIEW


class TestEvaluateRequirement:
    """Tests for requirement evaluation."""

    @pytest.fixture
    def executor(self):
        """Create executor."""
        return PolicyExecutor()

    def test_evaluate_gte_pass(self, executor):
        """Evaluate >= passes when actual >= expected."""
        req = RequireCondition("sources", ">=", 2)
        context = {"sources": 3}

        result = executor._evaluate_requirement(req, context)

        assert result.passed is True
        assert result.actual_value == 3

    def test_evaluate_gte_fail(self, executor):
        """Evaluate >= fails when actual < expected."""
        req = RequireCondition("sources", ">=", 2)
        context = {"sources": 1}

        result = executor._evaluate_requirement(req, context)

        assert result.passed is False

    def test_evaluate_lte(self, executor):
        """Evaluate <= operator."""
        req = RequireCondition("risk_level", "<=", 5)
        context = {"risk_level": 3}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_gt(self, executor):
        """Evaluate > operator."""
        req = RequireCondition("evidence_count", ">", 0)
        context = {"evidence_count": 1}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_lt(self, executor):
        """Evaluate < operator."""
        req = RequireCondition("claim_age_hours", "<", 24)
        context = {"claim_age_hours": 12}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_eq(self, executor):
        """Evaluate = operator."""
        req = RequireCondition("confidence", "=", "high")
        context = {"confidence": "high"}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_neq(self, executor):
        """Evaluate != operator."""
        req = RequireCondition("risk_level", "!=", "critical")
        context = {"risk_level": "low"}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_missing_field(self, executor):
        """Evaluate fails when field missing from context."""
        req = RequireCondition("missing_field", ">=", 1)
        context = {}

        result = executor._evaluate_requirement(req, context)

        assert result.passed is False
        assert "not found" in result.message

    def test_evaluate_no_contradiction(self, executor):
        """Evaluate no_contradiction requirement."""
        req = RequireCondition("no_contradiction", "=", True)
        context = {"has_contradiction": False}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

    def test_evaluate_no_contradiction_strong(self, executor):
        """Evaluate no_contradiction with strong modifier."""
        req = RequireCondition("no_contradiction", "=", True, modifier="strong")

        # Weak contradiction should pass with strong modifier
        context = {"has_contradiction": True, "contradiction_strength": "weak"}
        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

        # Strong contradiction should fail
        context = {"has_contradiction": True, "contradiction_strength": "strong"}
        result = executor._evaluate_requirement(req, context)
        assert result.passed is False

    def test_evaluate_temporal_consistency(self, executor):
        """Evaluate temporal_consistency requirement."""
        req = RequireCondition("temporal_consistency", "=", True)

        context = {"temporal_consistent": True}
        result = executor._evaluate_requirement(req, context)
        assert result.passed is True

        context = {"temporal_consistent": False}
        result = executor._evaluate_requirement(req, context)
        assert result.passed is False

    def test_evaluate_independent_sources(self, executor):
        """Evaluate sources with independent modifier."""
        req = RequireCondition("sources", ">=", 2, modifier="independent")

        # Should use independent_sources if available
        context = {"sources": 5, "independent_sources": 3}
        result = executor._evaluate_requirement(req, context)
        assert result.actual_value == 3

    def test_evaluate_unknown_operator(self, executor):
        """Evaluate with unknown operator."""
        req = RequireCondition("sources", "??", 2)
        context = {"sources": 3}

        result = executor._evaluate_requirement(req, context)
        assert result.passed is False
        assert "Unknown operator" in result.message


class TestEvaluateRule:
    """Tests for rule evaluation."""

    @pytest.fixture
    def executor(self):
        """Create executor."""
        return PolicyExecutor()

    def test_evaluate_known_condition_high_confidence(self, executor):
        """Evaluate known condition high_confidence."""
        rule = OnThenRule("high_confidence", "=", True, "auto_approve")
        context = {"confidence": "high"}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.AUTO_APPROVE

    def test_evaluate_known_condition_low_confidence(self, executor):
        """Evaluate known condition low_confidence."""
        rule = OnThenRule("low_confidence", "=", True, "human_review")
        context = {"confidence": "low"}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.HUMAN_REVIEW

    def test_evaluate_known_condition_disputed(self, executor):
        """Evaluate known condition disputed."""
        rule = OnThenRule("disputed", "=", True, "committee_quorum")
        context = {"has_contradiction": True}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.COMMITTEE_QUORUM

    def test_evaluate_known_condition_no_evidence(self, executor):
        """Evaluate known condition no_evidence."""
        rule = OnThenRule("no_evidence", "=", True, "auto_reject")
        context = {"evidence_count": 0}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.AUTO_REJECT

    def test_evaluate_known_condition_high_risk(self, executor):
        """Evaluate known condition high_risk."""
        rule = OnThenRule("high_risk", "=", True, "escalate")
        context = {"risk_level": "high"}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.ESCALATE

    def test_evaluate_field_comparison(self, executor):
        """Evaluate field comparison rule."""
        rule = OnThenRule("evidence_count", "<", 3, "flag_for_review")
        context = {"evidence_count": 2}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action == PolicyAction.FLAG_FOR_REVIEW

    def test_evaluate_rule_not_triggered(self, executor):
        """Evaluate rule that is not triggered."""
        rule = OnThenRule("high_confidence", "=", True, "auto_approve")
        context = {"confidence": "low"}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is False
        assert result.action is None
        assert result.action_params == {}

    def test_evaluate_rule_with_params(self, executor):
        """Evaluate rule preserves action params when triggered."""
        rule = OnThenRule(
            "high_risk", "=", True, "escalate",
            action_params={"priority": "critical", "notify": ["admin"]}
        )
        context = {"risk_level": "high"}

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is True
        assert result.action_params["priority"] == "critical"

    def test_evaluate_missing_field(self, executor):
        """Evaluate rule with missing field."""
        rule = OnThenRule("missing", "=", True, "defer")
        context = {}

        result = executor._evaluate_rule(rule, context)
        assert result.triggered is False


class TestExecutePolicy:
    """Tests for execute_policy convenience function."""

    def test_execute_policy_function(self):
        """Convenience function creates executor and runs."""
        policy = PolicyAST(
            name="test",
            domain="test",
            gate="G1",
            requirements=[RequireCondition("sources", ">=", 1)],
        )
        context = {"sources": 2}

        result = execute_policy(policy, context)

        assert isinstance(result, PolicyExecutionResult)
        assert result.final_action == PolicyAction.AUTO_APPROVE


class TestRequirementTypeError:
    """Tests for requirement evaluation with TypeError."""

    def test_evaluate_requirement_type_error(self):
        """Requirement evaluation handles TypeError gracefully."""
        executor = PolicyExecutor()
        req = RequireCondition("count", ">=", 5)
        # Pass incompatible types that cause TypeError
        context = {"count": {"nested": "dict"}}  # dict vs int comparison

        result = executor._evaluate_requirement(req, context)

        assert result.passed is False
        assert "Cannot compare" in result.message


class TestRuleTypeError:
    """Tests for rule evaluation with TypeError."""

    def test_evaluate_rule_type_error(self):
        """Rule evaluation handles TypeError gracefully."""
        executor = PolicyExecutor()
        rule = OnThenRule(
            condition_field="status",
            condition_operator="=",
            condition_value=123,  # int value
            action="auto_approve",
        )
        # Pass incompatible type
        context = {"status": {"nested": "dict"}}  # dict vs int comparison

        result = executor._evaluate_rule(rule, context)

        assert result.triggered is False


class TestTriggeredRuleHumanReview:
    """Tests for triggered rule with HUMAN_REVIEW action."""

    def test_requirements_not_met_with_human_review_rule(self):
        """When requirements fail but rule triggers human_review, use that action."""
        policy = PolicyAST(
            name="test_review",
            domain="test",
            gate="G1",
            requirements=[RequireCondition("sources", ">=", 5)],  # Will fail
            rules=[
                OnThenRule(
                    condition_field="risk_level",
                    condition_operator=">",
                    condition_value=0,
                    action="human_review",
                    action_params={"reviewer": "admin"},
                )
            ],
        )
        context = {"sources": 1, "risk_level": 5}  # sources fail, rule triggers

        executor = PolicyExecutor()
        result = executor.execute(policy, context)

        assert result.final_action == PolicyAction.HUMAN_REVIEW
        # Should have the action_params from the triggered rule
        assert result.final_action_params.get("reviewer") == "admin"
