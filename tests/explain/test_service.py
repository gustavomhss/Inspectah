"""
S39: Tests for Explainability Service
"""
import pytest
from datetime import datetime, timezone

from app.explain.service import (
    ExplainabilityService,
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    Counterfactual,
    ExplanationType,
    FactorDirection,
    ImpactLevel,
    ComparisonDifference,
    DecisionComparison,
    get_service,
)


class TestReasoningStep:
    """Tests for ReasoningStep."""

    def test_create_step(self):
        step = ReasoningStep(
            step_number=1,
            description="Test step",
            inputs=["input1", "input2"],
            output="result",
        )

        assert step.step_number == 1
        assert step.description == "Test step"
        assert len(step.inputs) == 2
        assert step.output == "result"

    def test_step_with_confidence(self):
        step = ReasoningStep(
            step_number=1,
            description="Test",
            inputs=[],
            output="done",
            confidence=0.85,
        )

        assert step.confidence == 0.85

    def test_step_with_evidence(self):
        step = ReasoningStep(
            step_number=1,
            description="Test",
            inputs=[],
            output="done",
            evidence_refs=["ev_001", "ev_002"],
        )

        assert len(step.evidence_refs) == 2

    def test_step_to_dict(self):
        step = ReasoningStep(
            step_number=1,
            description="Test step",
            inputs=["input1"],
            output="result",
            confidence=0.9,
        )

        result = step.to_dict()
        assert result["step_number"] == 1
        assert result["confidence"] == 0.9


class TestExplanationFactor:
    """Tests for ExplanationFactor."""

    def test_create_factor(self):
        factor = ExplanationFactor(
            name="evidence_count",
            value="5",
            weight=0.4,
            direction=FactorDirection.POSITIVE,
        )

        assert factor.name == "evidence_count"
        assert factor.weight == 0.4
        assert factor.direction == FactorDirection.POSITIVE

    def test_factor_with_description(self):
        factor = ExplanationFactor(
            name="source_reliability",
            value="high",
            weight=0.3,
            direction=FactorDirection.NEUTRAL,
            description="Reliability of the source",
            source="source_001",
        )

        assert factor.description is not None
        assert factor.source == "source_001"

    def test_factor_to_dict(self):
        factor = ExplanationFactor(
            name="test",
            value="100",
            weight=0.5,
            direction=FactorDirection.NEGATIVE,
        )

        result = factor.to_dict()
        assert result["name"] == "test"
        assert result["direction"] == "negative"


class TestCounterfactual:
    """Tests for Counterfactual."""

    def test_create_counterfactual(self):
        cf = Counterfactual(
            condition="If evidence count were higher",
            outcome="Confidence would increase",
        )

        assert cf.condition is not None
        assert cf.outcome is not None

    def test_counterfactual_with_likelihood(self):
        cf = Counterfactual(
            condition="If source were more reliable",
            outcome="Verdict would be more confident",
            likelihood=0.7,
        )

        assert cf.likelihood == 0.7

    def test_counterfactual_to_dict(self):
        cf = Counterfactual(
            condition="Test condition",
            outcome="Test outcome",
            likelihood=0.5,
            variables={"key": "value"},
        )

        result = cf.to_dict()
        assert result["condition"] == "Test condition"
        assert result["variables"] == {"key": "value"}


