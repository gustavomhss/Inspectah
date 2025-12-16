"""
S39 - Backpressure Controller

Manages consumer backpressure to prevent overload during high lag scenarios.
Implements adaptive rate limiting and circuit breaker patterns.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackpressureState(str, Enum):
    """Backpressure controller states."""
    NORMAL = "normal"           # No backpressure, full speed
    THROTTLED = "throttled"     # Reduced processing rate
    PAUSED = "paused"           # Processing paused
    RECOVERING = "recovering"   # Gradually increasing rate


class ThrottleLevel(str, Enum):
    """Throttle intensity levels."""
    NONE = "none"           # 100% throughput
    LIGHT = "light"         # 75% throughput
    MODERATE = "moderate"   # 50% throughput
    HEAVY = "heavy"         # 25% throughput
    EXTREME = "extreme"     # 10% throughput


@dataclass
class BackpressureConfig:
    """Configuration for backpressure controller."""
    # Lag thresholds
    lag_threshold_warning: int = 1000      # Start throttling
    lag_threshold_critical: int = 5000     # Heavy throttling
    lag_threshold_pause: int = 10000       # Pause processing

    # Recovery settings
    lag_recovery_threshold: int = 500      # Resume normal when below
    recovery_rate_increase: float = 0.1    # Rate increase per interval
    recovery_check_interval_seconds: int = 10

    # Rate limiting
    min_rate_percent: float = 0.1          # Minimum 10% throughput
    max_batch_size: int = 100
    min_batch_size: int = 10

    # Circuit breaker
    error_threshold: int = 10              # Errors before pause
    error_window_seconds: int = 60
    pause_duration_seconds: int = 30

    # Monitoring
    metrics_interval_seconds: int = 5


@dataclass
class BackpressureMetrics:
    """Metrics for backpressure monitoring."""
    current_lag: int = 0
    current_state: BackpressureState = BackpressureState.NORMAL
    throttle_level: ThrottleLevel = ThrottleLevel.NONE
    current_rate_percent: float = 100.0
    messages_processed: int = 0
    messages_dropped: int = 0
    errors_in_window: int = 0
    pauses_count: int = 0
    last_pause_at: Optional[datetime] = None
    last_resume_at: Optional[datetime] = None
    state_changed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_lag": self.current_lag,
            "current_state": self.current_state.value,
            "throttle_level": self.throttle_level.value,
            "current_rate_percent": round(self.current_rate_percent, 2),
            "messages_processed": self.messages_processed,
            "messages_dropped": self.messages_dropped,
            "errors_in_window": self.errors_in_window,
            "pauses_count": self.pauses_count,
            "last_pause_at": (
                self.last_pause_at.isoformat() if self.last_pause_at else None
            ),
            "last_resume_at": (
                self.last_resume_at.isoformat() if self.last_resume_at else None
            ),
            "state_changed_at": self.state_changed_at.isoformat(),
        }


@dataclass
class ErrorRecord:
    """Record of an error for circuit breaker."""
    timestamp: datetime
    error_type: str
    message: str


class BackpressureController:
    """
    Controls backpressure for Kafka consumers.

    Features:
    - Adaptive rate limiting based on consumer lag
    - Circuit breaker for error conditions
    - Gradual recovery after overload
    - Metrics and observability
    """

    def __init__(self, config: Optional[BackpressureConfig] = None):
        """
        Initialize BackpressureController.

        Args:
            config: Backpressure configuration
        """
        self.config = config or BackpressureConfig()
        self.metrics = BackpressureMetrics()
        self._errors: List[ErrorRecord] = []
        self._running = False
        self._recovery_task: Optional[asyncio.Task] = None
        self._pause_until: Optional[datetime] = None
        self._callbacks: List[Callable[[BackpressureState], None]] = []
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the backpressure controller."""
        if self._running:
            return
        self._running = True
        self._recovery_task = asyncio.create_task(self._recovery_loop())
        logger.info("BackpressureController started")

    async def stop(self) -> None:
        """Stop the backpressure controller."""
        self._running = False
        if self._recovery_task:
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                pass
            self._recovery_task = None
        logger.info("BackpressureController stopped")

    async def update_lag(self, lag: int) -> None:
        """
        Update current consumer lag and adjust state.

        Args:
            lag: Current consumer lag (messages behind)
        """
        async with self._lock:
            self.metrics.current_lag = lag
            await self._evaluate_state()

    async def record_error(self, error_type: str, message: str) -> None:
        """
        Record an error for circuit breaker evaluation.

        Args:
            error_type: Type of error
            message: Error message
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            self._errors.append(ErrorRecord(now, error_type, message))

            # Clean old errors
            cutoff = now - timedelta(seconds=self.config.error_window_seconds)
            self._errors = [e for e in self._errors if e.timestamp >= cutoff]

            self.metrics.errors_in_window = len(self._errors)

            # Check circuit breaker
            if len(self._errors) >= self.config.error_threshold:
                await self._trigger_pause("error_threshold_exceeded")

    async def record_success(self, count: int = 1) -> None:
        """
        Record successful message processing.

        Args:
            count: Number of messages processed
        """
        self.metrics.messages_processed += count

    async def should_process(self) -> bool:
        """
        Check if processing should continue.

        Returns:
            True if processing is allowed
        """
        # Check pause state
        if self.metrics.current_state == BackpressureState.PAUSED:
            if self._pause_until and datetime.now(timezone.utc) < self._pause_until:
                return False
            # Pause expired, start recovery
            await self._start_recovery()

        return self.metrics.current_state != BackpressureState.PAUSED

    async def get_batch_size(self) -> int:
        """
        Get recommended batch size based on current state.

        Returns:
            Recommended batch size
        """
        rate = self.metrics.current_rate_percent / 100.0
        batch_range = self.config.max_batch_size - self.config.min_batch_size
        batch_size = int(self.config.min_batch_size + (batch_range * rate))
        return max(self.config.min_batch_size, batch_size)

    async def get_delay_ms(self) -> int:
        """
        Get processing delay based on throttle level.

        Returns:
            Delay in milliseconds between batches
        """
        delays = {
            ThrottleLevel.NONE: 0,
            ThrottleLevel.LIGHT: 50,
            ThrottleLevel.MODERATE: 200,
            ThrottleLevel.HEAVY: 500,
            ThrottleLevel.EXTREME: 1000,
        }
        return delays.get(self.metrics.throttle_level, 0)

    async def _evaluate_state(self) -> None:
        """Evaluate and update backpressure state based on lag."""
        lag = self.metrics.current_lag
        old_state = self.metrics.current_state

        # Determine new state based on lag
        if lag >= self.config.lag_threshold_pause:
            new_state = BackpressureState.PAUSED
            throttle = ThrottleLevel.EXTREME
            rate = self.config.min_rate_percent * 100
        elif lag >= self.config.lag_threshold_critical:
            new_state = BackpressureState.THROTTLED
            throttle = ThrottleLevel.HEAVY
            rate = 25.0
        elif lag >= self.config.lag_threshold_warning:
            new_state = BackpressureState.THROTTLED
            throttle = ThrottleLevel.MODERATE
            rate = 50.0
        elif lag <= self.config.lag_recovery_threshold:
            if old_state == BackpressureState.RECOVERING:
                # Continue recovery
                new_state = BackpressureState.RECOVERING
                throttle = self.metrics.throttle_level
                rate = self.metrics.current_rate_percent
            else:
                new_state = BackpressureState.NORMAL
                throttle = ThrottleLevel.NONE
                rate = 100.0
        else:
            # Between recovery and warning - light throttle
            new_state = BackpressureState.THROTTLED
            throttle = ThrottleLevel.LIGHT
            rate = 75.0

        # Update metrics
        self.metrics.throttle_level = throttle
        self.metrics.current_rate_percent = rate

        # State transition
        if new_state != old_state:
            self.metrics.current_state = new_state
            self.metrics.state_changed_at = datetime.now(timezone.utc)

            logger.info(
                f"Backpressure state: {old_state.value} -> {new_state.value} "
                f"(lag={lag}, rate={rate}%)"
            )

            if new_state == BackpressureState.PAUSED:
                await self._trigger_pause("lag_threshold_exceeded")

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(new_state)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

    async def _trigger_pause(self, reason: str) -> None:
        """Trigger pause state."""
        self.metrics.current_state = BackpressureState.PAUSED
        self.metrics.pauses_count += 1
        self.metrics.last_pause_at = datetime.now(timezone.utc)
        self._pause_until = datetime.now(timezone.utc) + timedelta(
            seconds=self.config.pause_duration_seconds
        )

        logger.warning(
            f"Backpressure PAUSED: {reason} "
            f"(resume at {self._pause_until.isoformat()})"
        )

    async def _start_recovery(self) -> None:
        """Start gradual recovery from pause."""
        self.metrics.current_state = BackpressureState.RECOVERING
        self.metrics.last_resume_at = datetime.now(timezone.utc)
        self.metrics.current_rate_percent = self.config.min_rate_percent * 100
        self.metrics.throttle_level = ThrottleLevel.EXTREME
        self._pause_until = None

        logger.info("Backpressure starting recovery")

    async def _recovery_loop(self) -> None:
        """Gradual recovery loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.recovery_check_interval_seconds)

                async with self._lock:
                    if self.metrics.current_state == BackpressureState.RECOVERING:
                        # Check if lag is still low enough
                        if self.metrics.current_lag <= self.config.lag_recovery_threshold:
                            # Increase rate
                            new_rate = min(
                                100.0,
                                self.metrics.current_rate_percent +
                                (self.config.recovery_rate_increase * 100)
                            )
                            self.metrics.current_rate_percent = new_rate

                            # Update throttle level
                            if new_rate >= 100:
                                self.metrics.current_state = BackpressureState.NORMAL
                                self.metrics.throttle_level = ThrottleLevel.NONE
                                logger.info("Backpressure recovered to NORMAL")
                            elif new_rate >= 75:
                                self.metrics.throttle_level = ThrottleLevel.LIGHT
                            elif new_rate >= 50:
                                self.metrics.throttle_level = ThrottleLevel.MODERATE
                            elif new_rate >= 25:
                                self.metrics.throttle_level = ThrottleLevel.HEAVY
                            else:
                                self.metrics.throttle_level = ThrottleLevel.EXTREME
                        else:
                            # Lag increased, re-evaluate
                            await self._evaluate_state()

            except asyncio.CancelledError:
                break
            except (RuntimeError, ValueError, KeyError) as e:
                logger.error(f"Recovery loop error: {e}")

    def register_callback(
        self,
        callback: Callable[[BackpressureState], None],
    ) -> None:
        """
        Register callback for state changes.

        Args:
            callback: Function called on state change
        """
        self._callbacks.append(callback)

    def unregister_callback(
        self,
        callback: Callable[[BackpressureState], None],
    ) -> bool:
        """
        Unregister callback.

        Args:
            callback: Function to remove

        Returns:
            True if found and removed
        """
        try:
            self._callbacks.remove(callback)
            return True
        except ValueError:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.to_dict()

    def is_healthy(self) -> bool:
        """Check if controller is in healthy state."""
        return self.metrics.current_state in (
            BackpressureState.NORMAL,
            BackpressureState.RECOVERING,
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Global instance
_controller: Optional[BackpressureController] = None


async def get_backpressure_controller(
    config: Optional[BackpressureConfig] = None
) -> BackpressureController:
    """Get or create global backpressure controller."""
    global _controller
    if _controller is None:
        _controller = BackpressureController(config)
        await _controller.start()
    return _controller


def reset_backpressure_controller() -> None:
    """Reset global controller (for testing)."""
    global _controller
    _controller = None
