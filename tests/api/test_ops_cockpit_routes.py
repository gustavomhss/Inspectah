"""
Tests for api/ops_cockpit_routes — S37

Tests for ops cockpit routes.
"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.ops_cockpit_routes import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestListComponents:
    """Tests for list_components endpoint."""

    def test_list_components_success(self):
        """List components successfully."""
        mock_comp = MagicMock()
        mock_comp.__dict__ = {"id": "comp_1", "name": "Test Component"}

        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[mock_comp]):
            client = _client()
            response = client.get("/api/ops/cockpit/components")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_list_components_empty(self):
        """List components when none exist."""
        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[]):
            client = _client()
            response = client.get("/api/ops/cockpit/components")

            assert response.status_code == 200
            assert response.json() == []


class TestListIncidents:
    """Tests for list_incidents endpoint."""

    def test_list_incidents_success(self):
        """List incidents successfully."""
        with patch("app.api.ops_cockpit_routes.incident_service") as mock_service:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.execute.return_value.fetchall.return_value = [
                ("inc_1", "Test Incident", "HIGH", "OPEN", "comp_1", "slo_1,slo_2", "2024-01-01", "2024-01-02")
            ]
            mock_service._conn.return_value = mock_conn

            client = _client()
            response = client.get("/api/ops/cockpit/incidents")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == "inc_1"

    def test_list_incidents_empty_slos(self):
        """List incidents with empty SLOs."""
        with patch("app.api.ops_cockpit_routes.incident_service") as mock_service:
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_conn.execute.return_value.fetchall.return_value = [
                ("inc_2", "No SLOs", "MEDIUM", "OPEN", None, None, "2024-01-01", "2024-01-02")
            ]
            mock_service._conn.return_value = mock_conn

            client = _client()
            response = client.get("/api/ops/cockpit/incidents")

            assert response.status_code == 200
            data = response.json()
            assert data[0]["slo_ids"] == []


class TestOverview:
    """Tests for overview endpoint."""

    def test_overview_success(self):
        """Get overview successfully."""
        # Use SimpleNamespace instead of MagicMock to avoid __dict__ issues
        from types import SimpleNamespace
        mock_comp = SimpleNamespace(id="comp_1", name="Test")

        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[mock_comp]):
            with patch("app.api.ops_cockpit_routes.incident_service") as mock_inc_service:
                mock_conn = MagicMock()
                mock_conn.__enter__ = MagicMock(return_value=mock_conn)
                mock_conn.__exit__ = MagicMock(return_value=False)
                mock_conn.execute.return_value.fetchall.return_value = []
                mock_inc_service._conn.return_value = mock_conn

                with patch("app.api.ops_cockpit_routes.evaluate_slos", return_value=[]):
                    with patch("app.api.ops_cockpit_routes.flow_service") as mock_flow:
                        mock_flow.list_flows.return_value = []

                        client = _client()
                        response = client.get("/api/ops/cockpit/overview")

                        assert response.status_code == 200
                        data = response.json()
                        assert "components" in data
                        assert "incidents" in data
                        assert "slos" in data
                        assert "flows" in data

    def test_overview_flow_exception(self):
        """Get overview handles flow exception."""
        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[]):
            with patch("app.api.ops_cockpit_routes.incident_service") as mock_inc_service:
                mock_conn = MagicMock()
                mock_conn.__enter__ = MagicMock(return_value=mock_conn)
                mock_conn.__exit__ = MagicMock(return_value=False)
                mock_conn.execute.return_value.fetchall.return_value = []
                mock_inc_service._conn.return_value = mock_conn

                with patch("app.api.ops_cockpit_routes.evaluate_slos", return_value=[]):
                    with patch("app.api.ops_cockpit_routes.flow_service") as mock_flow:
                        mock_flow.list_flows.side_effect = Exception("DB error")

                        client = _client()
                        response = client.get("/api/ops/cockpit/overview")

                        assert response.status_code == 200
                        data = response.json()
                        assert data["flows"] == 0
                        assert data["flows_list"] == []


class TestFlows:
    """Tests for flows endpoint."""

    def test_flows_success(self):
        """Get flows successfully."""
        mock_comp = MagicMock()
        mock_comp.id = "flow_test"
        mock_comp.slos = ["slo_1"]

        mock_flow = MagicMock()
        mock_flow.id = "flow_1"
        mock_flow.slug = "test"
        mock_flow.domain = "generic"
        mock_flow.estado = "ATIVO"
        mock_flow.flow_version_id = "v1"
        mock_flow.active_version_id = "av1"
        mock_flow.test_version_id = None

        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[mock_comp]):
            with patch("app.api.ops_cockpit_routes.evaluate_slos", return_value=[{"slo_id": "slo_1", "status": "OK"}]):
                with patch("app.api.ops_cockpit_routes.flow_service") as mock_flow_service:
                    mock_flow_service.list_flows.return_value = [mock_flow]

                    client = _client()
                    response = client.get("/api/ops/cockpit/flows")

                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 1
                    assert data[0]["id"] == "flow_1"

    def test_flows_no_component(self):
        """Get flows when no component matches."""
        mock_flow = MagicMock()
        mock_flow.id = "flow_1"
        mock_flow.slug = "unknown"
        mock_flow.domain = "generic"
        mock_flow.estado = "DRAFT"
        mock_flow.flow_version_id = "v1"
        mock_flow.active_version_id = None
        mock_flow.test_version_id = None

        with patch("app.api.ops_cockpit_routes.load_components_map", return_value=[]):
            with patch("app.api.ops_cockpit_routes.evaluate_slos", return_value=[]):
                with patch("app.api.ops_cockpit_routes.flow_service") as mock_flow_service:
                    mock_flow_service.list_flows.return_value = [mock_flow]

                    client = _client()
                    response = client.get("/api/ops/cockpit/flows")

                    assert response.status_code == 200
                    data = response.json()
                    assert data[0]["component_id"] is None
                    assert data[0]["slos"] == []