class TestExplanation:
    """Tests for Explanation."""

    def test_create_explanation(self):
        explanation = Explanation(
            id="exp_test123",
            type=ExplanationType.VERDICT,
            target_id="verdict_001",
            summary="Test explanation",
            reasoning_path=[],
        )

        assert explanation.id == "exp_test123"
        assert explanation.type == ExplanationType.VERDICT
        assert explanation.summary == "Test explanation"

    def test_explanation_with_steps(self):
        steps = [
            ReasoningStep(1, "Step 1", [], "result1", confidence=0.8),
            ReasoningStep(2, "Step 2", [], "result2", confidence=0.9),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.SIGNAL,
            target_id="signal_001",
            summary="Signal explanation",
            reasoning_path=steps,
        )

        assert explanation.total_steps == 2

    def test_explanation_avg_confidence(self):
        steps = [
            ReasoningStep(1, "Step 1", [], "result1", confidence=0.8),
            ReasoningStep(2, "Step 2", [], "result2", confidence=1.0),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=steps,
        )

        assert explanation.avg_step_confidence == 0.9

    def test_explanation_avg_confidence_none(self):
        steps = [
            ReasoningStep(1, "Step 1", [], "result1"),
            ReasoningStep(2, "Step 2", [], "result2"),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=steps,
        )

        assert explanation.avg_step_confidence is None

    def test_get_step(self):
        steps = [
            ReasoningStep(1, "Step 1", [], "result1"),
            ReasoningStep(2, "Step 2", [], "result2"),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=steps,
        )

        step = explanation.get_step(2)
        assert step is not None
        assert step.description == "Step 2"

    def test_get_step_not_found(self):
        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=[],
        )

        step = explanation.get_step(99)
        assert step is None

    def test_get_positive_factors(self):
        factors = [
            ExplanationFactor("f1", "v1", 0.3, FactorDirection.POSITIVE),
            ExplanationFactor("f2", "v2", 0.3, FactorDirection.NEGATIVE),
            ExplanationFactor("f3", "v3", 0.4, FactorDirection.POSITIVE),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=[],
            factors=factors,
        )

        positive = explanation.get_positive_factors()
        assert len(positive) == 2

    def test_get_negative_factors(self):
        factors = [
            ExplanationFactor("f1", "v1", 0.3, FactorDirection.POSITIVE),
            ExplanationFactor("f2", "v2", 0.3, FactorDirection.NEGATIVE),
        ]

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test",
            reasoning_path=[],
            factors=factors,
        )

        negative = explanation.get_negative_factors()
        assert len(negative) == 1

    def test_explanation_to_dict(self):
        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_001",
            summary="Test summary",
            reasoning_path=[ReasoningStep(1, "Step 1", [], "result")],
            factors=[ExplanationFactor("f1", "v1", 0.5, FactorDirection.NEUTRAL)],
        )

        result = explanation.to_dict()
        assert result["id"] == "exp_test"
        assert result["type"] == "verdict"
        assert len(result["reasoning_path"]) == 1
        assert len(result["factors"]) == 1


class TestComparisonDifference:
    """Tests for ComparisonDifference."""

    def test_create_difference(self):
        diff = ComparisonDifference(
            aspect="confidence",
            value_a="0.8",
            value_b="0.9",
            impact=ImpactLevel.MEDIUM,
        )

        assert diff.aspect == "confidence"
        assert diff.impact == ImpactLevel.MEDIUM

    def test_difference_to_dict(self):
        diff = ComparisonDifference(
            aspect="type",
            value_a="verdict",
            value_b="signal",
            impact=ImpactLevel.HIGH,
            explanation="Different types",
        )

        result = diff.to_dict()
        assert result["impact"] == "high"
        assert result["explanation"] == "Different types"


