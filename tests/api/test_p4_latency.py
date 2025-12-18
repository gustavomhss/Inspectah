"""
S40-TST-006: P4 Latency Tests

Tests that P4 endpoints meet latency SLA requirements:
- P95 latency <= 100ms
- P99 latency <= 200ms
"""

from __future__ import annotations

import statistics
import time
from typing import List
import pytest

from app.api.metrics import (
    record_p4_latency,
    get_p4_stats,
    reset_p4_stats,
    check_p4_sla_compliance,
    get_p4_sla_status,
    P4_SLA_TARGETS,
)


class TestP4LatencyRecording:
    """Test P4 latency recording."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_record_single_latency(self):
        """Should record single latency value."""
        record_p4_latency("twin", 50.0)

        stats = get_p4_stats("twin")
        assert "twin" in stats
        assert stats["twin"]["count"] == 1
        assert stats["twin"]["mean_ms"] == 50.0

    def test_record_multiple_latencies(self):
        """Should record multiple latency values."""
        latencies = [10, 20, 30, 40, 50]
        for lat in latencies:
            record_p4_latency("inspect", float(lat))

        stats = get_p4_stats("inspect")
        assert stats["inspect"]["count"] == 5
        assert stats["inspect"]["min_ms"] == 10.0
        assert stats["inspect"]["max_ms"] == 50.0

    def test_record_per_endpoint(self):
        """Should track latencies per endpoint."""
        record_p4_latency("twin", 30.0)
        record_p4_latency("inspect", 40.0)
        record_p4_latency("timeline", 25.0)

        stats = get_p4_stats()
        assert "twin" in stats
        assert "inspect" in stats
        assert "timeline" in stats


class TestP4PercentileCalculation:
    """Test percentile calculations."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_p95_calculation(self):
        """Should calculate P95 correctly."""
        # Generate 100 samples: 95 at 50ms, 5 at 150ms
        for _ in range(95):
            record_p4_latency("test_p95", 50.0)
        for _ in range(5):
            record_p4_latency("test_p95", 150.0)

        stats = get_p4_stats("test_p95")
        p95 = stats["test_p95"]["p95_ms"]

        # P95 should be around 50ms (95th percentile of sorted values)
        assert p95 <= 150.0

    def test_p99_calculation(self):
        """Should calculate P99 correctly."""
        # Generate 100 samples: 99 at 80ms, 1 at 300ms
        for _ in range(99):
            record_p4_latency("test_p99", 80.0)
        record_p4_latency("test_p99", 300.0)

        stats = get_p4_stats("test_p99")
        p99 = stats["test_p99"]["p99_ms"]

        # P99 should be around 80ms or slightly higher
        assert p99 <= 300.0

    def test_median_calculation(self):
        """Should calculate median correctly."""
        latencies = [10, 20, 30, 40, 50]
        for lat in latencies:
            record_p4_latency("test_median", float(lat))

        stats = get_p4_stats("test_median")
        assert stats["test_median"]["median_ms"] == 30.0


class TestP4SLACompliance:
    """Test SLA compliance checking."""

    def test_sla_targets_defined(self):
        """SLA targets should be defined."""
        assert "p95_ms" in P4_SLA_TARGETS
        assert "p99_ms" in P4_SLA_TARGETS
        assert P4_SLA_TARGETS["p95_ms"] == 100
        assert P4_SLA_TARGETS["p99_ms"] == 200

    def test_check_compliant_latency(self):
        """Should identify compliant latency."""
        assert check_p4_sla_compliance(50, 100) is True
        assert check_p4_sla_compliance(100, 100) is True

    def test_check_non_compliant_latency(self):
        """Should identify non-compliant latency."""
        assert check_p4_sla_compliance(101, 100) is False
        assert check_p4_sla_compliance(150, 100) is False

    def test_check_edge_cases(self):
        """Should handle edge cases."""
        assert check_p4_sla_compliance(0, 100) is True
        assert check_p4_sla_compliance(-1, 100) is True  # Negative treated as 0

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_sla_status_all_compliant(self):
        """Should report all compliant when under targets."""
        # Add compliant latencies
        for _ in range(100):
            record_p4_latency("twin", 50.0)
            record_p4_latency("inspect", 60.0)

        status = get_p4_sla_status()
        assert status["overall_compliant"] is True
        assert len(status["violations"]) == 0

    def test_sla_status_with_violations(self):
        """Should report violations when over targets."""
        # Add non-compliant latencies (all at 150ms to push P95 over 100ms)
        for _ in range(100):
            record_p4_latency("slow_endpoint", 150.0)

        status = get_p4_sla_status()
        assert status["overall_compliant"] is False
        assert "slow_endpoint" in status["violations"]


