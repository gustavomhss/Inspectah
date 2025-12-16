"""
Tests for api/catalog_routes — S37

Tests for catalog routes.
"""

import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.catalog_routes import router, _service
from app.flows.service import FlowService


def _create_client_with_service_override(mock_service):
    """Create test client with service override."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[_service] = lambda: mock_service
    return TestClient(app)


class TestListCatalog:
    """Tests for list_catalog endpoint."""

    def test_list_catalog_success(self):
        """List catalog successfully."""
        mock_entries = [
            {"flow_id": "flow_1", "flow_version_id": "v1", "domain": "test", "hash": "abc123"},
            {"flow_id": "flow_2", "flow_version_id": "v1", "domain": "test", "hash": "def456"},
        ]

        mock_service = MagicMock(spec=FlowService)
        mock_service.list_catalog.return_value = mock_entries

        client = _create_client_with_service_override(mock_service)
        response = client.get("/api/flows/catalog")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        mock_service.list_catalog.assert_called_once()

    def test_list_catalog_empty(self):
        """List catalog when empty."""
        mock_service = MagicMock(spec=FlowService)
        mock_service.list_catalog.return_value = []

        client = _create_client_with_service_override(mock_service)
        response = client.get("/api/flows/catalog")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_catalog_exception(self):
        """List catalog handles service exception with generic error message."""
        mock_service = MagicMock(spec=FlowService)
        mock_service.list_catalog.side_effect = Exception("Database error")

        client = _create_client_with_service_override(mock_service)
        response = client.get("/api/flows/catalog")

        assert response.status_code == 500
        # Security: internal errors should return generic message (not expose stack trace)
        assert "Failed to load flow catalog" in response.json()["detail"]