class TestExplainabilityService:
    """Tests for ExplainabilityService."""

    def test_create_service(self):
        service = ExplainabilityService()
        assert service is not None

    def test_generate_verdict_explanation(self):
        service = ExplainabilityService()
        context = {
            "verdict": "false",
            "confidence": 0.85,
            "evidence": ["ev_001", "ev_002"],
            "sources": ["src_001", "src_002"],
        }

        explanation = service.generate_explanation(
            ExplanationType.VERDICT,
            "verdict_123",
            context,
        )

        assert explanation.type == ExplanationType.VERDICT
        assert explanation.target_id == "verdict_123"
        assert "false" in explanation.summary.lower()
        assert len(explanation.reasoning_path) >= 1

    def test_generate_signal_explanation(self):
        service = ExplainabilityService()
        context = {
            "signal_type": "mentiras",
            "value": 0.75,
            "scope": "global",
            "components": {"comp1": 0.8, "comp2": 0.7},
        }

        explanation = service.generate_explanation(
            ExplanationType.SIGNAL,
            "signal_123",
            context,
        )

        assert explanation.type == ExplanationType.SIGNAL
        assert "mentiras" in explanation.summary.lower()

    def test_generate_relation_explanation(self):
        service = ExplainabilityService()
        context = {
            "relation_type": "contradicts",
            "confidence": 0.9,
            "method": "semantic_similarity",
            "source_claim": "claim_001",
            "target_claim": "claim_002",
        }

        explanation = service.generate_explanation(
            ExplanationType.RELATION,
            "rel_123",
            context,
        )

        assert explanation.type == ExplanationType.RELATION
        assert "contradicts" in explanation.summary.lower()

    def test_generate_policy_explanation(self):
        service = ExplainabilityService()
        context = {
            "policy_name": "health_policy",
            "action": "approve",
            "rules_matched": ["rule1", "rule2"],
            "domain": "health",
        }

        explanation = service.generate_explanation(
            ExplanationType.POLICY,
            "policy_123",
            context,
        )

        assert explanation.type == ExplanationType.POLICY
        assert "health_policy" in explanation.summary.lower()

    def test_generate_flow_explanation(self):
        service = ExplainabilityService()
        context = {
            "flow_name": "claim_analysis",
            "status": "completed",
            "steps_executed": [
                {"name": "extract", "output": "done"},
                {"name": "analyze", "output": "done"},
            ],
            "duration_ms": 1500,
        }

        explanation = service.generate_explanation(
            ExplanationType.FLOW,
            "flow_123",
            context,
        )

        assert explanation.type == ExplanationType.FLOW
        assert "completed" in explanation.summary.lower()

    def test_generate_with_counterfactuals(self):
        service = ExplainabilityService()
        context = {
            "verdict": "true",
            "confidence": 0.9,
            "evidence": ["ev_001"],
            "sources": ["src_001"],
        }

        explanation = service.generate_explanation(
            ExplanationType.VERDICT,
            "verdict_123",
            context,
            include_counterfactuals=True,
        )

        assert len(explanation.counterfactuals) > 0

    def test_get_explanation(self):
        service = ExplainabilityService()
        context = {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []}

        explanation = service.generate_explanation(
            ExplanationType.VERDICT,
            "v_123",
            context,
        )

        retrieved = service.get_explanation(explanation.id)
        assert retrieved is not None
        assert retrieved.id == explanation.id

    def test_get_explanation_not_found(self):
        service = ExplainabilityService()
        retrieved = service.get_explanation("nonexistent_id")
        assert retrieved is None

    def test_list_explanations(self):
        service = ExplainabilityService()

        # Generate multiple explanations
        for i in range(5):
            service.generate_explanation(
                ExplanationType.VERDICT,
                f"v_{i}",
                {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []},
            )

        explanations = service.list_explanations()
        assert len(explanations) == 5

    def test_list_explanations_filtered(self):
        service = ExplainabilityService()

        service.generate_explanation(
            ExplanationType.VERDICT,
            "v_1",
            {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []},
        )
        service.generate_explanation(
            ExplanationType.SIGNAL,
            "s_1",
            {"signal_type": "mentiras", "value": 0.5, "scope": "global", "components": {}},
        )

        verdicts = service.list_explanations(exp_type=ExplanationType.VERDICT)
        assert len(verdicts) == 1

    def test_list_explanations_by_target(self):
        service = ExplainabilityService()

        service.generate_explanation(
            ExplanationType.VERDICT,
            "target_123",
            {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []},
        )
        service.generate_explanation(
            ExplanationType.VERDICT,
            "target_456",
            {"verdict": "false", "confidence": 0.8, "evidence": [], "sources": []},
        )

        results = service.list_explanations(target_id="target_123")
        assert len(results) == 1
        assert results[0].target_id == "target_123"

    def test_delete_explanation(self):
        service = ExplainabilityService()
        context = {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []}

        explanation = service.generate_explanation(
            ExplanationType.VERDICT,
            "v_123",
            context,
        )

        result = service.delete_explanation(explanation.id)
        assert result is True

        retrieved = service.get_explanation(explanation.id)
        assert retrieved is None

    def test_delete_nonexistent_explanation(self):
        service = ExplainabilityService()
        result = service.delete_explanation("nonexistent")
        assert result is False

    def test_register_custom_generator(self):
        service = ExplainabilityService()

        def custom_generator(target_id, context, include_cf):
            return Explanation(
                id="custom_exp",
                type=ExplanationType.VERDICT,
                target_id=target_id,
                summary="Custom explanation",
                reasoning_path=[],
            )

        service.register_generator(ExplanationType.VERDICT, custom_generator)
        explanation = service.generate_explanation(
            ExplanationType.VERDICT,
            "test",
            {},
        )

        assert explanation.id == "custom_exp"

    def test_generate_unknown_type_raises(self):
        service = ExplainabilityService()
        service._generators.clear()  # Remove all generators

        with pytest.raises(ValueError):
            service.generate_explanation(
                ExplanationType.VERDICT,
                "test",
                {},
            )


