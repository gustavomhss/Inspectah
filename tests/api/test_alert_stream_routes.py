"""
Tests for S39 Alert Stream API Routes.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api.alert_stream_routes import router
from app.ops.dashboard_service import (
    ActiveAlert,
    AlertSeverity,
)
from app.streaming.alert_streamer import (
    AlertEvent,
    AlertEventType,
    AlertStreamer,
    AlertSubscription,
    StreamerStats,
    reset_alert_streamer,
)


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_streamer():
    """Create mock alert streamer."""
    streamer = MagicMock(spec=AlertStreamer)
    streamer.stats = StreamerStats(
        active_subscribers=5,
        total_subscriptions=10,
        events_sent=100,
        started_at=datetime.now(timezone.utc),
    )
    return streamer


@pytest.fixture(autouse=True)
def reset_global_streamer():
    """Reset global streamer before each test."""
    reset_alert_streamer()
    yield
    reset_alert_streamer()


# ============================================================================
# Subscribe Tests
# ============================================================================

class TestSubscribeEndpoint:
    """Tests for subscription endpoint."""

    @pytest.mark.asyncio
    async def test_subscribe_success(self, client):
        """Test successful subscription."""
        response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={
                "severities": ["error", "critical"],
                "components": ["api", "database"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "subscription_id" in data
        assert data["subscription_id"].startswith("sub_")
        assert "stream_url" in data
        assert "error" in data["severities"]
        assert "api" in data["components"]

    @pytest.mark.asyncio
    async def test_subscribe_no_filters(self, client):
        """Test subscription without filters."""
        response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["severities"] == []
        assert data["components"] == []

    @pytest.mark.asyncio
    async def test_subscribe_invalid_severity(self, client):
        """Test subscription with invalid severity."""
        response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={
                "severities": ["invalid_severity"],
            },
        )

        assert response.status_code == 400
        assert "Invalid severity" in response.json()["detail"]


# ============================================================================
# Unsubscribe Tests
# ============================================================================

class TestUnsubscribeEndpoint:
    """Tests for unsubscribe endpoint."""

    @pytest.mark.asyncio
    async def test_unsubscribe_success(self, client):
        """Test successful unsubscription."""
        # First subscribe
        sub_response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={},
        )
        sub_id = sub_response.json()["subscription_id"]

        # Then unsubscribe
        response = client.delete(f"/api/v1/alerts/stream/subscribe/{sub_id}")

        assert response.status_code == 200
        assert response.json()["success"]

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self, client):
        """Test unsubscribe with non-existent ID."""
        response = client.delete("/api/v1/alerts/stream/subscribe/nonexistent")

        assert response.status_code == 404


# ============================================================================
# Fire Alert Tests
# ============================================================================

class TestFireAlertEndpoint:
    """Tests for fire alert endpoint."""

    @pytest.mark.asyncio
    async def test_fire_alert_success(self, client):
        """Test firing an alert."""
        response = client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "test_alert",
                "severity": "error",
                "message": "Test error message",
                "component": "api",
                "metadata": {"key": "value"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        assert "event" in data
        assert data["event"]["event_type"] == "alert_fired"

    @pytest.mark.asyncio
    async def test_fire_alert_invalid_severity(self, client):
        """Test firing alert with invalid severity."""
        response = client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "test",
                "severity": "invalid",
                "message": "Test",
                "component": "api",
            },
        )

        assert response.status_code == 400


# ============================================================================
# Acknowledge Alert Tests
# ============================================================================

class TestAcknowledgeEndpoint:
    """Tests for acknowledge endpoint."""

    @pytest.mark.asyncio
    async def test_acknowledge_success(self, client):
        """Test acknowledging an alert."""
        # First fire an alert
        fire_response = client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "ack_test",
                "severity": "warning",
                "message": "Will acknowledge",
                "component": "api",
            },
        )
        alert_id = fire_response.json()["event"]["alert"]["alert_id"]

        # Acknowledge
        response = client.post(
            f"/api/v1/alerts/stream/{alert_id}/acknowledge",
            json={"acknowledged_by": "admin"},
        )

        assert response.status_code == 200
        assert response.json()["success"]
        assert response.json()["event"]["event_type"] == "alert_acknowledged"

    @pytest.mark.asyncio
    async def test_acknowledge_not_found(self, client):
        """Test acknowledging non-existent alert."""
        response = client.post(
            "/api/v1/alerts/stream/nonexistent/acknowledge",
            json={"acknowledged_by": "admin"},
        )

        assert response.status_code == 404


# ============================================================================
# Escalate Alert Tests
# ============================================================================

class TestEscalateEndpoint:
    """Tests for escalate endpoint."""

    @pytest.mark.asyncio
    async def test_escalate_success(self, client):
        """Test escalating an alert."""
        # First fire an alert
        fire_response = client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "escalate_test",
                "severity": "warning",
                "message": "Will escalate",
                "component": "api",
            },
        )
        alert_id = fire_response.json()["event"]["alert"]["alert_id"]

        # Escalate
        response = client.post(
            f"/api/v1/alerts/stream/{alert_id}/escalate",
            json={
                "new_severity": "critical",
                "reason": "Getting worse",
            },
        )

        assert response.status_code == 200
        assert response.json()["success"]
        assert response.json()["event"]["event_type"] == "alert_escalated"

    @pytest.mark.asyncio
    async def test_escalate_invalid_severity(self, client):
        """Test escalating with invalid severity."""
        response = client.post(
            "/api/v1/alerts/stream/some_id/escalate",
            json={
                "new_severity": "invalid",
                "reason": "Test",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_escalate_not_found(self, client):
        """Test escalating non-existent alert."""
        response = client.post(
            "/api/v1/alerts/stream/nonexistent/escalate",
            json={
                "new_severity": "critical",
                "reason": "Test",
            },
        )

        assert response.status_code == 404


# ============================================================================
# Resolve Alert Tests
# ============================================================================

class TestResolveEndpoint:
    """Tests for resolve endpoint."""

    @pytest.mark.asyncio
    async def test_resolve_success(self, client):
        """Test resolving an alert."""
        # First fire an alert
        client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "resolve_test",
                "severity": "error",
                "message": "Will resolve",
                "component": "database",
            },
        )

        # Resolve
        response = client.delete("/api/v1/alerts/stream/resolve_test/database")

        assert response.status_code == 200
        assert response.json()["success"]
        assert response.json()["event"]["event_type"] == "alert_resolved"

    @pytest.mark.asyncio
    async def test_resolve_not_found(self, client):
        """Test resolving non-existent alert."""
        response = client.delete("/api/v1/alerts/stream/nonexistent/component")

        assert response.status_code == 200
        assert not response.json()["success"]
        assert response.json()["event"] is None


# ============================================================================
# Stats Tests
# ============================================================================

class TestStatsEndpoint:
    """Tests for stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_stats(self, client):
        """Test getting streaming stats."""
        response = client.get("/api/v1/alerts/stream/stats")

        assert response.status_code == 200
        data = response.json()
        assert "active_subscribers" in data
        assert "events_sent" in data


