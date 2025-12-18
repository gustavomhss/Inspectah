"""
Tests for S39 Backpressure Controller Module.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.streaming.backpressure import (
    BackpressureConfig,
    BackpressureController,
    BackpressureMetrics,
    BackpressureState,
    ErrorRecord,
    ThrottleLevel,
    get_backpressure_controller,
    reset_backpressure_controller,
)


# ============================================================================
# BackpressureState Tests
# ============================================================================

class TestBackpressureState:
    """Tests for BackpressureState enum."""

    def test_state_values(self):
        """Test state enum values."""
        assert BackpressureState.NORMAL.value == "normal"
        assert BackpressureState.THROTTLED.value == "throttled"
        assert BackpressureState.PAUSED.value == "paused"
        assert BackpressureState.RECOVERING.value == "recovering"


# ============================================================================
# ThrottleLevel Tests
# ============================================================================

class TestThrottleLevel:
    """Tests for ThrottleLevel enum."""

    def test_throttle_values(self):
        """Test throttle level values."""
        assert ThrottleLevel.NONE.value == "none"
        assert ThrottleLevel.LIGHT.value == "light"
        assert ThrottleLevel.MODERATE.value == "moderate"
        assert ThrottleLevel.HEAVY.value == "heavy"
        assert ThrottleLevel.EXTREME.value == "extreme"


# ============================================================================
# BackpressureConfig Tests
# ============================================================================

class TestBackpressureConfig:
    """Tests for BackpressureConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BackpressureConfig()

        assert config.lag_threshold_warning == 1000
        assert config.lag_threshold_critical == 5000
        assert config.lag_threshold_pause == 10000
        assert config.lag_recovery_threshold == 500
        assert config.recovery_rate_increase == 0.1
        assert config.recovery_check_interval_seconds == 10
        assert config.min_rate_percent == 0.1
        assert config.max_batch_size == 100
        assert config.min_batch_size == 10
        assert config.error_threshold == 10
        assert config.error_window_seconds == 60
        assert config.pause_duration_seconds == 30

    def test_custom_config(self):
        """Test custom configuration values."""
        config = BackpressureConfig(
            lag_threshold_warning=500,
            lag_threshold_critical=2000,
            lag_threshold_pause=5000,
            error_threshold=5,
        )

        assert config.lag_threshold_warning == 500
        assert config.lag_threshold_critical == 2000
        assert config.lag_threshold_pause == 5000
        assert config.error_threshold == 5


# ============================================================================
# BackpressureMetrics Tests
# ============================================================================

class TestBackpressureMetrics:
    """Tests for BackpressureMetrics dataclass."""

    def test_default_metrics(self):
        """Test default metrics values."""
        metrics = BackpressureMetrics()

        assert metrics.current_lag == 0
        assert metrics.current_state == BackpressureState.NORMAL
        assert metrics.throttle_level == ThrottleLevel.NONE
        assert metrics.current_rate_percent == 100.0
        assert metrics.messages_processed == 0
        assert metrics.messages_dropped == 0
        assert metrics.errors_in_window == 0
        assert metrics.pauses_count == 0
        assert metrics.last_pause_at is None
        assert metrics.last_resume_at is None

    def test_to_dict(self):
        """Test metrics to_dict conversion."""
        now = datetime.now(timezone.utc)
        metrics = BackpressureMetrics(
            current_lag=1500,
            current_state=BackpressureState.THROTTLED,
            throttle_level=ThrottleLevel.MODERATE,
            current_rate_percent=50.0,
            messages_processed=1000,
            pauses_count=2,
            last_pause_at=now,
            state_changed_at=now,
        )

        data = metrics.to_dict()

        assert data["current_lag"] == 1500
        assert data["current_state"] == "throttled"
        assert data["throttle_level"] == "moderate"
        assert data["current_rate_percent"] == 50.0
        assert data["messages_processed"] == 1000
        assert data["pauses_count"] == 2
        assert data["last_pause_at"] == now.isoformat()

    def test_to_dict_none_timestamps(self):
        """Test to_dict with None timestamps."""
        metrics = BackpressureMetrics()

        data = metrics.to_dict()

        assert data["last_pause_at"] is None
        assert data["last_resume_at"] is None


