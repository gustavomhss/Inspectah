"""
S39 - WebSocket Bridge

Bridges Kafka signals to WebSocket clients for real-time updates.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from weakref import WeakSet

from app.streaming.models import ComputedSignal, RawSignal, SignalType, Topics

logger = logging.getLogger(__name__)


class SubscriptionType(Enum):
    """Types of subscriptions."""

    CLAIM = "claim"
    DOMAIN = "domain"
    SIGNAL_TYPE = "signal_type"
    ALL = "all"


@dataclass
class Subscription:
    """Client subscription to signals."""

    subscription_type: SubscriptionType
    filter_value: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def matches(self, signal: RawSignal) -> bool:
        """Check if signal matches this subscription."""
        if self.subscription_type == SubscriptionType.ALL:
            return True
        elif self.subscription_type == SubscriptionType.CLAIM:
            return signal.claim_id == self.filter_value
        elif self.subscription_type == SubscriptionType.DOMAIN:
            return signal.domain == self.filter_value
        elif self.subscription_type == SubscriptionType.SIGNAL_TYPE:
            return signal.signal_type.value == self.filter_value
        return False


@dataclass
class ClientConnection:
    """Represents a WebSocket client connection."""

    connection_id: str
    websocket: Any  # WebSocket instance
    subscriptions: List[Subscription] = field(default_factory=list)
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: Optional[datetime] = None
    messages_sent: int = 0

    def add_subscription(self, subscription: Subscription) -> None:
        """Add subscription for this client."""
        self.subscriptions.append(subscription)

    def remove_subscription(self, subscription_type: SubscriptionType, filter_value: str) -> bool:
        """Remove subscription. Returns True if found and removed."""
        for i, sub in enumerate(self.subscriptions):
            if sub.subscription_type == subscription_type and sub.filter_value == filter_value:
                self.subscriptions.pop(i)
                return True
        return False

    def should_receive(self, signal: RawSignal) -> bool:
        """Check if client should receive this signal."""
        return any(sub.matches(signal) for sub in self.subscriptions)


@dataclass
class BridgeStats:
    """WebSocket bridge statistics."""

    active_connections: int = 0
    total_connections: int = 0
    messages_broadcasted: int = 0
    subscriptions_count: int = 0
    errors: int = 0
    started_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "active_connections": self.active_connections,
            "total_connections": self.total_connections,
            "messages_broadcasted": self.messages_broadcasted,
            "subscriptions_count": self.subscriptions_count,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class WebSocketBridge:
    """
    Bridges Kafka signals to WebSocket clients.

    Features:
    - Multiple subscription types (claim, domain, signal_type, all)
    - Auto-reconnect support
    - Message buffering for missed messages
    - Health monitoring
    """

    def __init__(
        self,
        buffer_size: int = 1000,
        buffer_duration_seconds: int = 300,
    ):
        """
        Initialize WebSocketBridge.

        Args:
            buffer_size: Max messages to buffer for reconnection
            buffer_duration_seconds: How long to keep buffered messages
        """
        self._connections: Dict[str, ClientConnection] = {}
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = buffer_size
        self._buffer_duration = buffer_duration_seconds
        self._running = False
        self.stats = BridgeStats()
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the bridge."""
        self._running = True
        self.stats.started_at = datetime.now(timezone.utc)
        logger.info("WebSocketBridge started")

    async def stop(self) -> None:
        """Stop the bridge and disconnect all clients."""
        self._running = False

        # Get all connection IDs first, then disconnect outside the lock
        async with self._lock:
            conn_ids = list(self._connections.keys())

        # Disconnect all clients (disconnect acquires its own lock)
        for conn_id in conn_ids:
            await self.disconnect(conn_id)

        logger.info("WebSocketBridge stopped")

    async def connect(
        self,
        connection_id: str,
        websocket: Any,
    ) -> ClientConnection:
        """
        Register a new WebSocket connection.

        Args:
            connection_id: Unique connection identifier
            websocket: WebSocket instance

        Returns:
            ClientConnection object
        """
        async with self._lock:
            connection = ClientConnection(
                connection_id=connection_id,
                websocket=websocket,
            )
            self._connections[connection_id] = connection
            self.stats.active_connections = len(self._connections)
            self.stats.total_connections += 1

        logger.info(f"Client connected: {connection_id}")
        return connection

    async def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect a WebSocket client.

        Args:
            connection_id: Connection to disconnect

        Returns:
            True if disconnected, False if not found
        """
        async with self._lock:
            if connection_id not in self._connections:
                return False

            connection = self._connections.pop(connection_id)
            self.stats.active_connections = len(self._connections)

            # Close WebSocket if possible
            try:
                if hasattr(connection.websocket, "close"):
                    await connection.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing websocket {connection_id}: {e}")

        logger.info(f"Client disconnected: {connection_id}")
        return True

    async def subscribe(
        self,
        connection_id: str,
        subscription_type: SubscriptionType,
        filter_value: Optional[str] = None,
    ) -> bool:
        """
        Subscribe a client to signals.

        Args:
            connection_id: Client connection ID
            subscription_type: Type of subscription
            filter_value: Filter value (claim_id, domain, signal_type)

        Returns:
            True if subscribed successfully
        """
        async with self._lock:
            if connection_id not in self._connections:
                return False

            subscription = Subscription(
                subscription_type=subscription_type,
                filter_value=filter_value,
            )
            self._connections[connection_id].add_subscription(subscription)
            self.stats.subscriptions_count += 1

        logger.debug(
            f"Client {connection_id} subscribed to {subscription_type.value}: {filter_value}"
        )
        return True

    async def unsubscribe(
        self,
        connection_id: str,
        subscription_type: SubscriptionType,
        filter_value: str,
    ) -> bool:
        """
        Unsubscribe a client from signals.

        Args:
            connection_id: Client connection ID
            subscription_type: Type of subscription
            filter_value: Filter value to unsubscribe from

        Returns:
            True if unsubscribed successfully
        """
        async with self._lock:
            if connection_id not in self._connections:
                return False

            removed = self._connections[connection_id].remove_subscription(
                subscription_type, filter_value
            )
            if removed:
                self.stats.subscriptions_count -= 1

        return removed

    async def broadcast(self, signal: RawSignal) -> int:
        """
        Broadcast a signal to all subscribed clients.

        Args:
            signal: Signal to broadcast

        Returns:
            Number of clients that received the signal
        """
        message = {
            "type": "signal",
            "data": signal.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add to buffer
        await self._add_to_buffer(message)

        # Send to subscribed clients
        sent_count = 0
        failed_connections: List[str] = []

        async with self._lock:
            for conn_id, connection in list(self._connections.items()):
                if connection.should_receive(signal):
                    success = await self._send_to_client_unlocked(connection, message)
                    if success:
                        sent_count += 1
                    else:
                        failed_connections.append(conn_id)

        # Disconnect failed connections outside the lock
        for conn_id in failed_connections:
            await self.disconnect(conn_id)

        self.stats.messages_broadcasted += 1
        return sent_count

    async def broadcast_computed(self, signal: ComputedSignal) -> int:
        """
        Broadcast a computed signal to all subscribed clients.

        Args:
            signal: Computed signal to broadcast

        Returns:
            Number of clients that received the signal
        """
        # Convert to RawSignal for matching
        raw = RawSignal(
            id=signal.id,
            claim_id=signal.claim_id,
            signal_type=signal.signal_type,
            value=signal.value,
            domain=signal.domain,
            components=signal.components,
            metadata=signal.metadata,
        )

        message = {
            "type": "computed_signal",
            "data": signal.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self._add_to_buffer(message)

        sent_count = 0
        failed_connections: List[str] = []

        async with self._lock:
            for conn_id, connection in list(self._connections.items()):
                if connection.should_receive(raw):
                    success = await self._send_to_client_unlocked(connection, message)
                    if success:
                        sent_count += 1
                    else:
                        failed_connections.append(conn_id)

        # Disconnect failed connections outside the lock
        for conn_id in failed_connections:
            await self.disconnect(conn_id)

        self.stats.messages_broadcasted += 1
        return sent_count

    async def _send_to_client_unlocked(
        self,
        connection: ClientConnection,
        message: Dict[str, Any],
    ) -> bool:
        """
        Send message to a specific client (must be called with lock held).

        Does NOT disconnect on failure - caller must handle disconnection
        outside of the lock to avoid deadlocks.
        """
        try:
            if hasattr(connection.websocket, "send_json"):
                await connection.websocket.send_json(message)
            elif hasattr(connection.websocket, "send"):
                await connection.websocket.send(json.dumps(message))
            else:
                logger.warning(f"Unknown websocket type for {connection.connection_id}")
                return False

            connection.messages_sent += 1
            connection.last_message_at = datetime.now(timezone.utc)
            return True

        except Exception as e:
            logger.error(f"Failed to send to {connection.connection_id}: {e}")
            self.stats.errors += 1
            return False

    async def _add_to_buffer(self, message: Dict[str, Any]) -> None:
        """Add message to reconnection buffer."""
        self._buffer.append(message)

        # Trim buffer if too large
        if len(self._buffer) > self._buffer_size:
            self._buffer = self._buffer[-self._buffer_size:]

    async def get_missed_messages(
        self,
        since: datetime,
        subscription: Subscription,
    ) -> List[Dict[str, Any]]:
        """
        Get messages that a client may have missed.

        Args:
            since: Get messages since this timestamp
            subscription: Client's subscription to filter messages

        Returns:
            List of missed messages
        """
        missed = []
        cutoff = datetime.now(timezone.utc).timestamp() - self._buffer_duration

        for message in self._buffer:
            msg_time = datetime.fromisoformat(message["timestamp"])
            if msg_time >= since and msg_time.timestamp() >= cutoff:
                # Check if message matches subscription
                if "data" in message:
                    try:
                        signal = RawSignal.from_dict(message["data"])
                        if subscription.matches(signal):
                            missed.append(message)
                    except (KeyError, TypeError, ValueError):
                        # Skip malformed messages in buffer
                        continue

        return missed

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return self.stats.to_dict()

    def get_connection(self, connection_id: str) -> Optional[ClientConnection]:
        """Get connection by ID."""
        return self._connections.get(connection_id)

    def get_all_connections(self) -> List[str]:
        """Get all connection IDs."""
        return list(self._connections.keys())


# Global bridge instance
_bridge: Optional[WebSocketBridge] = None


def get_bridge() -> WebSocketBridge:
    """Get or create global bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = WebSocketBridge()
    return _bridge
