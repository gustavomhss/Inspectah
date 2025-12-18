"""
Tests for app/api/policies_routes.py

Comprehensive tests for policies API routes.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.policies_routes import router
from app.policies.models import PromotionPolicyConfig
from app.policies.version_service import (
    PolicyVersion,
    PolicyAuditEntry,
    PolicyStatus,
    ChangeType,
)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _make_version(
    version_id: str = "v1",
    policy_id: str = "pol_1",
    status: PolicyStatus = PolicyStatus.DRAFT,
) -> PolicyVersion:
    """Helper to create mock policy version."""
    config = PromotionPolicyConfig(
        name="Test Policy",
        domain="politics",
        min_confidence=0.8,
        min_sources=2,
        require_debunk=False,
        require_human=False,
        sensitive=False,
        default_decision="HOLD",
        metadata={},
    )
    return PolicyVersion(
        version_id=version_id,
        policy_id=policy_id,
        version_number=1,
        config=config,
        status=status,
        created_at=datetime.now(timezone.utc),
        created_by="admin",
        content_hash="abc123",
        changelog="Initial version",
    )


class TestCreateVersion:
    """Tests for POST /versions endpoint."""

    def test_create_version_success(self):
        """Create version successfully."""
        version = _make_version()

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.create_version.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions?created_by=admin",
                json={
                    "config": {
                        "name": "Test Policy",
                        "domain": "politics",
                        "min_confidence": 0.8,
                        "min_sources": 2,
                        "require_debunk": False,
                        "require_human": False,
                        "sensitive": False,
                        "default_decision": "HOLD",
                    },
                    "changelog": "Initial version",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["version_id"] == "v1"
            assert data["status"] == "draft"

    def test_create_version_validation_error(self):
        """Create version with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.create_version.side_effect = ValueError("Invalid config")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions?created_by=admin",
                json={
                    "config": {
                        "name": "Test",
                        "domain": "test",
                        "min_confidence": 0.5,
                        "min_sources": 1,
                    },
                },
            )

            assert response.status_code == 400

    def test_create_version_with_parent(self):
        """Create version with parent version."""
        version = _make_version()

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.create_version.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions?created_by=admin",
                json={
                    "config": {
                        "name": "Test",
                        "domain": "politics",
                        "min_confidence": 0.8,
                        "min_sources": 2,
                    },
                    "parent_version_id": "v0",
                },
            )

            assert response.status_code == 200


class TestGetVersion:
    """Tests for GET /versions/{version_id} endpoint."""

    def test_get_version_success(self):
        """Get version successfully."""
        version = _make_version()

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.repository.get_version.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/versions/v1")

            assert response.status_code == 200
            data = response.json()
            assert data["version_id"] == "v1"

    def test_get_version_not_found(self):
        """Get version that doesn't exist."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.repository.get_version.return_value = None
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/versions/nonexistent")

            assert response.status_code == 404


class TestSubmitForReview:
    """Tests for POST /versions/{version_id}/submit endpoint."""

    def test_submit_for_review_success(self):
        """Submit version for review successfully."""
        version = _make_version(status=PolicyStatus.PENDING_REVIEW)

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.submit_for_review.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post("/api/v1/policies/versions/v1/submit?submitted_by=admin")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending_review"

    def test_submit_for_review_validation_error(self):
        """Submit version with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.submit_for_review.side_effect = ValueError("Cannot submit")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post("/api/v1/policies/versions/v1/submit?submitted_by=admin")

            assert response.status_code == 400


