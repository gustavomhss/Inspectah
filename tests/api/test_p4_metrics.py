"""
Tests for S40-BE-027: P4 API Latency Metrics.

Tests for app/api/metrics.py.
"""

from __future__ import annotations

import pytest

from app.api.metrics import (
    record_p4_request,
    record_p4_latency,
    get_p4_stats,
    reset_p4_stats,
    check_p4_sla_compliance,
    get_p4_sla_status,
    P4_SLA_TARGETS,
    p4_endpoint_latency_ms,
    p4_requests_total,
    p4_provenance_valid,
    p4_provenance_invalid,
    p4_current_latency_ms,
)


class TestP4Metrics:
    """Tests for P4 metrics recording."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_record_p4_request_success(self):
        """Test recording a successful P4 request."""
        # Should not raise any exception
        record_p4_request(
            endpoint="twin",
            latency_ms=50.5,
            status="success",
            provenance_valid=True,
        )

    def test_record_p4_request_error(self):
        """Test recording a failed P4 request."""
        record_p4_request(
            endpoint="inspect",
            latency_ms=150.0,
            status="error",
            provenance_valid=False,
        )

    def test_record_p4_request_default_values(self):
        """Test recording P4 request with default values."""
        record_p4_request(
            endpoint="timeline",
            latency_ms=75.0,
        )
        # Default status is "success" and provenance_valid is True

    def test_record_p4_latency_single(self):
        """Test recording a single latency value."""
        record_p4_latency("twin", 50.0)
        stats = get_p4_stats("twin")

        assert "twin" in stats
        assert stats["twin"]["count"] == 1
        assert stats["twin"]["min_ms"] == 50.0
        assert stats["twin"]["max_ms"] == 50.0
        assert stats["twin"]["mean_ms"] == 50.0

    def test_record_p4_latency_multiple(self):
        """Test recording multiple latency values."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 100.0)
        record_p4_latency("twin", 75.0)

        stats = get_p4_stats("twin")

        assert stats["twin"]["count"] == 3
        assert stats["twin"]["min_ms"] == 50.0
        assert stats["twin"]["max_ms"] == 100.0
        assert stats["twin"]["mean_ms"] == 75.0

    def test_record_p4_latency_multiple_endpoints(self):
        """Test recording latency for multiple endpoints."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 30.0)
        record_p4_latency("timeline", 80.0)

        stats = get_p4_stats()

        assert "twin" in stats
        assert "inspect" in stats
        assert "timeline" in stats
        assert stats["twin"]["mean_ms"] == 50.0
        assert stats["inspect"]["mean_ms"] == 30.0
        assert stats["timeline"]["mean_ms"] == 80.0

    def test_get_p4_stats_empty(self):
        """Test getting stats when no data recorded."""
        stats = get_p4_stats()
        assert stats == {}

    def test_get_p4_stats_specific_endpoint(self):
        """Test getting stats for a specific endpoint."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 30.0)

        stats = get_p4_stats("twin")

        assert "twin" in stats
        assert "inspect" not in stats

    def test_get_p4_stats_nonexistent_endpoint(self):
        """Test getting stats for nonexistent endpoint."""
        record_p4_latency("twin", 50.0)

        stats = get_p4_stats("nonexistent")
        assert stats == {}

    def test_reset_p4_stats(self):
        """Test resetting P4 stats."""
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 30.0)

        reset_p4_stats()

        stats = get_p4_stats()
        assert stats == {}


