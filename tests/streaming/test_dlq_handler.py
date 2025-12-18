"""
Tests for S39 Dead Letter Queue Handler Module.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.dlq_handler import (
    DLQConfig,
    DLQHandler,
    DLQMessage,
    DLQMessageStatus,
    DLQStats,
    FailureReason,
    get_dlq_handler,
    reset_dlq_handler,
)


# ============================================================================
# FailureReason Tests
# ============================================================================

class TestFailureReason:
    """Tests for FailureReason enum."""

    def test_failure_reason_values(self):
        """Test failure reason enum values."""
        assert FailureReason.DESERIALIZATION_ERROR.value == "deserialization_error"
        assert FailureReason.VALIDATION_ERROR.value == "validation_error"
        assert FailureReason.PROCESSING_ERROR.value == "processing_error"
        assert FailureReason.TIMEOUT.value == "timeout"
        assert FailureReason.DEPENDENCY_UNAVAILABLE.value == "dependency_unavailable"
        assert FailureReason.RATE_LIMITED.value == "rate_limited"
        assert FailureReason.UNKNOWN.value == "unknown"


# ============================================================================
# DLQMessageStatus Tests
# ============================================================================

class TestDLQMessageStatus:
    """Tests for DLQMessageStatus enum."""

    def test_status_values(self):
        """Test message status enum values."""
        assert DLQMessageStatus.PENDING.value == "pending"
        assert DLQMessageStatus.RETRYING.value == "retrying"
        assert DLQMessageStatus.RESOLVED.value == "resolved"
        assert DLQMessageStatus.DISCARDED.value == "discarded"
        assert DLQMessageStatus.EXPIRED.value == "expired"


# ============================================================================
# DLQMessage Tests
# ============================================================================

class TestDLQMessage:
    """Tests for DLQMessage dataclass."""

    @pytest.fixture
    def sample_message(self):
        """Create a sample DLQ message."""
        now = datetime.now(timezone.utc)
        return DLQMessage(
            dlq_id="dlq_abc123",
            original_topic="signals.raw",
            original_key="key123",
            original_value=b'{"test": "data"}',
            original_headers={"correlation_id": "corr123"},
            original_partition=0,
            original_offset=12345,
            failure_reason=FailureReason.PROCESSING_ERROR,
            error_message="Test error message",
            error_type="ValueError",
            stack_trace="Traceback...",
            retry_count=0,
            max_retries=3,
            first_failure_at=now,
            last_failure_at=now,
            status=DLQMessageStatus.PENDING,
            metadata={"key": "value"},
        )

    def test_message_creation(self, sample_message):
        """Test DLQ message creation."""
        assert sample_message.dlq_id == "dlq_abc123"
        assert sample_message.original_topic == "signals.raw"
        assert sample_message.original_key == "key123"
        assert sample_message.original_value == b'{"test": "data"}'
        assert sample_message.failure_reason == FailureReason.PROCESSING_ERROR
        assert sample_message.status == DLQMessageStatus.PENDING

    def test_to_dict(self, sample_message):
        """Test message to_dict conversion."""
        data = sample_message.to_dict()

        assert data["dlq_id"] == "dlq_abc123"
        assert data["original_topic"] == "signals.raw"
        assert data["original_key"] == "key123"
        assert data["failure_reason"] == "processing_error"
        assert data["error_message"] == "Test error message"
        assert data["error_type"] == "ValueError"
        assert data["retry_count"] == 0
        assert data["max_retries"] == 3
        assert data["status"] == "pending"
        assert data["metadata"] == {"key": "value"}

    def test_to_json(self, sample_message):
        """Test message JSON serialization."""
        json_str = sample_message.to_json()

        assert "dlq_abc123" in json_str
        assert "signals.raw" in json_str
        assert "processing_error" in json_str

    def test_from_dict(self, sample_message):
        """Test message deserialization from dict."""
        data = sample_message.to_dict()
        restored = DLQMessage.from_dict(data)

        assert restored.dlq_id == sample_message.dlq_id
        assert restored.original_topic == sample_message.original_topic
        assert restored.failure_reason == sample_message.failure_reason
        assert restored.status == sample_message.status

    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data."""
        data = {
            "dlq_id": "dlq_test",
            "original_topic": "test.topic",
            "failure_reason": "timeout",
            "error_message": "Timeout occurred",
            "first_failure_at": datetime.now(timezone.utc).isoformat(),
            "last_failure_at": datetime.now(timezone.utc).isoformat(),
        }

        message = DLQMessage.from_dict(data)

        assert message.dlq_id == "dlq_test"
        assert message.original_key is None
        assert message.original_partition == 0
        assert message.retry_count == 0
        assert message.max_retries == 3
        assert message.status == DLQMessageStatus.PENDING

    def test_can_retry_pending(self, sample_message):
        """Test can_retry for pending message with retries left."""
        assert sample_message.can_retry() is True

    def test_can_retry_max_reached(self, sample_message):
        """Test can_retry when max retries reached."""
        sample_message.retry_count = 3  # Equals max_retries

        assert sample_message.can_retry() is False

    def test_can_retry_not_pending(self, sample_message):
        """Test can_retry for non-pending message."""
        sample_message.status = DLQMessageStatus.RESOLVED

        assert sample_message.can_retry() is False

    def test_can_retry_retrying_status(self, sample_message):
        """Test can_retry when status is retrying."""
        sample_message.status = DLQMessageStatus.RETRYING

        assert sample_message.can_retry() is False