class TestDecisionComparison:
    """Tests for decision comparison."""

    def test_compare_same_type(self):
        service = ExplainabilityService()

        exp_a = service.generate_explanation(
            ExplanationType.VERDICT,
            "v_1",
            {"verdict": "true", "confidence": 0.9, "evidence": ["e1"], "sources": ["s1"]},
        )
        exp_b = service.generate_explanation(
            ExplanationType.VERDICT,
            "v_2",
            {"verdict": "false", "confidence": 0.8, "evidence": ["e2"], "sources": ["s2"]},
        )

        comparison = service.compare_decisions(exp_a, exp_b)

        assert comparison.similarity_score >= 0.0
        assert comparison.similarity_score <= 1.0

    def test_compare_different_types(self):
        service = ExplainabilityService()

        exp_a = service.generate_explanation(
            ExplanationType.VERDICT,
            "v_1",
            {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []},
        )
        exp_b = service.generate_explanation(
            ExplanationType.SIGNAL,
            "s_1",
            {"signal_type": "mentiras", "value": 0.5, "scope": "global", "components": {}},
        )

        comparison = service.compare_decisions(exp_a, exp_b)

        # Should have a type difference
        type_diffs = [d for d in comparison.differences if d.aspect == "type"]
        assert len(type_diffs) == 1
        assert type_diffs[0].impact == ImpactLevel.HIGH

    def test_compare_different_factor_directions(self):
        exp_a = Explanation(
            id="exp_a",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Explanation A",
            reasoning_path=[],
            factors=[
                ExplanationFactor("confidence", "0.9", 0.5, FactorDirection.POSITIVE),
            ],
        )

        exp_b = Explanation(
            id="exp_b",
            type=ExplanationType.VERDICT,
            target_id="v_2",
            summary="Explanation B",
            reasoning_path=[],
            factors=[
                ExplanationFactor("confidence", "0.3", 0.5, FactorDirection.NEGATIVE),
            ],
        )

        service = ExplainabilityService()
        comparison = service.compare_decisions(exp_a, exp_b)

        direction_diffs = [d for d in comparison.differences if "direction" in d.aspect]
        assert len(direction_diffs) == 1

    def test_comparison_to_dict(self):
        exp_a = Explanation(
            id="exp_a",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="A",
            reasoning_path=[],
        )
        exp_b = Explanation(
            id="exp_b",
            type=ExplanationType.VERDICT,
            target_id="v_2",
            summary="B",
            reasoning_path=[],
        )

        comparison = DecisionComparison(
            decision_a=exp_a,
            decision_b=exp_b,
            differences=[],
            similarity_score=0.95,
        )

        result = comparison.to_dict()
        assert result["similarity_score"] == 0.95


