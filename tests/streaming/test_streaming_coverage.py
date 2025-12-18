"""
S39 - Streaming Coverage Tests

Comprehensive tests to cover missing lines in streaming modules.
Focuses on error handling paths and edge cases.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ops.dashboard_service import ActiveAlert, AlertSeverity, reset_dashboard
from app.streaming.alert_streamer import (
    AlertEvent,
    AlertEventType,
    AlertStreamer,
    reset_alert_streamer,
)
from app.streaming.backpressure import (
    BackpressureConfig,
    BackpressureController,
    reset_backpressure_controller,
)
from app.streaming.consumer import ConsumerConfig, SignalConsumer
from app.streaming.dlq_handler import (
    DLQConfig,
    DLQHandler,
    FailureReason,
    reset_dlq_handler,
)
from app.streaming.models import RawSignal, SignalType
from app.streaming.producer import ProducerConfig, SignalProducer


# ============================================================================
# Consumer Coverage Tests
# ============================================================================


class TestConsumerInitializationErrors:
    """Tests for consumer initialization error paths (lines 179-201)."""

    @pytest.mark.asyncio
    async def test_initialize_kafka_exception(self):
        """Test consumer initialization handles Kafka exceptions (lines 198-201)."""
        consumer = SignalConsumer()

        # Mock the aiokafka import to make AIOKafkaConsumer available
        mock_kafka_consumer = AsyncMock()
        mock_kafka_consumer.start = AsyncMock(
            side_effect=Exception("Kafka connection failed")
        )

        # Create a mock module with AIOKafkaConsumer
        mock_aiokafka = MagicMock()
        mock_aiokafka.AIOKafkaConsumer = MagicMock(return_value=mock_kafka_consumer)

        with patch.dict("sys.modules", {"aiokafka": mock_aiokafka}):
            # Force reimport by deleting state flag
            consumer._state = consumer._state.__class__.CREATED

            with pytest.raises(Exception, match="Kafka connection failed"):
                await consumer.initialize()

            # Verify state is set to STOPPED on error
            assert consumer._state.value == "stopped"

    @pytest.mark.asyncio
    async def test_initialize_with_real_kafka_mock(self):
        """Test successful Kafka initialization (lines 179-192)."""
        consumer = SignalConsumer()

        # Create proper mock for successful init
        mock_kafka_consumer = AsyncMock()
        mock_kafka_consumer.start = AsyncMock()

        # Create mock module
        mock_aiokafka = MagicMock()
        mock_aiokafka.AIOKafkaConsumer = MagicMock(return_value=mock_kafka_consumer)

        with patch.dict("sys.modules", {"aiokafka": mock_aiokafka}):
            # Force reimport state
            consumer._state = consumer._state.__class__.CREATED

            await consumer.initialize()

            # Verify successful initialization
            assert consumer._state.value == "running"
            assert consumer._consumer is mock_kafka_consumer
            mock_kafka_consumer.start.assert_called_once()

            # Cleanup
            await consumer.close()


# ============================================================================
# Producer Coverage Tests
# ============================================================================


class TestProducerInitializationErrors:
    """Tests for producer initialization error paths (lines 133-151)."""

    @pytest.mark.asyncio
    async def test_initialize_kafka_exception(self):
        """Test producer initialization handles Kafka exceptions (lines 149-151)."""
        producer = SignalProducer()

        # Mock the aiokafka import
        mock_kafka_producer = AsyncMock()
        mock_kafka_producer.start = AsyncMock(
            side_effect=Exception("Kafka producer failed to start")
        )

        # Create mock module
        mock_aiokafka = MagicMock()
        mock_aiokafka.AIOKafkaProducer = MagicMock(return_value=mock_kafka_producer)

        with patch.dict("sys.modules", {"aiokafka": mock_aiokafka}):
            with pytest.raises(Exception, match="Kafka producer failed to start"):
                await producer.initialize()

            # Verify initialization failed
            assert not producer._initialized

    @pytest.mark.asyncio
    async def test_initialize_with_real_kafka_mock(self):
        """Test successful Kafka producer initialization (lines 133-144)."""
        producer = SignalProducer()

        # Create proper mock for successful init
        mock_kafka_producer = AsyncMock()
        mock_kafka_producer.start = AsyncMock()

        # Create mock module
        mock_aiokafka = MagicMock()
        mock_aiokafka.AIOKafkaProducer = MagicMock(return_value=mock_kafka_producer)

        with patch.dict("sys.modules", {"aiokafka": mock_aiokafka}):
            await producer.initialize()

            # Verify successful initialization
            assert producer._initialized
            assert producer._producer is mock_kafka_producer
            mock_kafka_producer.start.assert_called_once()

            # Cleanup
            await producer.close()


# ============================================================================
# Alert Streamer Coverage Tests
# ============================================================================


class TestAlertStreamerErrorPaths:
    """Tests for alert streamer error paths (lines 180-181, 437-438)."""

    @pytest.mark.asyncio
    async def test_heartbeat_loop_exception_handling(self):
        """Test heartbeat loop handles exceptions gracefully (lines 180-181)."""
        reset_dashboard()
        reset_alert_streamer()

        streamer = AlertStreamer(heartbeat_interval_seconds=0.1)
        await streamer.start()

        # Patch _send_heartbeat to raise exception
        original_send_heartbeat = streamer._send_heartbeat

        call_count = 0

        async def failing_heartbeat():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Heartbeat send failed")
            # Succeed on subsequent calls
            await original_send_heartbeat()

        streamer._send_heartbeat = failing_heartbeat

        # Let it run and handle the error
        await asyncio.sleep(0.3)

        # Streamer should still be running
        assert streamer._running

        await streamer.stop()

    @pytest.mark.asyncio
    async def test_queue_full_warning(self):
        """Test queue full handling logs warning (lines 437-438)."""
        reset_dashboard()
        reset_alert_streamer()

        async with AlertStreamer() as streamer:
            # Create subscription with matching filter
            sub_id = await streamer.subscribe(
                severities={AlertSeverity.ERROR}
            )

            # Create a limited-size queue to make it easier to fill
            original_queue = streamer._event_queues[sub_id]
            small_queue = asyncio.Queue(maxsize=2)
            streamer._event_queues[sub_id] = small_queue

            # Fill the small queue
            for i in range(2):
                event = AlertEvent(
                    event_id=f"fill_{i}",
                    event_type=AlertEventType.FIRED,
                    alert=None,
                    timestamp=datetime.now(timezone.utc),
                )
                await small_queue.put(event)

            # Now fire a matching alert - should trigger queue full warning at line 437-438
            alert = ActiveAlert(
                alert_id="test_alert",
                name="queue_full_test",
                severity=AlertSeverity.ERROR,
                message="Testing queue full",
                component="test",
                started_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )

            event = AlertEvent(
                event_id="overflow",
                event_type=AlertEventType.FIRED,
                alert=alert,
                timestamp=datetime.now(timezone.utc),
            )

            # Trigger broadcast which will hit the queue full exception
            sent_count = await streamer._broadcast_event(event)

            # Should handle gracefully (0 sent to full queue)
            assert sent_count == 0


# ============================================================================
# Backpressure Coverage Tests
# ============================================================================


class TestBackpressureRecoveryLoopErrors:
    """Tests for backpressure recovery loop error handling (lines 363-364)."""

    @pytest.mark.asyncio
    async def test_recovery_loop_runtime_error(self):
        """Test recovery loop handles RuntimeError (line 363-364)."""
        reset_backpressure_controller()

        config = BackpressureConfig(
            recovery_check_interval_seconds=0.05,
            lag_recovery_threshold=50
        )
        controller = BackpressureController(config)
        await controller.start()

        # Set conditions that will trigger the else path on line 357-359
        controller.metrics.current_state = controller.metrics.current_state.__class__.RECOVERING
        controller.metrics.current_lag = 100  # ABOVE recovery threshold to trigger _evaluate_state
        controller.metrics.current_rate_percent = 50.0

        # Patch _evaluate_state to raise error then succeed
        original_evaluate = controller._evaluate_state
        error_raised = False

        async def failing_evaluate():
            nonlocal error_raised
            if not error_raised:
                error_raised = True
                # This will hit line 363-364
                raise RuntimeError("Recovery evaluation failed")
            await original_evaluate()

        controller._evaluate_state = failing_evaluate

        # Wait for recovery loop to run and hit the error
        await asyncio.sleep(0.15)

        # Verify error was handled
        assert error_raised
        assert controller._running

        await controller.stop()
        reset_backpressure_controller()

    @pytest.mark.asyncio
    async def test_recovery_loop_value_error(self):
        """Test recovery loop handles ValueError (line 363-364)."""
        reset_backpressure_controller()

        config = BackpressureConfig(
            recovery_check_interval_seconds=0.05,
            lag_recovery_threshold=50
        )
        controller = BackpressureController(config)
        await controller.start()

        # Force into recovery state with lag ABOVE threshold
        controller.metrics.current_state = controller.metrics.current_state.__class__.RECOVERING
        controller.metrics.current_lag = 100  # Above recovery threshold

        # Patch to raise ValueError
        error_raised = False

        async def failing_eval():
            nonlocal error_raised
            if not error_raised:
                error_raised = True
                raise ValueError("Invalid value in recovery")

        controller._evaluate_state = failing_eval

        # Let recovery loop run
        await asyncio.sleep(0.15)

        # Should still be running despite error
        assert error_raised
        assert controller._running

        await controller.stop()
        reset_backpressure_controller()

    @pytest.mark.asyncio
    async def test_recovery_loop_key_error(self):
        """Test recovery loop handles KeyError (line 363-364)."""
        reset_backpressure_controller()

        config = BackpressureConfig(
            recovery_check_interval_seconds=0.05,
            lag_recovery_threshold=50
        )
        controller = BackpressureController(config)
        await controller.start()

        # Force recovery state with lag ABOVE threshold to trigger _evaluate_state call
        controller.metrics.current_state = controller.metrics.current_state.__class__.RECOVERING
        controller.metrics.current_lag = 100  # Above recovery threshold
        controller.metrics.current_rate_percent = 10.0

        # Patch to raise KeyError during recovery evaluation
        original_eval = controller._evaluate_state
        error_raised = False

        async def key_error_eval():
            nonlocal error_raised
            if not error_raised:
                error_raised = True
                # This will hit the except (RuntimeError, ValueError, KeyError) on line 363-364
                raise KeyError("Missing key in recovery")
            await original_eval()

        controller._evaluate_state = key_error_eval

        # Let recovery loop run
        await asyncio.sleep(0.15)

        # Verify error was caught and handled
        assert error_raised
        assert controller._running

        await controller.stop()
        reset_backpressure_controller()


# ============================================================================
# DLQ Handler Coverage Tests
# ============================================================================


class TestDLQAutoRetryLoopErrors:
    """Tests for DLQ auto-retry loop error handling (lines 540-541)."""

    @pytest.mark.asyncio
    async def test_auto_retry_loop_exception(self):
        """Test auto-retry loop handles exceptions gracefully (lines 540-541)."""
        reset_dlq_handler()

        config = DLQConfig(
            auto_retry=True,
            auto_retry_interval_seconds=0.1,
            max_retries=2,
        )
        handler = DLQHandler(config)
        await handler.start()

        # Add a message to DLQ
        error = ValueError("Test error")
        message = await handler.send_to_dlq(
            topic="test.topic",
            key="test_key",
            value=b"test data",
            headers={},
            partition=0,
            offset=100,
            error=error,
            failure_reason=FailureReason.PROCESSING_ERROR,
        )

        # Patch get_pending_messages to raise exception once
        original_get_pending = handler.get_pending_messages
        exception_raised = False

        async def failing_get_pending(*args, **kwargs):
            nonlocal exception_raised
            if not exception_raised:
                exception_raised = True
                raise RuntimeError("Failed to get pending messages")
            return await original_get_pending(*args, **kwargs)

        handler.get_pending_messages = failing_get_pending

        # Let auto-retry loop run and handle the error
        await asyncio.sleep(0.3)

        # Handler should still be running
        assert handler._running
        # Exception should have been caught and handled
        assert exception_raised

        await handler.stop()
        reset_dlq_handler()


# ============================================================================
# Integration Tests
# ============================================================================


class TestStreamingModulesIntegration:
    """Integration tests covering edge cases across modules."""

    @pytest.mark.asyncio
    async def test_consumer_with_backpressure_and_dlq(self):
        """Test consumer working with backpressure and DLQ handlers."""
        # Setup components
        consumer = SignalConsumer()
        await consumer.initialize()

        controller = BackpressureController()
        await controller.start()

        handler = DLQHandler()
        await handler.start()

        # Simulate processing with backpressure
        await controller.update_lag(500)
        should_process = await controller.should_process()
        assert should_process

        # Test DLQ integration
        error = Exception("Processing failed")
        await handler.send_to_dlq(
            topic="signals.raw",
            key="test",
            value=b"data",
            headers={},
            partition=0,
            offset=0,
            error=error,
        )

        stats = await handler.get_stats()
        assert stats.total_messages == 1

        # Cleanup
        await consumer.close()
        await controller.stop()
        await handler.stop()

    @pytest.mark.asyncio
    async def test_producer_with_retry_and_dlq(self):
        """Test producer retry mechanism with DLQ fallback."""
        config = ProducerConfig(retries=2, retry_backoff_ms=10)
        producer = SignalProducer(config)

        # Mock _do_send to fail all retries, but succeed for DLQ
        attempt_count = 0

        async def failing_send(envelope):
            nonlocal attempt_count
            # Let DLQ messages through to avoid infinite recursion
            if envelope.topic == "signals.dlq":
                return
            attempt_count += 1
            raise Exception(f"Send failed (attempt {attempt_count})")

        # Initialize and test
        await producer.initialize()

        with patch.object(producer, "_do_send", side_effect=failing_send):
            signal = RawSignal(
                claim_id="retry_test",
                signal_type=SignalType.LIES_IN_CIRCULATION,
                value=0.85,
            )

            result = await producer.send(signal)

            # Should fail after all retries
            assert result is False
            # Should have tried 3 times (initial + 2 retries)
            assert attempt_count == 3
            # Should have recorded failure
            assert producer.stats.messages_failed == 1
            # Should have sent to DLQ
            assert producer.stats.dlq_messages == 1

        await producer.close()

    @pytest.mark.asyncio
    async def test_alert_streamer_with_multiple_error_conditions(self):
        """Test alert streamer handles multiple concurrent error conditions."""
        reset_dashboard()
        reset_alert_streamer()

        streamer = AlertStreamer(heartbeat_interval_seconds=0.1, buffer_size=5)
        await streamer.start()

        # Create subscription
        sub_id = await streamer.subscribe()

        # Register a callback that raises exception
        def failing_callback(event):
            raise ValueError("Callback processing error")

        streamer.register_callback(failing_callback)

        # Fire multiple alerts rapidly
        for i in range(10):
            await streamer.fire_alert(
                name=f"stress_test_{i}",
                severity=AlertSeverity.WARNING,
                message=f"Alert {i}",
                component="test",
            )

        # Let it process
        await asyncio.sleep(0.2)

        # Streamer should still be functional
        assert streamer._running
        assert len(streamer._event_buffer) <= streamer._buffer_size

        # Unregister the failing callback
        streamer.unregister_callback(failing_callback)

        await streamer.stop()
        reset_alert_streamer()


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestStreamingEdgeCases:
    """Additional edge case tests for comprehensive coverage."""

    @pytest.mark.asyncio
    async def test_consumer_multiple_initialization_attempts(self):
        """Test consumer handles multiple initialization attempts correctly."""
        consumer = SignalConsumer()

        # First initialization
        await consumer.initialize()
        assert consumer._state.value == "running"

        # Second attempt should be idempotent
        await consumer.initialize()
        assert consumer._state.value == "running"

        # Third attempt after manual state change
        consumer._state = consumer._state.__class__.CREATED
        await consumer.initialize()
        assert consumer._state.value == "running"

        await consumer.close()

    @pytest.mark.asyncio
    async def test_producer_callbacks_with_errors(self):
        """Test producer callbacks handle errors correctly."""
        success_called = []
        error_called = []

        def on_success(envelope):
            success_called.append(envelope)

        def on_error(envelope, error):
            error_called.append((envelope, error))

        producer = SignalProducer(on_success=on_success, on_error=on_error)
        await producer.initialize()

        # Test successful send
        signal = RawSignal(
            claim_id="callback_test",
            signal_type=SignalType.BATTLEGROUND,
            value=0.5,
        )

        result = await producer.send(signal)
        assert result is True
        assert len(success_called) == 1

        # Test failed send
        with patch.object(
            producer, "_do_send", side_effect=Exception("Permanent failure")
        ):
            signal2 = RawSignal(
                claim_id="callback_error",
                signal_type=SignalType.FRAGILITY,
                value=0.3,
            )

            result2 = await producer.send(signal2)
            assert result2 is False
            assert len(error_called) == 1

        await producer.close()

    @pytest.mark.asyncio
    async def test_backpressure_state_transitions(self):
        """Test all backpressure state transitions work correctly."""
        config = BackpressureConfig(
            lag_threshold_warning=100,
            lag_threshold_critical=500,
            lag_threshold_pause=1000,
            lag_recovery_threshold=50,
        )
        controller = BackpressureController(config)
        await controller.start()

        # Track state changes
        state_changes = []

        def state_callback(new_state):
            state_changes.append(new_state)

        controller.register_callback(state_callback)

        # Normal -> Throttled (warning)
        await controller.update_lag(150)
        assert controller.metrics.current_state.value == "throttled"

        # Throttled -> Paused
        await controller.update_lag(1500)
        assert controller.metrics.current_state.value == "paused"

        # Paused -> Recovering (after pause expires)
        await asyncio.sleep(0.1)
        await controller.update_lag(40)
        should_process = await controller.should_process()

        # Normal operation after recovery
        await controller.update_lag(10)

        # Verify callback was called
        assert len(state_changes) > 0

        await controller.stop()

    @pytest.mark.asyncio
    async def test_dlq_handler_concurrent_operations(self):
        """Test DLQ handler handles concurrent operations correctly."""
        handler = DLQHandler()
        await handler.start()

        # Send multiple messages concurrently
        tasks = []
        for i in range(5):
            task = handler.send_to_dlq(
                topic=f"topic_{i}",
                key=f"key_{i}",
                value=f"data_{i}".encode(),
                headers={},
                partition=i,
                offset=i * 100,
                error=Exception(f"Error {i}"),
                failure_reason=FailureReason.PROCESSING_ERROR,
            )
            tasks.append(task)

        messages = await asyncio.gather(*tasks)

        # All messages should be stored
        assert len(messages) == 5
        assert all(msg.dlq_id in handler._messages for msg in messages)

        # Get stats
        stats = await handler.get_stats()
        assert stats.total_messages == 5
        assert stats.pending_count == 5

        await handler.stop()
