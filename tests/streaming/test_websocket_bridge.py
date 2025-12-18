"""
Tests for WebSocket Bridge.

S39 - WebSocket Bridge Tests
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.models import ComputedSignal, RawSignal, SignalType
from app.streaming.websocket_bridge import (
    BridgeStats,
    ClientConnection,
    Subscription,
    SubscriptionType,
    WebSocketBridge,
    get_bridge,
)


class TestSubscriptionType:
    """Tests for SubscriptionType enum."""

    def test_subscription_types(self):
        """Test all subscription types exist."""
        assert SubscriptionType.CLAIM.value == "claim"
        assert SubscriptionType.DOMAIN.value == "domain"
        assert SubscriptionType.SIGNAL_TYPE.value == "signal_type"
        assert SubscriptionType.ALL.value == "all"


class TestSubscription:
    """Tests for Subscription dataclass."""

    def test_creation(self):
        """Test creating subscription."""
        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        )

        assert sub.subscription_type == SubscriptionType.CLAIM
        assert sub.filter_value == "claim-123"
        assert sub.created_at is not None

    def test_matches_all(self):
        """Test ALL subscription matches everything."""
        sub = Subscription(subscription_type=SubscriptionType.ALL)

        signal = RawSignal(
            claim_id="any-claim",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
            domain="any-domain",
        )

        assert sub.matches(signal) is True

    def test_matches_claim(self):
        """Test CLAIM subscription matches by claim_id."""
        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        )

        matching = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        non_matching = RawSignal(
            claim_id="claim-456",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        assert sub.matches(matching) is True
        assert sub.matches(non_matching) is False

    def test_matches_domain(self):
        """Test DOMAIN subscription matches by domain."""
        sub = Subscription(
            subscription_type=SubscriptionType.DOMAIN,
            filter_value="politica",
        )

        matching = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
            domain="politica",
        )

        non_matching = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
            domain="economia",
        )

        assert sub.matches(matching) is True
        assert sub.matches(non_matching) is False

    def test_matches_signal_type(self):
        """Test SIGNAL_TYPE subscription matches by signal type."""
        sub = Subscription(
            subscription_type=SubscriptionType.SIGNAL_TYPE,
            filter_value="battleground",
        )

        matching = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        non_matching = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        assert sub.matches(matching) is True
        assert sub.matches(non_matching) is False


class TestClientConnection:
    """Tests for ClientConnection dataclass."""

    def test_creation(self):
        """Test creating client connection."""
        ws = MagicMock()
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=ws,
        )

        assert conn.connection_id == "conn-123"
        assert conn.websocket == ws
        assert conn.subscriptions == []
        assert conn.messages_sent == 0
        assert conn.connected_at is not None

    def test_add_subscription(self):
        """Test adding subscription."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        )

        conn.add_subscription(sub)

        assert len(conn.subscriptions) == 1
        assert conn.subscriptions[0] == sub

    def test_remove_subscription(self):
        """Test removing subscription."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        )
        conn.add_subscription(sub)

        removed = conn.remove_subscription(SubscriptionType.CLAIM, "claim-123")

        assert removed is True
        assert len(conn.subscriptions) == 0

    def test_remove_subscription_not_found(self):
        """Test removing non-existent subscription."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        removed = conn.remove_subscription(SubscriptionType.CLAIM, "claim-123")

        assert removed is False

    def test_remove_subscription_no_match(self):
        """Test removing subscription when there are subscriptions but none match."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        # Add some subscriptions
        conn.add_subscription(Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-456",
        ))
        conn.add_subscription(Subscription(
            subscription_type=SubscriptionType.DOMAIN,
            filter_value="politica",
        ))

        # Try to remove a subscription that doesn't match any of the existing ones
        removed = conn.remove_subscription(SubscriptionType.CLAIM, "claim-789")

        assert removed is False
        assert len(conn.subscriptions) == 2  # Original subscriptions still there

    def test_should_receive(self):
        """Test should_receive with multiple subscriptions."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        conn.add_subscription(Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        ))
        conn.add_subscription(Subscription(
            subscription_type=SubscriptionType.DOMAIN,
            filter_value="politica",
        ))

        # Matches claim subscription
        signal1 = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
            domain="economia",
        )
        assert conn.should_receive(signal1) is True

        # Matches domain subscription
        signal2 = RawSignal(
            claim_id="claim-456",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
            domain="politica",
        )
        assert conn.should_receive(signal2) is True

        # Matches neither
        signal3 = RawSignal(
            claim_id="claim-456",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
            domain="economia",
        )
        assert conn.should_receive(signal3) is False

    def test_should_receive_no_subscriptions(self):
        """Test should_receive with no subscriptions."""
        conn = ClientConnection(
            connection_id="conn-123",
            websocket=MagicMock(),
        )

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        assert conn.should_receive(signal) is False


