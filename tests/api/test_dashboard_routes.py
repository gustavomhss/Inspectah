"""
Tests for app/api/dashboard_routes.py

Comprehensive tests for dashboard API routes.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dashboard_routes import router
from app.ops.dashboard_service import (
    HealthStatus,
    AlertSeverity,
    MetricType,
    ComponentHealth,
    ActiveAlert,
)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@dataclass
class MockSnapshot:
    """Mock snapshot for testing."""
    overall_health: HealthStatus
    summary: str
    timestamp: datetime
    slos: list

    def to_dict(self):
        return {
            "overall_health": self.overall_health.value,
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat(),
            "slos": [s.to_dict() for s in self.slos],
        }


@dataclass
class MockSLO:
    """Mock SLO for testing."""
    slo_id: str
    in_violation: bool

    def to_dict(self):
        return {
            "slo_id": self.slo_id,
            "in_violation": self.in_violation,
        }


class TestGetSnapshot:
    """Tests for GET /snapshot endpoint."""

    def test_get_snapshot_success(self):
        """Get dashboard snapshot successfully."""
        mock_slo = MockSLO(slo_id="slo_1", in_violation=False)
        mock_snapshot = MockSnapshot(
            overall_health=HealthStatus.HEALTHY,
            summary="All systems operational",
            timestamp=datetime.now(timezone.utc),
            slos=[mock_slo],
        )

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_snapshot.return_value = mock_snapshot
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/snapshot")

            assert response.status_code == 200
            data = response.json()
            assert data["overall_health"] == "healthy"
            assert data["summary"] == "All systems operational"
            assert len(data["slos"]) == 1


class TestGetHealthStatus:
    """Tests for GET /health endpoint."""

    def test_get_health_all_healthy(self):
        """Get health status when all components healthy."""
        now = datetime.now(timezone.utc)
        components = [
            ComponentHealth("comp_1", "API", HealthStatus.HEALTHY, now, 10.0),
            ComponentHealth("comp_2", "DB", HealthStatus.HEALTHY, now, 20.0),
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.health.check_all.return_value = components
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health")

            assert response.status_code == 200
            data = response.json()
            assert data["overall"] == "healthy"
            assert data["total"] == 2
            assert data["healthy"] == 2
            assert data["degraded"] == 0
            assert data["unhealthy"] == 0

    def test_get_health_with_degraded(self):
        """Get health status with degraded components."""
        now = datetime.now(timezone.utc)
        components = [
            ComponentHealth("comp_1", "API", HealthStatus.HEALTHY, now, 10.0),
            ComponentHealth("comp_2", "DB", HealthStatus.DEGRADED, now, 100.0),
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.health.check_all.return_value = components
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health")

            assert response.status_code == 200
            data = response.json()
            assert data["overall"] == "degraded"
            assert data["degraded"] == 1

    def test_get_health_with_unhealthy(self):
        """Get health status with unhealthy components."""
        now = datetime.now(timezone.utc)
        components = [
            ComponentHealth("comp_1", "API", HealthStatus.HEALTHY, now, 10.0),
            ComponentHealth("comp_2", "DB", HealthStatus.UNHEALTHY, now, 1000.0),
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.health.check_all.return_value = components
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health")

            assert response.status_code == 200
            data = response.json()
            assert data["overall"] == "unhealthy"
            assert data["unhealthy"] == 1


class TestGetComponentHealth:
    """Tests for GET /health/{component_id} endpoint."""

    def test_get_component_health_success(self):
        """Get specific component health successfully."""
        now = datetime.now(timezone.utc)
        component = ComponentHealth("comp_1", "API", HealthStatus.HEALTHY, now, 10.0)

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.health.check_one.return_value = component
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health/comp_1")

            assert response.status_code == 200
            data = response.json()
            assert data["component_id"] == "comp_1"
            assert data["status"] == "healthy"

    def test_get_component_health_not_found(self):
        """Get component health when component not found."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.health.check_one.return_value = None
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health/nonexistent")

            assert response.status_code == 404