class TestP4StatsCalculations:
    """Tests for P4 statistics calculations."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_stats_min_max(self):
        """Test min/max calculation."""
        latencies = [10, 20, 30, 40, 50, 100, 150, 200]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        assert stats["twin"]["min_ms"] == 10.0
        assert stats["twin"]["max_ms"] == 200.0

    def test_stats_mean(self):
        """Test mean calculation."""
        latencies = [10, 20, 30, 40]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        assert stats["twin"]["mean_ms"] == 25.0  # (10+20+30+40)/4

    def test_stats_median_odd(self):
        """Test median calculation with odd number of values."""
        latencies = [10, 20, 30]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        assert stats["twin"]["median_ms"] == 20.0

    def test_stats_median_even(self):
        """Test median calculation with even number of values."""
        latencies = [10, 20, 30, 40]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        assert stats["twin"]["median_ms"] == 25.0  # (20+30)/2

    def test_stats_p95(self):
        """Test P95 calculation."""
        # Generate 100 values from 1 to 100
        for i in range(1, 101):
            record_p4_latency("twin", float(i))

        stats = get_p4_stats("twin")

        # P95 index is int(100 * 0.95) = 95, which is the 96th value (0-indexed)
        assert stats["twin"]["p95_ms"] == 96

    def test_stats_p99(self):
        """Test P99 calculation."""
        # Generate 100 values from 1 to 100
        for i in range(1, 101):
            record_p4_latency("twin", float(i))

        stats = get_p4_stats("twin")

        # P99 index is int(100 * 0.99) = 99, which is the 100th value (0-indexed)
        assert stats["twin"]["p99_ms"] == 100

    def test_stats_p95_small_sample(self):
        """Test P95 with small sample size."""
        latencies = [10, 20, 30]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        # With 3 values, P95 index is int(3*0.95) = 2
        assert stats["twin"]["p95_ms"] == 30.0

    def test_stats_p99_small_sample(self):
        """Test P99 with small sample size."""
        latencies = [10, 20, 30]
        for lat in latencies:
            record_p4_latency("twin", float(lat))

        stats = get_p4_stats("twin")

        # With 3 values, P99 index is int(3*0.99) = 2
        assert stats["twin"]["p99_ms"] == 30.0


class TestP4SLACompliance:
    """Tests for P4 SLA compliance checking."""

    def test_sla_targets_exist(self):
        """Test that SLA targets are defined."""
        assert "p95_ms" in P4_SLA_TARGETS
        assert "p99_ms" in P4_SLA_TARGETS
        assert P4_SLA_TARGETS["p95_ms"] == 100
        assert P4_SLA_TARGETS["p99_ms"] == 200

    def test_check_sla_compliance_pass(self):
        """Test SLA compliance check passes."""
        assert check_p4_sla_compliance(50.0, target_ms=100) is True
        assert check_p4_sla_compliance(100.0, target_ms=100) is True

    def test_check_sla_compliance_fail(self):
        """Test SLA compliance check fails."""
        assert check_p4_sla_compliance(101.0, target_ms=100) is False
        assert check_p4_sla_compliance(200.0, target_ms=100) is False

    def test_check_sla_compliance_default_target(self):
        """Test SLA compliance with default target."""
        assert check_p4_sla_compliance(50.0) is True  # Default target is 100ms
        assert check_p4_sla_compliance(150.0) is False

    def test_check_sla_compliance_edge_case(self):
        """Test SLA compliance at exact boundary."""
        assert check_p4_sla_compliance(100.0, target_ms=100) is True
        assert check_p4_sla_compliance(100.001, target_ms=100) is False


class TestP4SLAStatus:
    """Tests for get_p4_sla_status function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_sla_status_no_data(self):
        """Test SLA status with no data."""
        status = get_p4_sla_status()

        assert "targets" in status
        assert "compliance" in status
        assert "overall_compliant" in status
        assert status["overall_compliant"] is True  # No data = compliant

    def test_sla_status_compliant(self):
        """Test SLA status when compliant."""
        # Generate latencies that meet SLA (P95 < 100ms, P99 < 200ms)
        for i in range(100):
            record_p4_latency("twin", 50.0)  # All fast

        status = get_p4_sla_status()

        assert status["compliance"]["twin"]["p95_compliant"] is True
        assert status["compliance"]["twin"]["p99_compliant"] is True
        assert status["overall_compliant"] is True

    def test_sla_status_p95_violation(self):
        """Test SLA status when P95 is violated."""
        # Generate latencies where P95 > 100ms
        for i in range(95):
            record_p4_latency("twin", 50.0)
        for i in range(5):
            record_p4_latency("twin", 150.0)  # These make P95 fail

        status = get_p4_sla_status()

        # P95 should be around 150, which fails the 100ms target
        assert status["compliance"]["twin"]["p95_ms"] >= 100

    def test_sla_status_p99_violation(self):
        """Test SLA status when P99 is violated."""
        # Generate latencies where P99 > 200ms
        for i in range(99):
            record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 300.0)  # This pushes P99 above 200

        status = get_p4_sla_status()

        # With 100 values, P99 is at index 99
        assert status["compliance"]["twin"]["p99_ms"] == 300.0
        assert status["compliance"]["twin"]["p99_compliant"] is False

    def test_sla_status_multiple_endpoints(self):
        """Test SLA status with multiple endpoints."""
        for i in range(100):
            record_p4_latency("twin", 50.0)
            record_p4_latency("inspect", 30.0)

        status = get_p4_sla_status()

        assert "twin" in status["compliance"]
        assert "inspect" in status["compliance"]
        assert status["compliance"]["twin"]["p95_compliant"] is True
        assert status["compliance"]["inspect"]["p95_compliant"] is True
        assert status["overall_compliant"] is True

    def test_sla_status_one_endpoint_failing(self):
        """Test SLA status when one endpoint fails."""
        for i in range(100):
            record_p4_latency("twin", 50.0)  # Compliant
            record_p4_latency("inspect", 250.0)  # Non-compliant

        status = get_p4_sla_status()

        assert status["compliance"]["twin"]["p95_compliant"] is True
        assert status["compliance"]["inspect"]["p95_compliant"] is False
        assert status["overall_compliant"] is False