class TestBridgeStats:
    """Tests for BridgeStats dataclass."""

    def test_default_stats(self):
        """Test default stats."""
        stats = BridgeStats()

        assert stats.active_connections == 0
        assert stats.total_connections == 0
        assert stats.messages_broadcasted == 0
        assert stats.subscriptions_count == 0
        assert stats.errors == 0
        assert stats.started_at is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        now = datetime.now(timezone.utc)
        stats = BridgeStats(
            active_connections=5,
            total_connections=10,
            messages_broadcasted=100,
            subscriptions_count=15,
            errors=2,
            started_at=now,
        )

        d = stats.to_dict()

        assert d["active_connections"] == 5
        assert d["total_connections"] == 10
        assert d["messages_broadcasted"] == 100
        assert d["subscriptions_count"] == 15
        assert d["errors"] == 2
        assert d["started_at"] == now.isoformat()

    def test_to_dict_no_started_at(self):
        """Test to_dict when started_at is None."""
        stats = BridgeStats()
        d = stats.to_dict()

        assert d["started_at"] is None


class TestWebSocketBridge:
    """Tests for WebSocketBridge."""

    def test_creation(self):
        """Test creating bridge."""
        bridge = WebSocketBridge()

        assert bridge._buffer_size == 1000
        assert bridge._buffer_duration == 300
        assert bridge._running is False
        assert len(bridge._connections) == 0

    def test_creation_custom_config(self):
        """Test creating bridge with custom config."""
        bridge = WebSocketBridge(
            buffer_size=500,
            buffer_duration_seconds=600,
        )

        assert bridge._buffer_size == 500
        assert bridge._buffer_duration == 600


