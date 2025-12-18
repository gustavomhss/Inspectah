"""
S39 - Streaming Module

Kafka-based streaming infrastructure for real-time signal processing.
"""

from app.streaming.models import (
    RawSignal,
    ComputedSignal,
    SignalBatch,
    SignalEnvelope,
)
from app.streaming.producer import SignalProducer
from app.streaming.consumer import SignalConsumer
from app.streaming.websocket_bridge import WebSocketBridge
from app.streaming.alert_streamer import (
    AlertEvent,
    AlertEventType,
    AlertStreamer,
    AlertSubscription,
    StreamerStats,
    get_alert_streamer,
    reset_alert_streamer,
)
from app.streaming.topics import (
    TopicConfig,
    TopicPriority,
    CleanupPolicy,
    TopicRegistry,
    TopicManager,
    TopicHealth,
)
from app.streaming.backpressure import (
    BackpressureState,
    ThrottleLevel,
    BackpressureConfig,
    BackpressureMetrics,
    BackpressureController,
    get_backpressure_controller,
    reset_backpressure_controller,
)
from app.streaming.dlq_handler import (
    FailureReason,
    DLQMessageStatus,
    DLQMessage,
    DLQConfig,
    DLQStats,
    DLQHandler,
    get_dlq_handler,
    reset_dlq_handler,
)

__all__ = [
    # Signal models
    "RawSignal",
    "ComputedSignal",
    "SignalBatch",
    "SignalEnvelope",
    # Kafka
    "SignalProducer",
    "SignalConsumer",
    # WebSocket
    "WebSocketBridge",
    # Alert Streaming (S39)
    "AlertEvent",
    "AlertEventType",
    "AlertStreamer",
    "AlertSubscription",
    "StreamerStats",
    "get_alert_streamer",
    "reset_alert_streamer",
    # Topics (S39)
    "TopicConfig",
    "TopicPriority",
    "CleanupPolicy",
    "TopicRegistry",
    "TopicManager",
    "TopicHealth",
    # Backpressure (S39)
    "BackpressureState",
    "ThrottleLevel",
    "BackpressureConfig",
    "BackpressureMetrics",
    "BackpressureController",
    "get_backpressure_controller",
    "reset_backpressure_controller",
    # DLQ (S39)
    "FailureReason",
    "DLQMessageStatus",
    "DLQMessage",
    "DLQConfig",
    "DLQStats",
    "DLQHandler",
    "get_dlq_handler",
    "reset_dlq_handler",
]
