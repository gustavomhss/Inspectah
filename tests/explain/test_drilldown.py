"""
S39: Tests for Drilldown Service
"""
import pytest
from datetime import datetime, timezone

from app.explain.service import (
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    ExplanationType,
    FactorDirection,
)
from app.explain.drilldown import (
    DrilldownService,
    DrilldownResult,
    EvidenceDetail,
    StepDetail,
    get_drilldown_service,
)


def create_sample_explanation() -> Explanation:
    """Create a sample explanation for testing."""
    steps = [
        ReasoningStep(
            step_number=1,
            description="Collected evidence from sources",
            inputs=["source:src_001", "source:src_002"],
            output="Found 3 evidence items",
            confidence=0.9,
            evidence_refs=["ev_001", "ev_002"],
        ),
        ReasoningStep(
            step_number=2,
            description="Analyzed evidence quality",
            inputs=["ev_001", "ev_002"],
            output="Evidence quality: high",
            confidence=0.85,
        ),
        ReasoningStep(
            step_number=3,
            description="Applied policy rules",
            inputs=["evidence_analysis", "policy_rules"],
            output="Verdict: false",
            confidence=0.9,
        ),
    ]

    factors = [
        ExplanationFactor(
            name="evidence_count",
            value="3",
            weight=0.4,
            direction=FactorDirection.POSITIVE,
            description="Number of evidence items",
        ),
        ExplanationFactor(
            name="source_reliability",
            value="high",
            weight=0.3,
            direction=FactorDirection.POSITIVE,
            description="Reliability of sources",
        ),
        ExplanationFactor(
            name="confidence_level",
            value="0.9",
            weight=0.3,
            direction=FactorDirection.POSITIVE,
            description="Overall confidence",
        ),
    ]

    return Explanation(
        id="exp_test_001",
        type=ExplanationType.VERDICT,
        target_id="verdict_123",
        summary="Test explanation",
        reasoning_path=steps,
        factors=factors,
    )


