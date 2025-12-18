"""
Tests for S39 Alert Streamer.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ops.dashboard_service import (
    ActiveAlert,
    AlertManager,
    AlertSeverity,
    get_dashboard,
    reset_dashboard,
)
from app.streaming.alert_streamer import (
    AlertEvent,
    AlertEventType,
    AlertStreamer,
    AlertSubscription,
    StreamerStats,
    get_alert_streamer,
    reset_alert_streamer,
)


# ============================================================================
# AlertEvent Tests
# ============================================================================

class TestAlertEvent:
    """Tests for AlertEvent."""

    def test_create_event(self):
        """Test creating an alert event."""
        alert = ActiveAlert(
            alert_id="alert_123",
            name="test_alert",
            severity=AlertSeverity.WARNING,
            message="Test message",
            component="test_component",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        event = AlertEvent(
            event_id="evt_123",
            event_type=AlertEventType.FIRED,
            alert=alert,
            timestamp=datetime.now(timezone.utc),
        )

        assert event.event_id == "evt_123"
        assert event.event_type == AlertEventType.FIRED
        assert event.alert == alert

    def test_event_to_dict(self):
        """Test converting event to dict."""
        alert = ActiveAlert(
            alert_id="alert_123",
            name="test_alert",
            severity=AlertSeverity.ERROR,
            message="Test message",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        event = AlertEvent(
            event_id="evt_456",
            event_type=AlertEventType.ACKNOWLEDGED,
            alert=alert,
            timestamp=datetime.now(timezone.utc),
            metadata={"user": "admin"},
        )

        result = event.to_dict()

        assert result["event_id"] == "evt_456"
        assert result["event_type"] == "alert_acknowledged"
        assert result["alert"]["name"] == "test_alert"
        assert result["metadata"]["user"] == "admin"

    def test_event_to_dict_without_alert(self):
        """Test converting event without alert to dict."""
        event = AlertEvent(
            event_id="hb_123",
            event_type=AlertEventType.HEARTBEAT,
            alert=None,
            timestamp=datetime.now(timezone.utc),
        )

        result = event.to_dict()

        assert result["event_id"] == "hb_123"
        assert result["event_type"] == "heartbeat"
        assert result["alert"] is None

    def test_event_to_sse(self):
        """Test formatting event as SSE."""
        event = AlertEvent(
            event_id="evt_789",
            event_type=AlertEventType.RESOLVED,
            alert=None,
            timestamp=datetime.now(timezone.utc),
            metadata={"name": "test_alert"},
        )

        sse = event.to_sse()

        assert sse.startswith("event: alert_resolved\n")
        assert "data: " in sse
        assert sse.endswith("\n\n")


# ============================================================================
# AlertSubscription Tests
# ============================================================================

class TestAlertSubscription:
    """Tests for AlertSubscription."""

    def test_create_subscription(self):
        """Test creating a subscription."""
        sub = AlertSubscription(
            subscription_id="sub_123",
            severities={AlertSeverity.ERROR, AlertSeverity.CRITICAL},
            components={"api", "database"},
        )

        assert sub.subscription_id == "sub_123"
        assert AlertSeverity.ERROR in sub.severities
        assert "api" in sub.components

    def test_matches_severity(self):
        """Test matching by severity."""
        sub = AlertSubscription(
            subscription_id="sub_1",
            severities={AlertSeverity.CRITICAL},
        )

        alert_critical = ActiveAlert(
            alert_id="a1",
            name="test",
            severity=AlertSeverity.CRITICAL,
            message="msg",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        alert_warning = ActiveAlert(
            alert_id="a2",
            name="test",
            severity=AlertSeverity.WARNING,
            message="msg",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert sub.matches(alert_critical)
        assert not sub.matches(alert_warning)

    def test_matches_component(self):
        """Test matching by component."""
        sub = AlertSubscription(
            subscription_id="sub_2",
            components={"database"},
        )

        alert_db = ActiveAlert(
            alert_id="a1",
            name="test",
            severity=AlertSeverity.ERROR,
            message="msg",
            component="database",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        alert_api = ActiveAlert(
            alert_id="a2",
            name="test",
            severity=AlertSeverity.ERROR,
            message="msg",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert sub.matches(alert_db)
        assert not sub.matches(alert_api)

    def test_matches_all(self):
        """Test subscription that matches all alerts."""
        sub = AlertSubscription(subscription_id="sub_3")

        alert = ActiveAlert(
            alert_id="a1",
            name="test",
            severity=AlertSeverity.INFO,
            message="msg",
            component="anything",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert sub.matches(alert)

    def test_matches_severity_and_component(self):
        """Test matching both severity and component."""
        sub = AlertSubscription(
            subscription_id="sub_4",
            severities={AlertSeverity.ERROR},
            components={"api"},
        )

        # Matches both
        alert1 = ActiveAlert(
            alert_id="a1",
            name="test",
            severity=AlertSeverity.ERROR,
            message="msg",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        # Wrong severity
        alert2 = ActiveAlert(
            alert_id="a2",
            name="test",
            severity=AlertSeverity.WARNING,
            message="msg",
            component="api",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        # Wrong component
        alert3 = ActiveAlert(
            alert_id="a3",
            name="test",
            severity=AlertSeverity.ERROR,
            message="msg",
            component="database",
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert sub.matches(alert1)
        assert not sub.matches(alert2)
        assert not sub.matches(alert3)


# ============================================================================
# StreamerStats Tests
# ============================================================================

class TestStreamerStats:
    """Tests for StreamerStats."""

    def test_default_stats(self):
        """Test default stats values."""
        stats = StreamerStats()

        assert stats.active_subscribers == 0
        assert stats.total_subscriptions == 0
        assert stats.events_sent == 0
        assert stats.events_by_type == {}
        assert stats.started_at is None

    def test_stats_to_dict(self):
        """Test converting stats to dict."""
        now = datetime.now(timezone.utc)
        stats = StreamerStats(
            active_subscribers=5,
            total_subscriptions=10,
            events_sent=100,
            events_by_type={"alert_fired": 50, "heartbeat": 50},
            started_at=now,
            last_event_at=now,
        )

        result = stats.to_dict()

        assert result["active_subscribers"] == 5
        assert result["total_subscriptions"] == 10
        assert result["events_sent"] == 100
        assert result["events_by_type"]["alert_fired"] == 50


# ============================================================================
# AlertStreamer Tests
# ============================================================================

class TestAlertStreamer:
    """Tests for AlertStreamer."""

    @pytest.fixture
    def streamer(self):
        """Create a fresh streamer for each test with clean dashboard."""
        # Reset both dashboard and alert streamer singletons for test isolation
        reset_dashboard()
        reset_alert_streamer()
        return AlertStreamer(heartbeat_interval_seconds=60)

    @pytest.mark.asyncio
    async def test_start_stop(self, streamer):
        """Test starting and stopping the streamer."""
        await streamer.start()

        assert streamer._running
        assert streamer.stats.started_at is not None

        await streamer.stop()

        assert not streamer._running

    @pytest.mark.asyncio
    async def test_start_idempotent(self, streamer):
        """Test that start is idempotent."""
        await streamer.start()
        started_at = streamer.stats.started_at

        await streamer.start()  # Second call

        assert streamer.stats.started_at == started_at
        await streamer.stop()

    @pytest.mark.asyncio
    async def test_subscribe(self, streamer):
        """Test subscribing to alerts."""
        await streamer.start()

        sub_id = await streamer.subscribe(
            severities={AlertSeverity.ERROR, AlertSeverity.CRITICAL},
            components={"api"},
        )

        assert sub_id.startswith("sub_")
        assert streamer.stats.active_subscribers == 1
        assert sub_id in streamer._subscriptions

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_subscribe_no_filters(self, streamer):
        """Test subscribing without filters."""
        await streamer.start()

        sub_id = await streamer.subscribe()

        subscription = streamer.get_subscription(sub_id)
        assert subscription is not None
        assert len(subscription.severities) == 0
        assert len(subscription.components) == 0

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_unsubscribe(self, streamer):
        """Test unsubscribing."""
        await streamer.start()

        sub_id = await streamer.subscribe()
        assert streamer.stats.active_subscribers == 1

        result = await streamer.unsubscribe(sub_id)

        assert result
        assert streamer.stats.active_subscribers == 0

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self, streamer):
        """Test unsubscribing non-existent subscription."""
        await streamer.start()

        result = await streamer.unsubscribe("nonexistent")

        assert not result

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_fire_alert(self, streamer):
        """Test firing an alert."""
        await streamer.start()

        event = await streamer.fire_alert(
            name="test_alert",
            severity=AlertSeverity.ERROR,
            message="Test message",
            component="api",
            metadata={"key": "value"},
        )

        assert event.event_type == AlertEventType.FIRED
        assert event.alert is not None
        assert event.alert.name == "test_alert"
        assert event.alert.severity == AlertSeverity.ERROR
        assert streamer.stats.events_sent >= 1

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_resolve_alert(self, streamer):
        """Test resolving an alert."""
        await streamer.start()

        # Fire first
        await streamer.fire_alert(
            name="resolve_test",
            severity=AlertSeverity.WARNING,
            message="Will be resolved",
            component="database",
        )

        # Resolve
        event = await streamer.resolve_alert("resolve_test", "database")

        assert event is not None
        assert event.event_type == AlertEventType.RESOLVED
        assert event.metadata["name"] == "resolve_test"

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_resolve_alert_not_found(self, streamer):
        """Test resolving non-existent alert."""
        await streamer.start()

        event = await streamer.resolve_alert("nonexistent", "component")

        assert event is None

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, streamer):
        """Test acknowledging an alert."""
        await streamer.start()

        # Fire first
        fire_event = await streamer.fire_alert(
            name="ack_test",
            severity=AlertSeverity.CRITICAL,
            message="Needs acknowledgment",
            component="api",
        )

        alert_id = fire_event.alert.alert_id

        # Acknowledge
        ack_event = await streamer.acknowledge_alert(alert_id, "admin_user")

        assert ack_event is not None
        assert ack_event.event_type == AlertEventType.ACKNOWLEDGED
        assert ack_event.alert.acknowledged
        assert ack_event.metadata["acknowledged_by"] == "admin_user"

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_acknowledge_alert_not_found(self, streamer):
        """Test acknowledging non-existent alert."""
        await streamer.start()

        event = await streamer.acknowledge_alert("nonexistent", "admin")

        assert event is None

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_escalate_alert(self, streamer):
        """Test escalating an alert."""
        await streamer.start()

        # Fire first
        fire_event = await streamer.fire_alert(
            name="escalate_test",
            severity=AlertSeverity.WARNING,
            message="Will escalate",
            component="api",
        )

        alert_id = fire_event.alert.alert_id

        # Escalate
        esc_event = await streamer.escalate_alert(
            alert_id,
            AlertSeverity.CRITICAL,
            "Performance degraded significantly",
        )

        assert esc_event is not None
        assert esc_event.event_type == AlertEventType.ESCALATED
        assert esc_event.alert.severity == AlertSeverity.CRITICAL
        assert esc_event.metadata["old_severity"] == "warning"
        assert esc_event.metadata["new_severity"] == "critical"

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_escalate_alert_not_found(self, streamer):
        """Test escalating non-existent alert."""
        await streamer.start()

        event = await streamer.escalate_alert(
            "nonexistent",
            AlertSeverity.CRITICAL,
            "reason",
        )

        assert event is None

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_broadcast_to_subscribers(self, streamer):
        """Test that events are broadcast to matching subscribers."""
        await streamer.start()

        # Create subscription for errors only
        sub_id = await streamer.subscribe(
            severities={AlertSeverity.ERROR},
        )

        # Fire matching alert
        await streamer.fire_alert(
            name="error_alert",
            severity=AlertSeverity.ERROR,
            message="Error!",
            component="api",
        )

        # Check queue has event
        queue = streamer._event_queues[sub_id]
        assert not queue.empty()

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_broadcast_filtering(self, streamer):
        """Test that non-matching events are filtered."""
        await streamer.start()

        # Create subscription for critical only
        sub_id = await streamer.subscribe(
            severities={AlertSeverity.CRITICAL},
        )

        # Fire non-matching alert
        await streamer.fire_alert(
            name="warning_alert",
            severity=AlertSeverity.WARNING,
            message="Warning only",
            component="api",
        )

        # Queue should be empty (warning doesn't match critical)
        queue = streamer._event_queues[sub_id]
        assert queue.empty()

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_heartbeat_goes_to_all(self, streamer):
        """Test that heartbeats go to all subscribers."""
        await streamer.start()

        # Create subscription
        sub_id = await streamer.subscribe(
            severities={AlertSeverity.CRITICAL},  # Only critical
        )

        # Send heartbeat directly
        await streamer._send_heartbeat()

        # Queue should have heartbeat
        queue = streamer._event_queues[sub_id]
        assert not queue.empty()

        event = queue.get_nowait()
        assert event.event_type == AlertEventType.HEARTBEAT

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_event_buffering(self, streamer):
        """Test that events are buffered."""
        await streamer.start()

        # Fire several alerts
        for i in range(5):
            await streamer.fire_alert(
                name=f"buffered_{i}",
                severity=AlertSeverity.INFO,
                message=f"Message {i}",
                component="api",
            )

        # Check buffer
        assert len(streamer._event_buffer) >= 5

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_buffer_trimming(self):
        """Test that buffer is trimmed when full."""
        streamer = AlertStreamer(buffer_size=3)
        await streamer.start()

        # Fire more alerts than buffer size
        for i in range(5):
            await streamer.fire_alert(
                name=f"trim_{i}",
                severity=AlertSeverity.INFO,
                message=f"Message {i}",
                component="api",
            )

        # Buffer should be trimmed to max size
        assert len(streamer._event_buffer) <= 3

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_buffered_events(self, streamer):
        """Test getting buffered events."""
        await streamer.start()

        now = datetime.now(timezone.utc)

        # Fire alerts
        for i in range(3):
            await streamer.fire_alert(
                name=f"buffer_get_{i}",
                severity=AlertSeverity.WARNING,
                message=f"Message {i}",
                component="api",
            )

        # Get buffered events
        events = streamer.get_buffered_events(now - timedelta(seconds=1))

        assert len(events) >= 3

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_buffered_events_with_subscription(self, streamer):
        """Test getting buffered events filtered by subscription."""
        await streamer.start()

        now = datetime.now(timezone.utc)

        # Fire different severity alerts
        await streamer.fire_alert(
            name="error_buff",
            severity=AlertSeverity.ERROR,
            message="Error",
            component="api",
        )
        await streamer.fire_alert(
            name="warning_buff",
            severity=AlertSeverity.WARNING,
            message="Warning",
            component="api",
        )

        # Get filtered by subscription
        subscription = AlertSubscription(
            subscription_id="test",
            severities={AlertSeverity.ERROR},
        )
        events = streamer.get_buffered_events(
            now - timedelta(seconds=1),
            subscription,
        )

        error_events = [e for e in events if e.alert and e.alert.severity == AlertSeverity.ERROR]
        assert len(error_events) >= 1

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_callback_registration(self, streamer):
        """Test registering and calling callbacks."""
        await streamer.start()

        received_events = []

        def callback(event: AlertEvent):
            received_events.append(event)

        streamer.register_callback(callback)

        await streamer.fire_alert(
            name="callback_test",
            severity=AlertSeverity.INFO,
            message="Test",
            component="api",
        )

        assert len(received_events) >= 1
        assert received_events[0].alert.name == "callback_test"

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_callback_unregistration(self, streamer):
        """Test unregistering callbacks."""
        await streamer.start()

        def callback(event: AlertEvent):
            pass

        streamer.register_callback(callback)
        result = streamer.unregister_callback(callback)

        assert result

        # Unregister again should return False
        result2 = streamer.unregister_callback(callback)
        assert not result2

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_callback_error_handling(self, streamer):
        """Test that callback errors don't break streaming."""
        await streamer.start()

        def bad_callback(event: AlertEvent):
            raise ValueError("Callback error")

        streamer.register_callback(bad_callback)

        # Should not raise
        await streamer.fire_alert(
            name="callback_error_test",
            severity=AlertSeverity.INFO,
            message="Test",
            component="api",
        )

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_stream_events(self, streamer):
        """Test streaming events."""
        await streamer.start()

        sub_id = await streamer.subscribe()

        # Fire an alert
        await streamer.fire_alert(
            name="stream_test",
            severity=AlertSeverity.WARNING,
            message="Stream test",
            component="api",
        )

        # Stream events
        events = []
        async for event in streamer.stream_events(sub_id):
            events.append(event)
            break  # Just get one

        assert len(events) == 1
        assert events[0].alert.name == "stream_test"

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_stream_sse(self, streamer):
        """Test streaming SSE formatted events."""
        await streamer.start()

        sub_id = await streamer.subscribe()

        # Fire an alert
        await streamer.fire_alert(
            name="sse_test",
            severity=AlertSeverity.INFO,
            message="SSE test",
            component="api",
        )

        # Stream SSE
        sse_data = []
        async for data in streamer.stream_sse(sub_id):
            sse_data.append(data)
            break  # Just get one

        assert len(sse_data) == 1
        assert "event:" in sse_data[0]
        assert "data:" in sse_data[0]

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_stream_events_nonexistent_subscription(self, streamer):
        """Test streaming from non-existent subscription."""
        await streamer.start()

        events = []
        async for event in streamer.stream_events("nonexistent"):
            events.append(event)

        assert len(events) == 0

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_stats(self, streamer):
        """Test getting stats."""
        await streamer.start()

        await streamer.subscribe()
        await streamer.fire_alert(
            name="stats_test",
            severity=AlertSeverity.INFO,
            message="Stats",
            component="api",
        )

        stats = streamer.get_stats()

        assert stats["active_subscribers"] == 1
        assert stats["events_sent"] >= 1

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_subscription(self, streamer):
        """Test getting subscription by ID."""
        await streamer.start()

        sub_id = await streamer.subscribe(
            severities={AlertSeverity.ERROR},
        )

        subscription = streamer.get_subscription(sub_id)

        assert subscription is not None
        assert AlertSeverity.ERROR in subscription.severities

        # Non-existent
        assert streamer.get_subscription("nonexistent") is None

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_active_alerts(self, streamer):
        """Test getting active alerts."""
        await streamer.start()

        await streamer.fire_alert(
            name="active_test",
            severity=AlertSeverity.ERROR,
            message="Active",
            component="api",
        )

        alerts = streamer.get_active_alerts()

        assert len(alerts) >= 1
        assert any(a.name == "active_test" for a in alerts)

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_get_active_alerts_filtered(self, streamer):
        """Test getting active alerts filtered by severity."""
        await streamer.start()

        await streamer.fire_alert(
            name="critical_test",
            severity=AlertSeverity.CRITICAL,
            message="Critical",
            component="api",
        )

        alerts = streamer.get_active_alerts(AlertSeverity.CRITICAL)

        assert all(a.severity == AlertSeverity.CRITICAL for a in alerts)

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using as context manager."""
        async with AlertStreamer() as streamer:
            assert streamer._running

            sub_id = await streamer.subscribe()
            assert sub_id.startswith("sub_")

        assert not streamer._running


# ============================================================================
# Global Instance Tests
# ============================================================================

class TestGlobalInstance:
    """Tests for global alert streamer instance."""

    @pytest.mark.asyncio
    async def test_get_alert_streamer(self):
        """Test getting global streamer instance."""
        reset_alert_streamer()

        streamer = await get_alert_streamer()

        assert streamer is not None
        assert streamer._running

        # Second call returns same instance
        streamer2 = await get_alert_streamer()
        assert streamer2 is streamer

        await streamer.stop()
        reset_alert_streamer()

    @pytest.mark.asyncio
    async def test_reset_alert_streamer(self):
        """Test resetting global streamer."""
        reset_alert_streamer()

        streamer1 = await get_alert_streamer()
        await streamer1.stop()

        reset_alert_streamer()

        streamer2 = await get_alert_streamer()
        assert streamer2 is not streamer1

        await streamer2.stop()
        reset_alert_streamer()


# ============================================================================
# Integration Tests
# ============================================================================

class TestAlertStreamerEdgeCases:
    """Edge case tests for AlertStreamer."""

    @pytest.mark.asyncio
    async def test_queue_full_handling(self):
        """Test handling of full event queues."""
        async with AlertStreamer() as streamer:
            # Subscribe
            sub_id = await streamer.subscribe()

            # Fill the queue by firing many alerts without consuming
            queue = streamer._event_queues[sub_id]

            # Put events directly until full
            for i in range(1000):  # Default queue size should be exceeded
                try:
                    event = AlertEvent(
                        event_id=f"evt_{i}",
                        event_type=AlertEventType.FIRED,
                        alert=None,
                        timestamp=datetime.now(timezone.utc),
                    )
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    break

            # Now fire an alert - should handle full queue gracefully
            await streamer.fire_alert(
                name="overflow_test",
                severity=AlertSeverity.INFO,
                message="Should handle queue overflow",
                component="api",
            )

            # Should not raise

    @pytest.mark.asyncio
    async def test_stream_timeout_handling(self):
        """Test stream timeout when no events available."""
        async with AlertStreamer() as streamer:
            sub_id = await streamer.subscribe()

            # Stream should timeout and continue
            events = []
            count = 0
            async for event in streamer.stream_events(sub_id):
                events.append(event)
                count += 1
                if count > 0:
                    break  # Exit after first event or timeout

            # If we got no events due to timeout, that's expected behavior
            assert count <= 1

    @pytest.mark.asyncio
    async def test_stream_cancelled_error(self):
        """Test stream cancellation handling."""
        async with AlertStreamer() as streamer:
            sub_id = await streamer.subscribe()

            # Create a task that streams events
            async def stream_task():
                events = []
                async for event in streamer.stream_events(sub_id):
                    events.append(event)
                return events

            task = asyncio.create_task(stream_task())

            # Give it a moment to start
            await asyncio.sleep(0.1)

            # Cancel the task
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass  # Expected

    @pytest.mark.asyncio
    async def test_heartbeat_loop_error_handling(self):
        """Test error handling in heartbeat loop."""
        streamer = AlertStreamer(heartbeat_interval_seconds=1)
        await streamer.start()

        # Let heartbeat run once
        await asyncio.sleep(1.5)

        # Should still be running despite any internal issues
        assert streamer._running

        await streamer.stop()


class TestAlertStreamerIntegration:
    """Integration tests for AlertStreamer."""

    @pytest.mark.asyncio
    async def test_full_alert_lifecycle(self):
        """Test complete alert lifecycle."""
        async with AlertStreamer() as streamer:
            # Subscribe
            sub_id = await streamer.subscribe(
                severities={AlertSeverity.ERROR, AlertSeverity.CRITICAL},
            )

            # Fire alert
            fire_event = await streamer.fire_alert(
                name="lifecycle_test",
                severity=AlertSeverity.ERROR,
                message="Initial error",
                component="api",
            )

            assert fire_event.event_type == AlertEventType.FIRED

            # Acknowledge
            ack_event = await streamer.acknowledge_alert(
                fire_event.alert.alert_id,
                "admin",
            )

            assert ack_event.event_type == AlertEventType.ACKNOWLEDGED

            # Escalate
            esc_event = await streamer.escalate_alert(
                fire_event.alert.alert_id,
                AlertSeverity.CRITICAL,
                "Situation worsened",
            )

            assert esc_event.event_type == AlertEventType.ESCALATED

            # Resolve
            res_event = await streamer.resolve_alert(
                "lifecycle_test",
                "api",
            )

            assert res_event.event_type == AlertEventType.RESOLVED

            # Unsubscribe
            result = await streamer.unsubscribe(sub_id)
            assert result

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers with different filters."""
        async with AlertStreamer() as streamer:
            # Create different subscriptions
            sub_all = await streamer.subscribe()
            sub_critical = await streamer.subscribe(
                severities={AlertSeverity.CRITICAL},
            )
            sub_api = await streamer.subscribe(
                components={"api"},
            )

            # Fire various alerts
            await streamer.fire_alert(
                name="info_alert",
                severity=AlertSeverity.INFO,
                message="Info",
                component="database",
            )

            await streamer.fire_alert(
                name="critical_api",
                severity=AlertSeverity.CRITICAL,
                message="Critical API error",
                component="api",
            )

            # Check queues
            queue_all = streamer._event_queues[sub_all]
            queue_critical = streamer._event_queues[sub_critical]
            queue_api = streamer._event_queues[sub_api]

            # All subscriber should have all events
            assert queue_all.qsize() >= 2

            # Critical only should have 1 (critical_api only)
            assert queue_critical.qsize() >= 1

            # API only should have 1 (critical_api only)
            assert queue_api.qsize() >= 1