class TestApproveVersion:
    """Tests for POST /versions/{version_id}/approve endpoint."""

    def test_approve_version_success(self):
        """Approve version successfully."""
        version = _make_version(status=PolicyStatus.APPROVED)
        version.approved_by = "approver"
        version.approved_at = datetime.now(timezone.utc)

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.approve.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions/v1/approve?approved_by=approver",
                json={"comments": "Looks good"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"
            assert data["approved_by"] == "approver"

    def test_approve_version_validation_error(self):
        """Approve version with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.approve.side_effect = ValueError("Cannot approve")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions/v1/approve?approved_by=approver",
                json={"comments": ""},
            )

            assert response.status_code == 400


class TestActivateVersion:
    """Tests for POST /versions/{version_id}/activate endpoint."""

    def test_activate_version_success(self):
        """Activate version successfully."""
        version = _make_version(status=PolicyStatus.ACTIVE)
        version.activated_at = datetime.now(timezone.utc)

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.activate.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post("/api/v1/policies/versions/v1/activate?activated_by=admin")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "active"

    def test_activate_version_validation_error(self):
        """Activate version with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.activate.side_effect = ValueError("Cannot activate")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post("/api/v1/policies/versions/v1/activate?activated_by=admin")

            assert response.status_code == 400


class TestDeactivateVersion:
    """Tests for POST /versions/{version_id}/deactivate endpoint."""

    def test_deactivate_version_success(self):
        """Deactivate version successfully."""
        version = _make_version(status=PolicyStatus.DEPRECATED)
        version.deactivated_at = datetime.now(timezone.utc)

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.deactivate.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/versions/v1/deactivate?deactivated_by=admin&reason=Outdated"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "deprecated"

    def test_deactivate_version_validation_error(self):
        """Deactivate version with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.deactivate.side_effect = ValueError("Cannot deactivate")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post("/api/v1/policies/versions/v1/deactivate?deactivated_by=admin")

            assert response.status_code == 400


class TestGetActivePolicy:
    """Tests for GET /active/{domain} endpoint."""

    def test_get_active_policy_success(self):
        """Get active policy successfully."""
        config = PromotionPolicyConfig(
            name="Active Policy",
            domain="politics",
            min_confidence=0.8,
            min_sources=2,
            require_debunk=False,
            require_human=False,
            sensitive=False,
            default_decision="HOLD",
            metadata={},
        )

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_active_policy.return_value = config
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/active/politics")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Active Policy"
            assert data["domain"] == "politics"

    def test_get_active_policy_not_found(self):
        """Get active policy when none exists."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_active_policy.return_value = None
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/active/unknown")

            assert response.status_code == 404


class TestGetVersionHistory:
    """Tests for GET /history/{domain} endpoint."""

    def test_get_version_history_success(self):
        """Get version history successfully."""
        versions = [
            _make_version("v1", status=PolicyStatus.ACTIVE),
            _make_version("v2", status=PolicyStatus.DRAFT),
        ]

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_version_history.return_value = versions
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/history/politics")

            assert response.status_code == 200
            data = response.json()
            assert data["domain"] == "politics"
            assert data["total"] == 2
            assert len(data["versions"]) == 2

    def test_get_version_history_with_limit(self):
        """Get version history with limit."""
        versions = [_make_version(f"v{i}") for i in range(30)]

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_version_history.return_value = versions
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/history/politics?limit=10")

            assert response.status_code == 200
            data = response.json()
            assert len(data["versions"]) == 10

    def test_get_version_history_with_name_filter(self):
        """Get version history filtered by name."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_version_history.return_value = []
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/history/politics?name=test")

            assert response.status_code == 200


class TestRollback:
    """Tests for POST /rollback/{domain} endpoint."""

    def test_rollback_success(self):
        """Rollback to previous version successfully."""
        version = _make_version(status=PolicyStatus.ACTIVE)

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.rollback.return_value = version
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/rollback/politics?rolled_back_by=admin",
                json={
                    "target_version_id": "v1",
                    "reason": "Bugs in current version",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["version_id"] == "v1"

    def test_rollback_validation_error(self):
        """Rollback with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.rollback.side_effect = ValueError("Cannot rollback")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.post(
                "/api/v1/policies/rollback/politics?rolled_back_by=admin",
                json={"target_version_id": "v1", "reason": "Test"},
            )

            assert response.status_code == 400


class TestCompareVersions:
    """Tests for GET /compare endpoint."""

    def test_compare_versions_success(self):
        """Compare versions successfully."""
        comparison = MagicMock()
        comparison.version_a = "v1"
        comparison.version_b = "v2"
        comparison.differences = [{"field": "min_confidence", "old": 0.8, "new": 0.9}]
        comparison.summary = "1 field changed"

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.compare_versions.return_value = comparison
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/compare?version_a=v1&version_b=v2")

            assert response.status_code == 200
            data = response.json()
            assert data["version_a"] == "v1"
            assert data["version_b"] == "v2"
            assert len(data["differences"]) == 1

    def test_compare_versions_validation_error(self):
        """Compare versions with validation error."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.compare_versions.side_effect = ValueError("Invalid versions")
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/compare?version_a=v1&version_b=v2")

            assert response.status_code == 400


class TestGetAuditLog:
    """Tests for GET /audit endpoint."""

    def test_get_audit_log_all(self):
        """Get audit log for all policies."""
        entries = [
            PolicyAuditEntry(
                audit_id="audit_1",
                policy_id="pol_1",
                version_id="v1",
                change_type=ChangeType.CREATE,
                changed_at=datetime.now(timezone.utc),
                changed_by="admin",
                details={},
            ),
        ]

        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_audit_log.return_value = entries
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/audit")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["audit_id"] == "audit_1"

    def test_get_audit_log_filtered_by_policy(self):
        """Get audit log filtered by policy."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_audit_log.return_value = []
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/audit?policy_id=pol_1")

            assert response.status_code == 200
            mock_svc.get_audit_log.assert_called_once_with("pol_1", 100)

    def test_get_audit_log_with_limit(self):
        """Get audit log with custom limit."""
        with patch("app.api.policies_routes._get_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_audit_log.return_value = []
            mock_service.return_value = mock_svc

            client = _client()
            response = client.get("/api/v1/policies/audit?limit=50")

            assert response.status_code == 200
            mock_svc.get_audit_log.assert_called_once_with(None, 50)


class TestListStatuses:
    """Tests for GET /statuses endpoint."""

    def test_list_statuses_success(self):
        """List all policy statuses and change types."""
        client = _client()
        response = client.get("/api/v1/policies/statuses")

        assert response.status_code == 200
        data = response.json()
        assert "statuses" in data
        assert "change_types" in data
        assert len(data["statuses"]) == 6  # All PolicyStatus values
        assert len(data["change_types"]) == 7  # All ChangeType values

    def test_list_statuses_includes_descriptions(self):
        """List statuses includes descriptions."""
        client = _client()
        response = client.get("/api/v1/policies/statuses")

        assert response.status_code == 200
        data = response.json()

        # Check status descriptions
        draft_status = next(s for s in data["statuses"] if s["status"] == "draft")
        assert draft_status["description"] == "Em elaboracao"

        # Check change type descriptions
        create_change = next(c for c in data["change_types"] if c["type"] == "create")
        assert create_change["description"] == "Criacao de versao"
