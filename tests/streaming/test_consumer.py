"""
Tests for SignalConsumer.

S39 - Signal Consumer Tests
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.models import ComputedSignal, RawSignal, SignalType, Topics
from app.streaming.consumer import (
    ConsumerConfig,
    ConsumerState,
    ConsumerStats,
    SignalConsumer,
)


class TestConsumerConfig:
    """Tests for ConsumerConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ConsumerConfig()

        assert config.bootstrap_servers == "localhost:9092"
        assert config.group_id == "inspectah-signal-consumer"
        assert config.auto_offset_reset == "earliest"
        assert config.enable_auto_commit is False
        assert config.max_poll_records == 100
        assert config.backpressure_threshold == 1000

    def test_custom_config(self):
        """Test custom configuration."""
        config = ConsumerConfig(
            bootstrap_servers="kafka:9092",
            group_id="custom-group",
            max_poll_records=50,
        )

        assert config.bootstrap_servers == "kafka:9092"
        assert config.group_id == "custom-group"
        assert config.max_poll_records == 50


class TestConsumerState:
    """Tests for ConsumerState enum."""

    def test_state_values(self):
        """Test state values."""
        assert ConsumerState.CREATED.value == "created"
        assert ConsumerState.STARTING.value == "starting"
        assert ConsumerState.RUNNING.value == "running"
        assert ConsumerState.PAUSED.value == "paused"
        assert ConsumerState.STOPPING.value == "stopping"
        assert ConsumerState.STOPPED.value == "stopped"