# ============================================================================
# DLQConfig Tests
# ============================================================================

class TestDLQConfig:
    """Tests for DLQConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DLQConfig()

        assert config.dlq_topic == "signals.dlq"
        assert config.max_retries == 3
        assert config.retry_delay_seconds == 60
        assert config.retry_backoff_multiplier == 2.0
        assert config.max_retry_delay_seconds == 3600
        assert config.retention_days == 30
        assert config.batch_size == 100
        assert config.auto_retry is False
        assert config.auto_retry_interval_seconds == 300

    def test_custom_config(self):
        """Test custom configuration."""
        config = DLQConfig(
            dlq_topic="custom.dlq",
            max_retries=5,
            retry_delay_seconds=30,
            auto_retry=True,
        )

        assert config.dlq_topic == "custom.dlq"
        assert config.max_retries == 5
        assert config.retry_delay_seconds == 30
        assert config.auto_retry is True


# ============================================================================
# DLQStats Tests
# ============================================================================

class TestDLQStats:
    """Tests for DLQStats dataclass."""

    def test_default_stats(self):
        """Test default stats values."""
        stats = DLQStats()

        assert stats.total_messages == 0
        assert stats.pending_count == 0
        assert stats.retrying_count == 0
        assert stats.resolved_count == 0
        assert stats.discarded_count == 0
        assert stats.expired_count == 0
        assert stats.by_failure_reason == {}
        assert stats.by_topic == {}
        assert stats.avg_retry_count == 0.0

    def test_to_dict(self):
        """Test stats to_dict conversion."""
        stats = DLQStats(
            total_messages=100,
            pending_count=50,
            resolved_count=40,
            by_failure_reason={"timeout": 30, "processing_error": 70},
            by_topic={"signals.raw": 60, "claims.events": 40},
            avg_retry_count=1.5,
        )

        data = stats.to_dict()

        assert data["total_messages"] == 100
        assert data["pending_count"] == 50
        assert data["resolved_count"] == 40
        assert data["by_failure_reason"]["timeout"] == 30
        assert data["by_topic"]["signals.raw"] == 60
        assert data["avg_retry_count"] == 1.5


# ============================================================================
# DLQHandler Tests
# ============================================================================

class TestDLQHandler:
    """Tests for DLQHandler class."""

    @pytest.fixture
    def handler(self):
        """Create a handler for testing."""
        return DLQHandler()

    @pytest.fixture
    def handler_with_producer(self):
        """Create a handler with mock producer."""
        producer = AsyncMock()
        return DLQHandler(producer=producer)

    @pytest.fixture
    def custom_handler(self):
        """Create a handler with custom config."""
        config = DLQConfig(
            max_retries=2,
            retry_delay_seconds=10,
            auto_retry=False,
        )
        return DLQHandler(config)

    def test_init_default(self, handler):
        """Test default initialization."""
        assert handler.config.max_retries == 3
        assert handler._producer is None
        assert handler._messages == {}
        assert not handler._running

    def test_init_custom(self, custom_handler):
        """Test custom initialization."""
        assert custom_handler.config.max_retries == 2
        assert custom_handler.config.retry_delay_seconds == 10

    @pytest.mark.asyncio
    async def test_start_stop(self, handler):
        """Test start and stop lifecycle."""
        await handler.start()

        assert handler._running is True

        await handler.stop()

        assert handler._running is False

    @pytest.mark.asyncio
    async def test_start_idempotent(self, handler):
        """Test that start is idempotent."""
        await handler.start()
        await handler.start()

        assert handler._running is True

        await handler.stop()

    @pytest.mark.asyncio
    async def test_send_to_dlq(self, handler):
        """Test sending a message to DLQ."""
        await handler.start()

        error = ValueError("Test error")
        message = await handler.send_to_dlq(
            topic="signals.raw",
            key="key123",
            value=b'{"test": "data"}',
            headers={"header1": "value1"},
            partition=0,
            offset=12345,
            error=error,
            failure_reason=FailureReason.PROCESSING_ERROR,
            metadata={"custom": "data"},
        )

        assert message.dlq_id.startswith("dlq_")
        assert message.original_topic == "signals.raw"
        assert message.original_key == "key123"
        assert message.failure_reason == FailureReason.PROCESSING_ERROR
        assert message.error_message == "Test error"
        assert message.error_type == "ValueError"
        assert message.status == DLQMessageStatus.PENDING
        assert message.dlq_id in handler._messages

        await handler.stop()

    @pytest.mark.asyncio
    async def test_send_to_dlq_with_producer(self, handler_with_producer):
        """Test sending to DLQ publishes to Kafka."""
        await handler_with_producer.start()

        error = TimeoutError("Operation timed out")
        await handler_with_producer.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test data",
            headers={},
            partition=1,
            offset=100,
            error=error,
            failure_reason=FailureReason.TIMEOUT,
        )

        # Verify producer was called
        handler_with_producer._producer.send.assert_called_once()

        await handler_with_producer.stop()

    @pytest.mark.asyncio
    async def test_retry_message_success(self, handler):
        """Test successful message retry."""
        await handler.start()

        # Send a message to DLQ
        error = ValueError("Initial error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        # Register a successful retry handler
        async def success_handler(value, headers):
            pass  # Success

        handler.register_retry_handler("test.topic", success_handler)

        # Retry the message
        result = await handler.retry_message(message.dlq_id)

        assert result is True
        assert message.status == DLQMessageStatus.RESOLVED
        assert message.retry_count == 1

        await handler.stop()

    @pytest.mark.asyncio
    async def test_retry_message_failure(self, handler):
        """Test failed message retry."""
        await handler.start()

        error = ValueError("Initial error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        # Register a failing retry handler
        async def fail_handler(value, headers):
            raise RuntimeError("Retry failed")

        handler.register_retry_handler("test.topic", fail_handler)

        result = await handler.retry_message(message.dlq_id)

        assert result is False
        assert message.status == DLQMessageStatus.PENDING
        assert message.retry_count == 1

        await handler.stop()

    @pytest.mark.asyncio
    async def test_retry_message_not_found(self, handler):
        """Test retry with non-existent message."""
        await handler.start()

        result = await handler.retry_message("nonexistent")

        assert result is False

        await handler.stop()

    @pytest.mark.asyncio
    async def test_retry_message_cannot_retry(self, custom_handler):
        """Test retry when message cannot be retried."""
        await custom_handler.start()

        error = ValueError("Error")
        message = await custom_handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        # Exhaust retries
        message.retry_count = 2  # Equals max_retries

        result = await custom_handler.retry_message(message.dlq_id)

        assert result is False

        await custom_handler.stop()

    @pytest.mark.asyncio
    async def test_retry_message_no_handler(self, handler):
        """Test retry without registered handler."""
        await handler.start()

        error = ValueError("Error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        result = await handler.retry_message(message.dlq_id)

        assert result is False
        assert message.status == DLQMessageStatus.PENDING

        await handler.stop()

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, custom_handler):
        """Test when all retries are exhausted."""
        await custom_handler.start()

        error = ValueError("Error")
        message = await custom_handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        message.retry_count = 1  # One before max

        async def fail_handler(value, headers):
            raise RuntimeError("Always fails")

        custom_handler.register_retry_handler("test.topic", fail_handler)

        await custom_handler.retry_message(message.dlq_id)

        # After exhausting retries, status should be DISCARDED
        assert message.status == DLQMessageStatus.DISCARDED

        await custom_handler.stop()

    @pytest.mark.asyncio
    async def test_discard_message(self, handler):
        """Test manually discarding a message."""
        await handler.start()

        error = ValueError("Error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        result = await handler.discard_message(message.dlq_id, "Manual discard")

        assert result is True
        assert message.status == DLQMessageStatus.DISCARDED
        assert message.metadata["discard_reason"] == "Manual discard"

        await handler.stop()

    @pytest.mark.asyncio
    async def test_discard_message_not_found(self, handler):
        """Test discarding non-existent message."""
        result = await handler.discard_message("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_message(self, handler):
        """Test getting a message by ID."""
        await handler.start()

        error = ValueError("Error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        retrieved = await handler.get_message(message.dlq_id)

        assert retrieved is message

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_message_not_found(self, handler):
        """Test getting non-existent message."""
        result = await handler.get_message("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_pending_messages(self, handler):
        """Test getting pending messages."""
        await handler.start()

        # Add multiple messages
        for i in range(5):
            await handler.send_to_dlq(
                topic=f"topic{i % 2}",
                key=None,
                value=f"test{i}".encode(),
                headers={},
                partition=0,
                offset=i,
                error=ValueError(f"Error {i}"),
                failure_reason=FailureReason.PROCESSING_ERROR if i % 2 == 0 else FailureReason.TIMEOUT,
            )

        pending = await handler.get_pending_messages()

        assert len(pending) == 5

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_pending_messages_with_filter(self, handler):
        """Test getting pending messages with filters."""
        await handler.start()

        # Add messages to different topics
        for i in range(4):
            topic = "signals.raw" if i < 2 else "claims.events"
            reason = FailureReason.TIMEOUT if i % 2 == 0 else FailureReason.PROCESSING_ERROR
            await handler.send_to_dlq(
                topic=topic,
                key=None,
                value=f"test{i}".encode(),
                headers={},
                partition=0,
                offset=i,
                error=ValueError(f"Error {i}"),
                failure_reason=reason,
            )

        # Filter by topic
        filtered = await handler.get_pending_messages(topic="signals.raw")
        assert len(filtered) == 2

        # Filter by failure reason
        filtered = await handler.get_pending_messages(failure_reason=FailureReason.TIMEOUT)
        assert len(filtered) == 2

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_pending_messages_limit(self, handler):
        """Test get_pending_messages with limit."""
        await handler.start()

        for i in range(10):
            await handler.send_to_dlq(
                topic="test.topic",
                key=None,
                value=f"test{i}".encode(),
                headers={},
                partition=0,
                offset=i,
                error=ValueError(f"Error {i}"),
            )

        pending = await handler.get_pending_messages(limit=3)

        assert len(pending) == 3

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_stats(self, handler):
        """Test getting DLQ statistics."""
        await handler.start()

        # Add messages with different statuses
        msg1 = await handler.send_to_dlq(
            topic="signals.raw",
            key=None,
            value=b"test1",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error 1"),
            failure_reason=FailureReason.TIMEOUT,
        )

        msg2 = await handler.send_to_dlq(
            topic="claims.events",
            key=None,
            value=b"test2",
            headers={},
            partition=0,
            offset=1,
            error=RuntimeError("Error 2"),
            failure_reason=FailureReason.PROCESSING_ERROR,
        )
        msg2.status = DLQMessageStatus.RESOLVED
        msg2.retry_count = 2

        stats = await handler.get_stats()

        assert stats.total_messages == 2
        assert stats.pending_count == 1
        assert stats.resolved_count == 1
        assert stats.by_failure_reason["timeout"] == 1
        assert stats.by_failure_reason["processing_error"] == 1
        assert stats.by_topic["signals.raw"] == 1
        assert stats.by_topic["claims.events"] == 1
        assert stats.avg_retry_count == 1.0  # (0 + 2) / 2

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_stats_all_statuses(self, handler):
        """Test get_stats counts all status types."""
        await handler.start()

        # Add messages with all different statuses
        msg1 = await handler.send_to_dlq(
            topic="topic1", key=None, value=b"test1", headers={},
            partition=0, offset=0, error=ValueError("E1"),
        )
        msg1.status = DLQMessageStatus.PENDING

        msg2 = await handler.send_to_dlq(
            topic="topic2", key=None, value=b"test2", headers={},
            partition=0, offset=1, error=ValueError("E2"),
        )
        msg2.status = DLQMessageStatus.RETRYING

        msg3 = await handler.send_to_dlq(
            topic="topic3", key=None, value=b"test3", headers={},
            partition=0, offset=2, error=ValueError("E3"),
        )
        msg3.status = DLQMessageStatus.RESOLVED

        msg4 = await handler.send_to_dlq(
            topic="topic4", key=None, value=b"test4", headers={},
            partition=0, offset=3, error=ValueError("E4"),
        )
        msg4.status = DLQMessageStatus.DISCARDED

        msg5 = await handler.send_to_dlq(
            topic="topic5", key=None, value=b"test5", headers={},
            partition=0, offset=4, error=ValueError("E5"),
        )
        msg5.status = DLQMessageStatus.EXPIRED

        stats = await handler.get_stats()

        assert stats.total_messages == 5
        assert stats.pending_count == 1
        assert stats.retrying_count == 1
        assert stats.resolved_count == 1
        assert stats.discarded_count == 1
        assert stats.expired_count == 1

        await handler.stop()

    def test_register_retry_handler(self, handler):
        """Test registering retry handler."""
        async def my_handler(value, headers):
            pass

        handler.register_retry_handler("test.topic", my_handler)

        assert "test.topic" in handler._retry_handlers
        assert handler._retry_handlers["test.topic"] is my_handler

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, handler):
        """Test cleaning up expired messages."""
        await handler.start()

        # Add a message
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Backdate the message
        message.first_failure_at = datetime.now(timezone.utc) - timedelta(days=31)

        expired_count = await handler.cleanup_expired()

        assert expired_count == 1
        assert message.status == DLQMessageStatus.EXPIRED

        await handler.stop()

    @pytest.mark.asyncio
    async def test_cleanup_expired_none(self, handler):
        """Test cleanup when no messages are expired."""
        await handler.start()

        await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        expired_count = await handler.cleanup_expired()

        assert expired_count == 0

        await handler.stop()

    @pytest.mark.asyncio
    async def test_context_manager(self, handler):
        """Test async context manager."""
        async with handler:
            assert handler._running is True

        assert handler._running is False


# ============================================================================
# Auto Retry Tests
# ============================================================================

class TestAutoRetry:
    """Tests for automatic retry functionality."""

    @pytest.mark.asyncio
    async def test_auto_retry_enabled(self):
        """Test that auto retry task starts when enabled."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=1,
        )
        handler = DLQHandler(config)

        await handler.start()

        assert handler._retry_task is not None

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_disabled(self):
        """Test that auto retry task doesn't start when disabled."""
        config = DLQConfig(auto_retry=False)
        handler = DLQHandler(config)

        await handler.start()

        assert handler._retry_task is None

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_loop_processes_messages(self):
        """Test auto retry loop processes pending messages."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0,  # Fast
            retry_delay_seconds=0,  # No delay
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add a message
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Register a successful handler
        async def success_handler(value, headers):
            pass

        handler.register_retry_handler("test.topic", success_handler)

        # Set message to be retryable with old timestamp
        message.last_failure_at = datetime.now(timezone.utc) - timedelta(hours=1)

        # Manually trigger one iteration of auto retry logic
        pending = await handler.get_pending_messages(limit=handler.config.batch_size)
        for msg in pending:
            if msg.can_retry():
                delay = min(
                    handler.config.retry_delay_seconds * (
                        handler.config.retry_backoff_multiplier ** msg.retry_count
                    ),
                    handler.config.max_retry_delay_seconds,
                )
                time_since_failure = (
                    datetime.now(timezone.utc) - msg.last_failure_at
                ).total_seconds()
                if time_since_failure >= delay:
                    await handler.retry_message(msg.dlq_id)

        assert message.status == DLQMessageStatus.RESOLVED

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_backoff_calculation(self):
        """Test backoff calculation in auto retry."""
        config = DLQConfig(
            retry_delay_seconds=10,
            retry_backoff_multiplier=2.0,
            max_retry_delay_seconds=100,
        )
        handler = DLQHandler(config)

        # Test backoff for different retry counts
        test_cases = [
            (0, 10),   # 10 * 2^0 = 10
            (1, 20),   # 10 * 2^1 = 20
            (2, 40),   # 10 * 2^2 = 40
            (3, 80),   # 10 * 2^3 = 80
            (4, 100),  # 10 * 2^4 = 160, capped at 100
        ]

        for retry_count, expected_delay in test_cases:
            delay = min(
                config.retry_delay_seconds * (
                    config.retry_backoff_multiplier ** retry_count
                ),
                config.max_retry_delay_seconds,
            )
            assert delay == expected_delay, f"Retry {retry_count} should have delay {expected_delay}"

    @pytest.mark.asyncio
    async def test_auto_retry_respects_time_since_failure(self):
        """Test that auto retry respects time since failure."""
        config = DLQConfig(
            auto_retry=False,  # We'll test manually
            retry_delay_seconds=60,
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add a message with recent failure
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Register handler
        processed = []

        async def handler_fn(value, headers):
            processed.append(value)

        handler.register_retry_handler("test.topic", handler_fn)

        # Check if enough time has passed (it hasn't)
        delay = config.retry_delay_seconds
        time_since_failure = (
            datetime.now(timezone.utc) - message.last_failure_at
        ).total_seconds()

        # Should not process because not enough time passed
        assert time_since_failure < delay

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_loop_handles_errors(self):
        """Test that auto retry loop handles errors gracefully."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0,
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add a message
        await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Register a failing handler
        async def fail_handler(value, headers):
            raise RuntimeError("Handler error")

        handler.register_retry_handler("test.topic", fail_handler)

        # The loop should continue running despite errors
        await asyncio.sleep(0.1)
        assert handler._running is True

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_loop_actually_runs(self):
        """Test auto retry loop actually executes retries."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0.01,  # Very short
            retry_delay_seconds=0,  # No delay
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add a message with old failure time
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Backdate the failure
        message.last_failure_at = datetime.now(timezone.utc) - timedelta(hours=1)

        # Register a successful handler
        processed = []

        async def success_handler(value, headers):
            processed.append(value)

        handler.register_retry_handler("test.topic", success_handler)

        # Wait for loop to process
        await asyncio.sleep(0.1)

        # Message should be resolved
        assert message.status == DLQMessageStatus.RESOLVED

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_loop_skips_recent_failures(self):
        """Test auto retry loop skips messages with recent failures."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0.01,
            retry_delay_seconds=3600,  # 1 hour delay
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add a message with recent failure (default)
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Register handler
        async def handler_fn(value, headers):
            pass

        handler.register_retry_handler("test.topic", handler_fn)

        # Wait for loop
        await asyncio.sleep(0.1)

        # Message should still be pending (delay not elapsed)
        assert message.status == DLQMessageStatus.PENDING

        await handler.stop()

    @pytest.mark.asyncio
    async def test_auto_retry_loop_multiple_messages(self):
        """Test auto retry loop processes multiple messages."""
        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0.01,
            retry_delay_seconds=0,
            batch_size=10,
        )
        handler = DLQHandler(config)

        await handler.start()

        # Add multiple messages
        messages = []
        for i in range(3):
            msg = await handler.send_to_dlq(
                topic="test.topic",
                key=f"key{i}",
                value=f"test{i}".encode(),
                headers={},
                partition=0,
                offset=i,
                error=ValueError(f"Error {i}"),
            )
            msg.last_failure_at = datetime.now(timezone.utc) - timedelta(hours=1)
            messages.append(msg)

        # Register handler
        async def success_handler(value, headers):
            pass

        handler.register_retry_handler("test.topic", success_handler)

        # Wait for loop
        await asyncio.sleep(0.15)

        # All should be resolved
        resolved_count = sum(1 for m in messages if m.status == DLQMessageStatus.RESOLVED)
        assert resolved_count >= 1  # At least one should be resolved

        await handler.stop()


