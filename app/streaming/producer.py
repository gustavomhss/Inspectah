"""
S39 - Signal Producer

Kafka producer for publishing signals with:
- Batch support
- Retry logic with exponential backoff
- Dead letter queue for failed messages
- Metrics and observability
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.streaming.models import (
    RawSignal,
    SignalBatch,
    SignalEnvelope,
    SignalPriority,
    Topics,
)

logger = logging.getLogger(__name__)


@dataclass
class ProducerConfig:
    """Configuration for SignalProducer."""

    bootstrap_servers: str = "localhost:9092"
    client_id: str = "inspectah-signal-producer"
    acks: str = "all"
    retries: int = 3
    retry_backoff_ms: int = 100
    max_retry_backoff_ms: int = 10000
    batch_size: int = 100
    linger_ms: int = 5
    compression_type: str = "gzip"
    max_in_flight_requests_per_connection: int = 5
    enable_idempotence: bool = True
    request_timeout_ms: int = 30000


@dataclass
class ProducerStats:
    """Producer statistics."""

    messages_sent: int = 0
    messages_failed: int = 0
    batches_sent: int = 0
    bytes_sent: int = 0
    retries: int = 0
    dlq_messages: int = 0
    last_send_at: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

    def record_success(self, count: int = 1, bytes_size: int = 0) -> None:
        """Record successful send."""
        self.messages_sent += count
        self.bytes_sent += bytes_size
        self.last_send_at = datetime.now(timezone.utc)

    def record_failure(self, error: str) -> None:
        """Record failed send."""
        self.messages_failed += 1
        self.errors.append(error)
        if len(self.errors) > 100:
            self.errors = self.errors[-100:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "batches_sent": self.batches_sent,
            "bytes_sent": self.bytes_sent,
            "retries": self.retries,
            "dlq_messages": self.dlq_messages,
            "last_send_at": self.last_send_at.isoformat() if self.last_send_at else None,
            "recent_errors": self.errors[-10:],
        }


class SignalProducer:
    """
    Kafka producer for signals.

    Features:
    - Async message sending
    - Batch support for efficiency
    - Automatic retry with exponential backoff
    - Dead letter queue for failed messages
    - Metrics collection
    """

    def __init__(
        self,
        config: Optional[ProducerConfig] = None,
        on_success: Optional[Callable[[SignalEnvelope], None]] = None,
        on_error: Optional[Callable[[SignalEnvelope, Exception], None]] = None,
    ):
        """
        Initialize SignalProducer.

        Args:
            config: Producer configuration
            on_success: Callback for successful sends
            on_error: Callback for failed sends
        """
        self.config = config or ProducerConfig()
        self._producer = None
        self._initialized = False
        self._on_success = on_success
        self._on_error = on_error
        self.stats = ProducerStats()
        self._pending_callbacks: List[asyncio.Future] = []

    async def initialize(self) -> None:
        """Initialize the Kafka producer."""
        if self._initialized:
            return

        try:
            # Import here to allow mocking in tests
            from aiokafka import AIOKafkaProducer

            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                client_id=self.config.client_id,
                acks=self.config.acks,
                compression_type=self.config.compression_type,
                linger_ms=self.config.linger_ms,
                request_timeout_ms=self.config.request_timeout_ms,
                enable_idempotence=self.config.enable_idempotence,
            )
            await self._producer.start()
            self._initialized = True
            logger.info(f"SignalProducer initialized: {self.config.bootstrap_servers}")

        except ImportError:
            logger.warning("aiokafka not installed, producer running in mock mode")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize producer: {e}")
            raise

    async def close(self) -> None:
        """Close the producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
        self._initialized = False
        logger.info("SignalProducer closed")

    async def send(
        self,
        signal: RawSignal,
        topic: str = Topics.SIGNALS_RAW,
    ) -> bool:
        """
        Send a single signal to Kafka.

        Args:
            signal: Signal to send
            topic: Target topic

        Returns:
            True if sent successfully
        """
        envelope = SignalEnvelope(
            topic=topic,
            key=signal.claim_id,
            payload=signal.to_dict(),
            headers={
                "signal_type": signal.signal_type.value,
                "domain": signal.domain,
            },
        )

        return await self._send_with_retry(envelope)

    async def send_batch(
        self,
        batch: SignalBatch,
        topic: str = Topics.SIGNALS_RAW,
    ) -> int:
        """
        Send a batch of signals to Kafka.

        Args:
            batch: Batch of signals
            topic: Target topic

        Returns:
            Number of successfully sent signals
        """
        if not batch.signals:
            return 0

        success_count = 0
        tasks = []

        for signal in batch.signals:
            tasks.append(self.send(signal, topic))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if result is True:
                success_count += 1

        self.stats.batches_sent += 1
        logger.debug(f"Batch sent: {success_count}/{len(batch)} signals")

        return success_count

    async def _send_with_retry(self, envelope: SignalEnvelope) -> bool:
        """
        Send message with retry logic.

        Uses exponential backoff for retries.
        """
        last_error = None
        backoff_ms = self.config.retry_backoff_ms

        for attempt in range(self.config.retries + 1):
            try:
                await self._do_send(envelope)
                self.stats.record_success(
                    bytes_size=len(json.dumps(envelope.payload))
                )

                if self._on_success:
                    self._on_success(envelope)

                return True

            except Exception as e:
                last_error = e
                self.stats.retries += 1

                if attempt < self.config.retries:
                    logger.warning(
                        f"Send failed (attempt {attempt + 1}/{self.config.retries + 1}): {e}"
                    )
                    await asyncio.sleep(backoff_ms / 1000)
                    backoff_ms = min(
                        backoff_ms * 2,
                        self.config.max_retry_backoff_ms,
                    )

        # All retries failed - send to DLQ
        self.stats.record_failure(str(last_error))
        await self._send_to_dlq(envelope, last_error)

        if self._on_error:
            self._on_error(envelope, last_error)

        return False

    async def _do_send(self, envelope: SignalEnvelope) -> None:
        """Actually send the message to Kafka."""
        if not self._producer:
            # Mock mode - just log
            logger.debug(f"Mock send: {envelope.topic} / {envelope.key}")
            return

        await self._producer.send_and_wait(
            envelope.topic,
            key=envelope.key.encode("utf-8"),
            value=json.dumps(envelope.payload).encode("utf-8"),
            headers=[(k, v.encode("utf-8")) for k, v in envelope.headers.items()],
            partition=envelope.partition,
        )

    async def _send_to_dlq(
        self,
        envelope: SignalEnvelope,
        error: Exception,
    ) -> None:
        """Send failed message to dead letter queue."""
        dlq_envelope = SignalEnvelope(
            topic=Topics.SIGNALS_DLQ,
            key=envelope.key,
            payload={
                "original_topic": envelope.topic,
                "original_payload": envelope.payload,
                "error": str(error),
                "failed_at": datetime.now(timezone.utc).isoformat(),
            },
            headers={
                "original_topic": envelope.topic,
                "error_type": type(error).__name__,
            },
        )

        try:
            await self._do_send(dlq_envelope)
            self.stats.dlq_messages += 1
            logger.warning(f"Message sent to DLQ: {envelope.key}")
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get producer statistics."""
        return self.stats.to_dict()

    async def flush(self) -> None:
        """Flush pending messages."""
        if self._producer:
            await self._producer.flush()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Global producer instance
_producer: Optional[SignalProducer] = None


async def get_producer(config: Optional[ProducerConfig] = None) -> SignalProducer:
    """Get or create global producer instance."""
    global _producer
    if _producer is None:
        _producer = SignalProducer(config)
        await _producer.initialize()
    return _producer


async def publish_signal(signal: RawSignal, topic: str = Topics.SIGNALS_RAW) -> bool:
    """Convenience function to publish a signal."""
    producer = await get_producer()
    return await producer.send(signal, topic)