class TestPrometheusMetrics:
    """Tests for Prometheus metric objects."""

    def test_p4_endpoint_latency_histogram_exists(self):
        """Test that latency histogram is defined."""
        assert p4_endpoint_latency_ms is not None

    def test_p4_requests_total_counter_exists(self):
        """Test that requests counter is defined."""
        assert p4_requests_total is not None

    def test_p4_provenance_valid_counter_exists(self):
        """Test that provenance valid counter is defined."""
        assert p4_provenance_valid is not None

    def test_p4_provenance_invalid_counter_exists(self):
        """Test that provenance invalid counter is defined."""
        assert p4_provenance_invalid is not None

    def test_p4_current_latency_gauge_exists(self):
        """Test that current latency gauge is defined."""
        assert p4_current_latency_ms is not None

    def test_metrics_have_labels_method(self):
        """Test that metrics have labels method."""
        # These should be callable without error
        p4_endpoint_latency_ms.labels(endpoint="test", status="success")
        p4_requests_total.labels(endpoint="test", status="success")
        p4_provenance_valid.labels(endpoint="test")
        p4_provenance_invalid.labels(endpoint="test")
        p4_current_latency_ms.labels(endpoint="test")


class TestEdgeCases:
    """Tests for edge cases."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_record_zero_latency(self):
        """Test recording zero latency."""
        record_p4_latency("twin", 0.0)
        stats = get_p4_stats("twin")

        assert stats["twin"]["min_ms"] == 0.0
        assert stats["twin"]["mean_ms"] == 0.0

    def test_record_very_high_latency(self):
        """Test recording very high latency."""
        record_p4_latency("twin", 10000.0)  # 10 seconds
        stats = get_p4_stats("twin")

        assert stats["twin"]["max_ms"] == 10000.0

    def test_record_fractional_latency(self):
        """Test recording fractional latency."""
        record_p4_latency("twin", 0.001)  # 1 microsecond in ms
        stats = get_p4_stats("twin")

        assert stats["twin"]["min_ms"] == 0.001

    def test_single_value_stats(self):
        """Test stats with single value."""
        record_p4_latency("twin", 50.0)
        stats = get_p4_stats("twin")

        assert stats["twin"]["count"] == 1
        assert stats["twin"]["min_ms"] == 50.0
        assert stats["twin"]["max_ms"] == 50.0
        assert stats["twin"]["mean_ms"] == 50.0
        assert stats["twin"]["median_ms"] == 50.0
        assert stats["twin"]["p95_ms"] == 50.0
        assert stats["twin"]["p99_ms"] == 50.0

    def test_all_same_values(self):
        """Test stats when all values are the same."""
        for _ in range(100):
            record_p4_latency("twin", 75.0)

        stats = get_p4_stats("twin")

        assert stats["twin"]["min_ms"] == 75.0
        assert stats["twin"]["max_ms"] == 75.0
        assert stats["twin"]["mean_ms"] == 75.0
        assert stats["twin"]["median_ms"] == 75.0
        assert stats["twin"]["p95_ms"] == 75.0
        assert stats["twin"]["p99_ms"] == 75.0

    def test_negative_latency(self):
        """Test recording negative latency (edge case)."""
        # Negative latency shouldn't happen but should be handled
        record_p4_latency("twin", -10.0)
        stats = get_p4_stats("twin")

        assert stats["twin"]["min_ms"] == -10.0

    def test_endpoint_name_with_special_chars(self):
        """Test endpoint names with special characters."""
        record_p4_latency("twin/v2", 50.0)
        stats = get_p4_stats("twin/v2")

        assert "twin/v2" in stats

    def test_large_number_of_samples(self):
        """Test with large number of samples."""
        for i in range(10000):
            record_p4_latency("twin", float(i % 100))

        stats = get_p4_stats("twin")

        assert stats["twin"]["count"] == 10000
        assert stats["twin"]["min_ms"] == 0.0
        assert stats["twin"]["max_ms"] == 99.0


class TestSanitization:
    """Tests for input sanitization functions."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_sanitize_empty_endpoint(self):
        """Test sanitization of empty endpoint."""
        from app.api.metrics import _sanitize_endpoint
        assert _sanitize_endpoint("") == "unknown"
        assert _sanitize_endpoint(None) == "unknown"

    def test_sanitize_endpoint_special_chars(self):
        """Test sanitization removes special characters."""
        from app.api.metrics import _sanitize_endpoint
        result = _sanitize_endpoint("test<script>alert</script>")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_endpoint_preserves_valid(self):
        """Test sanitization preserves valid characters."""
        from app.api.metrics import _sanitize_endpoint
        assert _sanitize_endpoint("twin") == "twin"
        assert _sanitize_endpoint("twin/v2") == "twin/v2"
        assert _sanitize_endpoint("twin_v2") == "twin_v2"

    def test_sanitize_endpoint_length_limit(self):
        """Test sanitization limits length."""
        from app.api.metrics import _sanitize_endpoint
        long_endpoint = "a" * 100
        result = _sanitize_endpoint(long_endpoint)
        assert len(result) <= 64

    def test_sanitize_latency_none(self):
        """Test sanitization of None latency."""
        from app.api.metrics import _sanitize_latency
        assert _sanitize_latency(None) == 0.0

    def test_sanitize_latency_negative(self):
        """Test sanitization caps negative latency."""
        from app.api.metrics import _sanitize_latency
        assert _sanitize_latency(-100) == 0.0

    def test_sanitize_latency_very_high(self):
        """Test sanitization caps very high latency."""
        from app.api.metrics import _sanitize_latency
        # Should cap at 1 hour (3600000ms)
        assert _sanitize_latency(10000000) == 3600000.0

    def test_sanitize_latency_invalid_type(self):
        """Test sanitization handles invalid types."""
        from app.api.metrics import _sanitize_latency
        assert _sanitize_latency("not a number") == 0.0
        assert _sanitize_latency([1, 2, 3]) == 0.0