class TestCounterfactualGeneration:
    """Tests for counterfactual generation."""

    def test_generate_counterfactuals(self):
        service = ExplainabilityService()

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Test",
            reasoning_path=[],
            factors=[
                ExplanationFactor("evidence", "3", 0.5, FactorDirection.POSITIVE),
                ExplanationFactor("source_count", "2", 0.3, FactorDirection.NEUTRAL),
            ],
        )

        counterfactuals = service.generate_counterfactuals(explanation, num_counterfactuals=2)

        assert len(counterfactuals) == 2
        assert all(cf.condition is not None for cf in counterfactuals)
        assert all(cf.outcome is not None for cf in counterfactuals)

    def test_generate_counterfactuals_for_negative_factor(self):
        service = ExplainabilityService()

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Test",
            reasoning_path=[],
            factors=[
                ExplanationFactor("low_confidence", "0.3", 0.5, FactorDirection.NEGATIVE),
            ],
        )

        counterfactuals = service.generate_counterfactuals(explanation, num_counterfactuals=1)

        assert len(counterfactuals) == 1
        assert "positive" in counterfactuals[0].condition.lower()


class TestGlobalService:
    """Tests for global service instance."""

    def test_get_service_singleton(self):
        service1 = get_service()
        service2 = get_service()
        assert service1 is service2

    def test_get_service_type(self):
        service = get_service()
        assert isinstance(service, ExplainabilityService)


class TestAdditionalCoverage:
    """Additional tests for better coverage."""

    def test_generate_signal_no_components(self):
        service = ExplainabilityService()
        context = {
            "signal_type": "velocity",
            "value": 0.5,
            "scope": "source",
            "scope_id": "src_001",
            "components": {},  # Empty components
        }

        explanation = service.generate_explanation(
            ExplanationType.SIGNAL,
            "signal_empty",
            context,
        )

        assert explanation.type == ExplanationType.SIGNAL
        assert len(explanation.factors) == 0

    def test_generate_flow_empty_steps(self):
        service = ExplainabilityService()
        context = {
            "flow_name": "empty_flow",
            "status": "failed",
            "steps_executed": [],  # No steps
            "duration_ms": 100,
        }

        explanation = service.generate_explanation(
            ExplanationType.FLOW,
            "flow_empty",
            context,
        )

        assert explanation.type == ExplanationType.FLOW
        assert len(explanation.reasoning_path) >= 1  # Should have at least summary

    def test_comparison_identical_explanations(self):
        service = ExplainabilityService()

        exp_a = Explanation(
            id="exp_a",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Same",
            reasoning_path=[
                ReasoningStep(1, "Step 1", [], "result"),
            ],
            factors=[
                ExplanationFactor("f1", "v1", 0.5, FactorDirection.POSITIVE),
            ],
        )

        exp_b = Explanation(
            id="exp_b",
            type=ExplanationType.VERDICT,
            target_id="v_2",
            summary="Same",
            reasoning_path=[
                ReasoningStep(1, "Step 1", [], "result"),
            ],
            factors=[
                ExplanationFactor("f1", "v1", 0.5, FactorDirection.POSITIVE),
            ],
        )

        comparison = service.compare_decisions(exp_a, exp_b)
        # Should be highly similar
        assert comparison.similarity_score >= 0.9

    def test_generate_neutral_factor_counterfactual(self):
        service = ExplainabilityService()

        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Test",
            reasoning_path=[],
            factors=[
                ExplanationFactor("neutral_factor", "medium", 0.5, FactorDirection.NEUTRAL),
            ],
        )

        counterfactuals = service.generate_counterfactuals(explanation, num_counterfactuals=1)
        assert len(counterfactuals) == 1
        assert "stronger" in counterfactuals[0].condition.lower()

    def test_list_explanations_with_limit(self):
        service = ExplainabilityService()

        # Generate 5 explanations
        for i in range(5):
            service.generate_explanation(
                ExplanationType.VERDICT,
                f"v_{i}",
                {"verdict": "true", "confidence": 0.9, "evidence": [], "sources": []},
            )

        # Limit to 3
        explanations = service.list_explanations(limit=3)
        assert len(explanations) == 3


