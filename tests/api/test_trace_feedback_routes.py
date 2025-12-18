"""
Tests for api/trace_feedback_routes — S37

Tests for trace and feedback routes.
"""

import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.trace_feedback_routes import router, _trace_repo, _feedback_repo
from app.agents.trace_repository import TraceRepository
from app.feedback.repository import FeedbackRepository


def _create_client(trace_repo=None, feedback_repo=None) -> TestClient:
    """Create test client with optional repository overrides."""
    app = FastAPI()
    app.include_router(router)
    if trace_repo is not None:
        app.dependency_overrides[_trace_repo] = lambda: trace_repo
    if feedback_repo is not None:
        app.dependency_overrides[_feedback_repo] = lambda: feedback_repo
    return TestClient(app)


class TestTraceRepoFactory:
    """Tests for _trace_repo factory."""

    def test_trace_repo_returns_repository(self):
        """Factory returns TraceRepository."""
        result = _trace_repo()
        assert isinstance(result, TraceRepository)


class TestFeedbackRepoFactory:
    """Tests for _feedback_repo factory."""

    def test_feedback_repo_returns_repository(self):
        """Factory returns FeedbackRepository."""
        result = _feedback_repo()
        assert isinstance(result, FeedbackRepository)


class TestListRecentTraces:
    """Tests for list_recent_traces endpoint."""

    def test_list_recent_traces_success(self):
        """List recent traces successfully."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.list_recent.return_value = [{"id": "trace_1"}]

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/recent")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 1
        mock_repo.list_recent.assert_called_once_with(domain=None, limit=20)

    def test_list_recent_traces_with_domain(self):
        """List recent traces with domain filter."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.list_recent.return_value = []

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/recent?domain=politics")

        assert response.status_code == 200
        mock_repo.list_recent.assert_called_once_with(domain="politics", limit=20)

    def test_list_recent_traces_with_limit(self):
        """List recent traces with custom limit."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.list_recent.return_value = []

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/recent?limit=50")

        assert response.status_code == 200
        mock_repo.list_recent.assert_called_once_with(domain=None, limit=50)


class TestListTracesByDecision:
    """Tests for list_traces_by_decision endpoint."""

    def test_list_traces_by_decision_success(self):
        """List traces by decision successfully."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.list_traces_by_decision.return_value = [{"id": "trace_1"}]

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/decision/dec_123")

        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == "dec_123"
        assert len(data["agent_traces"]) == 1
        mock_repo.list_traces_by_decision.assert_called_once_with("dec_123")


class TestListTracesByClaim:
    """Tests for list_traces_by_claim endpoint."""

    def test_list_traces_by_claim_success(self):
        """List traces by claim successfully."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.list_traces_by_claim.return_value = [{"id": "trace_1"}]

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/claim/claim_123")

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "claim_123"
        mock_repo.list_traces_by_claim.assert_called_once_with("claim_123")


class TestTraceDetail:
    """Tests for trace_detail endpoint."""

    def test_trace_detail_success(self):
        """Get trace detail successfully."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.get_trace.return_value = {"id": "trace_123"}
        mock_repo.list_steps_for_trace.return_value = [{"step_id": "step_1"}]

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/trace_123")

        assert response.status_code == 200
        data = response.json()
        assert data["trace"]["id"] == "trace_123"
        assert len(data["steps"]) == 1
        mock_repo.get_trace.assert_called_once_with("trace_123")
        mock_repo.list_steps_for_trace.assert_called_once_with("trace_123")

    def test_trace_detail_not_found(self):
        """Get trace detail when not found."""
        mock_repo = MagicMock(spec=TraceRepository)
        mock_repo.get_trace.return_value = None

        client = _create_client(trace_repo=mock_repo)
        response = client.get("/api/traces/missing_trace")

        assert response.status_code == 404


class TestSubmitFeedbackTrace:
    """Tests for submit_feedback_trace endpoint."""

    def test_submit_feedback_trace_success(self):
        """Submit feedback on trace successfully."""
        mock_repo = MagicMock(spec=FeedbackRepository)

        client = _create_client(feedback_repo=mock_repo)
        response = client.post(
            "/api/feedback/trace",
            json={
                "target_id": "trace_123",
                "feedback_kind": "positive",
                "comment": "Good trace",
                "authored_by_actor": "tester",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ok"] is True
        assert "feedback_id" in data
        mock_repo.record_feedback_on_trace.assert_called_once()

    def test_submit_feedback_trace_missing_target(self):
        """Submit feedback without target_id fails."""
        mock_repo = MagicMock(spec=FeedbackRepository)
        client = _create_client(feedback_repo=mock_repo)
        response = client.post(
            "/api/feedback/trace",
            json={"feedback_kind": "positive"},
        )

        assert response.status_code == 400
        assert "target_id" in response.json()["detail"]


class TestSubmitFeedbackDecision:
    """Tests for submit_feedback_decision endpoint."""

    def test_submit_feedback_decision_success(self):
        """Submit feedback on decision successfully."""
        mock_repo = MagicMock(spec=FeedbackRepository)

        client = _create_client(feedback_repo=mock_repo)
        response = client.post(
            "/api/feedback/decision",
            json={
                "decision_record_id": "dec_123",
                "feedback_kind": "negative",
                "comment": "Bad decision",
                "authored_by_actor": "reviewer",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["ok"] is True
        mock_repo.record_feedback_on_decision.assert_called_once()

    def test_submit_feedback_decision_missing_id(self):
        """Submit feedback without decision_record_id fails."""
        mock_repo = MagicMock(spec=FeedbackRepository)
        client = _create_client(feedback_repo=mock_repo)
        response = client.post(
            "/api/feedback/decision",
            json={"feedback_kind": "positive"},
        )

        assert response.status_code == 400
        assert "decision_record_id" in response.json()["detail"]