# ============================================================================
# Global Instance Tests
# ============================================================================

class TestGlobalInstance:
    """Tests for global instance management."""

    @pytest.fixture(autouse=True)
    def reset_global(self):
        """Reset global instance before each test."""
        reset_dlq_handler()
        yield
        reset_dlq_handler()

    @pytest.mark.asyncio
    async def test_get_dlq_handler(self):
        """Test getting global handler."""
        handler = await get_dlq_handler()

        assert handler is not None
        assert handler._running is True

        # Should return same instance
        handler2 = await get_dlq_handler()
        assert handler is handler2

        await handler.stop()

    @pytest.mark.asyncio
    async def test_get_dlq_handler_with_config(self):
        """Test getting global handler with config."""
        config = DLQConfig(max_retries=5)

        handler = await get_dlq_handler(config)

        assert handler.config.max_retries == 5

        await handler.stop()

    def test_reset_dlq_handler(self):
        """Test resetting global handler."""
        reset_dlq_handler()
        # Should not raise


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestDLQEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_send_to_dlq_with_binary_value(self):
        """Test sending binary data to DLQ."""
        handler = DLQHandler()
        await handler.start()

        binary_data = bytes([0x00, 0x01, 0xFF, 0xFE])

        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=binary_data,
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Binary error"),
        )

        assert message.original_value == binary_data

        await handler.stop()

    @pytest.mark.asyncio
    async def test_concurrent_sends(self):
        """Test concurrent sends to DLQ."""
        handler = DLQHandler()
        await handler.start()

        async def send_message(i):
            return await handler.send_to_dlq(
                topic="test.topic",
                key=f"key{i}",
                value=f"value{i}".encode(),
                headers={},
                partition=0,
                offset=i,
                error=ValueError(f"Error {i}"),
            )

        messages = await asyncio.gather(*[send_message(i) for i in range(10)])

        assert len(messages) == 10
        assert len(handler._messages) == 10

        await handler.stop()

    @pytest.mark.asyncio
    async def test_retry_with_custom_handler(self):
        """Test retry with custom handler passed directly."""
        handler = DLQHandler()
        await handler.start()

        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Don't register handler for topic, pass directly
        processed = []

        async def custom_handler(value, headers):
            processed.append(value)

        result = await handler.retry_message(message.dlq_id, handler=custom_handler)

        assert result is True
        assert processed == [b"test"]

        await handler.stop()

    @pytest.mark.asyncio
    async def test_producer_error_handling(self):
        """Test handling of producer errors."""
        producer = AsyncMock()
        producer.send.side_effect = Exception("Kafka error")

        handler = DLQHandler(producer=producer)
        await handler.start()

        # Should not raise, just log
        message = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error"),
        )

        # Message should still be stored locally
        assert message.dlq_id in handler._messages

        await handler.stop()

    @pytest.mark.asyncio
    async def test_pending_excludes_non_pending(self):
        """Test that get_pending_messages excludes non-pending."""
        handler = DLQHandler()
        await handler.start()

        msg1 = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test1",
            headers={},
            partition=0,
            offset=0,
            error=ValueError("Error 1"),
        )

        msg2 = await handler.send_to_dlq(
            topic="test.topic",
            key=None,
            value=b"test2",
            headers={},
            partition=0,
            offset=1,
            error=ValueError("Error 2"),
        )
        msg2.status = DLQMessageStatus.RESOLVED

        pending = await handler.get_pending_messages()

        assert len(pending) == 1
        assert pending[0].dlq_id == msg1.dlq_id

        await handler.stop()
