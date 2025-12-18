"""
S39 - Alert Streamer

Real-time alert streaming via SSE and WebSocket.
Integrates with OpsDashboardService for alert notifications.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set
from uuid import uuid4

from app.ops.dashboard_service import (
    ActiveAlert,
    AlertManager,
    AlertSeverity,
    get_dashboard,
)

logger = logging.getLogger(__name__)


class AlertEventType(str, Enum):
    """Types of alert events."""
    FIRED = "alert_fired"
    RESOLVED = "alert_resolved"
    ACKNOWLEDGED = "alert_acknowledged"
    ESCALATED = "alert_escalated"
    HEARTBEAT = "heartbeat"


@dataclass
class AlertEvent:
    """Represents an alert event for streaming."""
    event_id: str
    event_type: AlertEventType
    alert: Optional[ActiveAlert]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "alert": self.alert.to_dict() if self.alert else None,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def to_sse(self) -> str:
        """Format as SSE event."""
        data = json.dumps(self.to_dict())
        return f"event: {self.event_type.value}\ndata: {data}\n\n"


@dataclass
class AlertSubscription:
    """Client subscription to alert events."""
    subscription_id: str
    severities: Set[AlertSeverity] = field(default_factory=lambda: set(AlertSeverity))
    components: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def matches(self, alert: ActiveAlert) -> bool:
        """Check if alert matches this subscription."""
        # If no severities specified, match all
        if self.severities and alert.severity not in self.severities:
            return False
        # If components specified, must match
        if self.components and alert.component not in self.components:
            return False
        return True


@dataclass
class StreamerStats:
    """Alert streamer statistics."""
    active_subscribers: int = 0
    total_subscriptions: int = 0
    events_sent: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    last_event_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "active_subscribers": self.active_subscribers,
            "total_subscriptions": self.total_subscriptions,
            "events_sent": self.events_sent,
            "events_by_type": self.events_by_type,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
        }


class AlertStreamer:
    """
    Real-time alert streamer.

    Features:
    - SSE (Server-Sent Events) streaming
    - WebSocket support
    - Subscription filtering by severity and component
    - Heartbeat for connection health
    - Event buffering for missed events
    """

    def __init__(
        self,
        heartbeat_interval_seconds: int = 30,
        buffer_size: int = 100,
    ):
        """
        Initialize AlertStreamer.

        Args:
            heartbeat_interval_seconds: Interval between heartbeats
            buffer_size: Max events to buffer for reconnection
        """
        self._heartbeat_interval = heartbeat_interval_seconds
        self._buffer_size = buffer_size
        self._subscriptions: Dict[str, AlertSubscription] = {}
        self._event_queues: Dict[str, asyncio.Queue] = {}
        self._event_buffer: List[AlertEvent] = []
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.stats = StreamerStats()
        self._lock = asyncio.Lock()
        self._callbacks: List[Callable[[AlertEvent], None]] = []

    async def start(self) -> None:
        """Start the alert streamer."""
        if self._running:
            return

        self._running = True
        self.stats.started_at = datetime.now(timezone.utc)

        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        logger.info("AlertStreamer started")

    async def stop(self) -> None:
        """Stop the alert streamer."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        # Clean up subscriptions
        async with self._lock:
            self._subscriptions.clear()
            self._event_queues.clear()
            self.stats.active_subscribers = 0

        logger.info("AlertStreamer stopped")

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to all subscribers."""
        while self._running:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def _send_heartbeat(self) -> None:
        """Send heartbeat to all subscribers."""
        event = AlertEvent(
            event_id=f"hb_{uuid4().hex[:8]}",
            event_type=AlertEventType.HEARTBEAT,
            alert=None,
            timestamp=datetime.now(timezone.utc),
            metadata={"subscribers": len(self._subscriptions)},
        )
        await self._broadcast_event(event)

    async def subscribe(
        self,
        severities: Optional[Set[AlertSeverity]] = None,
        components: Optional[Set[str]] = None,
    ) -> str:
        """
        Subscribe to alert events.

        Args:
            severities: Filter by severities (None = all)
            components: Filter by components (None = all)

        Returns:
            Subscription ID
        """
        subscription_id = f"sub_{uuid4().hex[:8]}"

        subscription = AlertSubscription(
            subscription_id=subscription_id,
            severities=severities or set(),
            components=components or set(),
        )

        async with self._lock:
            self._subscriptions[subscription_id] = subscription
            self._event_queues[subscription_id] = asyncio.Queue()
            self.stats.active_subscribers = len(self._subscriptions)
            self.stats.total_subscriptions += 1

        logger.debug(f"New subscription: {subscription_id}")
        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from alert events.

        Args:
            subscription_id: Subscription to cancel

        Returns:
            True if unsubscribed, False if not found
        """
        async with self._lock:
            if subscription_id not in self._subscriptions:
                return False

            del self._subscriptions[subscription_id]
            if subscription_id in self._event_queues:
                del self._event_queues[subscription_id]
            self.stats.active_subscribers = len(self._subscriptions)

        logger.debug(f"Unsubscribed: {subscription_id}")
        return True

    async def fire_alert(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        component: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AlertEvent:
        """
        Fire an alert and notify subscribers.

        Args:
            name: Alert name
            severity: Alert severity
            message: Alert message
            component: Component that triggered the alert
            metadata: Additional metadata

        Returns:
            Alert event
        """
        dashboard = get_dashboard()
        alert = dashboard.alerts.fire_alert(
            name=name,
            severity=severity,
            message=message,
            component=component,
            metadata=metadata,
        )

        event = AlertEvent(
            event_id=f"evt_{uuid4().hex[:8]}",
            event_type=AlertEventType.FIRED,
            alert=alert,
            timestamp=datetime.now(timezone.utc),
        )

        await self._broadcast_event(event)
        return event

    async def resolve_alert(
        self,
        name: str,
        component: str,
    ) -> Optional[AlertEvent]:
        """
        Resolve an alert and notify subscribers.

        Args:
            name: Alert name
            component: Component

        Returns:
            Alert event or None if not found
        """
        dashboard = get_dashboard()
        resolved = dashboard.alerts.resolve_alert(name, component)

        if resolved:
            event = AlertEvent(
                event_id=f"evt_{uuid4().hex[:8]}",
                event_type=AlertEventType.RESOLVED,
                alert=None,
                timestamp=datetime.now(timezone.utc),
                metadata={"name": name, "component": component},
            )
            await self._broadcast_event(event)
            return event

        return None

    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> Optional[AlertEvent]:
        """
        Acknowledge an alert and notify subscribers.

        Args:
            alert_id: Alert ID
            acknowledged_by: User acknowledging

        Returns:
            Alert event or None if not found
        """
        dashboard = get_dashboard()
        alert = dashboard.alerts.acknowledge(alert_id, acknowledged_by)

        if alert:
            event = AlertEvent(
                event_id=f"evt_{uuid4().hex[:8]}",
                event_type=AlertEventType.ACKNOWLEDGED,
                alert=alert,
                timestamp=datetime.now(timezone.utc),
                metadata={"acknowledged_by": acknowledged_by},
            )
            await self._broadcast_event(event)
            return event

        return None

    async def escalate_alert(
        self,
        alert_id: str,
        new_severity: AlertSeverity,
        reason: str,
    ) -> Optional[AlertEvent]:
        """
        Escalate an alert to higher severity.

        Args:
            alert_id: Alert ID
            new_severity: New severity level
            reason: Reason for escalation

        Returns:
            Alert event or None if not found
        """
        dashboard = get_dashboard()

        # Find and update alert
        for alert in dashboard.alerts.get_active():
            if alert.alert_id == alert_id:
                old_severity = alert.severity
                alert.severity = new_severity

                event = AlertEvent(
                    event_id=f"evt_{uuid4().hex[:8]}",
                    event_type=AlertEventType.ESCALATED,
                    alert=alert,
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "old_severity": old_severity.value,
                        "new_severity": new_severity.value,
                        "reason": reason,
                    },
                )
                await self._broadcast_event(event)
                return event

        return None

    async def _broadcast_event(self, event: AlertEvent) -> int:
        """
        Broadcast event to all matching subscribers.

        Args:
            event: Event to broadcast

        Returns:
            Number of subscribers notified
        """
        # Add to buffer
        self._event_buffer.append(event)
        if len(self._event_buffer) > self._buffer_size:
            self._event_buffer = self._event_buffer[-self._buffer_size:]

        # Update stats
        self.stats.events_sent += 1
        self.stats.last_event_at = event.timestamp
        event_type_key = event.event_type.value
        self.stats.events_by_type[event_type_key] = (
            self.stats.events_by_type.get(event_type_key, 0) + 1
        )

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Callback error: {e}")

        # Send to queues
        sent_count = 0
        async with self._lock:
            for sub_id, subscription in self._subscriptions.items():
                # Heartbeats go to all
                if event.event_type == AlertEventType.HEARTBEAT:
                    should_send = True
                elif event.alert:
                    should_send = subscription.matches(event.alert)
                else:
                    should_send = True

                if should_send and sub_id in self._event_queues:
                    try:
                        self._event_queues[sub_id].put_nowait(event)
                        sent_count += 1
                    except asyncio.QueueFull:
                        logger.warning(f"Queue full for {sub_id}")

        return sent_count

    async def stream_events(
        self,
        subscription_id: str,
    ) -> AsyncGenerator[AlertEvent, None]:
        """
        Stream events for a subscription.

        Args:
            subscription_id: Subscription ID

        Yields:
            Alert events
        """
        if subscription_id not in self._event_queues:
            return

        queue = self._event_queues[subscription_id]

        while self._running and subscription_id in self._subscriptions:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def stream_sse(
        self,
        subscription_id: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream events as SSE format.

        Args:
            subscription_id: Subscription ID

        Yields:
            SSE formatted strings
        """
        async for event in self.stream_events(subscription_id):
            yield event.to_sse()

    def get_buffered_events(
        self,
        since: datetime,
        subscription: Optional[AlertSubscription] = None,
    ) -> List[AlertEvent]:
        """
        Get buffered events since a timestamp.

        Args:
            since: Get events since this time
            subscription: Optional subscription to filter

        Returns:
            List of matching events
        """
        events = []
        for event in self._event_buffer:
            if event.timestamp >= since:
                if subscription is None:
                    events.append(event)
                elif event.alert is None or subscription.matches(event.alert):
                    events.append(event)
        return events

    def register_callback(
        self,
        callback: Callable[[AlertEvent], None],
    ) -> None:
        """
        Register callback for alert events.

        Args:
            callback: Function to call on events
        """
        self._callbacks.append(callback)

    def unregister_callback(
        self,
        callback: Callable[[AlertEvent], None],
    ) -> bool:
        """
        Unregister callback.

        Args:
            callback: Function to remove

        Returns:
            True if found and removed
        """
        try:
            self._callbacks.remove(callback)
            return True
        except ValueError:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get streamer statistics."""
        return self.stats.to_dict()

    def get_subscription(
        self,
        subscription_id: str,
    ) -> Optional[AlertSubscription]:
        """Get subscription by ID."""
        return self._subscriptions.get(subscription_id)

    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
    ) -> List[ActiveAlert]:
        """Get currently active alerts."""
        dashboard = get_dashboard()
        return dashboard.alerts.get_active(severity)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Global instance
_streamer: Optional[AlertStreamer] = None


async def get_alert_streamer() -> AlertStreamer:
    """Get or create global alert streamer."""
    global _streamer
    if _streamer is None:
        _streamer = AlertStreamer()
        await _streamer.start()
    return _streamer


def reset_alert_streamer() -> None:
    """Reset global alert streamer (for testing)."""
    global _streamer
    _streamer = None
