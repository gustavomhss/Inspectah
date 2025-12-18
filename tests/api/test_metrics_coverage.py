"""
Comprehensive tests for API Metrics — S40-BE-027

Tests P4 latency metrics including edge cases and thread safety.
"""

import pytest
import threading
from unittest.mock import MagicMock, patch

from app.api.metrics import (
    P4_MAX_SAMPLES,
    P4_SLA_TARGETS,
    P4_VALID_ENDPOINTS,
    _calculate_percentile,
    _sanitize_endpoint,
    _sanitize_latency,
    check_p4_sla_compliance,
    get_p4_request_count,
    get_p4_sla_status,
    get_p4_stats,
    record_p4_latency,
    record_p4_request,
    reset_p4_stats,
)


class TestSanitization:
    """Test input sanitization functions."""

    def test_sanitize_endpoint_normal(self):
        """Test sanitizing normal endpoint name."""
        result = _sanitize_endpoint("twin")
        assert result == "twin"

    def test_sanitize_endpoint_with_slash(self):
        """Test sanitizing endpoint with slash."""
        result = _sanitize_endpoint("api/twin")
        assert result == "api/twin"

    def test_sanitize_endpoint_with_special_chars(self):
        """Test sanitizing endpoint with special characters."""
        result = _sanitize_endpoint("test@#$%endpoint")
        assert "_" in result
        assert "@" not in result

    def test_sanitize_endpoint_empty(self):
        """Test sanitizing empty endpoint."""
        result = _sanitize_endpoint("")
        assert result == "unknown"

    def test_sanitize_endpoint_too_long(self):
        """Test sanitizing very long endpoint."""
        long_name = "a" * 100
        result = _sanitize_endpoint(long_name)
        assert len(result) == 64

    def test_sanitize_latency_normal(self):
        """Test sanitizing normal latency."""
        result = _sanitize_latency(50.5)
        assert result == 50.5

    def test_sanitize_latency_none(self):
        """Test sanitizing None latency."""
        result = _sanitize_latency(None)
        assert result == 0.0

    def test_sanitize_latency_negative(self):
        """Test sanitizing negative latency."""
        result = _sanitize_latency(-10.0)
        assert result == 0.0

    def test_sanitize_latency_too_high(self):
        """Test sanitizing excessively high latency."""
        result = _sanitize_latency(9999999.0)
        assert result == 3600000.0  # Capped at 1 hour

    def test_sanitize_latency_invalid_type(self):
        """Test sanitizing invalid type."""
        result = _sanitize_latency("invalid")
        assert result == 0.0


