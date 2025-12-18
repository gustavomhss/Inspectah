"""
Comprehensive tests for Circuit Breaker — S38-BE-005b

Tests all code paths including error handling, state transitions, and edge cases.
"""

import pytest
import time
import threading
from unittest.mock import MagicMock, patch

from app.ingestion.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitConfig,
    CircuitState,
    CircuitStats,
    get_circuit_breaker,
)


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality."""

    @pytest.fixture
    def breaker(self):
        """Create fresh circuit breaker."""
        return CircuitBreaker()

    def test_init(self, breaker):
        """Test initialization."""
        assert breaker._configs == {}
        assert breaker._stats == {}
        assert breaker._lock is not None

    def test_configure(self, breaker):
        """Test configuration."""
        breaker.configure(
            "test_source",
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0,
        )

        assert "test_source" in breaker._configs
        config = breaker._configs["test_source"]
        assert config.failure_threshold == 3
        assert config.success_threshold == 2
        assert config.timeout_seconds == 30.0

        assert "test_source" in breaker._stats
        stats = breaker._stats["test_source"]
        assert stats.state == CircuitState.CLOSED
        assert stats.failure_count == 0

    def test_configure_defaults(self, breaker):
        """Test configuration with defaults."""
        breaker.configure("default_source")

        config = breaker._configs["default_source"]
        assert config.failure_threshold == 5
        assert config.success_threshold == 3
        assert config.timeout_seconds == 60.0


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=3, success_threshold=2, timeout_seconds=1.0)
        return cb

    def test_initial_state_closed(self, breaker):
        """Test initial state is CLOSED."""
        assert breaker.is_available("api")
        state = breaker._get_state("api")
        assert state == CircuitState.CLOSED

    def test_transition_closed_to_open(self, breaker):
        """Test transition from CLOSED to OPEN after failures."""
        # Record failures to reach threshold
        for i in range(3):
            breaker.record_failure("api", f"error_{i}")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.OPEN
        assert not breaker.is_available("api")

    def test_transition_open_to_half_open(self, breaker):
        """Test transition from OPEN to HALF_OPEN after timeout."""
        # Move to OPEN
        for i in range(3):
            breaker.record_failure("api")

        assert breaker._stats["api"].state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(1.1)

        # Check state updates to HALF_OPEN
        state = breaker._get_state("api")
        assert state == CircuitState.HALF_OPEN

    def test_transition_half_open_to_closed(self, breaker):
        """Test transition from HALF_OPEN to CLOSED after successes."""
        # Move to OPEN
        for i in range(3):
            breaker.record_failure("api")

        # Wait for HALF_OPEN
        time.sleep(1.1)
        breaker._get_state("api")

        # Record successes to close circuit
        breaker.record_success("api")
        breaker.record_success("api")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.CLOSED

    def test_transition_half_open_to_open_on_failure(self, breaker):
        """Test that any failure in HALF_OPEN returns to OPEN."""
        # Move to OPEN
        for i in range(3):
            breaker.record_failure("api")

        # Wait for HALF_OPEN
        time.sleep(1.1)
        breaker._get_state("api")

        # One failure should reopen circuit
        breaker.record_failure("api")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.OPEN


class TestCircuitBreakerAvailability:
    """Test availability checks."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=2, success_threshold=2, timeout_seconds=1.0)
        return cb

    def test_is_available_closed(self, breaker):
        """Test availability when CLOSED."""
        assert breaker.is_available("api")

    def test_is_available_open(self, breaker):
        """Test availability when OPEN."""
        # Move to OPEN
        breaker.record_failure("api")
        breaker.record_failure("api")

        assert not breaker.is_available("api")

    def test_is_available_half_open_under_limit(self, breaker):
        """Test availability in HALF_OPEN under request limit."""
        # Move to OPEN then HALF_OPEN
        breaker.record_failure("api")
        breaker.record_failure("api")
        time.sleep(1.1)
        breaker._get_state("api")

        # Should be available for limited requests
        assert breaker.is_available("api")

    def test_is_available_half_open_over_limit(self, breaker):
        """Test availability in HALF_OPEN over request limit."""
        # Move to OPEN then HALF_OPEN
        breaker.record_failure("api")
        breaker.record_failure("api")
        time.sleep(1.1)
        breaker._get_state("api")

        # Exhaust half-open request quota
        config = breaker._configs["api"]
        stats = breaker._stats["api"]
        stats.half_open_requests = config.half_open_max_requests

        assert not breaker.is_available("api")

    def test_is_available_unconfigured_source(self, breaker):
        """Test availability for unconfigured source."""
        # Should return True for unconfigured sources
        assert breaker.is_available("unconfigured")


