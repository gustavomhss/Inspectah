"""
Tests for api/ops_incidents_routes — S37

Tests for ops incidents API routes.
"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.ops_incidents_routes import router
from app.ops.incidents import Incident, IncidentSeverity, IncidentState


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestCreateIncident:
    """Tests for create incident endpoint."""

    def test_create_incident_success(self):
        """Create incident successfully."""
        mock_incident = Incident(
            id="inc_1",
            title="Test Incident",
            description="Description",
            severity=IncidentSeverity.HIGH,
        )

        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.create_incident.return_value = mock_incident

            client = _client()
            response = client.post(
                "/api/ops/incidents",
                json={
                    "id": "inc_1",
                    "title": "Test Incident",
                    "description": "Description",
                    "severity": IncidentSeverity.HIGH,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "inc_1"
            assert data["title"] == "Test Incident"

    def test_create_incident_minimal(self):
        """Create incident with minimal fields."""
        mock_incident = Incident(
            id="inc_2",
            title="Minimal Incident",
            description="",
            severity=IncidentSeverity.MEDIUM,
        )

        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.create_incident.return_value = mock_incident

            client = _client()
            response = client.post(
                "/api/ops/incidents",
                json={
                    "id": "inc_2",
                    "title": "Minimal Incident",
                },
            )

            assert response.status_code == 200

    def test_create_incident_missing_id(self):
        """Create incident without id fails."""
        client = _client()
        response = client.post(
            "/api/ops/incidents",
            json={"title": "No ID"},
        )

        assert response.status_code == 400
        assert "campo obrigatório" in response.json()["detail"]

    def test_create_incident_missing_title(self):
        """Create incident without title fails."""
        client = _client()
        response = client.post(
            "/api/ops/incidents",
            json={"id": "inc_3"},
        )

        assert response.status_code == 400
        assert "campo obrigatório" in response.json()["detail"]

    def test_create_incident_value_error(self):
        """Create incident with invalid value."""
        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.create_incident.side_effect = ValueError("Invalid severity")

            client = _client()
            response = client.post(
                "/api/ops/incidents",
                json={
                    "id": "inc_4",
                    "title": "Invalid",
                    "severity": "INVALID",
                },
            )

            assert response.status_code == 400


class TestGetIncident:
    """Tests for get incident endpoint."""

    def test_get_incident_found(self):
        """Get existing incident."""
        mock_incident = Incident(
            id="inc_1",
            title="Test Incident",
            description="Description",
            severity=IncidentSeverity.HIGH,
            state=IncidentState.OPEN,
        )

        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.get.return_value = mock_incident

            client = _client()
            response = client.get("/api/ops/incidents/inc_1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "inc_1"
            assert data["state"] == IncidentState.OPEN

    def test_get_incident_not_found(self):
        """Get non-existent incident."""
        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.get.return_value = None

            client = _client()
            response = client.get("/api/ops/incidents/missing")

            assert response.status_code == 404
            assert "não encontrado" in response.json()["detail"]


class TestTransitionIncident:
    """Tests for transition incident endpoint."""

    def test_transition_incident_success(self):
        """Transition incident successfully."""
        mock_incident = Incident(
            id="inc_1",
            title="Test Incident",
            description="Description",
            severity=IncidentSeverity.HIGH,
            state=IncidentState.TRIAGE,
        )

        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.transition.return_value = mock_incident

            client = _client()
            response = client.post(
                "/api/ops/incidents/inc_1/transition",
                json={"new_state": IncidentState.TRIAGE},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["state"] == IncidentState.TRIAGE

    def test_transition_incident_missing_new_state(self):
        """Transition without new_state fails."""
        client = _client()
        response = client.post(
            "/api/ops/incidents/inc_1/transition",
            json={},
        )

        assert response.status_code == 400
        assert "new_state obrigatório" in response.json()["detail"]

    def test_transition_incident_invalid_transition(self):
        """Invalid transition fails."""
        with patch("app.api.ops_incidents_routes.service") as mock_service:
            mock_service.transition.side_effect = ValueError("Transição inválida")

            client = _client()
            response = client.post(
                "/api/ops/incidents/inc_1/transition",
                json={"new_state": IncidentState.CLOSED},
            )

            assert response.status_code == 400
            assert "Transição inválida" in response.json()["detail"]


class TestIncidentStates:
    """Tests for incident state constants."""

    def test_incident_states_exist(self):
        """All incident states exist."""
        assert IncidentState.OPEN == "OPEN"
        assert IncidentState.TRIAGE == "TRIAGE"
        assert IncidentState.MITIGATING == "MITIGATING"
        assert IncidentState.RESOLVED == "RESOLVED"
        assert IncidentState.CLOSED == "CLOSED"

    def test_terminal_states(self):
        """Terminal states are correct."""
        assert IncidentState.RESOLVED in IncidentState.TERMINAL
        assert IncidentState.CLOSED in IncidentState.TERMINAL
        assert IncidentState.OPEN not in IncidentState.TERMINAL


class TestIncidentSeverity:
    """Tests for incident severity constants."""

    def test_severity_levels_exist(self):
        """All severity levels exist."""
        assert IncidentSeverity.LOW == "LOW"
        assert IncidentSeverity.MEDIUM == "MEDIUM"
        assert IncidentSeverity.HIGH == "HIGH"
        assert IncidentSeverity.CRITICAL == "CRITICAL"

    def test_all_severities(self):
        """All severities set is complete."""
        assert len(IncidentSeverity.ALL) == 4
        assert IncidentSeverity.LOW in IncidentSeverity.ALL
        assert IncidentSeverity.CRITICAL in IncidentSeverity.ALL