class TestConsumerStats:
    """Tests for ConsumerStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = ConsumerStats()

        assert stats.messages_processed == 0
        assert stats.messages_failed == 0
        assert stats.commits == 0
        assert stats.lag == 0

    def test_record_processed(self):
        """Test recording processed message."""
        stats = ConsumerStats()

        stats.record_processed(50.0)

        assert stats.messages_processed == 1
        assert stats.processing_time_ms > 0
        assert stats.last_message_at is not None

    def test_record_failure(self):
        """Test recording failure."""
        stats = ConsumerStats()

        stats.record_failure("Parse error")

        assert stats.messages_failed == 1
        assert "Parse error" in stats.errors

    def test_ema_processing_time(self):
        """Test EMA calculation for processing time."""
        stats = ConsumerStats()

        # EMA formula: new = old * 0.9 + value * 0.1
        # Starting from 0, after 5 iterations of 100:
        # 0 -> 10 -> 19 -> 27.1 -> 34.39 -> 40.95
        for time_ms in [100, 100, 100, 100, 100]:
            stats.record_processed(time_ms)

        # Should be around 40 after 5 iterations (converges slowly from 0)
        assert 35 <= stats.processing_time_ms <= 50

    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = ConsumerStats()
        stats.record_processed(50.0)
        stats.record_failure("Error")

        d = stats.to_dict()

        assert d["messages_processed"] == 1
        assert d["messages_failed"] == 1
        assert "avg_processing_time_ms" in d


class TestSignalConsumer:
    """Tests for SignalConsumer."""

    def test_consumer_creation(self):
        """Test creating consumer."""
        consumer = SignalConsumer()

        assert consumer.config is not None
        assert consumer._state == ConsumerState.CREATED
        assert consumer.stats.messages_processed == 0

    def test_consumer_custom_config(self):
        """Test consumer with custom config."""
        config = ConsumerConfig(max_poll_records=50)
        consumer = SignalConsumer(config)

        assert consumer.config.max_poll_records == 50

    def test_register_handler(self):
        """Test registering signal handler."""
        consumer = SignalConsumer()

        async def custom_handler(signal):
            return None

        consumer.register_handler(SignalType.BATTLEGROUND, custom_handler)

        assert SignalType.BATTLEGROUND in consumer._handlers


class TestSignalConsumerAsync:
    """Async tests for SignalConsumer."""

    @pytest.mark.asyncio
    async def test_initialize_mock_mode(self):
        """Test initialization without aiokafka (mock mode)."""
        consumer = SignalConsumer()

        await consumer.initialize()

        assert consumer._state == ConsumerState.RUNNING
        assert consumer.stats.started_at is not None

        await consumer.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using consumer as context manager."""
        async with SignalConsumer() as consumer:
            assert consumer._state == ConsumerState.RUNNING

    @pytest.mark.asyncio
    async def test_process_single(self):
        """Test processing single signal."""
        consumer = SignalConsumer()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
        )

        result = await consumer.process_single(signal)

        assert result is not None
        assert isinstance(result, ComputedSignal)
        assert result.claim_id == "claim-123"
        assert result.value == 0.85

    @pytest.mark.asyncio
    async def test_custom_handler(self):
        """Test using custom handler."""
        handler_called = []

        async def custom_handler(signal):
            handler_called.append(signal)
            return ComputedSignal(
                id=signal.id,
                claim_id=signal.claim_id,
                signal_type=signal.signal_type,
                value=signal.value * 2,  # Double the value
                confidence=0.99,
                domain=signal.domain,
            )

        consumer = SignalConsumer(handler=custom_handler)

        signal = RawSignal(
            claim_id="claim-custom",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        result = await consumer.process_single(signal)

        assert len(handler_called) == 1
        assert result.value == 1.0  # Doubled

    @pytest.mark.asyncio
    async def test_type_specific_handler(self):
        """Test type-specific handler."""
        battleground_results = []
        fragility_results = []

        async def battleground_handler(signal):
            battleground_results.append(signal)
            return ComputedSignal(
                id=signal.id,
                claim_id=signal.claim_id,
                signal_type=signal.signal_type,
                value=signal.value,
                confidence=0.9,
                domain=signal.domain,
            )

        async def fragility_handler(signal):
            fragility_results.append(signal)
            return ComputedSignal(
                id=signal.id,
                claim_id=signal.claim_id,
                signal_type=signal.signal_type,
                value=signal.value,
                confidence=0.8,
                domain=signal.domain,
            )

        consumer = SignalConsumer()
        consumer.register_handler(SignalType.BATTLEGROUND, battleground_handler)
        consumer.register_handler(SignalType.FRAGILITY, fragility_handler)

        # Process battleground signal
        bg_signal = RawSignal(
            claim_id="claim-bg",
            signal_type=SignalType.BATTLEGROUND,
            value=0.75,
        )
        result_bg = await consumer.process_single(bg_signal)

        # Process fragility signal
        fg_signal = RawSignal(
            claim_id="claim-fg",
            signal_type=SignalType.FRAGILITY,
            value=0.65,
        )
        result_fg = await consumer.process_single(fg_signal)

        assert len(battleground_results) == 1
        assert len(fragility_results) == 1
        assert result_bg.confidence == 0.9
        assert result_fg.confidence == 0.8

    @pytest.mark.asyncio
    async def test_pause_resume(self):
        """Test pause and resume functionality."""
        consumer = SignalConsumer()
        await consumer.initialize()

        assert consumer._state == ConsumerState.RUNNING

        consumer.pause()
        assert consumer._state == ConsumerState.PAUSED
        assert consumer._paused is True

        consumer.resume()
        assert consumer._state == ConsumerState.RUNNING
        assert consumer._paused is False

        await consumer.close()

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting consumer stats."""
        consumer = SignalConsumer()
        await consumer.initialize()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
        )

        await consumer.process_single(signal)
        stats = consumer.get_stats()

        assert "messages_processed" in stats
        assert "started_at" in stats

        await consumer.close()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping consumer."""
        consumer = SignalConsumer()
        await consumer.initialize()

        assert consumer._running is False  # Not started via start()

        await consumer.stop()

        assert consumer._running is False

        await consumer.close()


class TestConsumerStatsEdgeCases:
    """Edge case tests for ConsumerStats."""

    def test_error_list_trimming(self):
        """Test error list is trimmed when exceeding 100."""
        stats = ConsumerStats()

        # Add 150 errors
        for i in range(150):
            stats.record_failure(f"Error {i}")

        # Should only keep last 100
        assert len(stats.errors) == 100
        assert stats.messages_failed == 150
        # Should have errors 50-149
        assert "Error 50" in stats.errors
        assert "Error 149" in stats.errors


class TestSignalConsumerKafkaInit:
    """Tests for SignalConsumer with Kafka initialization."""

    @pytest.mark.asyncio
    async def test_initialize_with_kafka(self):
        """Test initialization with mocked aiokafka."""
        mock_kafka_consumer = AsyncMock()
        mock_kafka_consumer.start = AsyncMock()
        mock_kafka_consumer.stop = AsyncMock()

        with patch.dict("sys.modules", {"aiokafka": MagicMock()}):
            with patch("app.streaming.consumer.AIOKafkaConsumer", return_value=mock_kafka_consumer, create=True):
                # Need to re-import to pick up the mock
                import importlib
                import app.streaming.consumer as consumer_module

                # The module already has ImportError fallback, so test initialization error
                consumer = SignalConsumer()
                consumer._state = ConsumerState.CREATED

                # Manually set consumer to test close path
                consumer._consumer = mock_kafka_consumer
                await consumer.close()

                mock_kafka_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_already_running(self):
        """Test initialize when already running."""
        consumer = SignalConsumer()
        await consumer.initialize()

        # Should not reinitialize
        consumer._state = ConsumerState.RUNNING
        await consumer.initialize()

        await consumer.close()

    @pytest.mark.asyncio
    async def test_get_consumer_singleton(self):
        """Test get_consumer returns singleton."""
        from app.streaming.consumer import get_consumer, _consumer
        import app.streaming.consumer as consumer_module

        # Reset singleton
        consumer_module._consumer = None

        consumer1 = await get_consumer()
        consumer2 = await get_consumer()

        assert consumer1 is consumer2

        # Cleanup
        consumer_module._consumer = None

    @pytest.mark.asyncio
    async def test_poll_and_process_mock_mode(self):
        """Test _poll_and_process in mock mode (no consumer)."""
        consumer = SignalConsumer()
        consumer._consumer = None  # Mock mode

        # Should just sleep and return
        await consumer._poll_and_process()

    @pytest.mark.asyncio
    async def test_poll_and_process_with_consumer(self):
        """Test _poll_and_process with mocked Kafka consumer."""
        consumer = SignalConsumer()

        mock_kafka = AsyncMock()
        mock_kafka.getmany = AsyncMock(return_value={})
        consumer._consumer = mock_kafka

        # Enable auto_commit to skip commit logic
        consumer.config.enable_auto_commit = True

        await consumer._poll_and_process()

        mock_kafka.getmany.assert_called_once()

    @pytest.mark.asyncio
    async def test_poll_and_process_backpressure(self):
        """Test _poll_and_process with backpressure."""
        consumer = SignalConsumer()
        consumer.config.backpressure_threshold = 0  # Trigger backpressure

        mock_kafka = AsyncMock()
        consumer._consumer = mock_kafka

        # Add item to pending queue
        await consumer._pending_messages.put("test")

        await consumer._poll_and_process()

        # getmany should not be called due to backpressure
        mock_kafka.getmany.assert_not_called()

    @pytest.mark.asyncio
    async def test_poll_and_process_with_messages(self):
        """Test _poll_and_process with actual messages."""
        consumer = SignalConsumer()

        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        mock_record = MagicMock()
        mock_record.value = signal.to_json().encode("utf-8")

        topic_partition = MagicMock()
        mock_kafka = AsyncMock()
        mock_kafka.getmany = AsyncMock(return_value={topic_partition: [mock_record]})
        mock_kafka.commit = AsyncMock()
        consumer._consumer = mock_kafka
        consumer._last_commit = 0  # Force commit

        await consumer._poll_and_process()

        assert consumer.stats.messages_processed == 1

    @pytest.mark.asyncio
    async def test_maybe_commit_auto_commit(self):
        """Test _maybe_commit with auto_commit enabled."""
        consumer = SignalConsumer()
        consumer.config.enable_auto_commit = True

        mock_kafka = AsyncMock()
        consumer._consumer = mock_kafka

        await consumer._maybe_commit()

        # Should not call commit
        mock_kafka.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_commit(self):
        """Test _commit method."""
        consumer = SignalConsumer()

        mock_kafka = AsyncMock()
        mock_kafka.commit = AsyncMock()
        consumer._consumer = mock_kafka

        await consumer._commit()

        mock_kafka.commit.assert_called_once()
        assert consumer.stats.commits == 1

    @pytest.mark.asyncio
    async def test_commit_no_consumer(self):
        """Test _commit with no consumer."""
        consumer = SignalConsumer()
        consumer._consumer = None

        # Should not raise
        await consumer._commit()

        assert consumer.stats.commits == 0

    @pytest.mark.asyncio
    async def test_commit_failure(self):
        """Test _commit handles failure."""
        consumer = SignalConsumer()

        mock_kafka = AsyncMock()
        mock_kafka.commit = AsyncMock(side_effect=Exception("Commit failed"))
        consumer._consumer = mock_kafka

        # Should not raise
        await consumer._commit()

        # Commit count should not increase on failure
        assert consumer.stats.commits == 0

    @pytest.mark.asyncio
    async def test_get_lag_no_consumer(self):
        """Test get_lag with no consumer."""
        consumer = SignalConsumer()
        consumer._consumer = None

        lag = await consumer.get_lag()

        assert lag == {}

    @pytest.mark.asyncio
    async def test_get_lag_with_consumer(self):
        """Test get_lag with mocked consumer."""
        consumer = SignalConsumer()

        # Create mock topic partition
        mock_tp = MagicMock()
        mock_tp.topic = "signals.raw"
        mock_tp.partition = 0

        mock_kafka = AsyncMock()
        mock_kafka.assignment = MagicMock(return_value=[mock_tp])
        mock_kafka.position = AsyncMock(return_value=50)
        mock_kafka.end_offsets = AsyncMock(return_value={mock_tp: 100})
        consumer._consumer = mock_kafka

        lag = await consumer.get_lag()

        assert lag == {"signals.raw-0": 50}
        assert consumer.stats.lag == 50

    @pytest.mark.asyncio
    async def test_get_lag_error(self):
        """Test get_lag handles errors."""
        consumer = SignalConsumer()

        mock_kafka = AsyncMock()
        mock_kafka.assignment = MagicMock(side_effect=Exception("Assignment error"))
        consumer._consumer = mock_kafka

        lag = await consumer.get_lag()

        assert lag == {}

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        """Test start method with quick stop."""
        consumer = SignalConsumer()

        # Start in background and stop quickly
        async def stop_after_delay():
            await asyncio.sleep(0.2)
            await consumer.stop()

        start_task = asyncio.create_task(consumer.start())
        stop_task = asyncio.create_task(stop_after_delay())

        await asyncio.wait_for(asyncio.gather(start_task, stop_task), timeout=5.0)

        assert consumer._state == ConsumerState.STOPPED

    @pytest.mark.asyncio
    async def test_start_paused(self):
        """Test start with paused state."""
        consumer = SignalConsumer()

        async def pause_and_stop():
            await asyncio.sleep(0.1)
            consumer.pause()
            await asyncio.sleep(0.2)
            await consumer.stop()

        start_task = asyncio.create_task(consumer.start())
        control_task = asyncio.create_task(pause_and_stop())

        await asyncio.wait_for(asyncio.gather(start_task, control_task), timeout=5.0)

    @pytest.mark.asyncio
    async def test_start_cancelled(self):
        """Test start cancelled."""
        consumer = SignalConsumer()

        start_task = asyncio.create_task(consumer.start())
        await asyncio.sleep(0.1)
        start_task.cancel()

        try:
            await start_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_with_error(self):
        """Test start with error in poll_and_process."""
        consumer = SignalConsumer()

        # Make poll fail once, then stop
        call_count = 0

        async def failing_poll():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Poll error")
            await consumer.stop()

        with patch.object(consumer, "_poll_and_process", side_effect=failing_poll):
            await consumer.start()

        assert consumer.stats.messages_failed >= 1

    @pytest.mark.asyncio
    async def test_poll_error_handling(self):
        """Test poll error raises exception."""
        consumer = SignalConsumer()

        mock_kafka = AsyncMock()
        mock_kafka.getmany = AsyncMock(side_effect=Exception("Poll failed"))
        consumer._consumer = mock_kafka

        with pytest.raises(Exception, match="Poll failed"):
            await consumer._poll_and_process()


class TestSignalConsumerWithMockKafka:
    """Tests for SignalConsumer with mocked Kafka."""

    @pytest.fixture
    def mock_record(self):
        """Create mock Kafka record."""
        signal = RawSignal(
            claim_id="claim-mock",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
        )
        record = MagicMock()
        record.value = signal.to_json().encode("utf-8")
        record.topic = Topics.SIGNALS_RAW
        record.partition = 0
        record.offset = 100
        return record

    @pytest.mark.asyncio
    async def test_process_message(self, mock_record):
        """Test processing a Kafka message."""
        consumer = SignalConsumer()
        await consumer.initialize()

        result = await consumer._process_message(mock_record)

        assert result is not None
        assert consumer.stats.messages_processed == 1

        await consumer.close()

    @pytest.mark.asyncio
    async def test_process_invalid_json(self):
        """Test handling invalid JSON message."""
        invalid_record = MagicMock()
        invalid_record.value = b"not valid json"

        consumer = SignalConsumer()
        await consumer.initialize()

        result = await consumer._process_message(invalid_record)

        assert result is None
        assert consumer.stats.messages_failed == 1

        await consumer.close()

    @pytest.mark.asyncio
    async def test_process_invalid_signal(self):
        """Test handling invalid signal data."""
        invalid_record = MagicMock()
        invalid_record.value = json.dumps({"invalid": "data"}).encode("utf-8")

        consumer = SignalConsumer()
        await consumer.initialize()

        result = await consumer._process_message(invalid_record)

        assert result is None
        assert consumer.stats.messages_failed == 1

        await consumer.close()

    @pytest.mark.asyncio
    async def test_handler_exception(self, mock_record):
        """Test handling exception in message handler."""
        async def failing_handler(signal):
            raise Exception("Handler failed")

        consumer = SignalConsumer(handler=failing_handler)
        await consumer.initialize()

        result = await consumer._process_message(mock_record)

        assert result is None
        assert consumer.stats.messages_failed == 1

        await consumer.close()