class TestPercentileCalculation:
    """Tests for percentile calculation function."""

    def test_percentile_empty_list(self):
        """Test percentile of empty list."""
        from app.api.metrics import _calculate_percentile
        assert _calculate_percentile([], 0.95) == 0.0

    def test_percentile_single_value(self):
        """Test percentile with single value."""
        from app.api.metrics import _calculate_percentile
        assert _calculate_percentile([50.0], 0.95) == 50.0
        assert _calculate_percentile([50.0], 0.99) == 50.0

    def test_percentile_two_values(self):
        """Test percentile with two values."""
        from app.api.metrics import _calculate_percentile
        result = _calculate_percentile([10.0, 100.0], 0.95)
        assert result in [10.0, 100.0]

    def test_percentile_boundary(self):
        """Test percentile at boundaries."""
        from app.api.metrics import _calculate_percentile
        values = [float(i) for i in range(1, 101)]
        assert _calculate_percentile(values, 0.0) == 1.0
        assert _calculate_percentile(values, 1.0) == 100.0

    def test_percentile_sorted_requirement(self):
        """Test that percentile works with sorted input."""
        from app.api.metrics import _calculate_percentile
        sorted_values = [10.0, 20.0, 30.0, 40.0, 50.0]
        # The function expects sorted input
        result = _calculate_percentile(sorted_values, 0.5)
        assert result in sorted_values


