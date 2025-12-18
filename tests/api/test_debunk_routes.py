"""
Tests for api/debunk/routes — S37

Tests for debunk API routes.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.debunk.routes import router, get_repo
from app.debunk.models import (
    DebunkDecisionType,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTaskType,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository
from app.debunk import service


def _make_repo(tmp_path: Path) -> DebunkRepository:
    db_path = tmp_path / "debunk_test.sqlite"
    return DebunkRepository(db_path=db_path)


def _client(repo: DebunkRepository) -> TestClient:
    app = FastAPI()
    app.dependency_overrides[get_repo] = lambda: repo
    app.include_router(router, prefix="/api")
    return TestClient(app)


class TestGetRepo:
    """Tests for get_repo function."""

    def test_get_repo_returns_repository(self):
        """Get repo returns DebunkRepository instance."""
        repo = get_repo()
        assert isinstance(repo, DebunkRepository)


class TestCreateIssue:
    """Tests for create issue endpoint."""

    def test_create_issue_success(self, tmp_path: Path):
        """Create issue successfully."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-test",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "HIGH",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_id"] == "claim-test"
        assert data["status"] == DebunkIssueStatus.OPEN.value

    def test_create_issue_duplicate_fails(self, tmp_path: Path):
        """Create duplicate issue fails."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        payload = {
            "target_type": "CLAIM",
            "target_id": "claim-dup",
            "question": "Is this true?",
            "reason": "Needs verification",
            "risk_level": "MEDIUM",
            "priority": 5,
            "origin": "test",
            "opened_by": "tester",
        }

        # First creation succeeds
        resp1 = client.post("/api/debunk/issues", json=payload)
        assert resp1.status_code == 201

        # Second creation fails
        resp2 = client.post("/api/debunk/issues", json=payload)
        assert resp2.status_code == 409

    def test_create_issue_invalid_priority(self, tmp_path: Path):
        """Create issue with invalid priority fails."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-test",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "HIGH",
                "priority": 150,  # Invalid > 100
                "origin": "test",
                "opened_by": "tester",
            },
        )

        assert response.status_code == 422


class TestListIssues:
    """Tests for list issues endpoint."""

    def test_list_issues_empty(self, tmp_path: Path):
        """List issues when none exist."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.get("/api/debunk/issues")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_issues_with_filter(self, tmp_path: Path):
        """List issues with status filter."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-filter",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "MEDIUM",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )

        # Filter by OPEN status
        response = client.get("/api/debunk/issues?statuses=OPEN")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == DebunkIssueStatus.OPEN.value

    def test_list_issues_multiple_statuses(self, tmp_path: Path):
        """List issues with multiple status filters."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-multi",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "MEDIUM",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )

        # Filter by multiple statuses
        response = client.get("/api/debunk/issues?statuses=OPEN,TRIAGED")

        assert response.status_code == 200


class TestGetIssue:
    """Tests for get issue endpoint."""

    def test_get_issue_found(self, tmp_path: Path):
        """Get existing issue."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        create_resp = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-get",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "HIGH",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )
        issue_id = create_resp.json()["id"]

        response = client.get(f"/api/debunk/issues/{issue_id}")

        assert response.status_code == 200
        data = response.json()
        assert "issue" in data
        assert "tasks" in data
        assert "decisions" in data

    def test_get_issue_not_found(self, tmp_path: Path):
        """Get non-existent issue."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.get("/api/debunk/issues/missing-id")

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]


class TestCreateTask:
    """Tests for create task endpoint."""

    def test_create_task_success(self, tmp_path: Path):
        """Create task successfully."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue first
        create_resp = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-task",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "MEDIUM",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )
        issue_id = create_resp.json()["id"]

        # Create a task
        response = client.post(
            f"/api/debunk/issues/{issue_id}/tasks",
            json={
                "task_type": "FACT_CHECK",
                "instructions": "Check the facts",
                "assigned_to": "analyst",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == DebunkTaskType.FACT_CHECK.value

    def test_create_task_issue_not_found(self, tmp_path: Path):
        """Create task for non-existent issue fails."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.post(
            "/api/debunk/issues/missing-id/tasks",
            json={
                "task_type": "FACT_CHECK",
                "instructions": "Check the facts",
            },
        )

        assert response.status_code == 400


class TestAddDecision:
    """Tests for add decision endpoint."""

    def test_add_decision_success(self, tmp_path: Path):
        """Add decision successfully."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        create_resp = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-decision",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "HIGH",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )
        issue_id = create_resp.json()["id"]

        # Add a task and complete it
        task_resp = client.post(
            f"/api/debunk/issues/{issue_id}/tasks",
            json={
                "task_type": "FACT_CHECK",
                "instructions": "Check the facts",
                "assigned_to": "analyst",
            },
        )

        # Add decision
        response = client.post(
            f"/api/debunk/issues/{issue_id}/decisions",
            json={
                "decision_type": "CLAIM_BEM_SUPORTADO",
                "rationale": "Evidence supports the claim",
                "recommended_truth_action": "SUGERE_PROMOVER",
                "created_by": "analyst",
                "confidence": 0.9,
                "evidence_refs": ["evidence://item1"],
            },
        )

        assert response.status_code == 201

    def test_add_decision_invalid_issue(self, tmp_path: Path):
        """Add decision to non-existent issue fails."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        response = client.post(
            "/api/debunk/issues/missing-id/decisions",
            json={
                "decision_type": "CLAIM_BEM_SUPORTADO",
                "rationale": "Evidence supports the claim",
                "recommended_truth_action": "SUGERE_PROMOVER",
                "created_by": "analyst",
                "confidence": 0.9,
            },
        )

        assert response.status_code == 400


class TestTransitionIssue:
    """Tests for transition issue endpoint."""

    def test_transition_issue_success(self, tmp_path: Path):
        """Transition issue status successfully."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        create_resp = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-transition",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "MEDIUM",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )
        issue_id = create_resp.json()["id"]

        # Transition to TRIAGED
        response = client.post(
            f"/api/debunk/issues/{issue_id}/status/TRIAGED?actor=analyst"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == DebunkIssueStatus.TRIAGED.value

    def test_transition_issue_invalid_state(self, tmp_path: Path):
        """Transition to invalid state fails."""
        repo = _make_repo(tmp_path)
        client = _client(repo)

        # Create an issue
        create_resp = client.post(
            "/api/debunk/issues",
            json={
                "target_type": "CLAIM",
                "target_id": "claim-invalid-transition",
                "question": "Is this true?",
                "reason": "Needs verification",
                "risk_level": "MEDIUM",
                "priority": 5,
                "origin": "test",
                "opened_by": "tester",
            },
        )
        issue_id = create_resp.json()["id"]

        # Try to transition directly to RESOLVED (invalid)
        response = client.post(
            f"/api/debunk/issues/{issue_id}/status/RESOLVED?actor=analyst"
        )

        assert response.status_code == 400
