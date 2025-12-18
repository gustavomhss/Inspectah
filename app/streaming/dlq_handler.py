"""
S39 - Dead Letter Queue Handler

Handles failed messages by routing them to DLQ with error context.
Supports retry, inspection, and reprocessing of failed messages.
"""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class FailureReason(str, Enum):
    """Reasons for message failure."""
    DESERIALIZATION_ERROR = "deserialization_error"
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    TIMEOUT = "timeout"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


class DLQMessageStatus(str, Enum):
    """Status of a DLQ message."""
    PENDING = "pending"           # Awaiting review
    RETRYING = "retrying"         # Being retried
    RESOLVED = "resolved"         # Successfully reprocessed
    DISCARDED = "discarded"       # Manually discarded
    EXPIRED = "expired"           # Past retention


@dataclass
class DLQMessage:
    """
    Message stored in the Dead Letter Queue.

    Contains original message plus error context for debugging.
    """
    dlq_id: str
    original_topic: str
    original_key: Optional[str]
    original_value: bytes
    original_headers: Dict[str, str]
    original_partition: int
    original_offset: int
    failure_reason: FailureReason
    error_message: str
    error_type: str
    stack_trace: Optional[str]
    retry_count: int
    max_retries: int
    first_failure_at: datetime
    last_failure_at: datetime
    status: DLQMessageStatus
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dlq_id": self.dlq_id,
            "original_topic": self.original_topic,
            "original_key": self.original_key,
            "original_value_b64": self.original_value.decode("utf-8", errors="replace"),
            "original_headers": self.original_headers,
            "original_partition": self.original_partition,
            "original_offset": self.original_offset,
            "failure_reason": self.failure_reason.value,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "stack_trace": self.stack_trace,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "first_failure_at": self.first_failure_at.isoformat(),
            "last_failure_at": self.last_failure_at.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DLQMessage:
        """Create from dictionary."""
        return cls(
            dlq_id=data["dlq_id"],
            original_topic=data["original_topic"],
            original_key=data.get("original_key"),
            original_value=data.get("original_value_b64", "").encode("utf-8"),
            original_headers=data.get("original_headers", {}),
            original_partition=data.get("original_partition", 0),
            original_offset=data.get("original_offset", 0),
            failure_reason=FailureReason(data["failure_reason"]),
            error_message=data["error_message"],
            error_type=data.get("error_type", "Exception"),
            stack_trace=data.get("stack_trace"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            first_failure_at=datetime.fromisoformat(data["first_failure_at"]),
            last_failure_at=datetime.fromisoformat(data["last_failure_at"]),
            status=DLQMessageStatus(data.get("status", "pending")),
            metadata=data.get("metadata", {}),
        )

    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return (
            self.status == DLQMessageStatus.PENDING and
            self.retry_count < self.max_retries
        )


@dataclass
class DLQConfig:
    """Configuration for DLQ handler."""
    dlq_topic: str = "signals.dlq"
    max_retries: int = 3
    retry_delay_seconds: int = 60
    retry_backoff_multiplier: float = 2.0
    max_retry_delay_seconds: int = 3600
    retention_days: int = 30
    batch_size: int = 100
    auto_retry: bool = False
    auto_retry_interval_seconds: int = 300


@dataclass
class DLQStats:
    """Statistics for DLQ handler."""
    total_messages: int = 0
    pending_count: int = 0
    retrying_count: int = 0
    resolved_count: int = 0
    discarded_count: int = 0
    expired_count: int = 0
    by_failure_reason: Dict[str, int] = field(default_factory=dict)
    by_topic: Dict[str, int] = field(default_factory=dict)
    avg_retry_count: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_messages": self.total_messages,
            "pending_count": self.pending_count,
            "retrying_count": self.retrying_count,
            "resolved_count": self.resolved_count,
            "discarded_count": self.discarded_count,
            "expired_count": self.expired_count,
            "by_failure_reason": self.by_failure_reason,
            "by_topic": self.by_topic,
            "avg_retry_count": round(self.avg_retry_count, 2),
        }


