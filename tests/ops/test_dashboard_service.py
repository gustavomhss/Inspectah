"""
S38: Tests for Ops Dashboard Service
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.ops.dashboard_service import (
    HealthStatus,
    AlertSeverity,
    MetricType,
    ComponentHealth,
    ActiveAlert,
    MetricValue,
    SLOStatus,
    DashboardSnapshot,
    HealthChecker,
    AlertManager,
    MetricsCollector,
    OpsDashboardService,
    get_dashboard,
    reset_dashboard,
)


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestAlertSeverity:
    """Tests for AlertSeverity enum."""

    def test_alert_severity_values(self):
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestMetricType:
    """Tests for MetricType enum."""

    def test_metric_type_values(self):
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"


class TestComponentHealth:
    """Tests for ComponentHealth dataclass."""

    def test_create_healthy_component(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        health = ComponentHealth(
            component_id="db",
            name="Database",
            status=HealthStatus.HEALTHY,
            last_check=now,
            latency_ms=5.0,
        )

        assert health.component_id == "db"
        assert health.status == HealthStatus.HEALTHY
        assert health.latency_ms == 5.0

    def test_component_to_dict(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        health = ComponentHealth(
            component_id="cache",
            name="Redis Cache",
            status=HealthStatus.DEGRADED,
            last_check=now,
            latency_ms=150.0,
            details={"connections": 10},
        )

        result = health.to_dict()
        assert result["component_id"] == "cache"
        assert result["status"] == "degraded"
        assert result["latency_ms"] == 150.0
        assert result["details"]["connections"] == 10


class TestActiveAlert:
    """Tests for ActiveAlert dataclass."""

    def test_create_alert(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = ActiveAlert(
            alert_id="alert_001",
            name="HighLatency",
            severity=AlertSeverity.WARNING,
            message="Database latency above threshold",
            component="database",
            started_at=now,
        )

        assert alert.alert_id == "alert_001"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.acknowledged is False

    def test_alert_to_dict(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = ActiveAlert(
            alert_id="alert_002",
            name="ServiceDown",
            severity=AlertSeverity.CRITICAL,
            message="Service unavailable",
            component="api",
            started_at=now,
        )

        result = alert.to_dict()
        assert result["severity"] == "critical"
        assert result["acknowledged"] is False
        assert "duration_minutes" in result


class TestMetricValue:
    """Tests for MetricValue dataclass."""

    def test_create_metric(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        metric = MetricValue(
            name="request_count",
            metric_type=MetricType.COUNTER,
            value=100.0,
            timestamp=now,
            unit="requests",
        )

        assert metric.name == "request_count"
        assert metric.value == 100.0
        assert metric.unit == "requests"

    def test_metric_to_dict(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        metric = MetricValue(
            name="latency",
            metric_type=MetricType.GAUGE,
            value=45.5,
            timestamp=now,
            labels={"endpoint": "/api/health"},
            unit="ms",
        )

        result = metric.to_dict()
        assert result["name"] == "latency"
        assert result["type"] == "gauge"
        assert result["value"] == 45.5
        assert result["unit"] == "ms"


class TestSLOStatus:
    """Tests for SLOStatus dataclass."""

    def test_create_slo(self):
        slo = SLOStatus(
            slo_id="slo_001",
            name="API Availability",
            target=99.9,
            current=99.5,
            budget_remaining=0.4,
            period_days=30,
            in_violation=True,
        )

        assert slo.slo_id == "slo_001"
        assert slo.in_violation is True

    def test_slo_to_dict(self):
        slo = SLOStatus(
            slo_id="slo_002",
            name="Latency P99",
            target=95.0,
            current=98.0,
            budget_remaining=3.0,
            period_days=7,
            in_violation=False,
        )

        result = slo.to_dict()
        assert result["target"] == 95.0
        assert result["in_violation"] is False


class TestHealthChecker:
    """Tests for HealthChecker."""

    @pytest.fixture
    def checker(self):
        return HealthChecker()

    def test_register_and_check(self, checker):
        def my_check():
            return {"status": "healthy", "details": {"test": True}}

        checker.register("test", "Test Component", my_check)
        result = checker.check_one("test")

        assert result is not None
        assert result.status == HealthStatus.HEALTHY

    def test_check_one_not_found(self, checker):
        result = checker.check_one("nonexistent")
        assert result is None

    def test_check_all(self, checker):
        def check_db():
            return {"status": "healthy", "details": {}}

        def check_cache():
            return {"status": "degraded", "details": {}}

        checker.register("db", "Database", check_db)
        checker.register("cache", "Cache", check_cache)

        results = checker.check_all()
        assert len(results) == 2

    def test_check_with_error(self, checker):
        def failing_check():
            raise Exception("Connection failed")

        checker.register("failing", "Failing Service", failing_check)
        result = checker.check_one("failing")

        assert result is not None
        assert result.status == HealthStatus.UNHEALTHY
        assert "error" in result.details


class TestAlertManager:
    """Tests for AlertManager."""

    @pytest.fixture
    def manager(self):
        return AlertManager()

    def test_fire_alert(self, manager):
        alert = manager.fire_alert(
            name="TestAlert",
            severity=AlertSeverity.WARNING,
            message="Test message",
            component="test",
        )

        assert alert is not None
        assert alert.name == "TestAlert"
        assert alert.severity == AlertSeverity.WARNING

    def test_fire_duplicate_alert_returns_existing(self, manager):
        alert1 = manager.fire_alert(
            name="SameAlert",
            severity=AlertSeverity.WARNING,
            message="First",
            component="test",
        )
        alert2 = manager.fire_alert(
            name="SameAlert",
            severity=AlertSeverity.CRITICAL,
            message="Second",
            component="test",
        )

        assert alert1.alert_id == alert2.alert_id

    def test_get_active_alerts(self, manager):
        manager.fire_alert(
            name="Alert1",
            severity=AlertSeverity.WARNING,
            message="Warning",
            component="test",
        )
        manager.fire_alert(
            name="Alert2",
            severity=AlertSeverity.CRITICAL,
            message="Critical",
            component="test",
        )

        active = manager.get_active()
        assert len(active) == 2

    def test_get_active_by_severity(self, manager):
        manager.fire_alert(
            name="Warning1",
            severity=AlertSeverity.WARNING,
            message="Warning",
            component="test",
        )
        manager.fire_alert(
            name="Critical1",
            severity=AlertSeverity.CRITICAL,
            message="Critical",
            component="test2",
        )

        warnings = manager.get_active(AlertSeverity.WARNING)
        assert len(warnings) == 1
        assert warnings[0].severity == AlertSeverity.WARNING

    def test_acknowledge_alert(self, manager):
        alert = manager.fire_alert(
            name="ToAck",
            severity=AlertSeverity.ERROR,
            message="Error",
            component="test",
        )

        result = manager.acknowledge(alert.alert_id, "admin")
        assert result is not None
        assert result.acknowledged is True
        assert result.acknowledged_by == "admin"

    def test_resolve_alert(self, manager):
        manager.fire_alert(
            name="ToResolve",
            severity=AlertSeverity.WARNING,
            message="Warning",
            component="test_component",
        )

        resolved = manager.resolve_alert("ToResolve", "test_component")
        assert resolved is True

        active = manager.get_active()
        assert len(active) == 0

    def test_resolve_nonexistent_alert(self, manager):
        resolved = manager.resolve_alert("NonExistent", "test")
        assert resolved is False


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    @pytest.fixture
    def collector(self):
        return MetricsCollector()

    def test_set_metric(self, collector):
        collector.set_metric(
            name="request_count",
            value=100.0,
            metric_type=MetricType.COUNTER,
        )

        metrics = collector.collect_all()
        assert len(metrics) == 1
        assert metrics[0].name == "request_count"

    def test_set_metric_with_labels(self, collector):
        collector.set_metric(
            name="latency",
            value=45.5,
            metric_type=MetricType.GAUGE,
            labels={"endpoint": "/api/health"},
            unit="ms",
        )

        metrics = collector.collect_all()
        assert len(metrics) == 1
        assert metrics[0].labels["endpoint"] == "/api/health"

    def test_register_collector(self, collector):
        def custom_collector():
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            return [
                MetricValue(
                    name="custom",
                    metric_type=MetricType.GAUGE,
                    value=42.0,
                    timestamp=now,
                )
            ]

        collector.register_collector(custom_collector)
        metrics = collector.collect_all()
        assert any(m.name == "custom" for m in metrics)


class TestOpsDashboardService:
    """Tests for OpsDashboardService."""

    @pytest.fixture
    def dashboard(self):
        return OpsDashboardService()

    def test_get_snapshot(self, dashboard):
        snapshot = dashboard.get_snapshot()

        assert isinstance(snapshot, DashboardSnapshot)
        assert snapshot.overall_health is not None
        assert isinstance(snapshot.components, list)
        assert isinstance(snapshot.alerts, list)

    def test_get_metrics_summary(self, dashboard):
        dashboard.metrics.set_metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
        )

        summary = dashboard.get_metrics_summary()
        assert "total_metrics" in summary
        assert "by_type" in summary

    def test_get_component_history(self, dashboard):
        dashboard.get_snapshot()
        history = dashboard.get_component_history("api", limit=10)
        assert isinstance(history, list)

    def test_register_slo(self, dashboard):
        dashboard.register_slo(
            slo_id="test_slo",
            name="Test SLO",
            target=99.0,
            calculator=lambda: 99.5,
            period_days=7,
        )

        snapshot = dashboard.get_snapshot()
        assert len(snapshot.slos) >= 1

    def test_evaluate_health_dependencies(self, dashboard):
        dashboard.health.register(
            "service_a",
            "Service A",
            lambda: {"status": "unhealthy"},
            dependencies=[],
        )
        dashboard.health.register(
            "service_b",
            "Service B",
            lambda: {"status": "healthy"},
            dependencies=["service_a"],
        )

        impacts = dashboard.evaluate_health_dependencies()
        assert isinstance(impacts, dict)


class TestGetDashboard:
    """Tests for singleton dashboard getter."""

    def test_get_dashboard_returns_instance(self):
        dashboard = get_dashboard()
        assert isinstance(dashboard, OpsDashboardService)

    def test_get_dashboard_returns_same_instance(self):
        dashboard1 = get_dashboard()
        dashboard2 = get_dashboard()
        assert dashboard1 is dashboard2

    def test_reset_dashboard_creates_new_instance(self):
        """Test that reset_dashboard creates a new instance."""
        dashboard1 = get_dashboard()
        reset_dashboard()
        dashboard2 = get_dashboard()
        assert dashboard1 is not dashboard2

    def test_reset_dashboard_clears_state(self):
        """Test that reset_dashboard clears all state."""
        dashboard = get_dashboard()
        # Fire an alert
        dashboard.alerts.fire_alert(
            name="test",
            severity=AlertSeverity.WARNING,
            message="Test alert",
            component="test",
        )
        assert len(dashboard.alerts.get_active()) > 0

        reset_dashboard()
        new_dashboard = get_dashboard()
        assert len(new_dashboard.alerts.get_active()) == 0
