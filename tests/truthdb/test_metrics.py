"""
Tests for TruthDB Metrics — S37

Tests for metrics functions and LatencyTimer.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.truthdb import metrics


class TestIncrementFunctions:
    """Tests for increment counter functions."""

    def test_inc_promotion_attempt(self):
        """Increment promotion attempt counter."""
        initial = metrics._local.get("promotion_attempt:claim_type:test", 0)

        metrics.inc_promotion_attempt("claim_type", env="test")

        assert metrics._local["promotion_attempt:claim_type:test"] == initial + 1

    def test_inc_promotion_success(self):
        """Increment promotion success counter."""
        initial = metrics._local.get("promotion_success:claim_type:test", 0)

        metrics.inc_promotion_success("claim_type", env="test")

        assert metrics._local["promotion_success:claim_type:test"] == initial + 1

    def test_inc_contestation(self):
        """Increment contestation counter."""
        initial = metrics._local.get("contestation:claim_type:test:pending", 0)

        metrics.inc_contestation("claim_type", env="test", outcome="pending")

        assert metrics._local["contestation:claim_type:test:pending"] == initial + 1

    def test_inc_contestation_processed(self):
        """Increment contestation with processed outcome."""
        initial = metrics._local.get("contestation:claim_type:test:processed", 0)

        metrics.inc_contestation("claim_type", env="test", outcome="processed")

        assert metrics._local["contestation:claim_type:test:processed"] == initial + 1

    def test_inc_flow_error(self):
        """Increment flow error counter."""
        initial = metrics._local.get("flow_error:promotion:test:exception", 0)

        metrics.inc_flow_error("promotion", env="test", error_type="exception")

        assert metrics._local["flow_error:promotion:test:exception"] == initial + 1

    def test_inc_flow_error_default_type(self):
        """Increment flow error with default error type."""
        initial = metrics._local.get("flow_error:validation:prod:unknown", 0)

        metrics.inc_flow_error("validation", env="prod")

        assert metrics._local["flow_error:validation:prod:unknown"] == initial + 1


class TestRecordFunctions:
    """Tests for record metric functions."""

    def test_record_transition(self):
        """Record a transition."""
        with patch.object(metrics, "_transitions") as mock_transitions:
            mock_labels = MagicMock()
            mock_transitions.labels.return_value = mock_labels

            metrics.record_transition("PENDING", "VERIFIED", "success", "admin")

            mock_transitions.labels.assert_called_once_with("PENDING", "VERIFIED", "success", "admin")
            mock_labels.inc.assert_called_once()

    def test_record_failure(self):
        """Record a failure."""
        initial = metrics._local.get("truth_failure:invalid_claim", 0)

        with patch.object(metrics, "_failures") as mock_failures:
            mock_labels = MagicMock()
            mock_failures.labels.return_value = mock_labels

            metrics.record_failure("invalid_claim")

            mock_failures.labels.assert_called_once_with(reason="invalid_claim")
            mock_labels.inc.assert_called_once()

        assert metrics._local["truth_failure:invalid_claim"] == initial + 1

    def test_observe_latency(self):
        """Observe latency metric."""
        with patch.object(metrics, "_latency") as mock_latency:
            mock_labels = MagicMock()
            mock_latency.labels.return_value = mock_labels

            metrics.observe_latency("PENDING", "VERIFIED", 1.5)

            mock_latency.labels.assert_called_once_with("PENDING", "VERIFIED")
            mock_labels.observe.assert_called_once_with(1.5)


class TestSnapshot:
    """Tests for snapshot function."""

    def test_snapshot(self):
        """Snapshot returns current counters."""
        metrics._local["test_counter"] = 42

        result = metrics.snapshot()

        assert isinstance(result, dict)
        assert "counters" in result
        assert result["counters"]["test_counter"] == 42


class TestLatencyTimer:
    """Tests for LatencyTimer context manager."""

    def test_latency_timer_basic(self):
        """Basic latency timer usage."""
        timer = metrics.LatencyTimer(flow_type="test_flow", env="test")

        with timer:
            pass  # Simulate some work

        assert timer._start > 0

    def test_latency_timer_with_states(self):
        """Latency timer with from/to states."""
        with patch.object(metrics, "observe_latency") as mock_observe:
            timer = metrics.LatencyTimer(from_state="PENDING", to_state="VERIFIED")

            with timer:
                pass

            mock_observe.assert_called_once()
            args = mock_observe.call_args[0]
            assert args[0] == "PENDING"
            assert args[1] == "VERIFIED"
            assert args[2] >= 0  # elapsed time

    def test_latency_timer_without_states(self):
        """Latency timer without from/to states uses local counter."""
        initial = metrics._local.get("latency:generic:test", 0)

        timer = metrics.LatencyTimer(flow_type=None, env="test")

        with timer:
            pass

        assert metrics._local["latency:generic:test"] == initial + 1

    def test_latency_timer_with_flow_type(self):
        """Latency timer with flow type."""
        initial = metrics._local.get("latency:promotion:test", 0)

        timer = metrics.LatencyTimer(flow_type="promotion", env="test")

        with timer:
            pass

        assert metrics._local["latency:promotion:test"] == initial + 1

    def test_latency_timer_returns_self(self):
        """Latency timer returns self on enter."""
        timer = metrics.LatencyTimer(flow_type="test")

        with timer as t:
            assert t is timer

    def test_latency_timer_does_not_suppress_exception(self):
        """Latency timer does not suppress exceptions."""
        timer = metrics.LatencyTimer(flow_type="test")

        with pytest.raises(ValueError, match="test error"):
            with timer:
                raise ValueError("test error")