class TestGetComponentHistory:
    """Tests for GET /health/{component_id}/history endpoint."""

    def test_get_component_history_success(self):
        """Get component health history successfully."""
        history = [
            {"timestamp": "2024-01-01T00:00:00Z", "status": "healthy"},
            {"timestamp": "2024-01-01T01:00:00Z", "status": "degraded"},
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_component_history.return_value = history
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health/comp_1/history")

            assert response.status_code == 200
            data = response.json()
            assert data["component_id"] == "comp_1"
            assert len(data["history"]) == 2

    def test_get_component_history_with_limit(self):
        """Get component history with custom limit."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_component_history.return_value = []
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/health/comp_1/history?limit=50")

            assert response.status_code == 200
            mock_dash.get_component_history.assert_called_once_with("comp_1", 50)


class TestGetMetrics:
    """Tests for GET /metrics endpoint."""

    def test_get_metrics_success(self):
        """Get metrics summary successfully."""
        metrics_summary = {
            "total_metrics": 10,
            "metrics": [
                {"name": "api_latency", "value": 50.0, "type": "gauge"},
            ],
        }

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_metrics_summary.return_value = metrics_summary
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/metrics")

            assert response.status_code == 200
            data = response.json()
            assert data["total_metrics"] == 10


class TestSetMetric:
    """Tests for POST /metrics endpoint."""

    def test_set_metric_success(self):
        """Set metric value successfully."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/metrics",
                json={
                    "name": "test_metric",
                    "value": 42.0,
                    "metric_type": "gauge",
                    "labels": {"env": "test"},
                    "unit": "ms",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["name"] == "test_metric"
            assert data["value"] == 42.0

    def test_set_metric_invalid_type(self):
        """Set metric with invalid type."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/metrics",
                json={
                    "name": "test_metric",
                    "value": 42.0,
                    "metric_type": "invalid_type",
                },
            )

            assert response.status_code == 400


class TestGetAlerts:
    """Tests for GET /alerts endpoint."""

    def test_get_alerts_all(self):
        """Get all active alerts."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alerts = [
            ActiveAlert("alert_1", "CPU High", AlertSeverity.WARNING, "CPU > 80%", "api", now),
            ActiveAlert("alert_2", "DB Down", AlertSeverity.CRITICAL, "DB unreachable", "db", now),
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.get_active.return_value = alerts
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/alerts")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert data["critical"] == 1
            assert data["warning"] == 1

    def test_get_alerts_filtered_by_severity(self):
        """Get alerts filtered by severity."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alerts = [
            ActiveAlert("alert_1", "Critical Issue", AlertSeverity.CRITICAL, "Issue", "api", now),
        ]

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.get_active.return_value = alerts
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/alerts?severity=critical")

            assert response.status_code == 200
            data = response.json()
            assert data["critical"] == 1

    def test_get_alerts_invalid_severity(self):
        """Get alerts with invalid severity."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/alerts?severity=invalid")

            assert response.status_code == 400


class TestFireAlert:
    """Tests for POST /alerts endpoint."""

    def test_fire_alert_success(self):
        """Fire alert successfully."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = ActiveAlert("alert_1", "Test Alert", AlertSeverity.WARNING, "Test", "api", now)

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.fire_alert.return_value = alert
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/alerts",
                json={
                    "name": "Test Alert",
                    "severity": "warning",
                    "message": "Test message",
                    "component": "api",
                    "metadata": {"key": "value"},
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Alert"

    def test_fire_alert_invalid_severity(self):
        """Fire alert with invalid severity."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/alerts",
                json={
                    "name": "Test",
                    "severity": "invalid",
                    "message": "Test",
                    "component": "api",
                },
            )

            assert response.status_code == 400


class TestAcknowledgeAlert:
    """Tests for POST /alerts/{alert_id}/acknowledge endpoint."""

    def test_acknowledge_alert_success(self):
        """Acknowledge alert successfully."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = ActiveAlert("alert_1", "Test", AlertSeverity.WARNING, "Test", "api", now)
        alert.acknowledged = True
        alert.acknowledged_by = "admin"

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.acknowledge.return_value = alert
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/alerts/alert_1/acknowledge",
                json={"acknowledged_by": "admin"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["acknowledged"] is True

    def test_acknowledge_alert_not_found(self):
        """Acknowledge alert that doesn't exist."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.acknowledge.return_value = None
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.post(
                "/api/v1/dashboard/alerts/nonexistent/acknowledge",
                json={"acknowledged_by": "admin"},
            )

            assert response.status_code == 404


class TestResolveAlert:
    """Tests for DELETE /alerts/{name}/{component} endpoint."""

    def test_resolve_alert_success(self):
        """Resolve alert successfully."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.resolve_alert.return_value = True
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.delete("/api/v1/dashboard/alerts/cpu_high/api")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["name"] == "cpu_high"
            assert data["component"] == "api"

    def test_resolve_alert_not_found(self):
        """Resolve alert that doesn't exist."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.alerts.resolve_alert.return_value = False
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.delete("/api/v1/dashboard/alerts/nonexistent/api")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False


class TestGetSLOs:
    """Tests for GET /slos endpoint."""

    def test_get_slos_success(self):
        """Get SLOs successfully."""
        mock_slo1 = MockSLO(slo_id="slo_1", in_violation=False)
        mock_slo2 = MockSLO(slo_id="slo_2", in_violation=True)
        mock_snapshot = MockSnapshot(
            overall_health=HealthStatus.HEALTHY,
            summary="Test",
            timestamp=datetime.now(timezone.utc),
            slos=[mock_slo1, mock_slo2],
        )

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_snapshot.return_value = mock_snapshot
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/slos")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert data["in_violation"] == 1


class TestGetDependencyImpacts:
    """Tests for GET /dependencies endpoint."""

    def test_get_dependency_impacts_success(self):
        """Get dependency impacts successfully."""
        impacts = {
            "comp_1": ["comp_2", "comp_3"],
            "comp_2": [],
        }

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.evaluate_health_dependencies.return_value = impacts
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/dependencies")

            assert response.status_code == 200
            data = response.json()
            assert data["unhealthy_components_count"] == 2
            assert "comp_1" in data["impacts"]

    def test_get_dependency_impacts_empty(self):
        """Get dependency impacts when no unhealthy components."""
        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.evaluate_health_dependencies.return_value = {}
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/dependencies")

            assert response.status_code == 200
            data = response.json()
            assert data["unhealthy_components_count"] == 0


class TestGetSummary:
    """Tests for GET /summary endpoint."""

    def test_get_summary_success(self):
        """Get executive summary successfully."""
        mock_snapshot = MockSnapshot(
            overall_health=HealthStatus.HEALTHY,
            summary="All systems operational",
            timestamp=datetime.now(timezone.utc),
            slos=[],
        )

        with patch("app.api.dashboard_routes.get_dashboard") as mock_dashboard:
            mock_dash = MagicMock()
            mock_dash.get_snapshot.return_value = mock_snapshot
            mock_dashboard.return_value = mock_dash

            client = _client()
            response = client.get("/api/v1/dashboard/summary")

            assert response.status_code == 200
            data = response.json()
            assert data["overall_health"] == "healthy"
            assert data["summary"] == "All systems operational"
            assert "timestamp" in data
