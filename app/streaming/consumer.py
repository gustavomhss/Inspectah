"""
S39 - Signal Consumer

Kafka consumer for processing signals with:
- Processing pipeline
- Backpressure handling
- Lag monitoring
- Commit management
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set

from app.streaming.models import (
    ComputedSignal,
    RawSignal,
    SignalType,
    Topics,
)

logger = logging.getLogger(__name__)


class ConsumerState(Enum):
    """Consumer lifecycle state."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class ConsumerConfig:
    """Configuration for SignalConsumer."""

    bootstrap_servers: str = "localhost:9092"
    group_id: str = "inspectah-signal-consumer"
    topics: List[str] = field(default_factory=lambda: [Topics.SIGNALS_RAW])
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    max_poll_records: int = 100
    max_poll_interval_ms: int = 300000
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 3000
    fetch_max_wait_ms: int = 500
    fetch_min_bytes: int = 1
    backpressure_threshold: int = 1000
    commit_interval_ms: int = 5000


@dataclass
class ConsumerStats:
    """Consumer statistics."""

    messages_processed: int = 0
    messages_failed: int = 0
    commits: int = 0
    rebalances: int = 0
    lag: int = 0
    processing_time_ms: float = 0.0
    started_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

    def record_processed(self, processing_time_ms: float) -> None:
        """Record processed message."""
        self.messages_processed += 1
        self.processing_time_ms = (
            self.processing_time_ms * 0.9 + processing_time_ms * 0.1
        )  # EMA
        self.last_message_at = datetime.now(timezone.utc)

    def record_failure(self, error: str) -> None:
        """Record processing failure."""
        self.messages_failed += 1
        self.errors.append(error)
        if len(self.errors) > 100:
            self.errors = self.errors[-100:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "messages_processed": self.messages_processed,
            "messages_failed": self.messages_failed,
            "commits": self.commits,
            "rebalances": self.rebalances,
            "lag": self.lag,
            "avg_processing_time_ms": round(self.processing_time_ms, 2),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "recent_errors": self.errors[-10:],
        }


# Type for message handlers
MessageHandler = Callable[[RawSignal], Coroutine[Any, Any, Optional[ComputedSignal]]]


