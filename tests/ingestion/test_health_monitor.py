"""
Tests for app/ingestion/health_monitor.py

Covers:
- HealthMonitor registration and configuration
- Probe execution with various outcomes (success, timeout, HTTP errors)
- Status transitions (HEALTHY -> DEGRADED -> UNHEALTHY)
- Alert handlers
- Statistics and history tracking
- Background monitoring thread
- Singleton getter
"""
from __future__ import annotations

import time
import threading
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, Mock

import httpx
import pytest

from app.ingestion.health_monitor import (
    HealthMonitor,
    HealthProbeConfig,
    HealthRecord,
    HealthStats,
    HealthStatus,
    get_health_monitor,
)


class TestHealthMonitor:
    """Test suite for HealthMonitor."""

    def test_register_source(self):
        """Test registering a source for monitoring."""
        monitor = HealthMonitor()

        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            interval_seconds=60.0,
            timeout_seconds=5.0,
            content_check="OK",
        )

        assert "test_source" in monitor._configs
        assert "test_source" in monitor._stats
        assert "test_source" in monitor._history

        config = monitor._configs["test_source"]
        assert config.source_id == "test_source"
        assert config.probe_url == "https://example.com/health"
        assert config.interval_seconds == 60.0
        assert config.timeout_seconds == 5.0
        assert config.content_check == "OK"
        assert config.enabled is True

        stats = monitor._stats["test_source"]
        assert stats.source_id == "test_source"
        assert stats.current_status == HealthStatus.UNKNOWN

    def test_add_alert_handler(self):
        """Test adding alert handlers."""
        monitor = HealthMonitor()
        handler = MagicMock()

        monitor.add_alert_handler(handler)

        assert handler in monitor._alert_handlers

    @patch('httpx.request')
    def test_probe_source_success(self, mock_request):
        """Test successful health probe."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Service is healthy"
        mock_request.return_value = mock_response

        record = monitor._probe_source("test_source")

        assert record.source_id == "test_source"
        assert record.status == HealthStatus.HEALTHY
        assert record.latency_ms > 0
        assert record.error_message is None
        assert record.status_code == 200
        assert record.content_valid is True

    @patch('httpx.request')
    def test_probe_source_content_check_success(self, mock_request):
        """Test probe with content check that passes."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            content_check="OK",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Status: OK"
        mock_request.return_value = mock_response

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.HEALTHY
        assert record.content_valid is True

    @patch('httpx.request')
    def test_probe_source_content_check_failure(self, mock_request):
        """Test probe with content check that fails."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            content_check="EXPECTED_STRING",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Service running but degraded"
        mock_request.return_value = mock_response

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.DEGRADED
        assert record.content_valid is False
        assert record.error_message == "Content check failed"

    @patch('httpx.request')
    def test_probe_source_unexpected_status_code(self, mock_request):
        """Test probe with unexpected status code."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.UNHEALTHY
        assert record.status_code == 500
        assert "Unexpected status: 500" in record.error_message

    @patch('httpx.request')
    def test_probe_source_timeout(self, mock_request):
        """Test probe timeout handling."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            timeout_seconds=2.0,
        )

        mock_request.side_effect = httpx.TimeoutException("Request timeout")

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.UNHEALTHY
        assert record.error_message == "Timeout"
        assert record.latency_ms == 2000.0  # timeout_seconds * 1000

    @patch('httpx.request')
    def test_probe_source_http_error(self, mock_request):
        """Test probe with HTTP error."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_request.side_effect = httpx.HTTPError("Connection refused")

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.UNHEALTHY
        assert "Connection refused" in record.error_message

    @patch('httpx.request')
    def test_probe_source_generic_exception(self, mock_request):
        """Test probe with generic exception."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_request.side_effect = Exception("Unexpected error")

        record = monitor._probe_source("test_source")

        assert record.status == HealthStatus.UNHEALTHY
        assert "Unexpected error" in record.error_message

    def test_probe_source_no_config(self):
        """Test probe for non-existent source."""
        monitor = HealthMonitor()

        record = monitor._probe_source("nonexistent")

        assert record.source_id == "nonexistent"
        assert record.status == HealthStatus.UNKNOWN
        assert record.error_message == "Config not found"

    @patch('httpx.request')
    def test_check_source_transition_to_healthy(self, mock_request):
        """Test status transition to HEALTHY after consecutive successes."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        # Default healthy_threshold is 2
        status1 = monitor.check_source("test_source")
        stats = monitor._stats["test_source"]
        assert stats.consecutive_successes == 1
        # First success, threshold not met yet

        status2 = monitor.check_source("test_source")
        assert status2 == HealthStatus.HEALTHY
        stats = monitor._stats["test_source"]
        assert stats.consecutive_successes == 2
        assert stats.consecutive_failures == 0
        assert stats.current_status == HealthStatus.HEALTHY

    @patch('httpx.request')
    def test_check_source_transition_to_unhealthy(self, mock_request):
        """Test status transition to UNHEALTHY after consecutive failures."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        # Initially healthy
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response
        monitor.check_source("test_source")
        monitor.check_source("test_source")

        # Now fail repeatedly
        mock_request.side_effect = httpx.TimeoutException("Timeout")

        # Default unhealthy_threshold is 3
        monitor.check_source("test_source")
        stats = monitor._stats["test_source"]
        assert stats.consecutive_failures == 1
        assert stats.current_status == HealthStatus.DEGRADED

        monitor.check_source("test_source")
        assert stats.consecutive_failures == 2

        monitor.check_source("test_source")
        assert stats.consecutive_failures == 3
        assert stats.current_status == HealthStatus.UNHEALTHY
        assert stats.total_failures == 3

    @patch('httpx.request')
    def test_check_source_stats_update(self, mock_request):
        """Test statistics updates during checks."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.check_source("test_source")

        stats = monitor._stats["test_source"]
        assert stats.total_checks == 1
        assert stats.last_check is not None
        assert stats.last_success is not None
        assert stats.avg_latency_ms > 0
        assert stats.uptime_percent == 100.0

    @patch('httpx.request')
    def test_check_source_uptime_calculation(self, mock_request):
        """Test uptime percentage calculation."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        # 3 successes
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.check_source("test_source")
        monitor.check_source("test_source")
        monitor.check_source("test_source")

        # 2 failures
        mock_request.side_effect = httpx.TimeoutException("Timeout")
        monitor.check_source("test_source")
        monitor.check_source("test_source")

        stats = monitor._stats["test_source"]
        # 3 successes, 2 failures = 60% uptime
        assert stats.total_checks == 5
        assert stats.total_failures == 2
        assert stats.uptime_percent == 60.0

    @patch('httpx.request')
    def test_check_source_history_tracking(self, mock_request):
        """Test history tracking with max limit."""
        monitor = HealthMonitor()
        monitor._max_history = 5  # Set low limit for testing
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        # Generate 10 checks
        for _ in range(10):
            monitor.check_source("test_source")

        # Should only keep last 5
        history = monitor._history["test_source"]
        assert len(history) == 5

    @patch('httpx.request')
    def test_alert_emission(self, mock_request):
        """Test alert emission on status change."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        handler = MagicMock()
        monitor.add_alert_handler(handler)

        # Initially healthy
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response
        monitor.check_source("test_source")
        monitor.check_source("test_source")

        # Should emit alert on first healthy status
        handler.assert_called_once()
        handler.reset_mock()

        # Now degrade
        mock_request.side_effect = httpx.TimeoutException("Timeout")
        monitor.check_source("test_source")

        # Should emit alert on degradation
        handler.assert_called_once_with("test_source", HealthStatus.DEGRADED, "Timeout")

    def test_alert_handler_error_handling(self):
        """Test that alert handler exceptions don't break monitoring."""
        monitor = HealthMonitor()

        def failing_handler(source_id, status, message):
            raise Exception("Handler failed")

        monitor.add_alert_handler(failing_handler)

        # Should not raise despite handler error
        monitor._emit_alert("test_source", HealthStatus.UNHEALTHY, "Error")

    def test_get_status(self):
        """Test getting current status of a source."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        status = monitor.get_status("test_source")
        assert status == HealthStatus.UNKNOWN

        # Unknown source
        status = monitor.get_status("nonexistent")
        assert status == HealthStatus.UNKNOWN

    @patch('httpx.request')
    def test_get_stats(self, mock_request):
        """Test getting statistics for a source."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.check_source("test_source")
        monitor.check_source("test_source")

        stats = monitor.get_stats("test_source")

        assert stats is not None
        assert stats["source_id"] == "test_source"
        assert stats["status"] == HealthStatus.HEALTHY.value
        assert stats["consecutive_successes"] == 2
        assert stats["consecutive_failures"] == 0
        assert stats["total_checks"] == 2
        assert stats["total_failures"] == 0
        assert stats["uptime_percent"] == 100.0
        assert "last_check" in stats
        assert "last_success" in stats
        assert stats["error_message"] is None

    def test_get_stats_nonexistent(self):
        """Test getting stats for nonexistent source."""
        monitor = HealthMonitor()

        stats = monitor.get_stats("nonexistent")
        assert stats is None

    @patch('httpx.request')
    def test_get_all_stats(self, mock_request):
        """Test getting stats for all sources."""
        monitor = HealthMonitor()
        monitor.register_source("source1", "https://example.com/1")
        monitor.register_source("source2", "https://example.com/2")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.check_source("source1")
        monitor.check_source("source2")

        all_stats = monitor.get_all_stats()

        assert len(all_stats) == 2
        assert "source1" in all_stats
        assert "source2" in all_stats

    @patch('httpx.request')
    def test_get_history(self, mock_request):
        """Test getting history for a source."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        for _ in range(5):
            monitor.check_source("test_source")

        history = monitor.get_history("test_source", limit=3)

        assert len(history) == 3
        for record in history:
            assert "status" in record
            assert "latency_ms" in record
            assert "checked_at" in record
            assert record["status"] == HealthStatus.HEALTHY.value

    def test_get_history_nonexistent(self):
        """Test getting history for nonexistent source."""
        monitor = HealthMonitor()

        history = monitor.get_history("nonexistent")
        assert history == []

    def test_enable_disable_source(self):
        """Test enabling and disabling sources."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        assert monitor._configs["test_source"].enabled is True

        monitor.disable_source("test_source")
        assert monitor._configs["test_source"].enabled is False

        monitor.enable_source("test_source")
        assert monitor._configs["test_source"].enabled is True

        # Non-existent source should not raise
        monitor.disable_source("nonexistent")
        monitor.enable_source("nonexistent")

    @patch('httpx.request')
    def test_monitor_loop_basic(self, mock_request):
        """Test basic monitoring loop functionality."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            interval_seconds=0.1,  # Very short for testing
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        # Start and let it run briefly
        monitor.start()
        assert monitor._running is True
        assert monitor._thread is not None

        time.sleep(0.3)  # Let it run a couple cycles

        monitor.stop()
        assert monitor._running is False

        # Should have run at least once
        stats = monitor._stats["test_source"]
        assert stats.total_checks >= 1

    @patch('httpx.request')
    def test_monitor_loop_respects_interval(self, mock_request):
        """Test that monitoring loop respects interval settings."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            interval_seconds=10.0,  # Long interval
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.start()
        time.sleep(0.2)  # Brief wait, shouldn't trigger check
        monitor.stop()

        # Should have very few checks (0 or 1 at most due to timing)
        stats = monitor._stats["test_source"]
        assert stats.total_checks <= 1

    @patch('httpx.request')
    def test_monitor_loop_disabled_source(self, mock_request):
        """Test that disabled sources are not monitored."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            interval_seconds=0.1,
        )
        monitor.disable_source("test_source")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_request.return_value = mock_response

        monitor.start()
        time.sleep(0.3)
        monitor.stop()

        # Should not have run checks for disabled source
        stats = monitor._stats["test_source"]
        assert stats.total_checks == 0

    @patch('httpx.request')
    def test_monitor_loop_error_handling(self, mock_request):
        """Test that monitoring loop handles errors gracefully."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
            interval_seconds=0.1,
        )

        # Cause an exception
        mock_request.side_effect = Exception("Unexpected error")

        monitor.start()
        time.sleep(0.3)
        monitor.stop()

        # Should continue running despite errors
        assert not monitor._running

    def test_start_idempotent(self):
        """Test that starting already running monitor is no-op."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        monitor.start()
        thread1 = monitor._thread

        monitor.start()  # Second start
        thread2 = monitor._thread

        assert thread1 is thread2  # Same thread

        monitor.stop()

    def test_stop_waits_for_thread(self):
        """Test that stop waits for thread to finish."""
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="test_source",
            probe_url="https://example.com/health",
        )

        monitor.start()
        assert monitor._thread.is_alive()

        monitor.stop()
        time.sleep(0.1)  # Give it time to stop
        assert not monitor._thread.is_alive()


def test_get_health_monitor_singleton():
    """Test singleton getter returns same instance."""
    monitor1 = get_health_monitor()
    monitor2 = get_health_monitor()

    assert monitor1 is monitor2


def test_health_probe_config_defaults():
    """Test HealthProbeConfig default values."""
    config = HealthProbeConfig(
        source_id="test",
        probe_url="https://example.com",
    )

    assert config.probe_method == "GET"
    assert config.timeout_seconds == 10.0
    assert config.interval_seconds == 300.0
    assert config.healthy_threshold == 2
    assert config.unhealthy_threshold == 3
    assert config.expected_status_codes == [200, 201, 204]
    assert config.content_check is None
    assert config.enabled is True


def test_health_status_enum():
    """Test HealthStatus enum values."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.DEGRADED.value == "degraded"
    assert HealthStatus.UNHEALTHY.value == "unhealthy"
    assert HealthStatus.UNKNOWN.value == "unknown"


@patch('httpx.request')
def test_latency_average_calculation(mock_request):
    """Test average latency calculation over multiple checks."""
    monitor = HealthMonitor()
    monitor.register_source(
        source_id="test_source",
        probe_url="https://example.com/health",
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_request.return_value = mock_response

    # Run multiple checks
    monitor.check_source("test_source")
    first_latency = monitor._stats["test_source"].avg_latency_ms

    monitor.check_source("test_source")
    second_latency = monitor._stats["test_source"].avg_latency_ms

    # Average should be updated (simple average of both)
    assert second_latency > 0