class TestRequestCount:
    """Tests for get_p4_request_count function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_request_count_empty(self):
        """Test request count when empty."""
        from app.api.metrics import get_p4_request_count
        assert get_p4_request_count() == {}

    def test_request_count_single_endpoint(self):
        """Test request count for single endpoint."""
        from app.api.metrics import get_p4_request_count
        record_p4_latency("twin", 50.0)
        record_p4_latency("twin", 60.0)

        counts = get_p4_request_count()
        assert counts["twin"] == 2

    def test_request_count_multiple_endpoints(self):
        """Test request count for multiple endpoints."""
        from app.api.metrics import get_p4_request_count
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 30.0)
        record_p4_latency("inspect", 40.0)

        counts = get_p4_request_count()
        assert counts["twin"] == 1
        assert counts["inspect"] == 2

    def test_request_count_filter_endpoint(self):
        """Test request count with endpoint filter."""
        from app.api.metrics import get_p4_request_count
        record_p4_latency("twin", 50.0)
        record_p4_latency("inspect", 30.0)

        counts = get_p4_request_count("twin")
        assert "twin" in counts
        assert "inspect" not in counts

    def test_request_count_nonexistent_endpoint(self):
        """Test request count for nonexistent endpoint."""
        from app.api.metrics import get_p4_request_count
        record_p4_latency("twin", 50.0)

        counts = get_p4_request_count("nonexistent")
        assert counts == {}


class TestMemoryManagement:
    """Tests for memory management in metrics."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_memory_limit_enforced(self):
        """Test that memory limit is enforced."""
        from app.api.metrics import P4_MAX_SAMPLES

        # Record more than max samples
        for i in range(P4_MAX_SAMPLES + 1000):
            record_p4_latency("twin", float(i))

        stats = get_p4_stats("twin")
        # Should have exactly P4_MAX_SAMPLES
        assert stats["twin"]["count"] == P4_MAX_SAMPLES

    def test_memory_keeps_recent_samples(self):
        """Test that memory management keeps recent samples."""
        from app.api.metrics import P4_MAX_SAMPLES

        # Record more than max samples, with identifiable recent values
        total = P4_MAX_SAMPLES + 100
        for i in range(total):
            record_p4_latency("twin", float(i))

        stats = get_p4_stats("twin")
        # Min should be from the trimmed beginning
        assert stats["twin"]["min_ms"] >= 100  # Oldest samples trimmed
        assert stats["twin"]["max_ms"] == float(total - 1)  # Recent kept


class TestValidEndpoints:
    """Tests for valid endpoint constants."""

    def test_valid_endpoints_defined(self):
        """Test that valid endpoints are defined."""
        from app.api.metrics import P4_VALID_ENDPOINTS

        assert "twin" in P4_VALID_ENDPOINTS
        assert "inspect" in P4_VALID_ENDPOINTS
        assert "timeline" in P4_VALID_ENDPOINTS

    def test_valid_endpoints_is_frozenset(self):
        """Test that valid endpoints is immutable."""
        from app.api.metrics import P4_VALID_ENDPOINTS

        assert isinstance(P4_VALID_ENDPOINTS, frozenset)