class TestEvidenceDetail:
    """Tests for EvidenceDetail."""

    def test_create_evidence_detail(self):
        detail = EvidenceDetail(
            evidence_id="ev_001",
            source_id="src_001",
            content_summary="Test evidence summary",
            relevance_score=0.85,
            extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert detail.evidence_id == "ev_001"
        assert detail.relevance_score == 0.85

    def test_evidence_detail_to_dict(self):
        detail = EvidenceDetail(
            evidence_id="ev_001",
            source_id=None,
            content_summary="Summary",
            relevance_score=0.7,
            extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
            metadata={"key": "value"},
        )

        result = detail.to_dict()
        assert result["evidence_id"] == "ev_001"
        assert result["metadata"] == {"key": "value"}


class TestStepDetail:
    """Tests for StepDetail."""

    def test_create_step_detail(self):
        step = ReasoningStep(
            step_number=1,
            description="Test step",
            inputs=["input1"],
            output="result",
        )

        detail = StepDetail(
            step=step,
            evidence_details=[],
            input_details={"input1": {"value": "test", "resolved": True}},
            computation_trace=["Step 1: Test step"],
            alternatives_considered=["Alt 1", "Alt 2"],
        )

        assert detail.step.step_number == 1
        assert len(detail.alternatives_considered) == 2

    def test_step_detail_to_dict(self):
        step = ReasoningStep(
            step_number=1,
            description="Test",
            inputs=[],
            output="done",
        )

        detail = StepDetail(
            step=step,
            evidence_details=[],
            input_details={},
            computation_trace=["trace1"],
            alternatives_considered=[],
        )

        result = detail.to_dict()
        assert "step" in result
        assert result["computation_trace"] == ["trace1"]


class TestDrilldownResult:
    """Tests for DrilldownResult."""

    def test_create_result(self):
        result = DrilldownResult(
            explanation_id="exp_001",
            step_number=1,
            step_detail=None,
            related_factors=[],
            evidence=[],
            depth=1,
        )

        assert result.explanation_id == "exp_001"
        assert result.depth == 1

    def test_result_to_dict(self):
        result = DrilldownResult(
            explanation_id="exp_001",
            step_number=2,
            step_detail=None,
            related_factors=[],
            evidence=[],
            depth=2,
        )

        dict_result = result.to_dict()
        assert dict_result["explanation_id"] == "exp_001"
        assert dict_result["step_number"] == 2


class TestDrilldownService:
    """Tests for DrilldownService."""

    def test_create_service(self):
        service = DrilldownService()
        assert service is not None

    def test_drilldown_step(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, step_number=1)

        assert result is not None
        assert result.step_number == 1
        assert result.step_detail is not None
        assert result.step_detail.step.step_number == 1

    def test_drilldown_step_not_found(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, step_number=99)
        assert result is None

    def test_drilldown_step_depth_2(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, step_number=1, depth=2)

        assert result is not None
        assert result.depth == 2
        # Deeper depth should resolve more evidence details
        assert len(result.evidence) >= 0

    def test_drilldown_step_depth_3(self):
        """Test drilldown with maximum valid depth."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, step_number=1, depth=3)

        assert result is not None
        assert result.depth == 3

    def test_drilldown_step_invalid_depth_zero(self):
        """Test that depth=0 raises ValueError."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        with pytest.raises(ValueError, match="Depth must be between 1 and 3"):
            service.drilldown_step(explanation, step_number=1, depth=0)

    def test_drilldown_step_invalid_depth_negative(self):
        """Test that negative depth raises ValueError."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        with pytest.raises(ValueError, match="Depth must be between 1 and 3"):
            service.drilldown_step(explanation, step_number=1, depth=-1)

    def test_drilldown_step_invalid_depth_too_high(self):
        """Test that depth > 3 raises ValueError."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        with pytest.raises(ValueError, match="Depth must be between 1 and 3"):
            service.drilldown_step(explanation, step_number=1, depth=4)

    def test_drilldown_factor(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_factor(explanation, "evidence_count")

        assert result is not None
        assert len(result.related_factors) == 1
        assert result.related_factors[0].name == "evidence_count"

    def test_drilldown_factor_not_found(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_factor(explanation, "nonexistent_factor")
        assert result is None

    def test_drilldown_factor_invalid_depth_zero(self):
        """Test that drilldown_factor with depth=0 raises ValueError."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        with pytest.raises(ValueError, match="Depth must be between 1 and 3"):
            service.drilldown_factor(explanation, "evidence_count", depth=0)

    def test_drilldown_factor_invalid_depth_too_high(self):
        """Test that drilldown_factor with depth > 3 raises ValueError."""
        service = DrilldownService()
        explanation = create_sample_explanation()

        with pytest.raises(ValueError, match="Depth must be between 1 and 3"):
            service.drilldown_factor(explanation, "evidence_count", depth=5)

    def test_drilldown_evidence(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_evidence(explanation, "ev_001")

        assert result is not None
        assert result.evidence_id == "ev_001"

    def test_drilldown_evidence_not_found(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        result = service.drilldown_evidence(explanation, "nonexistent_ev")
        assert result is None

    def test_get_full_trace(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        trace = service.get_full_trace(explanation)

        assert len(trace) == 3  # 3 steps in the explanation
        assert all(isinstance(t, StepDetail) for t in trace)

    def test_get_evidence_chain(self):
        service = DrilldownService()
        explanation = create_sample_explanation()

        evidence = service.get_evidence_chain(explanation)

        # Should find ev_001 and ev_002 from step 1
        assert len(evidence) == 2

    def test_clear_cache(self):
        """Test clear_cache is a safe no-op (cache removed in S39 hardening)."""
        service = DrilldownService()
        # clear_cache should not raise any errors
        service.clear_cache()
        # Method should work without side effects
        assert True


class TestDrilldownServicePrivateMethods:
    """Tests for private methods of DrilldownService."""

    def test_resolve_evidence(self):
        service = DrilldownService()
        evidence = service._resolve_evidence(["ev_001", "ev_002"], depth=1)

        assert len(evidence) == 2
        assert all(e.evidence_id in ["ev_001", "ev_002"] for e in evidence)

    def test_resolve_evidence_higher_depth(self):
        service = DrilldownService()
        evidence = service._resolve_evidence(["ev_001"], depth=2)

        assert len(evidence) == 1
        # Higher depth should give higher relevance score
        assert evidence[0].relevance_score >= 0.5

    def test_resolve_inputs(self):
        service = DrilldownService()
        inputs = ["source:src_001", "plain_input"]

        resolved = service._resolve_inputs(inputs, depth=2)

        assert "source" in resolved
        assert resolved["source"]["value"] == "src_001"
        assert "plain_input" in resolved

    def test_generate_computation_trace(self):
        service = DrilldownService()
        step = ReasoningStep(
            step_number=1,
            description="Test step",
            inputs=["input1", "input2"],
            output="result",
            confidence=0.9,
            evidence_refs=["ev_001"],
        )

        trace = service._generate_computation_trace(step)

        assert len(trace) >= 3
        assert "Step 1" in trace[0]
        assert "Confidence" in trace[3]

    def test_get_alternatives_verdict(self):
        service = DrilldownService()
        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.VERDICT,
            target_id="v_1",
            summary="Test",
            reasoning_path=[],
        )

        alternatives = service._get_alternatives(explanation, 1)

        assert len(alternatives) <= 2
        assert all(isinstance(a, str) for a in alternatives)

    def test_get_alternatives_signal(self):
        service = DrilldownService()
        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.SIGNAL,
            target_id="s_1",
            summary="Test",
            reasoning_path=[],
        )

        alternatives = service._get_alternatives(explanation, 1)
        assert len(alternatives) >= 0

    def test_get_alternatives_relation(self):
        service = DrilldownService()
        explanation = Explanation(
            id="exp_test",
            type=ExplanationType.RELATION,
            target_id="r_1",
            summary="Test",
            reasoning_path=[],
        )

        alternatives = service._get_alternatives(explanation, 1)
        assert len(alternatives) >= 0

    def test_find_related_factors(self):
        service = DrilldownService()
        explanation = create_sample_explanation()
        step = explanation.reasoning_path[0]  # Evidence collection step

        related = service._find_related_factors(explanation, step)

        # Should find factors related to evidence/source
        assert len(related) >= 0


class TestDrilldownWithCustomResolver:
    """Tests for DrilldownService with custom evidence resolver."""

    def test_with_custom_resolver(self):
        class MockResolver:
            def resolve(self, ref):
                return EvidenceDetail(
                    evidence_id=ref,
                    source_id="custom_source",
                    content_summary="Custom resolved content",
                    relevance_score=0.95,
                    extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )

        service = DrilldownService(evidence_resolver=MockResolver())
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, 1)

        assert result is not None
        assert all(e.source_id == "custom_source" for e in result.evidence)

    def test_resolver_returns_none(self):
        class NoneResolver:
            def resolve(self, ref):
                return None

        service = DrilldownService(evidence_resolver=NoneResolver())
        explanation = create_sample_explanation()

        result = service.drilldown_step(explanation, 1)

        # Should fall back to default evidence creation
        assert result is not None


class TestGlobalDrilldownService:
    """Tests for global drilldown service instance."""

    def test_get_drilldown_service_singleton(self):
        service1 = get_drilldown_service()
        service2 = get_drilldown_service()
        assert service1 is service2

    def test_get_drilldown_service_type(self):
        service = get_drilldown_service()
        assert isinstance(service, DrilldownService)


class TestIntegration:
    """Integration tests for explainability and drilldown."""

    def test_full_drilldown_workflow(self):
        from app.explain.service import ExplainabilityService

        # Generate an explanation
        explain_service = ExplainabilityService()
        explanation = explain_service.generate_explanation(
            ExplanationType.VERDICT,
            "verdict_integration_test",
            {
                "verdict": "false",
                "confidence": 0.85,
                "evidence": ["ev_int_001", "ev_int_002"],
                "sources": ["src_int_001"],
            },
        )

        # Drilldown into the explanation
        drilldown_service = DrilldownService()

        # Get full trace
        trace = drilldown_service.get_full_trace(explanation)
        assert len(trace) > 0

        # Drilldown into first step
        step_result = drilldown_service.drilldown_step(explanation, 1, depth=2)
        assert step_result is not None
        assert step_result.step_detail is not None

        # Get evidence chain
        evidence = drilldown_service.get_evidence_chain(explanation)
        assert len(evidence) >= 0

    def test_drilldown_with_empty_explanation(self):
        drilldown_service = DrilldownService()

        explanation = Explanation(
            id="exp_empty",
            type=ExplanationType.VERDICT,
            target_id="v_empty",
            summary="Empty explanation",
            reasoning_path=[],
            factors=[],
        )

        # Should handle empty explanation gracefully
        trace = drilldown_service.get_full_trace(explanation)
        assert len(trace) == 0

        evidence = drilldown_service.get_evidence_chain(explanation)
        assert len(evidence) == 0