class TestCircuitBreakerCall:
    """Test circuit breaker call method."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=2, timeout_seconds=1.0)
        return cb

    def test_call_success(self, breaker):
        """Test successful call."""
        func = MagicMock(return_value="result")

        result = breaker.call("api", func)

        assert result == "result"
        func.assert_called_once()

        stats = breaker._stats["api"]
        assert stats.success_count == 1
        assert stats.total_successes == 1
        assert stats.total_requests == 1

    def test_call_failure_raises(self, breaker):
        """Test call with failure raises exception."""
        func = MagicMock(side_effect=ValueError("test error"))

        with pytest.raises(ValueError, match="test error"):
            breaker.call("api", func)

        stats = breaker._stats["api"]
        assert stats.failure_count == 1
        assert stats.total_failures == 1

    def test_call_failure_with_fallback(self, breaker):
        """Test call with failure uses fallback."""
        func = MagicMock(side_effect=RuntimeError("error"))
        fallback = MagicMock(return_value="fallback_result")

        result = breaker.call("api", func, fallback=fallback)

        assert result == "fallback_result"
        fallback.assert_called_once()

    def test_call_circuit_open_raises(self, breaker):
        """Test call when circuit is OPEN raises error."""
        # Open circuit
        breaker.record_failure("api")
        breaker.record_failure("api")

        func = MagicMock()

        with pytest.raises(CircuitBreakerError, match="Circuit open for api"):
            breaker.call("api", func)

        func.assert_not_called()

    def test_call_circuit_open_with_fallback(self, breaker):
        """Test call when circuit is OPEN uses fallback."""
        # Open circuit
        breaker.record_failure("api")
        breaker.record_failure("api")

        func = MagicMock()
        fallback = MagicMock(return_value="fallback")

        result = breaker.call("api", func, fallback=fallback)

        assert result == "fallback"
        func.assert_not_called()
        fallback.assert_called_once()

    def test_call_increments_half_open_requests(self, breaker):
        """Test call increments half-open request counter."""
        # Move to HALF_OPEN
        breaker.record_failure("api")
        breaker.record_failure("api")
        time.sleep(1.1)
        breaker._get_state("api")

        func = MagicMock(return_value="ok")

        breaker.call("api", func)

        stats = breaker._stats["api"]
        assert stats.half_open_requests == 1

    def test_call_increments_total_requests(self, breaker):
        """Test call increments total request counter."""
        func = MagicMock(return_value="ok")

        breaker.call("api", func)
        breaker.call("api", func)

        stats = breaker._stats["api"]
        assert stats.total_requests == 2


class TestCircuitBreakerStats:
    """Test statistics methods."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=5)
        return cb

    def test_record_success(self, breaker):
        """Test recording success."""
        breaker.record_success("api")

        stats = breaker._stats["api"]
        assert stats.success_count == 1
        assert stats.total_successes == 1
        assert stats.last_success_time is not None
        assert stats.failure_count == 0  # Reset on success

    def test_record_success_resets_failure_count(self, breaker):
        """Test success resets failure count."""
        breaker.record_failure("api")
        assert breaker._stats["api"].failure_count == 1

        breaker.record_success("api")
        assert breaker._stats["api"].failure_count == 0

    def test_record_success_unconfigured_source(self, breaker):
        """Test recording success for unconfigured source."""
        # Should not raise error
        breaker.record_success("unconfigured")

    def test_record_failure(self, breaker):
        """Test recording failure."""
        breaker.record_failure("api", "test error")

        stats = breaker._stats["api"]
        assert stats.failure_count == 1
        assert stats.total_failures == 1
        assert stats.last_failure_time is not None
        assert stats.success_count == 0  # Reset on failure

    def test_record_failure_resets_success_count(self, breaker):
        """Test failure resets success count."""
        breaker.record_success("api")
        assert breaker._stats["api"].success_count == 1

        breaker.record_failure("api")
        assert breaker._stats["api"].success_count == 0

    def test_record_failure_unconfigured_source(self, breaker):
        """Test recording failure for unconfigured source."""
        # Should not raise error
        breaker.record_failure("unconfigured")

    def test_get_stats(self, breaker):
        """Test getting statistics."""
        breaker.record_success("api")
        breaker.record_failure("api")

        stats = breaker.get_stats("api")

        assert stats is not None
        assert stats["source_id"] == "api"
        assert stats["state"] == "closed"
        assert stats["total_successes"] == 1
        assert stats["total_failures"] == 1
        assert stats["failure_threshold"] == 5
        assert "last_success_time" in stats
        assert "last_failure_time" in stats

    def test_get_stats_nonexistent(self, breaker):
        """Test getting stats for nonexistent source."""
        stats = breaker.get_stats("nonexistent")
        assert stats is None

    def test_get_stats_reflects_state(self, breaker):
        """Test stats reflect current state."""
        # CLOSED
        stats = breaker.get_stats("api")
        assert stats["state"] == "closed"

        # OPEN
        for i in range(5):
            breaker.record_failure("api")
        stats = breaker.get_stats("api")
        assert stats["state"] == "open"