class SignalConsumer:
    """
    Kafka consumer for signals.

    Features:
    - Async message consumption
    - Pluggable message handlers
    - Automatic commit management
    - Backpressure handling
    - Lag monitoring
    """

    def __init__(
        self,
        config: Optional[ConsumerConfig] = None,
        handler: Optional[MessageHandler] = None,
    ):
        """
        Initialize SignalConsumer.

        Args:
            config: Consumer configuration
            handler: Message handler function
        """
        self.config = config or ConsumerConfig()
        self._consumer = None
        self._handler = handler or self._default_handler
        self._state = ConsumerState.CREATED
        self.stats = ConsumerStats()
        self._running = False
        self._paused = False
        self._pending_messages: asyncio.Queue = asyncio.Queue()
        self._handlers: Dict[SignalType, MessageHandler] = {}
        self._last_commit = time.time()

    def register_handler(
        self,
        signal_type: SignalType,
        handler: MessageHandler,
    ) -> None:
        """Register handler for specific signal type."""
        self._handlers[signal_type] = handler
        logger.info(f"Registered handler for {signal_type.value}")

    async def _default_handler(self, signal: RawSignal) -> Optional[ComputedSignal]:
        """Default handler - just logs and passes through."""
        logger.debug(f"Processing signal: {signal.id} ({signal.signal_type.value})")
        return ComputedSignal(
            id=signal.id,
            claim_id=signal.claim_id,
            signal_type=signal.signal_type,
            value=signal.value,
            confidence=1.0,
            domain=signal.domain,
            source_signals=[signal.id],
            components=signal.components,
            metadata=signal.metadata,
        )

    async def initialize(self) -> None:
        """Initialize the Kafka consumer."""
        if self._state != ConsumerState.CREATED:
            return

        self._state = ConsumerState.STARTING

        try:
            from aiokafka import AIOKafkaConsumer

            self._consumer = AIOKafkaConsumer(
                *self.config.topics,
                bootstrap_servers=self.config.bootstrap_servers,
                group_id=self.config.group_id,
                auto_offset_reset=self.config.auto_offset_reset,
                enable_auto_commit=self.config.enable_auto_commit,
                max_poll_records=self.config.max_poll_records,
                session_timeout_ms=self.config.session_timeout_ms,
                heartbeat_interval_ms=self.config.heartbeat_interval_ms,
            )
            await self._consumer.start()
            self._state = ConsumerState.RUNNING
            self.stats.started_at = datetime.now(timezone.utc)
            logger.info(f"SignalConsumer initialized: {self.config.topics}")

        except ImportError:
            logger.warning("aiokafka not installed, consumer running in mock mode")
            self._state = ConsumerState.RUNNING
            self.stats.started_at = datetime.now(timezone.utc)
        except Exception as e:
            self._state = ConsumerState.STOPPED
            logger.error(f"Failed to initialize consumer: {e}")
            raise

    async def close(self) -> None:
        """Close the consumer."""
        self._state = ConsumerState.STOPPING
        self._running = False

        if self._consumer:
            await self._consumer.stop()
            self._consumer = None

        self._state = ConsumerState.STOPPED
        logger.info("SignalConsumer closed")

    async def start(self) -> None:
        """Start consuming messages."""
        await self.initialize()
        self._running = True

        logger.info("Consumer started, beginning to consume messages")

        while self._running:
            try:
                if self._paused:
                    await asyncio.sleep(0.1)
                    continue

                await self._poll_and_process()

            except asyncio.CancelledError:
                logger.info("Consumer cancelled")
                break
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                self.stats.record_failure(str(e))
                await asyncio.sleep(1)  # Back off on error

        await self.close()

    async def stop(self) -> None:
        """Stop consuming messages."""
        logger.info("Stopping consumer...")
        self._running = False

    def pause(self) -> None:
        """Pause message consumption."""
        self._paused = True
        self._state = ConsumerState.PAUSED
        logger.info("Consumer paused")

    def resume(self) -> None:
        """Resume message consumption."""
        self._paused = False
        self._state = ConsumerState.RUNNING
        logger.info("Consumer resumed")

    async def _poll_and_process(self) -> None:
        """Poll for messages and process them."""
        if not self._consumer:
            # Mock mode - simulate messages
            await asyncio.sleep(0.1)
            return

        # Check backpressure
        if self._pending_messages.qsize() > self.config.backpressure_threshold:
            logger.warning(
                f"Backpressure triggered: {self._pending_messages.qsize()} pending"
            )
            await asyncio.sleep(0.5)
            return

        # Poll for messages
        try:
            messages = await self._consumer.getmany(
                timeout_ms=self.config.fetch_max_wait_ms,
                max_records=self.config.max_poll_records,
            )

            for topic_partition, records in messages.items():
                for record in records:
                    await self._process_message(record)

            # Check if we should commit
            await self._maybe_commit()

        except Exception as e:
            logger.error(f"Poll error: {e}")
            raise

    async def _process_message(self, record: Any) -> None:
        """Process a single message."""
        start_time = time.time()

        try:
            # Deserialize
            payload = json.loads(record.value.decode("utf-8"))
            signal = RawSignal.from_dict(payload)

            # Find appropriate handler
            handler = self._handlers.get(signal.signal_type, self._handler)

            # Process
            result = await handler(signal)

            # Record success
            processing_time_ms = (time.time() - start_time) * 1000
            self.stats.record_processed(processing_time_ms)

            logger.debug(
                f"Processed signal {signal.id} in {processing_time_ms:.2f}ms"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
            self.stats.record_failure(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            self.stats.record_failure(str(e))

    async def _maybe_commit(self) -> None:
        """Commit offsets if interval has passed."""
        if self.config.enable_auto_commit:
            return

        now = time.time()
        if (now - self._last_commit) * 1000 >= self.config.commit_interval_ms:
            await self._commit()
            self._last_commit = now

    async def _commit(self) -> None:
        """Commit current offsets."""
        if not self._consumer:
            return

        try:
            await self._consumer.commit()
            self.stats.commits += 1
            logger.debug("Offsets committed")
        except Exception as e:
            logger.error(f"Commit failed: {e}")

    async def get_lag(self) -> Dict[str, int]:
        """Get consumer lag per partition."""
        if not self._consumer:
            return {}

        lag = {}
        try:
            for tp in self._consumer.assignment():
                position = await self._consumer.position(tp)
                end_offset = (await self._consumer.end_offsets([tp]))[tp]
                lag[f"{tp.topic}-{tp.partition}"] = end_offset - position
        except Exception as e:
            logger.error(f"Failed to get lag: {e}")

        total_lag = sum(lag.values())
        self.stats.lag = total_lag

        return lag

    def get_stats(self) -> Dict[str, Any]:
        """Get consumer statistics."""
        return self.stats.to_dict()

    async def process_single(self, signal: RawSignal) -> Optional[ComputedSignal]:
        """
        Process a single signal directly (for testing/debugging).

        Args:
            signal: Signal to process

        Returns:
            Computed signal or None on failure
        """
        handler = self._handlers.get(signal.signal_type, self._handler)
        return await handler(signal)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Global consumer instance
_consumer: Optional[SignalConsumer] = None


async def get_consumer(config: Optional[ConsumerConfig] = None) -> SignalConsumer:
    """Get or create global consumer instance."""
    global _consumer
    if _consumer is None:
        _consumer = SignalConsumer(config)
    return _consumer