class TestSLAStatusEnhanced:
    """Tests for enhanced SLA status function."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_sla_status_includes_headroom(self):
        """Test SLA status includes headroom metrics."""
        for i in range(100):
            record_p4_latency("twin", 50.0)

        status = get_p4_sla_status()

        assert "p95_headroom_ms" in status["compliance"]["twin"]
        assert "p99_headroom_ms" in status["compliance"]["twin"]
        # With p95=50 and target=100, headroom should be 50
        assert status["compliance"]["twin"]["p95_headroom_ms"] == 50

    def test_sla_status_includes_violations_list(self):
        """Test SLA status includes violations list."""
        for i in range(100):
            record_p4_latency("twin", 50.0)  # Compliant
            record_p4_latency("inspect", 250.0)  # Non-compliant

        status = get_p4_sla_status()

        assert "violations" in status
        assert "inspect" in status["violations"]
        assert "twin" not in status["violations"]

    def test_sla_status_includes_request_count(self):
        """Test SLA status includes request counts."""
        for i in range(100):
            record_p4_latency("twin", 50.0)

        status = get_p4_sla_status()

        assert status["compliance"]["twin"]["request_count"] == 100
        assert status["compliance"]["twin"]["sample_count"] == 100

    def test_sla_status_includes_total_endpoints(self):
        """Test SLA status includes total endpoints."""
        for i in range(10):
            record_p4_latency("twin", 50.0)
            record_p4_latency("inspect", 30.0)

        status = get_p4_sla_status()

        assert status["total_endpoints"] == 2

    def test_sla_targets_defensive_copy(self):
        """Test SLA targets returns defensive copy."""
        status = get_p4_sla_status()

        # Modifying returned targets shouldn't affect original
        status["targets"]["p95_ms"] = 9999

        from app.api.metrics import P4_SLA_TARGETS
        assert P4_SLA_TARGETS["p95_ms"] == 100


class TestThreadSafety:
    """Tests for thread safety."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_concurrent_writes(self):
        """Test concurrent writes don't corrupt data."""
        import threading

        def write_latencies(endpoint: str, count: int):
            for i in range(count):
                record_p4_latency(endpoint, float(i))

        threads = [
            threading.Thread(target=write_latencies, args=("twin", 1000)),
            threading.Thread(target=write_latencies, args=("twin", 1000)),
            threading.Thread(target=write_latencies, args=("inspect", 1000)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = get_p4_stats()

        # Should have all samples (or capped at max)
        assert stats["twin"]["count"] == 2000
        assert stats["inspect"]["count"] == 1000

    def test_concurrent_read_write(self):
        """Test concurrent reads and writes."""
        import threading

        errors = []

        def write_latencies():
            for i in range(100):
                record_p4_latency("twin", float(i))

        def read_stats():
            for _ in range(100):
                try:
                    stats = get_p4_stats()
                    # Should not raise, even during concurrent writes
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=write_latencies),
            threading.Thread(target=read_stats),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_concurrent_reset(self):
        """Test concurrent reset doesn't cause errors."""
        import threading

        errors = []

        def write_and_reset():
            for i in range(50):
                record_p4_latency("twin", float(i))
                if i % 10 == 0:
                    reset_p4_stats()

        def read_stats():
            for _ in range(50):
                try:
                    get_p4_stats()
                    get_p4_sla_status()
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=write_and_reset),
            threading.Thread(target=read_stats),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestSLAComplianceEdgeCases:
    """Tests for SLA compliance edge cases."""

    def test_compliance_with_invalid_latency(self):
        """Test compliance check with invalid latency."""
        # Should return False for invalid values
        assert check_p4_sla_compliance("not_a_number") is False
        assert check_p4_sla_compliance(None) is False

    def test_compliance_with_invalid_target(self):
        """Test compliance check with invalid target."""
        assert check_p4_sla_compliance(50.0, "not_a_number") is False
        assert check_p4_sla_compliance(50.0, None) is False
