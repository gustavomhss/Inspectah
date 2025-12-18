"""
S39: Tests for Explainability API Routes
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.api.explain_routes import router
from app.explain.service import (
    ExplainabilityService,
    ExplanationType,
    Explanation,
    ReasoningStep,
    ExplanationFactor,
    FactorDirection,
    DecisionComparison,
    ComparisonDifference,
    ImpactLevel,
    Counterfactual,
)
from app.explain.drilldown import (
    DrilldownService,
    DrilldownResult,
    EvidenceDetail,
    StepDetail,
)


@pytest.fixture
def client():
    """Create test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_explanation():
    """Create sample explanation for testing."""
    return Explanation(
        id="exp_test_001",
        type=ExplanationType.VERDICT,
        target_id="claim_123",
        summary="Test explanation",
        reasoning_path=[
            ReasoningStep(
                step_number=1,
                description="Collected evidence",
                inputs=["source:src_001"],
                output="Found 3 items",
                confidence=0.9,
                evidence_refs=["ev_001"],
            ),
        ],
        factors=[
            ExplanationFactor(
                name="evidence_count",
                value="3",
                weight=0.5,
                direction=FactorDirection.POSITIVE,
                description="Number of evidence items",
            ),
        ],
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )


@pytest.fixture
def sample_drilldown_result():
    """Create sample drilldown result."""
    step = ReasoningStep(
        step_number=1,
        description="Test step",
        inputs=["input1"],
        output="output",
        confidence=0.9,
    )
    return DrilldownResult(
        explanation_id="exp_test_001",
        step_number=1,
        step_detail=StepDetail(
            step=step,
            evidence_details=[],
            input_details={},
            computation_trace=["trace1"],
            alternatives_considered=["alt1"],
        ),
        related_factors=[],
        evidence=[],
        depth=1,
    )


class TestGenerateExplanation:
    """Tests for generate explanation endpoint."""

    def test_generate_verdict_explanation(self, client, sample_explanation):
        """Test generating verdict explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.generate_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/explain/generate",
                json={
                    "type": "verdict",
                    "target_id": "claim_123",
                    "context": {"verdict": "false", "confidence": 0.9},
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "exp_test_001"
            assert data["type"] == "verdict"

    def test_generate_signal_explanation(self, client, sample_explanation):
        """Test generating signal explanation."""
        sample_explanation.type = ExplanationType.SIGNAL
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.generate_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/explain/generate",
                json={
                    "type": "signal",
                    "target_id": "sig_001",
                    "context": {"signal_type": "lies_in_circulation"},
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "signal"

    def test_generate_with_counterfactuals(self, client, sample_explanation):
        """Test generating explanation with counterfactuals."""
        sample_explanation.counterfactuals = [
            Counterfactual(
                condition="If evidence were stronger",
                outcome="Verdict would be true",
                likelihood=0.8,
                variables={"evidence_count": 5},
            ),
        ]
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.generate_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/explain/generate",
                json={
                    "type": "verdict",
                    "target_id": "claim_123",
                    "context": {},
                    "include_counterfactuals": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["counterfactuals"] is not None
            assert len(data["counterfactuals"]) == 1

    def test_generate_invalid_type(self, client):
        """Test invalid explanation type."""
        response = client.post(
            "/api/v1/explain/generate",
            json={
                "type": "invalid_type",
                "target_id": "x",
                "context": {},
            },
        )

        assert response.status_code == 400
        assert "Invalid explanation type" in response.json()["detail"]


class TestListExplanations:
    """Tests for list explanations endpoint."""

    def test_list_all(self, client, sample_explanation):
        """Test listing all explanations."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.list_explanations.return_value = [sample_explanation]
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_list_with_filter(self, client, sample_explanation):
        """Test listing with type filter."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.list_explanations.return_value = [sample_explanation]
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/?type=verdict")

            assert response.status_code == 200
            mock_service.list_explanations.assert_called_once()

    def test_list_with_pagination(self, client, sample_explanation):
        """Test listing with pagination."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.list_explanations.return_value = []
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/?limit=10&offset=5")

            assert response.status_code == 200
            mock_service.list_explanations.assert_called_with(
                exp_type=None,
                target_id=None,
                limit=10,
                offset=5,
            )