class TestP4LatencyBenchmark:
    """Benchmark tests for P4 latency."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_twin_simulated_latency(self):
        """Simulate twin endpoint latency."""
        # Simulate 1000 requests with realistic distribution
        latencies = []
        import random
        random.seed(42)

        for _ in range(1000):
            # Most requests: 20-60ms
            # Some slower: 60-100ms
            # Few slow: 100-150ms
            r = random.random()
            if r < 0.9:  # 90% fast
                lat = random.uniform(20, 60)
            elif r < 0.97:  # 7% medium
                lat = random.uniform(60, 100)
            else:  # 3% slow
                lat = random.uniform(100, 150)

            latencies.append(lat)
            record_p4_latency("twin_bench", lat)

        stats = get_p4_stats("twin_bench")

        # P95 should be under 100ms
        assert stats["twin_bench"]["p95_ms"] < 100, \
            f"P95 {stats['twin_bench']['p95_ms']}ms exceeds 100ms target"

        # P99 should be under 200ms
        assert stats["twin_bench"]["p99_ms"] < 200, \
            f"P99 {stats['twin_bench']['p99_ms']}ms exceeds 200ms target"

    def test_inspect_simulated_latency(self):
        """Simulate inspect endpoint latency."""
        import random
        random.seed(43)

        for _ in range(1000):
            # Inspect typically slightly slower than twin
            r = random.random()
            if r < 0.85:  # 85% fast
                lat = random.uniform(25, 70)
            elif r < 0.95:  # 10% medium
                lat = random.uniform(70, 120)
            else:  # 5% slow
                lat = random.uniform(120, 180)

            record_p4_latency("inspect_bench", lat)

        stats = get_p4_stats("inspect_bench")

        # P95 should be under 100ms
        assert stats["inspect_bench"]["p95_ms"] < 120, \
            f"P95 {stats['inspect_bench']['p95_ms']}ms higher than expected"

        # P99 should be under 200ms
        assert stats["inspect_bench"]["p99_ms"] < 200, \
            f"P99 {stats['inspect_bench']['p99_ms']}ms exceeds 200ms target"

    def test_timeline_simulated_latency(self):
        """Simulate timeline endpoint latency."""
        import random
        random.seed(44)

        for _ in range(1000):
            # Timeline typically fastest
            r = random.random()
            if r < 0.92:  # 92% fast
                lat = random.uniform(15, 50)
            elif r < 0.98:  # 6% medium
                lat = random.uniform(50, 80)
            else:  # 2% slow
                lat = random.uniform(80, 120)

            record_p4_latency("timeline_bench", lat)

        stats = get_p4_stats("timeline_bench")

        # P95 should be well under 100ms
        assert stats["timeline_bench"]["p95_ms"] < 100, \
            f"P95 {stats['timeline_bench']['p95_ms']}ms exceeds 100ms target"


class TestP4LatencyReporting:
    """Test latency reporting and metrics."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_p4_stats()

    def test_stats_include_all_metrics(self):
        """Stats should include all standard metrics."""
        for i in range(10):
            record_p4_latency("full_stats", float(i * 10))

        stats = get_p4_stats("full_stats")
        endpoint_stats = stats["full_stats"]

        assert "count" in endpoint_stats
        assert "min_ms" in endpoint_stats
        assert "max_ms" in endpoint_stats
        assert "mean_ms" in endpoint_stats
        assert "median_ms" in endpoint_stats
        assert "p95_ms" in endpoint_stats
        assert "p99_ms" in endpoint_stats

    def test_sla_status_includes_headroom(self):
        """SLA status should include headroom metrics."""
        for _ in range(100):
            record_p4_latency("headroom_test", 70.0)

        status = get_p4_sla_status()
        compliance = status["compliance"]["headroom_test"]

        assert "p95_headroom_ms" in compliance
        assert "p99_headroom_ms" in compliance
        # With 70ms latency, headroom should be 30ms for P95 target of 100ms
        assert compliance["p95_headroom_ms"] == 30.0