class TestCircuitBreakerControl:
    """Test manual control methods."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=3)
        return cb

    def test_reset(self, breaker):
        """Test resetting circuit."""
        # Add some stats
        breaker.record_failure("api")
        breaker.record_success("api")

        breaker.reset("api")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.CLOSED
        assert stats.failure_count == 0
        assert stats.success_count == 0
        assert stats.total_requests == 0

    def test_reset_nonexistent(self, breaker):
        """Test resetting nonexistent source."""
        # Should not raise error
        breaker.reset("nonexistent")

    def test_force_open(self, breaker):
        """Test forcing circuit open."""
        breaker.force_open("api")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.OPEN
        assert not breaker.is_available("api")

    def test_force_open_nonexistent(self, breaker):
        """Test force open on nonexistent source."""
        # Should not raise error
        breaker.force_open("nonexistent")

    def test_force_close(self, breaker):
        """Test forcing circuit closed."""
        # Open circuit
        for i in range(3):
            breaker.record_failure("api")
        assert breaker._stats["api"].state == CircuitState.OPEN

        # Force close
        breaker.force_close("api")

        stats = breaker._stats["api"]
        assert stats.state == CircuitState.CLOSED
        assert stats.failure_count == 0
        assert breaker.is_available("api")

    def test_force_close_nonexistent(self, breaker):
        """Test force close on nonexistent source."""
        # Should not raise error
        breaker.force_close("nonexistent")


class TestCircuitBreakerThreadSafety:
    """Test thread safety."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=100)
        return cb

    def test_concurrent_success_recording(self, breaker):
        """Test concurrent success recording."""
        def record_successes():
            for _ in range(10):
                breaker.record_success("api")

        threads = [threading.Thread(target=record_successes) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = breaker._stats["api"]
        assert stats.total_successes == 50

    def test_concurrent_failure_recording(self, breaker):
        """Test concurrent failure recording."""
        def record_failures():
            for _ in range(10):
                breaker.record_failure("api")

        threads = [threading.Thread(target=record_failures) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = breaker._stats["api"]
        assert stats.total_failures == 50


class TestCircuitBreakerGetState:
    """Test internal _get_state method."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=2, timeout_seconds=1.0)
        return cb

    def test_get_state_unconfigured(self, breaker):
        """Test _get_state for unconfigured source."""
        state = breaker._get_state("unconfigured")
        assert state == CircuitState.CLOSED

    def test_get_state_no_config(self, breaker):
        """Test _get_state with stats but no config."""
        # Add stats without config
        breaker._stats["orphan"] = CircuitStats(source_id="orphan")

        state = breaker._get_state("orphan")
        assert state == CircuitState.CLOSED


class TestGlobalSingleton:
    """Test global singleton instance."""

    def test_get_circuit_breaker_singleton(self):
        """Test singleton returns same instance."""
        cb1 = get_circuit_breaker()
        cb2 = get_circuit_breaker()

        assert cb1 is cb2

    def test_get_circuit_breaker_initializes(self):
        """Test singleton initializes on first call."""
        # Reset module-level singleton
        import app.ingestion.circuit_breaker
        app.ingestion.circuit_breaker._circuit_breaker = None

        cb = get_circuit_breaker()
        assert cb is not None
        assert isinstance(cb, CircuitBreaker)


class TestCircuitConfig:
    """Test CircuitConfig dataclass."""

    def test_config_creation(self):
        """Test creating config."""
        config = CircuitConfig(
            source_id="test",
            failure_threshold=10,
            success_threshold=5,
            timeout_seconds=120.0,
            half_open_max_requests=2,
        )

        assert config.source_id == "test"
        assert config.failure_threshold == 10
        assert config.success_threshold == 5
        assert config.timeout_seconds == 120.0
        assert config.half_open_max_requests == 2

    def test_config_defaults(self):
        """Test config default values."""
        config = CircuitConfig(source_id="test")

        assert config.failure_threshold == 5
        assert config.success_threshold == 3
        assert config.timeout_seconds == 60.0
        assert config.half_open_max_requests == 3


class TestCircuitStats:
    """Test CircuitStats dataclass."""

    def test_stats_creation(self):
        """Test creating stats."""
        stats = CircuitStats(source_id="test")

        assert stats.source_id == "test"
        assert stats.state == CircuitState.CLOSED
        assert stats.failure_count == 0
        assert stats.success_count == 0
        assert stats.total_requests == 0
        assert stats.state_changed_at is not None

    def test_stats_with_values(self):
        """Test stats with custom values."""
        stats = CircuitStats(
            source_id="test",
            state=CircuitState.OPEN,
            failure_count=5,
            success_count=10,
            total_requests=20,
        )

        assert stats.state == CircuitState.OPEN
        assert stats.failure_count == 5
        assert stats.success_count == 10
        assert stats.total_requests == 20


class TestCircuitBreakerEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def breaker(self):
        """Create configured breaker."""
        cb = CircuitBreaker()
        cb.configure("api", failure_threshold=2, success_threshold=2, timeout_seconds=0.5)
        return cb

    def test_very_short_timeout(self, breaker):
        """Test circuit with very short timeout."""
        # Open circuit
        breaker.record_failure("api")
        breaker.record_failure("api")

        # Wait minimal time
        time.sleep(0.6)

        # Should transition to HALF_OPEN
        state = breaker._get_state("api")
        assert state == CircuitState.HALF_OPEN

    def test_state_change_timestamp_updates(self, breaker):
        """Test state_changed_at updates on transitions."""
        initial_time = breaker._stats["api"].state_changed_at

        # Trigger state change
        breaker.record_failure("api")
        breaker.record_failure("api")

        changed_time = breaker._stats["api"].state_changed_at
        assert changed_time > initial_time

    def test_half_open_requests_reset_on_transition(self, breaker):
        """Test half_open_requests resets on OPEN to HALF_OPEN."""
        # Open circuit
        breaker.record_failure("api")
        breaker.record_failure("api")

        # Manually set half_open_requests
        breaker._stats["api"].half_open_requests = 5

        # Transition to HALF_OPEN
        time.sleep(0.6)
        breaker._get_state("api")

        assert breaker._stats["api"].half_open_requests == 0

    def test_multiple_sources_independent(self):
        """Test multiple sources operate independently."""
        breaker = CircuitBreaker()
        breaker.configure("api1", failure_threshold=2)
        breaker.configure("api2", failure_threshold=2)

        # Fail only api1
        breaker.record_failure("api1")
        breaker.record_failure("api1")

        # api1 should be open, api2 still closed
        assert not breaker.is_available("api1")
        assert breaker.is_available("api2")