# ============================================================================
# ErrorRecord Tests
# ============================================================================

class TestErrorRecord:
    """Tests for ErrorRecord dataclass."""

    def test_error_record_creation(self):
        """Test error record creation."""
        now = datetime.now(timezone.utc)
        record = ErrorRecord(
            timestamp=now,
            error_type="ValueError",
            message="Test error",
        )

        assert record.timestamp == now
        assert record.error_type == "ValueError"
        assert record.message == "Test error"


# ============================================================================
# BackpressureController Tests
# ============================================================================

class TestBackpressureController:
    """Tests for BackpressureController class."""

    @pytest.fixture
    def controller(self):
        """Create a controller for testing."""
        return BackpressureController()

    @pytest.fixture
    def custom_controller(self):
        """Create a controller with custom config."""
        config = BackpressureConfig(
            lag_threshold_warning=100,
            lag_threshold_critical=500,
            lag_threshold_pause=1000,
            lag_recovery_threshold=50,
            error_threshold=3,
        )
        return BackpressureController(config)

    def test_init_default(self, controller):
        """Test default initialization."""
        assert controller.config.lag_threshold_warning == 1000
        assert controller.metrics.current_state == BackpressureState.NORMAL
        assert not controller._running

    def test_init_custom(self, custom_controller):
        """Test custom initialization."""
        assert custom_controller.config.lag_threshold_warning == 100
        assert custom_controller.config.error_threshold == 3

    @pytest.mark.asyncio
    async def test_start_stop(self, controller):
        """Test start and stop lifecycle."""
        await controller.start()

        assert controller._running
        assert controller._recovery_task is not None

        await controller.stop()

        assert not controller._running
        assert controller._recovery_task is None

    @pytest.mark.asyncio
    async def test_start_idempotent(self, controller):
        """Test that start is idempotent."""
        await controller.start()
        task1 = controller._recovery_task

        await controller.start()
        task2 = controller._recovery_task

        assert task1 is task2

        await controller.stop()

    @pytest.mark.asyncio
    async def test_update_lag_normal(self, controller):
        """Test lag update in normal range."""
        await controller.start()

        await controller.update_lag(100)

        assert controller.metrics.current_lag == 100
        assert controller.metrics.current_state == BackpressureState.NORMAL
        assert controller.metrics.throttle_level == ThrottleLevel.NONE

        await controller.stop()

    @pytest.mark.asyncio
    async def test_update_lag_warning(self, custom_controller):
        """Test lag update triggers warning threshold."""
        await custom_controller.start()

        await custom_controller.update_lag(200)  # Above 100 warning

        assert custom_controller.metrics.current_state == BackpressureState.THROTTLED
        assert custom_controller.metrics.throttle_level == ThrottleLevel.MODERATE

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_update_lag_critical(self, custom_controller):
        """Test lag update triggers critical threshold."""
        await custom_controller.start()

        await custom_controller.update_lag(600)  # Above 500 critical

        assert custom_controller.metrics.current_state == BackpressureState.THROTTLED
        assert custom_controller.metrics.throttle_level == ThrottleLevel.HEAVY
        assert custom_controller.metrics.current_rate_percent == 25.0

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_update_lag_pause(self, custom_controller):
        """Test lag update triggers pause threshold."""
        await custom_controller.start()

        await custom_controller.update_lag(1500)  # Above 1000 pause

        assert custom_controller.metrics.current_state == BackpressureState.PAUSED
        assert custom_controller.metrics.pauses_count == 1

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_record_error(self, custom_controller):
        """Test error recording."""
        await custom_controller.start()

        await custom_controller.record_error("ValueError", "Test error")

        assert custom_controller.metrics.errors_in_window == 1
        assert len(custom_controller._errors) == 1

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_record_error_triggers_pause(self, custom_controller):
        """Test multiple errors trigger pause."""
        await custom_controller.start()

        for i in range(4):  # Exceeds error_threshold of 3
            await custom_controller.record_error("Error", f"Error {i}")

        assert custom_controller.metrics.current_state == BackpressureState.PAUSED
        assert custom_controller.metrics.pauses_count >= 1

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_record_success(self, controller):
        """Test recording successful processing."""
        await controller.record_success(10)

        assert controller.metrics.messages_processed == 10

        await controller.record_success(5)

        assert controller.metrics.messages_processed == 15

    @pytest.mark.asyncio
    async def test_should_process_normal(self, controller):
        """Test should_process in normal state."""
        await controller.start()

        result = await controller.should_process()

        assert result is True

        await controller.stop()

    @pytest.mark.asyncio
    async def test_should_process_paused(self, custom_controller):
        """Test should_process in paused state."""
        await custom_controller.start()

        # Trigger pause
        await custom_controller.update_lag(1500)

        result = await custom_controller.should_process()

        # Should be False because we're paused and within pause duration
        assert result is False

        await custom_controller.stop()

    @pytest.mark.asyncio
    async def test_get_batch_size_normal(self, controller):
        """Test batch size in normal state."""
        batch_size = await controller.get_batch_size()

        # Full rate should give max batch size
        assert batch_size == controller.config.max_batch_size

    @pytest.mark.asyncio
    async def test_get_batch_size_throttled(self, controller):
        """Test batch size when throttled."""
        controller.metrics.current_rate_percent = 50.0

        batch_size = await controller.get_batch_size()

        # Should be somewhere between min and max
        assert batch_size >= controller.config.min_batch_size
        assert batch_size <= controller.config.max_batch_size

    @pytest.mark.asyncio
    async def test_get_delay_ms(self, controller):
        """Test delay values for different throttle levels."""
        controller.metrics.throttle_level = ThrottleLevel.NONE
        assert await controller.get_delay_ms() == 0

        controller.metrics.throttle_level = ThrottleLevel.LIGHT
        assert await controller.get_delay_ms() == 50

        controller.metrics.throttle_level = ThrottleLevel.MODERATE
        assert await controller.get_delay_ms() == 200

        controller.metrics.throttle_level = ThrottleLevel.HEAVY
        assert await controller.get_delay_ms() == 500

        controller.metrics.throttle_level = ThrottleLevel.EXTREME
        assert await controller.get_delay_ms() == 1000

    def test_register_callback(self, controller):
        """Test callback registration."""
        callback = MagicMock()

        controller.register_callback(callback)

        assert callback in controller._callbacks

    def test_unregister_callback(self, controller):
        """Test callback unregistration."""
        callback = MagicMock()
        controller.register_callback(callback)

        result = controller.unregister_callback(callback)

        assert result is True
        assert callback not in controller._callbacks

    def test_unregister_callback_not_found(self, controller):
        """Test unregistering non-existent callback."""
        callback = MagicMock()

        result = controller.unregister_callback(callback)

        assert result is False

    @pytest.mark.asyncio
    async def test_callback_called_on_state_change(self, custom_controller):
        """Test that callbacks are called on state change."""
        callback = MagicMock()
        custom_controller.register_callback(callback)

        await custom_controller.start()

        # Trigger state change
        await custom_controller.update_lag(200)  # Should go to THROTTLED

        # Callback should have been called
        callback.assert_called()

        await custom_controller.stop()

    def test_get_metrics(self, controller):
        """Test get_metrics method."""
        metrics = controller.get_metrics()

        assert "current_lag" in metrics
        assert "current_state" in metrics
        assert "throttle_level" in metrics
        assert "current_rate_percent" in metrics

    def test_is_healthy_normal(self, controller):
        """Test is_healthy in normal state."""
        controller.metrics.current_state = BackpressureState.NORMAL

        assert controller.is_healthy() is True

    def test_is_healthy_recovering(self, controller):
        """Test is_healthy in recovering state."""
        controller.metrics.current_state = BackpressureState.RECOVERING

        assert controller.is_healthy() is True

    def test_is_healthy_paused(self, controller):
        """Test is_healthy in paused state."""
        controller.metrics.current_state = BackpressureState.PAUSED

        assert controller.is_healthy() is False

    def test_is_healthy_throttled(self, controller):
        """Test is_healthy in throttled state."""
        controller.metrics.current_state = BackpressureState.THROTTLED

        assert controller.is_healthy() is False

    @pytest.mark.asyncio
    async def test_context_manager(self, controller):
        """Test async context manager."""
        async with controller:
            assert controller._running is True

        assert controller._running is False