class TestWebSocketBridgeAsync:
    """Async tests for WebSocketBridge."""

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping bridge."""
        bridge = WebSocketBridge()

        await bridge.start()
        assert bridge._running is True
        assert bridge.stats.started_at is not None

        await bridge.stop()
        assert bridge._running is False

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting a client."""
        bridge = WebSocketBridge()
        ws = MagicMock()

        conn = await bridge.connect("conn-123", ws)

        assert conn.connection_id == "conn-123"
        assert bridge.stats.active_connections == 1
        assert bridge.stats.total_connections == 1
        assert "conn-123" in bridge._connections

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a client."""
        bridge = WebSocketBridge()
        ws = AsyncMock()

        await bridge.connect("conn-123", ws)
        result = await bridge.disconnect("conn-123")

        assert result is True
        assert bridge.stats.active_connections == 0
        assert "conn-123" not in bridge._connections

    @pytest.mark.asyncio
    async def test_disconnect_not_found(self):
        """Test disconnecting non-existent client."""
        bridge = WebSocketBridge()

        result = await bridge.disconnect("conn-123")

        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect_closes_websocket(self):
        """Test disconnect closes websocket."""
        bridge = WebSocketBridge()
        ws = AsyncMock()

        await bridge.connect("conn-123", ws)
        await bridge.disconnect("conn-123")

        ws.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_handles_close_error(self):
        """Test disconnect handles websocket close error."""
        bridge = WebSocketBridge()
        ws = AsyncMock()
        ws.close.side_effect = Exception("Close failed")

        await bridge.connect("conn-123", ws)
        result = await bridge.disconnect("conn-123")

        # Should still disconnect successfully
        assert result is True
        assert "conn-123" not in bridge._connections

    @pytest.mark.asyncio
    async def test_disconnect_no_close_method(self):
        """Test disconnect when websocket has no close method."""
        bridge = WebSocketBridge()

        # Create websocket without close method
        ws = MagicMock(spec=[])  # Empty spec means no methods

        await bridge.connect("conn-123", ws)
        result = await bridge.disconnect("conn-123")

        # Should still disconnect successfully
        assert result is True
        assert "conn-123" not in bridge._connections

    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test subscribing a client."""
        bridge = WebSocketBridge()
        ws = MagicMock()

        await bridge.connect("conn-123", ws)
        result = await bridge.subscribe(
            "conn-123",
            SubscriptionType.CLAIM,
            "claim-456",
        )

        assert result is True
        assert bridge.stats.subscriptions_count == 1
        conn = bridge.get_connection("conn-123")
        assert len(conn.subscriptions) == 1

    @pytest.mark.asyncio
    async def test_subscribe_not_found(self):
        """Test subscribing non-existent client."""
        bridge = WebSocketBridge()

        result = await bridge.subscribe(
            "conn-123",
            SubscriptionType.CLAIM,
            "claim-456",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribing a client."""
        bridge = WebSocketBridge()
        ws = MagicMock()

        await bridge.connect("conn-123", ws)
        await bridge.subscribe("conn-123", SubscriptionType.CLAIM, "claim-456")

        result = await bridge.unsubscribe(
            "conn-123",
            SubscriptionType.CLAIM,
            "claim-456",
        )

        assert result is True
        assert bridge.stats.subscriptions_count == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self):
        """Test unsubscribing non-existent client."""
        bridge = WebSocketBridge()

        result = await bridge.unsubscribe(
            "conn-123",
            SubscriptionType.CLAIM,
            "claim-456",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """Test broadcasting a signal."""
        bridge = WebSocketBridge()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await bridge.connect("conn-1", ws1)
        await bridge.connect("conn-2", ws2)

        await bridge.subscribe("conn-1", SubscriptionType.ALL)
        await bridge.subscribe("conn-2", SubscriptionType.CLAIM, "claim-123")

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.75,
        )

        sent_count = await bridge.broadcast(signal)

        # Both clients should receive (conn-1 has ALL, conn-2 matches claim)
        assert sent_count == 2
        assert bridge.stats.messages_broadcasted == 1
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_filtered(self):
        """Test broadcast only sends to matching subscriptions."""
        bridge = WebSocketBridge()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await bridge.connect("conn-1", ws1)
        await bridge.connect("conn-2", ws2)

        await bridge.subscribe("conn-1", SubscriptionType.CLAIM, "claim-123")
        await bridge.subscribe("conn-2", SubscriptionType.CLAIM, "claim-456")

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        sent_count = await bridge.broadcast(signal)

        # Only conn-1 should receive
        assert sent_count == 1
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_send_method(self):
        """Test broadcast uses send() if send_json not available."""
        bridge = WebSocketBridge()

        ws = MagicMock()
        ws.send = AsyncMock()
        del ws.send_json  # Remove send_json

        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        sent_count = await bridge.broadcast(signal)

        assert sent_count == 1
        ws.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_computed(self):
        """Test broadcasting a computed signal."""
        bridge = WebSocketBridge()

        ws = AsyncMock()
        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        signal = ComputedSignal(
            id="computed-123",
            claim_id="claim-456",
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
            confidence=0.85,
            domain="politica",
        )

        sent_count = await bridge.broadcast_computed(signal)

        assert sent_count == 1
        ws.send_json.assert_called_once()
        call_args = ws.send_json.call_args[0][0]
        assert call_args["type"] == "computed_signal"

    @pytest.mark.asyncio
    async def test_broadcast_computed_no_match(self):
        """Test broadcasting computed signal with no matching subscriptions."""
        bridge = WebSocketBridge()

        ws = AsyncMock()
        await bridge.connect("conn-1", ws)
        # Subscribe to a specific claim
        await bridge.subscribe("conn-1", SubscriptionType.CLAIM, "claim-different")

        signal = ComputedSignal(
            id="computed-123",
            claim_id="claim-456",  # Different claim
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
            confidence=0.85,
            domain="politica",
        )

        sent_count = await bridge.broadcast_computed(signal)

        assert sent_count == 0
        ws.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_computed_with_failure(self):
        """Test broadcast_computed handles send error."""
        bridge = WebSocketBridge()

        ws = AsyncMock()
        ws.send_json.side_effect = Exception("Send failed")
        ws.close = AsyncMock()

        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        signal = ComputedSignal(
            id="computed-123",
            claim_id="claim-456",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
            confidence=0.8,
            domain="default",
        )

        sent_count = await bridge.broadcast_computed(signal)

        assert sent_count == 0
        assert bridge.stats.errors == 1
        # Client should be disconnected
        assert "conn-1" not in bridge._connections

    @pytest.mark.asyncio
    async def test_broadcast_handles_send_error(self):
        """Test broadcast handles send error and disconnects client."""
        bridge = WebSocketBridge()

        ws = AsyncMock()
        ws.send_json.side_effect = Exception("Send failed")
        ws.close = AsyncMock()

        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        sent_count = await bridge.broadcast(signal)

        assert sent_count == 0
        assert bridge.stats.errors == 1
        # Client should be disconnected
        assert "conn-1" not in bridge._connections

    @pytest.mark.asyncio
    async def test_broadcast_unknown_websocket_type(self):
        """Test broadcast handles unknown websocket type."""
        bridge = WebSocketBridge()

        ws = MagicMock()
        del ws.send_json
        del ws.send

        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        sent_count = await bridge.broadcast(signal)

        assert sent_count == 0

    @pytest.mark.asyncio
    async def test_buffer_messages(self):
        """Test messages are buffered."""
        bridge = WebSocketBridge(buffer_size=10)

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        await bridge.broadcast(signal)

        assert len(bridge._buffer) == 1
        assert bridge._buffer[0]["type"] == "signal"

    @pytest.mark.asyncio
    async def test_buffer_trimmed(self):
        """Test buffer is trimmed when full."""
        bridge = WebSocketBridge(buffer_size=5)

        for i in range(10):
            signal = RawSignal(
                claim_id=f"claim-{i}",
                signal_type=SignalType.FRAGILITY,
                value=i * 0.1,
            )
            await bridge.broadcast(signal)

        # Buffer should only have last 5 messages
        assert len(bridge._buffer) == 5
        # Last message should be claim-9
        assert bridge._buffer[-1]["data"]["claim_id"] == "claim-9"

    @pytest.mark.asyncio
    async def test_get_missed_messages(self):
        """Test getting missed messages."""
        bridge = WebSocketBridge()

        # Add some messages
        for i in range(3):
            signal = RawSignal(
                claim_id="claim-123",
                signal_type=SignalType.BATTLEGROUND,
                value=i * 0.1,
            )
            await bridge.broadcast(signal)

        # Get missed messages
        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        subscription = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-123",
        )

        missed = await bridge.get_missed_messages(since, subscription)

        assert len(missed) == 3

    @pytest.mark.asyncio
    async def test_get_missed_messages_filtered(self):
        """Test get_missed_messages filters by subscription."""
        bridge = WebSocketBridge()

        # Add messages for different claims
        for i in range(3):
            signal = RawSignal(
                claim_id=f"claim-{i}",
                signal_type=SignalType.FRAGILITY,
                value=i * 0.1,
            )
            await bridge.broadcast(signal)

        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        subscription = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="claim-1",
        )

        missed = await bridge.get_missed_messages(since, subscription)

        assert len(missed) == 1
        assert missed[0]["data"]["claim_id"] == "claim-1"

    @pytest.mark.asyncio
    async def test_get_missed_messages_time_filter(self):
        """Test get_missed_messages filters by time."""
        bridge = WebSocketBridge()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )
        await bridge.broadcast(signal)

        # Request messages from the future
        since = datetime.now(timezone.utc) + timedelta(hours=1)
        subscription = Subscription(subscription_type=SubscriptionType.ALL)

        missed = await bridge.get_missed_messages(since, subscription)

        assert len(missed) == 0

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting bridge stats."""
        bridge = WebSocketBridge()
        await bridge.start()

        ws = AsyncMock()
        await bridge.connect("conn-1", ws)
        await bridge.subscribe("conn-1", SubscriptionType.ALL)

        stats = bridge.get_stats()

        assert stats["active_connections"] == 1
        assert stats["total_connections"] == 1
        assert stats["subscriptions_count"] == 1
        assert stats["started_at"] is not None

        await bridge.stop()

    @pytest.mark.asyncio
    async def test_get_connection(self):
        """Test getting connection by ID."""
        bridge = WebSocketBridge()
        ws = MagicMock()

        await bridge.connect("conn-123", ws)

        conn = bridge.get_connection("conn-123")
        assert conn is not None
        assert conn.connection_id == "conn-123"

        # Non-existent
        assert bridge.get_connection("conn-456") is None

    @pytest.mark.asyncio
    async def test_get_all_connections(self):
        """Test getting all connection IDs."""
        bridge = WebSocketBridge()

        await bridge.connect("conn-1", MagicMock())
        await bridge.connect("conn-2", MagicMock())
        await bridge.connect("conn-3", MagicMock())

        connections = bridge.get_all_connections()

        assert len(connections) == 3
        assert "conn-1" in connections
        assert "conn-2" in connections
        assert "conn-3" in connections

    @pytest.mark.asyncio
    async def test_stop_disconnects_all(self):
        """Test stop disconnects all clients."""
        bridge = WebSocketBridge()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await bridge.connect("conn-1", ws1)
        await bridge.connect("conn-2", ws2)

        await bridge.stop()

        assert len(bridge._connections) == 0
        ws1.close.assert_called_once()
        ws2.close.assert_called_once()


class TestSubscriptionEdgeCases:
    """Edge case tests for Subscription."""

    def test_matches_claim_with_none_filter(self):
        """Test matching with None filter value returns False."""
        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value=None,  # No filter value means it won't match
        )

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        # None != "claim-123", so it returns False
        assert sub.matches(signal) is False

    def test_matches_unknown_subscription_type(self):
        """Test matching with mocked unknown subscription type."""
        sub = Subscription(
            subscription_type=SubscriptionType.CLAIM,
            filter_value="test",
        )

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        # Patch subscription_type to be something unrecognized
        sub.subscription_type = MagicMock()
        sub.subscription_type.__eq__ = lambda self, other: False

        # Should return False for unrecognized type
        assert sub.matches(signal) is False


