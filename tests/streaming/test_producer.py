"""
Tests for SignalProducer.

S39 - Signal Producer Tests
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.models import RawSignal, SignalBatch, SignalEnvelope, SignalType, Topics
from app.streaming.producer import (
    ProducerConfig,
    ProducerStats,
    SignalProducer,
)


class TestProducerConfig:
    """Tests for ProducerConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ProducerConfig()

        assert config.bootstrap_servers == "localhost:9092"
        assert config.client_id == "inspectah-signal-producer"
        assert config.acks == "all"
        assert config.retries == 3
        assert config.batch_size == 100
        assert config.enable_idempotence is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = ProducerConfig(
            bootstrap_servers="kafka:9092",
            retries=5,
            batch_size=50,
        )

        assert config.bootstrap_servers == "kafka:9092"
        assert config.retries == 5
        assert config.batch_size == 50


class TestProducerStats:
    """Tests for ProducerStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = ProducerStats()

        assert stats.messages_sent == 0
        assert stats.messages_failed == 0
        assert stats.retries == 0

    def test_record_success(self):
        """Test recording successful send."""
        stats = ProducerStats()

        stats.record_success(count=5, bytes_size=1000)

        assert stats.messages_sent == 5
        assert stats.bytes_sent == 1000
        assert stats.last_send_at is not None

    def test_record_failure(self):
        """Test recording failure."""
        stats = ProducerStats()

        stats.record_failure("Connection error")

        assert stats.messages_failed == 1
        assert "Connection error" in stats.errors

    def test_error_limit(self):
        """Test error list is limited."""
        stats = ProducerStats()

        for i in range(150):
            stats.record_failure(f"Error {i}")

        assert len(stats.errors) == 100
        assert stats.messages_failed == 150

    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = ProducerStats()
        stats.record_success(10, 500)
        stats.record_failure("Test error")

        d = stats.to_dict()

        assert d["messages_sent"] == 10
        assert d["messages_failed"] == 1
        assert d["bytes_sent"] == 500
        assert "recent_errors" in d


class TestSignalProducer:
    """Tests for SignalProducer."""

    def test_producer_creation(self):
        """Test creating producer."""
        producer = SignalProducer()

        assert producer.config is not None
        assert producer.stats.messages_sent == 0
        assert not producer._initialized

    def test_producer_custom_config(self):
        """Test producer with custom config."""
        config = ProducerConfig(retries=5)
        producer = SignalProducer(config)

        assert producer.config.retries == 5

    def test_producer_callbacks(self):
        """Test producer with callbacks."""
        on_success = MagicMock()
        on_error = MagicMock()

        producer = SignalProducer(on_success=on_success, on_error=on_error)

        assert producer._on_success == on_success
        assert producer._on_error == on_error


class TestSignalProducerAsync:
    """Async tests for SignalProducer."""

    @pytest.mark.asyncio
    async def test_initialize_mock_mode(self):
        """Test initialization without aiokafka (mock mode)."""
        producer = SignalProducer()

        # Should not raise even without aiokafka
        await producer.initialize()

        assert producer._initialized

        await producer.close()

    @pytest.mark.asyncio
    async def test_send_mock_mode(self):
        """Test sending in mock mode."""
        producer = SignalProducer()
        await producer.initialize()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
        )

        result = await producer.send(signal)

        assert result is True
        assert producer.stats.messages_sent == 1

        await producer.close()

    @pytest.mark.asyncio
    async def test_send_batch_mock_mode(self):
        """Test sending batch in mock mode."""
        producer = SignalProducer()
        await producer.initialize()

        batch = SignalBatch()
        for i in range(5):
            batch.add(RawSignal(
                claim_id=f"claim-{i}",
                signal_type=SignalType.BATTLEGROUND,
                value=i * 0.1,
            ))

        count = await producer.send_batch(batch)

        assert count == 5
        assert producer.stats.messages_sent == 5
        assert producer.stats.batches_sent == 1

        await producer.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using producer as context manager."""
        async with SignalProducer() as producer:
            assert producer._initialized

            signal = RawSignal(
                claim_id="claim-123",
                signal_type=SignalType.FRAGILITY,
                value=0.5,
            )

            result = await producer.send(signal)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting producer stats."""
        producer = SignalProducer()
        await producer.initialize()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
        )

        await producer.send(signal)
        stats = producer.get_stats()

        assert stats["messages_sent"] == 1
        assert stats["messages_failed"] == 0

        await producer.close()

    @pytest.mark.asyncio
    async def test_success_callback(self):
        """Test success callback is called."""
        callback_results = []

        def on_success(envelope):
            callback_results.append(envelope)

        producer = SignalProducer(on_success=on_success)
        await producer.initialize()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
        )

        await producer.send(signal)

        assert len(callback_results) == 1
        assert callback_results[0].key == "claim-123"

        await producer.close()

    @pytest.mark.asyncio
    async def test_send_empty_batch(self):
        """Test sending empty batch."""
        producer = SignalProducer()
        await producer.initialize()

        batch = SignalBatch()
        count = await producer.send_batch(batch)

        assert count == 0

        await producer.close()

    @pytest.mark.asyncio
    async def test_flush(self):
        """Test flush method."""
        producer = SignalProducer()
        await producer.initialize()

        # Should not raise
        await producer.flush()

        await producer.close()


class TestProducerStatsEdgeCases:
    """Edge case tests for ProducerStats."""

    def test_record_multiple_successes(self):
        """Test recording multiple successful sends."""
        stats = ProducerStats()

        stats.record_success(5, 1000)
        stats.record_success(10, 2000)
        stats.record_success(3, 500)

        assert stats.messages_sent == 18
        assert stats.bytes_sent == 3500
        assert stats.last_send_at is not None

    def test_retries_field(self):
        """Test retries field is incremented."""
        stats = ProducerStats()

        # Retries field is manually incremented
        stats.retries += 1
        stats.retries += 1

        assert stats.retries == 2

    def test_dlq_messages_field(self):
        """Test dlq_messages field."""
        stats = ProducerStats()

        stats.dlq_messages += 1

        assert stats.dlq_messages == 1

    def test_error_list_trimming(self):
        """Test error list is trimmed when exceeding 100."""
        stats = ProducerStats()

        # Add 150 errors
        for i in range(150):
            stats.record_failure(f"Error {i}")

        # Should only keep last 100
        assert len(stats.errors) == 100
        assert stats.messages_failed == 150


class TestSignalProducerKafkaInit:
    """Tests for SignalProducer with Kafka initialization."""

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialize when already initialized."""
        producer = SignalProducer()
        await producer.initialize()

        # Should not reinitialize
        await producer.initialize()

        assert producer._initialized is True

        await producer.close()

    @pytest.mark.asyncio
    async def test_close_with_mock_producer(self):
        """Test close with mock Kafka producer."""
        producer = SignalProducer()
        mock_kafka = AsyncMock()
        producer._producer = mock_kafka
        producer._initialized = True

        await producer.close()

        mock_kafka.stop.assert_called_once()
        assert producer._initialized is False

    @pytest.mark.asyncio
    async def test_flush_with_producer(self):
        """Test flush with mock Kafka producer."""
        producer = SignalProducer()
        mock_kafka = AsyncMock()
        producer._producer = mock_kafka
        producer._initialized = True

        await producer.flush()

        mock_kafka.flush.assert_called_once()

        await producer.close()

    @pytest.mark.asyncio
    async def test_do_send_with_producer(self):
        """Test _do_send with mock Kafka producer."""
        producer = SignalProducer()
        mock_kafka = AsyncMock()
        mock_kafka.send_and_wait = AsyncMock()
        producer._producer = mock_kafka

        envelope = SignalEnvelope(
            topic="test.topic",
            key="test-key",
            payload={"test": "data"},
            headers={"header": "value"},
        )

        await producer._do_send(envelope)

        mock_kafka.send_and_wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_dlq_failure(self):
        """Test _send_to_dlq when DLQ send fails."""
        producer = SignalProducer()
        producer._initialized = True

        # Make _do_send fail
        async def failing_send(envelope):
            if envelope.topic == Topics.SIGNALS_DLQ:
                raise Exception("DLQ send failed")

        with patch.object(producer, "_do_send", side_effect=failing_send):
            envelope = SignalEnvelope(
                topic="test.topic",
                key="test-key",
                payload={"test": "data"},
            )

            # Should not raise, just log the error
            await producer._send_to_dlq(envelope, Exception("Original error"))

    @pytest.mark.asyncio
    async def test_get_producer_singleton(self):
        """Test get_producer returns singleton."""
        from app.streaming.producer import get_producer
        import app.streaming.producer as producer_module

        # Reset singleton
        producer_module._producer = None

        producer1 = await get_producer()
        producer2 = await get_producer()

        assert producer1 is producer2

        # Cleanup
        await producer1.close()
        producer_module._producer = None

    @pytest.mark.asyncio
    async def test_publish_signal(self):
        """Test publish_signal convenience function."""
        from app.streaming.producer import publish_signal
        import app.streaming.producer as producer_module

        # Reset singleton
        producer_module._producer = None

        signal = RawSignal(
            claim_id="claim-publish",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        result = await publish_signal(signal)

        assert result is True

        # Cleanup
        if producer_module._producer:
            await producer_module._producer.close()
        producer_module._producer = None


class TestSignalProducerWithMockKafka:
    """Tests for SignalProducer with mocked Kafka."""

    @pytest.fixture
    def mock_kafka_producer(self):
        """Create mock Kafka producer."""
        mock = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.send_and_wait = AsyncMock()
        mock.flush = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_send_with_kafka(self, mock_kafka_producer):
        """Test sending with real Kafka mock."""
        with patch("app.streaming.producer.SignalProducer._do_send", new_callable=AsyncMock) as mock_send:
            producer = SignalProducer()
            producer._initialized = True

            signal = RawSignal(
                claim_id="claim-123",
                signal_type=SignalType.BATTLEGROUND,
                value=0.75,
            )

            result = await producer.send(signal)

            assert result is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry logic on failure."""
        call_count = 0

        async def failing_send(envelope):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            # Success on 3rd try

        with patch.object(SignalProducer, "_do_send", side_effect=failing_send):
            config = ProducerConfig(retries=3, retry_backoff_ms=10)
            producer = SignalProducer(config)
            producer._initialized = True

            signal = RawSignal(
                claim_id="claim-retry",
                signal_type=SignalType.FRAGILITY,
                value=0.5,
            )

            result = await producer.send(signal)

            assert result is True
            assert call_count == 3
            assert producer.stats.retries == 2

    @pytest.mark.asyncio
    async def test_dlq_on_all_retries_fail(self):
        """Test DLQ when all retries fail."""
        dlq_messages = []

        async def always_fail(envelope):
            if envelope.topic == Topics.SIGNALS_DLQ:
                dlq_messages.append(envelope)
            else:
                raise Exception("Permanent failure")

        with patch.object(SignalProducer, "_do_send", side_effect=always_fail):
            config = ProducerConfig(retries=2, retry_backoff_ms=10)
            producer = SignalProducer(config)
            producer._initialized = True

            signal = RawSignal(
                claim_id="claim-dlq",
                signal_type=SignalType.SILENCE_RADAR,
                value=0.9,
            )

            result = await producer.send(signal)

            assert result is False
            assert producer.stats.messages_failed == 1
            assert producer.stats.dlq_messages == 1
            assert len(dlq_messages) == 1

    @pytest.mark.asyncio
    async def test_error_callback(self):
        """Test error callback is called on failure."""
        error_results = []

        def on_error(envelope, error):
            error_results.append((envelope, error))

        async def always_fail(envelope):
            if envelope.topic != Topics.SIGNALS_DLQ:
                raise Exception("Test error")

        with patch.object(SignalProducer, "_do_send", side_effect=always_fail):
            config = ProducerConfig(retries=0, retry_backoff_ms=10)
            producer = SignalProducer(config, on_error=on_error)
            producer._initialized = True

            signal = RawSignal(
                claim_id="claim-error",
                signal_type=SignalType.BATTLEGROUND,
                value=0.5,
            )

            await producer.send(signal)

            assert len(error_results) == 1
            assert error_results[0][0].key == "claim-error"
            assert "Test error" in str(error_results[0][1])