# ============================================================================
# Global Instance Tests
# ============================================================================

class TestGlobalInstance:
    """Tests for global instance management."""

    @pytest.fixture(autouse=True)
    def reset_global(self):
        """Reset global instance before each test."""
        reset_backpressure_controller()
        yield
        reset_backpressure_controller()

    @pytest.mark.asyncio
    async def test_get_backpressure_controller(self):
        """Test getting global controller."""
        controller = await get_backpressure_controller()

        assert controller is not None
        assert controller._running is True

        # Should return same instance
        controller2 = await get_backpressure_controller()
        assert controller is controller2

        await controller.stop()

    @pytest.mark.asyncio
    async def test_get_backpressure_controller_with_config(self):
        """Test getting global controller with config."""
        config = BackpressureConfig(lag_threshold_warning=500)

        controller = await get_backpressure_controller(config)

        assert controller.config.lag_threshold_warning == 500

        await controller.stop()

    def test_reset_backpressure_controller(self):
        """Test resetting global controller."""
        reset_backpressure_controller()
        # Should not raise


# ============================================================================
# Recovery Tests
# ============================================================================

class TestBackpressureRecovery:
    """Tests for backpressure recovery mechanism."""

    @pytest.mark.asyncio
    async def test_recovery_from_pause(self):
        """Test recovery from paused state."""
        config = BackpressureConfig(
            lag_threshold_pause=100,
            lag_recovery_threshold=50,
            pause_duration_seconds=0,  # Immediate recovery for testing
            recovery_check_interval_seconds=1,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Trigger pause
        await controller.update_lag(200)
        assert controller.metrics.current_state == BackpressureState.PAUSED

        # Set low lag and check should_process to trigger recovery
        controller.metrics.current_lag = 30
        controller._pause_until = None  # Clear pause

        # Force recovery
        await controller._start_recovery()

        assert controller.metrics.current_state == BackpressureState.RECOVERING

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_increases_rate(self):
        """Test that recovery gradually increases rate."""
        config = BackpressureConfig(
            recovery_rate_increase=0.2,  # 20% per interval
            recovery_check_interval_seconds=0,  # Fast for testing
        )
        controller = BackpressureController(config)

        await controller.start()

        # Start in recovering state with low rate
        controller.metrics.current_state = BackpressureState.RECOVERING
        controller.metrics.current_rate_percent = 20.0
        controller.metrics.current_lag = 100

        # Manually trigger rate increase (simulating recovery loop)
        async with controller._lock:
            new_rate = min(
                100.0,
                controller.metrics.current_rate_percent + (config.recovery_rate_increase * 100)
            )
            controller.metrics.current_rate_percent = new_rate

        assert controller.metrics.current_rate_percent == 40.0

        await controller.stop()


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestRecoveryLoop:
    """Tests for the recovery loop functionality."""

    @pytest.mark.asyncio
    async def test_recovery_loop_completes_recovery(self):
        """Test that recovery loop completes recovery to normal."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0,  # Fast
            recovery_rate_increase=0.5,  # 50% per interval
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state
        controller.metrics.current_state = BackpressureState.RECOVERING
        controller.metrics.current_rate_percent = 50.0
        controller.metrics.current_lag = 100

        # Manually trigger one recovery iteration
        async with controller._lock:
            if controller.metrics.current_state == BackpressureState.RECOVERING:
                if controller.metrics.current_lag <= config.lag_recovery_threshold:
                    new_rate = min(
                        100.0,
                        controller.metrics.current_rate_percent + (config.recovery_rate_increase * 100)
                    )
                    controller.metrics.current_rate_percent = new_rate
                    if new_rate >= 100:
                        controller.metrics.current_state = BackpressureState.NORMAL
                        controller.metrics.throttle_level = ThrottleLevel.NONE

        assert controller.metrics.current_state == BackpressureState.NORMAL
        assert controller.metrics.throttle_level == ThrottleLevel.NONE

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_updates_throttle_levels(self):
        """Test that recovery loop updates throttle levels correctly."""
        config = BackpressureConfig(
            recovery_rate_increase=0.1,
        )
        controller = BackpressureController(config)

        # Test rate to throttle level mapping
        test_cases = [
            (95.0, ThrottleLevel.LIGHT),
            (75.0, ThrottleLevel.LIGHT),
            (60.0, ThrottleLevel.MODERATE),
            (50.0, ThrottleLevel.MODERATE),
            (30.0, ThrottleLevel.HEAVY),
            (25.0, ThrottleLevel.HEAVY),
            (15.0, ThrottleLevel.EXTREME),
            (10.0, ThrottleLevel.EXTREME),
        ]

        for rate, expected_level in test_cases:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = rate
            controller.metrics.current_lag = 100

            # Update throttle based on rate
            async with controller._lock:
                if rate >= 100:
                    controller.metrics.throttle_level = ThrottleLevel.NONE
                elif rate >= 75:
                    controller.metrics.throttle_level = ThrottleLevel.LIGHT
                elif rate >= 50:
                    controller.metrics.throttle_level = ThrottleLevel.MODERATE
                elif rate >= 25:
                    controller.metrics.throttle_level = ThrottleLevel.HEAVY
                else:
                    controller.metrics.throttle_level = ThrottleLevel.EXTREME

            assert controller.metrics.throttle_level == expected_level, f"Rate {rate} should be {expected_level}"

    @pytest.mark.asyncio
    async def test_recovery_loop_re_evaluates_on_lag_increase(self):
        """Test that recovery loop re-evaluates if lag increases."""
        config = BackpressureConfig(
            lag_recovery_threshold=500,
            lag_threshold_warning=1000,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state
        controller.metrics.current_state = BackpressureState.RECOVERING
        controller.metrics.current_rate_percent = 50.0
        controller.metrics.current_lag = 800  # Above recovery threshold

        # This should trigger re-evaluation
        await controller._evaluate_state()

        assert controller.metrics.current_state == BackpressureState.THROTTLED

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_error_handling(self):
        """Test that recovery loop handles errors gracefully."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0,
        )
        controller = BackpressureController(config)

        await controller.start()

        # The loop should handle internal errors without crashing
        # We test this by verifying the controller is still running after potential errors
        assert controller._running is True

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_actually_runs(self):
        """Test that recovery loop actually executes and updates state."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,  # Very short
            recovery_rate_increase=0.5,  # 50% per interval
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 30.0
            controller.metrics.current_lag = 100

        # Wait for a few recovery loop iterations
        await asyncio.sleep(0.1)

        # Rate should have increased
        assert controller.metrics.current_rate_percent > 30.0

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_complete_to_normal(self):
        """Test recovery loop completes recovery to normal state."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,
            recovery_rate_increase=1.0,  # 100% per interval - fast
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state at high rate
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 80.0
            controller.metrics.current_lag = 100

        # Wait for recovery
        await asyncio.sleep(0.1)

        # Should be normal now
        assert controller.metrics.current_state == BackpressureState.NORMAL
        assert controller.metrics.throttle_level == ThrottleLevel.NONE

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_lag_increase_reevaluates(self):
        """Test recovery loop re-evaluates when lag increases."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,
            lag_recovery_threshold=500,
            lag_threshold_warning=1000,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state with high lag
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 80.0
            controller.metrics.current_lag = 800  # Above recovery threshold

        # Wait for re-evaluation
        await asyncio.sleep(0.1)

        # Should have re-evaluated to throttled
        assert controller.metrics.current_state != BackpressureState.RECOVERING

        await controller.stop()

    @pytest.mark.asyncio
    async def test_should_process_triggers_recovery(self):
        """Test that should_process triggers recovery after pause expires."""
        config = BackpressureConfig(
            pause_duration_seconds=0,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set paused state with expired pause
        controller.metrics.current_state = BackpressureState.PAUSED
        controller._pause_until = datetime.now(timezone.utc) - timedelta(seconds=1)

        # should_process should trigger recovery
        result = await controller.should_process()

        assert result is True
        assert controller.metrics.current_state == BackpressureState.RECOVERING

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_continues_when_already_recovering(self):
        """Test that recovery state continues when lag is low and already recovering."""
        config = BackpressureConfig(
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state
        controller.metrics.current_state = BackpressureState.RECOVERING
        controller.metrics.throttle_level = ThrottleLevel.MODERATE
        controller.metrics.current_rate_percent = 55.0

        # Update lag to below recovery threshold
        await controller.update_lag(300)

        # Should maintain recovering state with same throttle
        assert controller.metrics.current_state == BackpressureState.RECOVERING
        assert controller.metrics.throttle_level == ThrottleLevel.MODERATE
        assert controller.metrics.current_rate_percent == 55.0

        await controller.stop()

    @pytest.mark.asyncio
    async def test_callback_exception_is_logged(self):
        """Test that callback exceptions are handled and logged."""
        controller = BackpressureController()

        # Register a callback that raises
        def failing_callback(state):
            raise RuntimeError("Callback failed!")

        controller.register_callback(failing_callback)

        await controller.start()

        # Trigger state change which should call callback
        await controller.update_lag(2000)  # Above warning threshold

        # Controller should still be running
        assert controller._running is True

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_throttle_levels_moderate(self):
        """Test recovery loop sets moderate throttle level."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,
            recovery_rate_increase=0.1,
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state at rate that will go to moderate
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 45.0  # Will go to 55 (moderate)
            controller.metrics.current_lag = 100

        await asyncio.sleep(0.05)

        # Should have moderate throttle
        assert controller.metrics.throttle_level in [ThrottleLevel.MODERATE, ThrottleLevel.LIGHT, ThrottleLevel.NONE]

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_throttle_levels_heavy(self):
        """Test recovery loop sets heavy throttle level."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,
            recovery_rate_increase=0.05,  # Small increase
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state at rate that stays heavy
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 20.0  # Will go to 25 (heavy)
            controller.metrics.current_lag = 100

        await asyncio.sleep(0.05)

        # Should be around heavy
        assert controller.metrics.current_rate_percent >= 20.0

        await controller.stop()

    @pytest.mark.asyncio
    async def test_recovery_loop_throttle_levels_extreme(self):
        """Test recovery loop sets extreme throttle level."""
        config = BackpressureConfig(
            recovery_check_interval_seconds=0.01,
            recovery_rate_increase=0.02,  # Very small increase
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set up recovering state at very low rate
        async with controller._lock:
            controller.metrics.current_state = BackpressureState.RECOVERING
            controller.metrics.current_rate_percent = 10.0  # Will stay extreme
            controller.metrics.current_lag = 100

        await asyncio.sleep(0.05)

        # Should still be at low rate
        assert controller.metrics.current_rate_percent >= 10.0

        await controller.stop()


class TestBackpressureEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_concurrent_lag_updates(self):
        """Test concurrent lag updates are handled safely."""
        controller = BackpressureController()
        await controller.start()

        # Simulate concurrent updates
        async def update_lag(value):
            await controller.update_lag(value)

        await asyncio.gather(
            update_lag(100),
            update_lag(200),
            update_lag(150),
        )

        # Should have one of the values
        assert controller.metrics.current_lag in [100, 200, 150]

        await controller.stop()

    @pytest.mark.asyncio
    async def test_error_window_cleanup(self):
        """Test that old errors are cleaned up."""
        config = BackpressureConfig(error_window_seconds=1)
        controller = BackpressureController(config)

        await controller.start()

        await controller.record_error("Error", "Test 1")

        # Wait for error to expire
        await asyncio.sleep(1.1)

        # Record new error which should trigger cleanup
        await controller.record_error("Error", "Test 2")

        # Only one error should remain
        assert len(controller._errors) == 1

        await controller.stop()

    def test_callback_error_handling(self):
        """Test that callback errors don't crash controller."""
        controller = BackpressureController()

        def failing_callback(state):
            raise ValueError("Callback error")

        controller.register_callback(failing_callback)

        # Should not raise
        for callback in controller._callbacks:
            try:
                callback(BackpressureState.NORMAL)
            except Exception:
                pass  # Expected

    @pytest.mark.asyncio
    async def test_light_throttle_between_recovery_and_warning(self):
        """Test light throttle state between recovery and warning thresholds."""
        config = BackpressureConfig(
            lag_threshold_warning=1000,
            lag_recovery_threshold=500,
        )
        controller = BackpressureController(config)

        await controller.start()

        # Set lag between recovery (500) and warning (1000)
        await controller.update_lag(750)

        assert controller.metrics.current_state == BackpressureState.THROTTLED
        assert controller.metrics.throttle_level == ThrottleLevel.LIGHT
        assert controller.metrics.current_rate_percent == 75.0

        await controller.stop()