class TestGetExplanation:
    """Tests for get explanation endpoint."""

    def test_get_existing(self, client, sample_explanation):
        """Test getting existing explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/exp_test_001")

            assert response.status_code == 200
            assert response.json()["id"] == "exp_test_001"

    def test_get_not_found(self, client):
        """Test getting non-existent explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = None
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/nonexistent")

            assert response.status_code == 404


class TestDeleteExplanation:
    """Tests for delete explanation endpoint."""

    def test_delete_existing(self, client):
        """Test deleting existing explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.delete_explanation.return_value = True
            mock_get.return_value = mock_service

            response = client.delete("/api/v1/explain/exp_test_001")

            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_delete_not_found(self, client):
        """Test deleting non-existent explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.delete_explanation.return_value = False
            mock_get.return_value = mock_service

            response = client.delete("/api/v1/explain/nonexistent")

            assert response.status_code == 404


class TestCompareDecisions:
    """Tests for compare decisions endpoint."""

    def test_compare_two_explanations(self, client, sample_explanation):
        """Test comparing two explanations."""
        comparison = DecisionComparison(
            decision_a=sample_explanation,
            decision_b=sample_explanation,
            differences=[
                ComparisonDifference(
                    aspect="summary",
                    value_a="A",
                    value_b="B",
                    impact=ImpactLevel.LOW,
                    explanation="Different summaries",
                ),
            ],
            similarity_score=0.8,
        )

        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = sample_explanation
            mock_service.compare_decisions.return_value = comparison
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/explain/compare",
                json={
                    "explanation_a_id": "exp_001",
                    "explanation_b_id": "exp_002",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["similarity_score"] == 0.8
            assert len(data["differences"]) == 1

    def test_compare_not_found(self, client):
        """Test comparing with non-existent explanation."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = None
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/explain/compare",
                json={
                    "explanation_a_id": "nonexistent",
                    "explanation_b_id": "exp_002",
                },
            )

            assert response.status_code == 404


class TestCounterfactuals:
    """Tests for counterfactuals endpoint."""

    def test_generate_counterfactuals(self, client, sample_explanation):
        """Test generating counterfactuals."""
        counterfactuals = [
            Counterfactual(
                condition="If X",
                outcome="Then Y",
                likelihood=0.8,
                variables={"factor1": "changed"},
            ),
        ]

        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = sample_explanation
            mock_service.generate_counterfactuals.return_value = counterfactuals
            mock_get.return_value = mock_service

            response = client.post("/api/v1/explain/counterfactuals/exp_test_001")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["condition"] == "If X"


class TestDrilldownStep:
    """Tests for drilldown step endpoint."""

    def test_drilldown_step(self, client, sample_explanation, sample_drilldown_result):
        """Test drilling down into a step."""
        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.drilldown_step.return_value = sample_drilldown_result
                mock_get_drilldown.return_value = mock_drilldown

                response = client.post(
                    "/api/v1/explain/drilldown/step",
                    json={
                        "explanation_id": "exp_test_001",
                        "step_number": 1,
                        "depth": 1,
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert data["step_number"] == 1

    def test_drilldown_step_not_found(self, client, sample_explanation):
        """Test drilling into non-existent step."""
        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.drilldown_step.return_value = None
                mock_get_drilldown.return_value = mock_drilldown

                response = client.post(
                    "/api/v1/explain/drilldown/step",
                    json={
                        "explanation_id": "exp_test_001",
                        "step_number": 99,
                        "depth": 1,
                    },
                )

                assert response.status_code == 404


class TestDrilldownFactor:
    """Tests for drilldown factor endpoint."""

    def test_drilldown_factor(self, client, sample_explanation, sample_drilldown_result):
        """Test drilling into a factor."""
        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.drilldown_factor.return_value = sample_drilldown_result
                mock_get_drilldown.return_value = mock_drilldown

                response = client.post(
                    "/api/v1/explain/drilldown/factor",
                    json={
                        "explanation_id": "exp_test_001",
                        "factor_name": "evidence_count",
                    },
                )

                assert response.status_code == 200


class TestDrilldownEvidence:
    """Tests for drilldown evidence endpoint."""

    def test_drilldown_evidence(self, client, sample_explanation):
        """Test drilling into evidence."""
        evidence_detail = EvidenceDetail(
            evidence_id="ev_001",
            source_id="src_001",
            content_summary="Test content",
            relevance_score=0.9,
            extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.drilldown_evidence.return_value = evidence_detail
                mock_get_drilldown.return_value = mock_drilldown

                response = client.post(
                    "/api/v1/explain/drilldown/evidence",
                    json={
                        "explanation_id": "exp_test_001",
                        "evidence_ref": "ev_001",
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert data["evidence_id"] == "ev_001"


class TestTrace:
    """Tests for trace endpoints."""

    def test_get_full_trace(self, client, sample_explanation):
        """Test getting full trace."""
        step = ReasoningStep(
            step_number=1,
            description="Test",
            inputs=[],
            output="done",
        )
        step_detail = StepDetail(
            step=step,
            evidence_details=[],
            input_details={},
            computation_trace=[],
            alternatives_considered=[],
        )

        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.get_full_trace.return_value = [step_detail]
                mock_get_drilldown.return_value = mock_drilldown

                response = client.get("/api/v1/explain/trace/exp_test_001")

                assert response.status_code == 200
                data = response.json()
                assert data["total_steps"] == 1

    def test_get_evidence_chain(self, client, sample_explanation):
        """Test getting evidence chain."""
        evidence = EvidenceDetail(
            evidence_id="ev_001",
            source_id=None,
            content_summary="Test",
            relevance_score=0.8,
            extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        with patch("app.api.explain_routes.get_service") as mock_get_service:
            with patch("app.api.explain_routes.get_drilldown_service") as mock_get_drilldown:
                mock_service = MagicMock()
                mock_service.get_explanation.return_value = sample_explanation
                mock_get_service.return_value = mock_service

                mock_drilldown = MagicMock()
                mock_drilldown.get_evidence_chain.return_value = [evidence]
                mock_get_drilldown.return_value = mock_drilldown

                response = client.get("/api/v1/explain/evidence-chain/exp_test_001")

                assert response.status_code == 200
                data = response.json()
                assert data["total_evidence"] == 1


class TestUtilityEndpoints:
    """Tests for utility endpoints."""

    def test_list_types(self, client):
        """Test listing explanation types."""
        response = client.get("/api/v1/explain/types")

        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert len(data["types"]) >= 5

    def test_get_stats(self, client):
        """Test getting stats."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_stats.return_value = {"total": 10}
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/stats")

            assert response.status_code == 200

    def test_clear_cache(self, client):
        """Test clearing cache."""
        with patch("app.api.explain_routes.get_drilldown_service") as mock_get:
            mock_drilldown = MagicMock()
            mock_get.return_value = mock_drilldown

            response = client.post("/api/v1/explain/clear-cache")

            assert response.status_code == 200
            mock_drilldown.clear_cache.assert_called_once()


class TestResponseModels:
    """Tests for response model conversions."""

    def test_explanation_response_with_all_fields(self, client, sample_explanation):
        """Test explanation response includes all fields."""
        sample_explanation.counterfactuals = [
            Counterfactual(
                condition="If X",
                outcome="Y",
                likelihood=0.9,
                variables={"f1": "changed"},
            ),
        ]
        sample_explanation.metadata = {"key": "value"}

        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/exp_test_001")

            assert response.status_code == 200
            data = response.json()
            assert data["counterfactuals"] is not None
            assert data["metadata"] == {"key": "value"}
            assert data["created_at"] is not None

    def test_factor_response_direction(self, client, sample_explanation):
        """Test factor direction is properly converted."""
        with patch("app.api.explain_routes.get_service") as mock_get:
            mock_service = MagicMock()
            mock_service.get_explanation.return_value = sample_explanation
            mock_get.return_value = mock_service

            response = client.get("/api/v1/explain/exp_test_001")

            assert response.status_code == 200
            data = response.json()
            assert data["factors"][0]["direction"] == "positive"