class TestWebSocketBridgeEdgeCases:
    """Edge case tests for WebSocketBridge."""

    @pytest.mark.asyncio
    async def test_get_missed_messages_invalid_data(self):
        """Test get_missed_messages handles invalid message data."""
        bridge = WebSocketBridge()

        # Add an invalid message to the buffer
        invalid_message = {
            "type": "signal",
            "data": {"invalid": "data"},  # Missing required fields
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        bridge._buffer.append(invalid_message)

        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        subscription = Subscription(subscription_type=SubscriptionType.ALL)

        # Should not raise, just skip invalid messages
        missed = await bridge.get_missed_messages(since, subscription)

        # Invalid message should be skipped
        assert len(missed) == 0

    @pytest.mark.asyncio
    async def test_get_missed_messages_no_data_key(self):
        """Test get_missed_messages handles messages without data key."""
        bridge = WebSocketBridge()

        # Add a message without 'data' key
        no_data_message = {
            "type": "other",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        bridge._buffer.append(no_data_message)

        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        subscription = Subscription(subscription_type=SubscriptionType.ALL)

        missed = await bridge.get_missed_messages(since, subscription)

        # Message without data should be skipped
        assert len(missed) == 0


class TestGetBridge:
    """Tests for get_bridge function."""

    def test_get_bridge_singleton(self):
        """Test get_bridge returns singleton."""
        # Reset global
        import app.streaming.websocket_bridge as ws_module
        ws_module._bridge = None

        bridge1 = get_bridge()
        bridge2 = get_bridge()

        assert bridge1 is bridge2

        # Cleanup
        ws_module._bridge = None

    def test_get_bridge_creates_instance(self):
        """Test get_bridge creates instance if none exists."""
        import app.streaming.websocket_bridge as ws_module
        ws_module._bridge = None

        bridge = get_bridge()

        assert bridge is not None
        assert isinstance(bridge, WebSocketBridge)

        # Cleanup
        ws_module._bridge = None