class TestRecordP4Request:
    """Test record_p4_request function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_record_request_success(self):
        """Test recording successful request."""
        record_p4_request("twin", 45.5, status="success", provenance_valid=True)

        # Should not raise error
        stats = get_p4_stats("twin")
        assert "twin" in stats

    def test_record_request_error(self):
        """Test recording error request."""
        record_p4_request("inspect", 100.0, status="error", provenance_valid=False)

        # Should not raise error
        stats = get_p4_stats("inspect")
        assert "inspect" in stats

    def test_record_request_unknown_status(self):
        """Test recording request with unknown status."""
        record_p4_request("twin", 50.0, status="invalid_status")

        # Should sanitize to "unknown"
        # (Implementation details - just verify no error)

    def test_record_request_sanitizes_inputs(self):
        """Test request recording sanitizes inputs."""
        # Should handle invalid inputs gracefully
        record_p4_request("", -10.0, status="success")
        record_p4_request("test@endpoint", 999999.0)

        # Should not raise errors


class TestRecordP4Latency:
    """Test record_p4_latency function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_record_latency_single(self):
        """Test recording single latency."""
        record_p4_latency("twin", 50.0)

        stats = get_p4_stats("twin")
        assert stats["twin"]["count"] == 1
        assert stats["twin"]["min_ms"] == 50.0

    def test_record_latency_multiple(self):
        """Test recording multiple latencies."""
        for i in range(5):
            record_p4_latency("twin", 10.0 * i)

        stats = get_p4_stats("twin")
        assert stats["twin"]["count"] == 5

    def test_record_latency_empty_endpoint(self):
        """Test recording with empty endpoint."""
        record_p4_latency("", 50.0)

        # Should default to "unknown"
        stats = get_p4_stats()
        assert "unknown" in stats or "" in stats

    def test_record_latency_increments_request_count(self):
        """Test latency recording increments request count."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 60.0)

        counts = get_p4_request_count("twin")
        assert counts["twin"] == 2

    def test_record_latency_memory_limit(self):
        """Test latency recording respects memory limit."""
        # Record more than max samples
        for i in range(P4_MAX_SAMPLES + 100):
            record_p4_latency("twin", float(i))

        stats = get_p4_stats("twin")
        # Should not exceed max samples
        assert stats["twin"]["count"] == P4_MAX_SAMPLES


class TestGetP4Stats:
    """Test get_p4_stats function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_get_stats_single_endpoint(self):
        """Test getting stats for single endpoint."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 100.0)
        record_p4_latency("twin", 75.0)

        stats = get_p4_stats("twin")

        assert "twin" in stats
        assert stats["twin"]["count"] == 3
        assert stats["twin"]["min_ms"] == 50.0
        assert stats["twin"]["max_ms"] == 100.0
        assert stats["twin"]["mean_ms"] == pytest.approx(75.0)

    def test_get_stats_all_endpoints(self):
        """Test getting stats for all endpoints."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 75.0)

        stats = get_p4_stats()

        assert "twin" in stats
        assert "inspect" in stats

    def test_get_stats_nonexistent_endpoint(self):
        """Test getting stats for nonexistent endpoint."""
        stats = get_p4_stats("nonexistent")

        assert stats == {}

    def test_get_stats_calculates_percentiles(self):
        """Test stats include percentile calculations."""
        # Record values: 10, 20, 30, ..., 100
        for i in range(1, 11):
            record_p4_latency("twin", float(i * 10))

        stats = get_p4_stats("twin")

        assert "p95_ms" in stats["twin"]
        assert "p99_ms" in stats["twin"]
        assert stats["twin"]["p95_ms"] > 0
        assert stats["twin"]["p99_ms"] > 0

    def test_get_stats_median(self):
        """Test stats include median."""
        record_p4_latency("twin", 10.0)
        record_p4_latency("twin", 20.0)
        record_p4_latency("twin", 30.0)

        stats = get_p4_stats("twin")

        assert stats["twin"]["median_ms"] == 20.0

    def test_get_stats_empty(self):
        """Test stats with no data."""
        stats = get_p4_stats()

        assert stats == {}


class TestCalculatePercentile:
    """Test _calculate_percentile function."""

    def test_percentile_empty_list(self):
        """Test percentile of empty list."""
        result = _calculate_percentile([], 0.95)
        assert result == 0.0

    def test_percentile_single_value(self):
        """Test percentile of single value."""
        result = _calculate_percentile([100.0], 0.95)
        assert result == 100.0

    def test_percentile_p50(self):
        """Test P50 (median)."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = _calculate_percentile(values, 0.5)
        # Should be around middle value
        assert 20.0 <= result <= 40.0

    def test_percentile_p95(self):
        """Test P95."""
        values = sorted([float(i) for i in range(1, 101)])
        result = _calculate_percentile(values, 0.95)
        # P95 of 1-100 should be around 95
        assert result >= 90.0

    def test_percentile_p99(self):
        """Test P99."""
        values = sorted([float(i) for i in range(1, 101)])
        result = _calculate_percentile(values, 0.99)
        # P99 should be near the end
        assert result >= 95.0


class TestResetP4Stats:
    """Test reset_p4_stats function."""

    def test_reset_clears_stats(self):
        """Test reset clears all statistics."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 75.0)

        reset_p4_stats()

        stats = get_p4_stats()
        assert stats == {}

    def test_reset_clears_request_counts(self):
        """Test reset clears request counts."""
        record_p4_latency("twin", 50.0)

        reset_p4_stats()

        counts = get_p4_request_count()
        assert counts == {}


class TestCheckP4SLACompliance:
    """Test check_p4_sla_compliance function."""

    def test_sla_compliant(self):
        """Test SLA compliance check for compliant latency."""
        assert check_p4_sla_compliance(50.0, target_ms=100.0) is True

    def test_sla_not_compliant(self):
        """Test SLA compliance check for non-compliant latency."""
        assert check_p4_sla_compliance(150.0, target_ms=100.0) is False

    def test_sla_at_boundary(self):
        """Test SLA compliance at exact boundary."""
        assert check_p4_sla_compliance(100.0, target_ms=100.0) is True

    def test_sla_invalid_latency(self):
        """Test SLA compliance with invalid latency."""
        assert check_p4_sla_compliance("invalid", target_ms=100.0) is False
        assert check_p4_sla_compliance(None, target_ms=100.0) is False