# ============================================================================
# Active Alerts Tests
# ============================================================================

class TestActiveAlertsEndpoint:
    """Tests for active alerts endpoint."""

    @pytest.mark.asyncio
    async def test_get_active_alerts(self, client):
        """Test getting active alerts."""
        # Fire some alerts
        client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "active1",
                "severity": "warning",
                "message": "Active 1",
                "component": "api",
            },
        )

        response = client.get("/api/v1/alerts/stream/active")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_active_alerts_filtered(self, client):
        """Test getting active alerts filtered by severity."""
        # Fire alerts
        client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "critical1",
                "severity": "critical",
                "message": "Critical",
                "component": "api",
            },
        )

        response = client.get("/api/v1/alerts/stream/active?severity=critical")

        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_get_active_alerts_invalid_severity(self, client):
        """Test getting alerts with invalid severity filter."""
        response = client.get("/api/v1/alerts/stream/active?severity=invalid")

        assert response.status_code == 400


# ============================================================================
# Buffer Tests
# ============================================================================

class TestBufferEndpoint:
    """Tests for buffer endpoint."""

    @pytest.mark.asyncio
    async def test_get_buffered_events(self, client):
        """Test getting buffered events."""
        # Fire some alerts
        client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "buffered1",
                "severity": "info",
                "message": "Buffer test",
                "component": "api",
            },
        )

        response = client.get("/api/v1/alerts/stream/buffer")

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert "since" in data

    @pytest.mark.asyncio
    async def test_get_buffered_events_with_timestamp(self, client):
        """Test getting buffered events since timestamp."""
        now = datetime.now(timezone.utc).isoformat()

        response = client.get(f"/api/v1/alerts/stream/buffer?since={now}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_buffered_events_invalid_timestamp(self, client):
        """Test getting buffered events with invalid timestamp."""
        response = client.get("/api/v1/alerts/stream/buffer?since=invalid")

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_buffered_events_with_subscription(self, client):
        """Test getting buffered events filtered by subscription."""
        # Subscribe first
        sub_response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={"severities": ["error"]},
        )
        sub_id = sub_response.json()["subscription_id"]

        response = client.get(f"/api/v1/alerts/stream/buffer?subscription_id={sub_id}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_buffered_events_nonexistent_subscription(self, client):
        """Test getting buffered events with non-existent subscription."""
        response = client.get("/api/v1/alerts/stream/buffer?subscription_id=nonexistent")

        assert response.status_code == 404


# ============================================================================
# SSE Endpoint Tests
# ============================================================================

class TestSSEEndpoint:
    """Tests for SSE streaming endpoint."""

    @pytest.mark.asyncio
    async def test_sse_endpoint_not_found(self, client):
        """Test SSE endpoint with non-existent subscription."""
        response = client.get("/api/v1/alerts/stream/sse/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_sse_subscription_url_format(self, client):
        """Test that subscription returns correct SSE URL format."""
        # Subscribe and verify the stream URL format
        sub_response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={},
        )

        assert sub_response.status_code == 200
        data = sub_response.json()

        # Verify the stream URL is properly formatted
        assert "stream_url" in data
        assert data["stream_url"].startswith("/api/v1/alerts/stream/sse/")
        assert data["subscription_id"] in data["stream_url"]


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint."""

    def test_websocket_nonexistent_subscription(self, client):
        """Test WebSocket with non-existent subscription."""
        # WebSocket connections to nonexistent subscriptions should close
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/alerts/stream/ws/nonexistent"):
                pass  # Should raise before getting here


# ============================================================================
# Integration Tests
# ============================================================================

class TestAlertStreamIntegration:
    """Integration tests for alert streaming."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test complete alert streaming workflow."""
        # 1. Subscribe
        sub_response = client.post(
            "/api/v1/alerts/stream/subscribe",
            json={"severities": ["error", "critical"]},
        )
        assert sub_response.status_code == 200
        sub_id = sub_response.json()["subscription_id"]

        # 2. Fire alert
        fire_response = client.post(
            "/api/v1/alerts/stream/fire",
            json={
                "name": "workflow_alert",
                "severity": "error",
                "message": "Workflow test",
                "component": "api",
            },
        )
        assert fire_response.status_code == 200
        alert_id = fire_response.json()["event"]["alert"]["alert_id"]

        # 3. Acknowledge
        ack_response = client.post(
            f"/api/v1/alerts/stream/{alert_id}/acknowledge",
            json={"acknowledged_by": "ops_team"},
        )
        assert ack_response.status_code == 200

        # 4. Escalate
        esc_response = client.post(
            f"/api/v1/alerts/stream/{alert_id}/escalate",
            json={
                "new_severity": "critical",
                "reason": "Impact growing",
            },
        )
        assert esc_response.status_code == 200

        # 5. Check stats
        stats_response = client.get("/api/v1/alerts/stream/stats")
        assert stats_response.status_code == 200
        assert stats_response.json()["events_sent"] >= 3

        # 6. Resolve
        resolve_response = client.delete("/api/v1/alerts/stream/workflow_alert/api")
        assert resolve_response.status_code == 200
        assert resolve_response.json()["success"]

        # 7. Unsubscribe
        unsub_response = client.delete(f"/api/v1/alerts/stream/subscribe/{sub_id}")
        assert unsub_response.status_code == 200

    @pytest.mark.asyncio
    async def test_multiple_subscribers_workflow(self, client):
        """Test workflow with multiple subscribers."""
        # Create multiple subscriptions
        subs = []
        for i in range(3):
            response = client.post(
                "/api/v1/alerts/stream/subscribe",
                json={},
            )
            subs.append(response.json()["subscription_id"])

        # Fire alerts
        for i in range(2):
            client.post(
                "/api/v1/alerts/stream/fire",
                json={
                    "name": f"multi_alert_{i}",
                    "severity": "warning",
                    "message": f"Multi test {i}",
                    "component": "api",
                },
            )

        # Check stats
        stats = client.get("/api/v1/alerts/stream/stats").json()
        assert stats["active_subscribers"] == 3

        # Unsubscribe all
        for sub_id in subs:
            client.delete(f"/api/v1/alerts/stream/subscribe/{sub_id}")

        stats_after = client.get("/api/v1/alerts/stream/stats").json()
        assert stats_after["active_subscribers"] == 0