class DLQHandler:
    """
    Handler for Dead Letter Queue operations.

    Features:
    - Route failed messages to DLQ with full context
    - Automatic retry with exponential backoff
    - Manual inspection and reprocessing
    - Statistics and monitoring
    - Message expiration
    """

    def __init__(
        self,
        config: Optional[DLQConfig] = None,
        producer: Optional[Any] = None,
    ):
        """
        Initialize DLQHandler.

        Args:
            config: DLQ configuration
            producer: Kafka producer for publishing to DLQ
        """
        self.config = config or DLQConfig()
        self._producer = producer
        self._messages: Dict[str, DLQMessage] = {}
        self._retry_handlers: Dict[str, Callable] = {}
        self._running = False
        self._retry_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the DLQ handler."""
        if self._running:
            return

        self._running = True

        if self.config.auto_retry:
            self._retry_task = asyncio.create_task(self._auto_retry_loop())

        logger.info("DLQHandler started")

    async def stop(self) -> None:
        """Stop the DLQ handler."""
        self._running = False

        if self._retry_task:
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
            self._retry_task = None

        logger.info("DLQHandler stopped")

    async def send_to_dlq(
        self,
        topic: str,
        key: Optional[str],
        value: bytes,
        headers: Dict[str, str],
        partition: int,
        offset: int,
        error: Exception,
        failure_reason: FailureReason = FailureReason.PROCESSING_ERROR,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DLQMessage:
        """
        Send a failed message to the DLQ.

        Args:
            topic: Original topic
            key: Message key
            value: Message value (bytes)
            headers: Message headers
            partition: Original partition
            offset: Original offset
            error: Exception that caused failure
            failure_reason: Category of failure
            metadata: Additional context

        Returns:
            DLQ message record
        """
        now = datetime.now(timezone.utc)

        dlq_message = DLQMessage(
            dlq_id=f"dlq_{uuid4().hex[:12]}",
            original_topic=topic,
            original_key=key,
            original_value=value,
            original_headers=headers,
            original_partition=partition,
            original_offset=offset,
            failure_reason=failure_reason,
            error_message=str(error),
            error_type=type(error).__name__,
            stack_trace=traceback.format_exc(),
            retry_count=0,
            max_retries=self.config.max_retries,
            first_failure_at=now,
            last_failure_at=now,
            status=DLQMessageStatus.PENDING,
            metadata=metadata or {},
        )

        async with self._lock:
            self._messages[dlq_message.dlq_id] = dlq_message

        # Publish to Kafka DLQ topic
        await self._publish_to_dlq(dlq_message)

        logger.warning(
            f"Message sent to DLQ: {dlq_message.dlq_id} "
            f"(topic={topic}, reason={failure_reason.value})"
        )

        return dlq_message

    async def _publish_to_dlq(self, message: DLQMessage) -> None:
        """Publish message to Kafka DLQ topic."""
        if self._producer is None:
            logger.debug("No producer configured, skipping DLQ publish")
            return

        try:
            await self._producer.send(
                self.config.dlq_topic,
                key=message.dlq_id,
                value=message.to_json().encode("utf-8"),
                headers={
                    "dlq_id": message.dlq_id,
                    "original_topic": message.original_topic,
                    "failure_reason": message.failure_reason.value,
                },
            )
        except Exception as e:
            logger.error(f"Failed to publish to DLQ topic: {e}")

    async def retry_message(
        self,
        dlq_id: str,
        handler: Optional[Callable] = None,
    ) -> bool:
        """
        Retry processing a DLQ message.

        Args:
            dlq_id: DLQ message ID
            handler: Optional custom retry handler

        Returns:
            True if retry succeeded
        """
        async with self._lock:
            message = self._messages.get(dlq_id)
            if not message:
                logger.warning(f"DLQ message not found: {dlq_id}")
                return False

            if not message.can_retry():
                logger.warning(
                    f"DLQ message cannot be retried: {dlq_id} "
                    f"(status={message.status.value}, retries={message.retry_count})"
                )
                return False

            message.status = DLQMessageStatus.RETRYING
            message.retry_count += 1

        # Get retry handler
        retry_handler = handler or self._retry_handlers.get(message.original_topic)
        if not retry_handler:
            logger.error(f"No retry handler for topic: {message.original_topic}")
            async with self._lock:
                message.status = DLQMessageStatus.PENDING
            return False

        # Attempt retry
        try:
            await retry_handler(
                message.original_value,
                message.original_headers,
            )

            async with self._lock:
                message.status = DLQMessageStatus.RESOLVED
                logger.info(f"DLQ message resolved: {dlq_id}")

            return True

        except Exception as e:
            async with self._lock:
                message.last_failure_at = datetime.now(timezone.utc)
                message.error_message = str(e)
                message.stack_trace = traceback.format_exc()

                if message.retry_count >= message.max_retries:
                    message.status = DLQMessageStatus.DISCARDED
                    logger.warning(
                        f"DLQ message exhausted retries: {dlq_id}"
                    )
                else:
                    message.status = DLQMessageStatus.PENDING

            return False

    async def discard_message(self, dlq_id: str, reason: str = "") -> bool:
        """
        Manually discard a DLQ message.

        Args:
            dlq_id: DLQ message ID
            reason: Reason for discarding

        Returns:
            True if discarded
        """
        async with self._lock:
            message = self._messages.get(dlq_id)
            if not message:
                return False

            message.status = DLQMessageStatus.DISCARDED
            message.metadata["discard_reason"] = reason
            message.metadata["discarded_at"] = datetime.now(timezone.utc).isoformat()

        logger.info(f"DLQ message discarded: {dlq_id} (reason={reason})")
        return True

    async def get_message(self, dlq_id: str) -> Optional[DLQMessage]:
        """Get a DLQ message by ID."""
        return self._messages.get(dlq_id)

    async def get_pending_messages(
        self,
        topic: Optional[str] = None,
        failure_reason: Optional[FailureReason] = None,
        limit: int = 100,
    ) -> List[DLQMessage]:
        """
        Get pending DLQ messages.

        Args:
            topic: Filter by original topic
            failure_reason: Filter by failure reason
            limit: Max messages to return

        Returns:
            List of pending messages
        """
        messages = []
        for msg in self._messages.values():
            if msg.status != DLQMessageStatus.PENDING:
                continue
            if topic and msg.original_topic != topic:
                continue
            if failure_reason and msg.failure_reason != failure_reason:
                continue
            messages.append(msg)
            if len(messages) >= limit:
                break

        return sorted(messages, key=lambda m: m.first_failure_at)

    async def get_stats(self) -> DLQStats:
        """Get DLQ statistics."""
        stats = DLQStats()

        total_retries = 0
        for msg in self._messages.values():
            stats.total_messages += 1
            total_retries += msg.retry_count

            # By status
            if msg.status == DLQMessageStatus.PENDING:
                stats.pending_count += 1
            elif msg.status == DLQMessageStatus.RETRYING:
                stats.retrying_count += 1
            elif msg.status == DLQMessageStatus.RESOLVED:
                stats.resolved_count += 1
            elif msg.status == DLQMessageStatus.DISCARDED:
                stats.discarded_count += 1
            elif msg.status == DLQMessageStatus.EXPIRED:
                stats.expired_count += 1

            # By failure reason
            reason = msg.failure_reason.value
            stats.by_failure_reason[reason] = (
                stats.by_failure_reason.get(reason, 0) + 1
            )

            # By topic
            stats.by_topic[msg.original_topic] = (
                stats.by_topic.get(msg.original_topic, 0) + 1
            )

        if stats.total_messages > 0:
            stats.avg_retry_count = total_retries / stats.total_messages

        return stats

    def register_retry_handler(
        self,
        topic: str,
        handler: Callable,
    ) -> None:
        """
        Register a retry handler for a topic.

        Args:
            topic: Topic name
            handler: Async function(value, headers) to reprocess message
        """
        self._retry_handlers[topic] = handler
        logger.info(f"Registered retry handler for topic: {topic}")

    async def cleanup_expired(self) -> int:
        """
        Clean up expired messages.

        Returns:
            Number of messages expired
        """
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=self.config.retention_days
        )

        expired_count = 0
        async with self._lock:
            for dlq_id, msg in list(self._messages.items()):
                if msg.first_failure_at < cutoff:
                    msg.status = DLQMessageStatus.EXPIRED
                    expired_count += 1

        if expired_count > 0:
            logger.info(f"Expired {expired_count} DLQ messages")

        return expired_count

    async def _auto_retry_loop(self) -> None:
        """Automatic retry loop for pending messages."""
        while self._running:
            try:
                await asyncio.sleep(self.config.auto_retry_interval_seconds)

                pending = await self.get_pending_messages(
                    limit=self.config.batch_size
                )

                for msg in pending:
                    if msg.can_retry():
                        # Calculate backoff delay
                        delay = min(
                            self.config.retry_delay_seconds * (
                                self.config.retry_backoff_multiplier ** msg.retry_count
                            ),
                            self.config.max_retry_delay_seconds,
                        )

                        # Check if enough time has passed
                        time_since_failure = (
                            datetime.now(timezone.utc) - msg.last_failure_at
                        ).total_seconds()

                        if time_since_failure >= delay:
                            await self.retry_message(msg.dlq_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto retry loop error: {e}")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Global instance
_handler: Optional[DLQHandler] = None


async def get_dlq_handler(
    config: Optional[DLQConfig] = None,
    producer: Optional[Any] = None,
) -> DLQHandler:
    """Get or create global DLQ handler."""
    global _handler
    if _handler is None:
        _handler = DLQHandler(config, producer)
        await _handler.start()
    return _handler


def reset_dlq_handler() -> None:
    """Reset global handler (for testing)."""
    global _handler
    _handler = None