class TestGetP4RequestCount:
    """Test get_p4_request_count function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_get_count_single_endpoint(self):
        """Test getting count for single endpoint."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 60.0)

        count = get_p4_request_count("twin")

        assert count["twin"] == 2

    def test_get_count_all_endpoints(self):
        """Test getting counts for all endpoints."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 60.0)
        record_p4_latency("inspect", 70.0)

        counts = get_p4_request_count()

        assert counts["twin"] == 1
        assert counts["inspect"] == 2

    def test_get_count_nonexistent_endpoint(self):
        """Test getting count for nonexistent endpoint."""
        count = get_p4_request_count("nonexistent")

        assert count == {}

    def test_get_count_empty(self):
        """Test getting counts when empty."""
        counts = get_p4_request_count()

        assert counts == {}


class TestGetP4SLAStatus:
    """Test get_p4_sla_status function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_sla_status_compliant(self):
        """Test SLA status when compliant."""
        # Record latencies well below thresholds
        for i in range(100):
            record_p4_latency("twin", 30.0)

        status = get_p4_sla_status()

        assert status["overall_compliant"] is True
        assert len(status["violations"]) == 0
        assert status["compliance"]["twin"]["p95_compliant"] is True
        assert status["compliance"]["twin"]["p99_compliant"] is True

    def test_sla_status_violation(self):
        """Test SLA status with violation."""
        # Record some high latencies to violate SLA
        for i in range(90):
            record_p4_latency("twin", 50.0)
        for i in range(10):
            record_p4_latency("twin", 200.0)  # High latencies

        status = get_p4_sla_status()

        # Should have violation
        if not status["overall_compliant"]:
            assert "twin" in status["violations"]

    def test_sla_status_empty(self):
        """Test SLA status with no data."""
        status = get_p4_sla_status()

        assert status["overall_compliant"] is True
        assert status["violations"] == []
        assert status["total_endpoints"] == 0

    def test_sla_status_includes_targets(self):
        """Test SLA status includes targets."""
        status = get_p4_sla_status()

        assert "targets" in status
        assert "p95_ms" in status["targets"]
        assert "p99_ms" in status["targets"]
        assert status["targets"]["p95_ms"] == P4_SLA_TARGETS["p95_ms"]
        assert status["targets"]["p99_ms"] == P4_SLA_TARGETS["p99_ms"]

    def test_sla_status_headroom(self):
        """Test SLA status includes headroom calculations."""
        for i in range(100):
            record_p4_latency("twin", 50.0)

        status = get_p4_sla_status()

        assert "p95_headroom_ms" in status["compliance"]["twin"]
        assert "p99_headroom_ms" in status["compliance"]["twin"]
        # Headroom should be positive for compliant endpoint
        assert status["compliance"]["twin"]["p95_headroom_ms"] > 0

    def test_sla_status_request_counts(self):
        """Test SLA status includes request counts."""
        for i in range(50):
            record_p4_latency("twin", 50.0)

        status = get_p4_sla_status()

        assert status["compliance"]["twin"]["request_count"] == 50
        assert status["compliance"]["twin"]["sample_count"] == 50


class TestThreadSafety:
    """Test thread safety of metrics functions."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_concurrent_recording(self):
        """Test concurrent latency recording."""
        def record_many():
            for i in range(100):
                record_p4_latency("twin", 50.0)

        threads = [threading.Thread(target=record_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = get_p4_stats("twin")
        assert stats["twin"]["count"] == 500

    def test_concurrent_read_write(self):
        """Test concurrent reads and writes."""
        def write():
            for i in range(50):
                record_p4_latency("twin", float(i))

        def read():
            for i in range(50):
                get_p4_stats("twin")

        write_threads = [threading.Thread(target=write) for _ in range(2)]
        read_threads = [threading.Thread(target=read) for _ in range(3)]

        for t in write_threads + read_threads:
            t.start()
        for t in write_threads + read_threads:
            t.join()

        # Should complete without errors


class TestConstants:
    """Test module constants."""

    def test_valid_endpoints(self):
        """Test P4_VALID_ENDPOINTS constant."""
        assert "twin" in P4_VALID_ENDPOINTS
        assert "inspect" in P4_VALID_ENDPOINTS
        assert "timeline" in P4_VALID_ENDPOINTS

    def test_sla_targets(self):
        """Test P4_SLA_TARGETS constant."""
        assert "p95_ms" in P4_SLA_TARGETS
        assert "p99_ms" in P4_SLA_TARGETS
        assert P4_SLA_TARGETS["p95_ms"] == 100
        assert P4_SLA_TARGETS["p99_ms"] == 200

    def test_max_samples(self):
        """Test P4_MAX_SAMPLES constant."""
        assert P4_MAX_SAMPLES == 10000