class TestServiceCoverageTargeted:
    """Targeted tests for service coverage."""

    def test_compare_only_in_b_factors_line_340(self):
        """Line 340: Factors only in second decision (only_in_b)."""
        service = ExplainabilityService()

        # Create two explanations with different factors
        exp_a = Explanation(
            id="exp_a",
            type=ExplanationType.VERDICT,
            target_id="v_a",
            summary="Explanation A",
            reasoning_path=[],
            factors=[
                ExplanationFactor("common", "val", 0.5, FactorDirection.POSITIVE),
            ],
        )

        exp_b = Explanation(
            id="exp_b",
            type=ExplanationType.VERDICT,
            target_id="v_b",
            summary="Explanation B",
            reasoning_path=[],
            factors=[
                ExplanationFactor("common", "val", 0.5, FactorDirection.POSITIVE),
                ExplanationFactor("only_in_b", "val", 0.3, FactorDirection.NEUTRAL),
            ],
        )

        comparison = service.compare_decisions(exp_a, exp_b)
        # Should detect that only_in_b is missing from A
        assert any("only in second" in d.explanation.lower() for d in comparison.differences)

    def test_compare_weight_difference_line_365(self):
        """Line 365: Weight difference > 0.1 for common factors."""
        service = ExplainabilityService()

        exp_a = Explanation(
            id="exp_a",
            type=ExplanationType.VERDICT,
            target_id="v_a",
            summary="A",
            reasoning_path=[],
            factors=[
                ExplanationFactor("weight_test", "val", 0.5, FactorDirection.POSITIVE),
            ],
        )

        exp_b = Explanation(
            id="exp_b",
            type=ExplanationType.VERDICT,
            target_id="v_b",
            summary="B",
            reasoning_path=[],
            factors=[
                ExplanationFactor("weight_test", "val", 0.8, FactorDirection.POSITIVE),
            ],
        )

        comparison = service.compare_decisions(exp_a, exp_b)
        # Difference is 0.3, should be detected
        assert any("weight" in d.aspect for d in comparison.differences)

    def test_signal_with_counterfactuals_line_578(self):
        """Line 578: Signal explanation with counterfactuals."""
        service = ExplainabilityService()

        explanation = service.generate_explanation(
            ExplanationType.SIGNAL,
            "signal_cf_test",
            {
                "signal_type": "conflict",
                "value": 0.8,
                "scope": "national",
                "components": {"src1": 0.5, "src2": 0.3},  # Dict, not list
            },
            include_counterfactuals=True,
        )

        assert explanation.counterfactuals is not None
        assert len(explanation.counterfactuals) > 0

    def test_relation_with_counterfactuals_line_642(self):
        """Line 642: Relation explanation with counterfactuals."""
        service = ExplainabilityService()

        explanation = service.generate_explanation(
            ExplanationType.RELATION,
            "rel_cf_test",
            {
                "relation_type": "supports",
                "source_claim": "claim_001",
                "target_claim": "claim_002",
                "confidence": 0.85,
                "method": "semantic_similarity",
            },
            include_counterfactuals=True,
        )

        assert explanation.counterfactuals is not None
        assert len(explanation.counterfactuals) > 0

    def test_policy_with_counterfactuals_line_698(self):
        """Line 698: Policy explanation with counterfactuals."""
        service = ExplainabilityService()

        explanation = service.generate_explanation(
            ExplanationType.POLICY,
            "policy_cf_test",
            {
                "policy_name": "content_moderation",
                "action": "flag",
                "rules_matched": ["rule1", "rule2"],
                "domain": "political",
            },
            include_counterfactuals=True,
        )

        assert explanation.counterfactuals is not None
        assert len(explanation.counterfactuals) > 0

    def test_flow_with_counterfactuals_line_769(self):
        """Line 769: Flow explanation with counterfactuals."""
        service = ExplainabilityService()

        explanation = service.generate_explanation(
            ExplanationType.FLOW,
            "flow_cf_test",
            {
                "flow_name": "claim_pipeline",
                "status": "completed",
                "steps_executed": [
                    {"name": "extract", "inputs": [], "output": "done"},
                    {"name": "validate", "inputs": [], "output": "done"},
                ],
                "duration_ms": 1500,
            },
            include_counterfactuals=True,
        )

        assert explanation.counterfactuals is not None
        assert len(explanation.counterfactuals) > 0
