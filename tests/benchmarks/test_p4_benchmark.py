"""
Tests for S40-BE-028: P4 Latency Benchmark Script.

Tests for scripts/benchmarks/p4_latency_benchmark.py.
"""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import patch, MagicMock

# Import from benchmark script
import sys
sys.path.insert(0, "scripts/benchmarks")

from scripts.benchmarks.p4_latency_benchmark import (
    BenchmarkResult,
    EndpointSummary,
    BenchmarkSummary,
    SLA_TARGETS,
    simulate_twin_request,
    simulate_inspect_request,
    simulate_timeline_request,
    calculate_endpoint_summary,
    run_benchmark,
    format_text_report,
    format_json_report,
    ENDPOINT_SIMULATORS,
)


class TestBenchmarkDataclasses:
    """Tests for benchmark dataclasses."""

    def test_benchmark_result_create(self):
        """Test creating BenchmarkResult."""
        result = BenchmarkResult(
            iteration=1,
            endpoint="twin",
            claim_id="claim-001",
            decision_id=None,
            request_at=1000.0,
            response_at=1000.05,
            latency_ms=50.0,
            success=True,
            provenance_valid=True,
        )
        assert result.iteration == 1
        assert result.endpoint == "twin"
        assert result.latency_ms == 50.0
        assert result.success is True
        assert result.error is None

    def test_benchmark_result_with_error(self):
        """Test creating BenchmarkResult with error."""
        result = BenchmarkResult(
            iteration=2,
            endpoint="inspect",
            claim_id="",
            decision_id="dec-001",
            request_at=1000.0,
            response_at=1000.0,
            latency_ms=0.0,
            success=False,
            provenance_valid=False,
            error="Connection timeout",
        )
        assert result.success is False
        assert result.error == "Connection timeout"

    def test_endpoint_summary_create(self):
        """Test creating EndpointSummary."""
        summary = EndpointSummary(
            endpoint="twin",
            total_requests=100,
            successful=98,
            failed=2,
            min_latency_ms=10.0,
            max_latency_ms=100.0,
            mean_latency_ms=45.0,
            median_latency_ms=42.0,
            p95_latency_ms=85.0,
            p99_latency_ms=95.0,
            stddev_latency_ms=15.0,
            provenance_valid_pct=99.0,
            sla_p95_compliant=True,
            sla_p99_compliant=True,
        )
        assert summary.endpoint == "twin"
        assert summary.successful == 98
        assert summary.sla_p95_compliant is True

    def test_benchmark_summary_create(self):
        """Test creating BenchmarkSummary."""
        ep_summary = EndpointSummary(
            endpoint="twin",
            total_requests=100,
            successful=100,
            failed=0,
            min_latency_ms=10.0,
            max_latency_ms=100.0,
            mean_latency_ms=45.0,
            median_latency_ms=42.0,
            p95_latency_ms=85.0,
            p99_latency_ms=95.0,
            stddev_latency_ms=15.0,
            provenance_valid_pct=100.0,
            sla_p95_compliant=True,
            sla_p99_compliant=True,
        )
        summary = BenchmarkSummary(
            endpoints={"twin": ep_summary},
            total_iterations=100,
            successful=100,
            failed=0,
            throughput_per_sec=50.0,
            duration_seconds=2.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:02Z",
            sla_targets=SLA_TARGETS,
            overall_sla_compliant=True,
        )
        assert summary.total_iterations == 100
        assert summary.overall_sla_compliant is True


class TestSLATargets:
    """Tests for SLA targets."""

    def test_sla_targets_defined(self):
        """Test that SLA targets are defined."""
        assert "p95_ms" in SLA_TARGETS
        assert "p99_ms" in SLA_TARGETS

    def test_sla_targets_values(self):
        """Test SLA target values."""
        assert SLA_TARGETS["p95_ms"] == 100
        assert SLA_TARGETS["p99_ms"] == 200


class TestSimulators:
    """Tests for endpoint simulators."""

    @pytest.mark.asyncio
    async def test_simulate_twin_request(self):
        """Test twin request simulation."""
        result = await simulate_twin_request("claim-001", base_latency_ms=10)

        assert result.endpoint == "twin"
        assert result.claim_id == "claim-001"
        assert result.success is True
        assert result.latency_ms >= 10  # At least base latency
        assert result.latency_ms < 200  # Should be reasonable

    @pytest.mark.asyncio
    async def test_simulate_inspect_request(self):
        """Test inspect request simulation."""
        result = await simulate_inspect_request("dec-001", base_latency_ms=10)

        assert result.endpoint == "inspect"
        assert result.decision_id == "dec-001"
        assert result.success is True
        assert result.latency_ms >= 10

    @pytest.mark.asyncio
    async def test_simulate_timeline_request(self):
        """Test timeline request simulation."""
        result = await simulate_timeline_request("claim-001", base_latency_ms=10)

        assert result.endpoint == "timeline"
        assert result.claim_id == "claim-001"
        assert result.success is True
        assert result.latency_ms >= 10

    def test_endpoint_simulators_defined(self):
        """Test that endpoint simulators are defined."""
        assert "twin" in ENDPOINT_SIMULATORS
        assert "inspect" in ENDPOINT_SIMULATORS
        assert "timeline" in ENDPOINT_SIMULATORS


class TestCalculateEndpointSummary:
    """Tests for calculate_endpoint_summary function."""

    def test_calculate_summary_with_results(self):
        """Test calculating summary from results."""
        results = [
            BenchmarkResult(
                iteration=i,
                endpoint="twin",
                claim_id=f"claim-{i}",
                decision_id=None,
                request_at=1000.0,
                response_at=1000.05,
                latency_ms=float(50 + i),  # 50, 51, 52, ...
                success=True,
                provenance_valid=True,
            )
            for i in range(10)
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.endpoint == "twin"
        assert summary.total_requests == 10
        assert summary.successful == 10
        assert summary.failed == 0
        assert summary.min_latency_ms == 50.0
        assert summary.max_latency_ms == 59.0
        assert summary.provenance_valid_pct == 100.0

    def test_calculate_summary_with_failures(self):
        """Test calculating summary with some failures."""
        results = [
            BenchmarkResult(
                iteration=i,
                endpoint="twin",
                claim_id=f"claim-{i}",
                decision_id=None,
                request_at=1000.0,
                response_at=1000.05,
                latency_ms=50.0,
                success=i < 8,  # 8 successes, 2 failures
                provenance_valid=True,
            )
            for i in range(10)
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.successful == 8
        assert summary.failed == 2

    def test_calculate_summary_no_results(self):
        """Test calculating summary with no results."""
        summary = calculate_endpoint_summary("twin", [])

        assert summary.total_requests == 0
        assert summary.successful == 0
        assert summary.sla_p95_compliant is False

    def test_calculate_summary_all_failures(self):
        """Test calculating summary when all requests fail."""
        results = [
            BenchmarkResult(
                iteration=i,
                endpoint="twin",
                claim_id=f"claim-{i}",
                decision_id=None,
                request_at=1000.0,
                response_at=1000.0,
                latency_ms=0.0,
                success=False,
                provenance_valid=False,
                error="Failed",
            )
            for i in range(5)
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.successful == 0
        assert summary.failed == 5
        assert summary.sla_p95_compliant is False
        assert summary.sla_p99_compliant is False

    def test_calculate_summary_sla_compliance(self):
        """Test SLA compliance calculation."""
        # All fast requests
        results = [
            BenchmarkResult(
                iteration=i,
                endpoint="twin",
                claim_id=f"claim-{i}",
                decision_id=None,
                request_at=1000.0,
                response_at=1000.05,
                latency_ms=50.0,  # Well under SLA
                success=True,
                provenance_valid=True,
            )
            for i in range(100)
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.p95_latency_ms <= SLA_TARGETS["p95_ms"]
        assert summary.p99_latency_ms <= SLA_TARGETS["p99_ms"]
        assert summary.sla_p95_compliant is True
        assert summary.sla_p99_compliant is True

    def test_calculate_summary_sla_violation(self):
        """Test SLA violation detection."""
        # Slow requests
        results = [
            BenchmarkResult(
                iteration=i,
                endpoint="twin",
                claim_id=f"claim-{i}",
                decision_id=None,
                request_at=1000.0,
                response_at=1000.3,
                latency_ms=300.0,  # Over SLA
                success=True,
                provenance_valid=True,
            )
            for i in range(100)
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.p95_latency_ms > SLA_TARGETS["p95_ms"]
        assert summary.sla_p95_compliant is False

    def test_calculate_summary_provenance_tracking(self):
        """Test provenance validity tracking."""
        results = []
        for i in range(100):
            results.append(
                BenchmarkResult(
                    iteration=i,
                    endpoint="twin",
                    claim_id=f"claim-{i}",
                    decision_id=None,
                    request_at=1000.0,
                    response_at=1000.05,
                    latency_ms=50.0,
                    success=True,
                    provenance_valid=i < 95,  # 95% valid
                )
            )

        summary = calculate_endpoint_summary("twin", results)

        assert summary.provenance_valid_pct == 95.0

    def test_calculate_summary_filters_by_endpoint(self):
        """Test that summary only includes matching endpoint."""
        results = [
            BenchmarkResult(
                iteration=0, endpoint="twin", claim_id="c1", decision_id=None,
                request_at=1000.0, response_at=1000.05, latency_ms=50.0,
                success=True, provenance_valid=True,
            ),
            BenchmarkResult(
                iteration=1, endpoint="inspect", claim_id="", decision_id="d1",
                request_at=1000.0, response_at=1000.03, latency_ms=30.0,
                success=True, provenance_valid=True,
            ),
            BenchmarkResult(
                iteration=2, endpoint="twin", claim_id="c2", decision_id=None,
                request_at=1000.0, response_at=1000.06, latency_ms=60.0,
                success=True, provenance_valid=True,
            ),
        ]

        summary = calculate_endpoint_summary("twin", results)

        assert summary.total_requests == 2
        assert summary.mean_latency_ms == 55.0


class TestRunBenchmark:
    """Tests for run_benchmark function."""

    @pytest.mark.asyncio
    async def test_run_benchmark_single_endpoint(self):
        """Test running benchmark for single endpoint."""
        results, summary = await run_benchmark(
            endpoints=["twin"],
            iterations=10,
            concurrent=5,
        )

        assert len(results) >= 1
        assert "twin" in summary.endpoints
        assert summary.successful + summary.failed == len(results)

    @pytest.mark.asyncio
    async def test_run_benchmark_multiple_endpoints(self):
        """Test running benchmark for multiple endpoints."""
        results, summary = await run_benchmark(
            endpoints=["twin", "inspect", "timeline"],
            iterations=30,
            concurrent=10,
        )

        assert "twin" in summary.endpoints
        assert "inspect" in summary.endpoints
        assert "timeline" in summary.endpoints

    @pytest.mark.asyncio
    async def test_run_benchmark_overall_compliance(self):
        """Test overall SLA compliance calculation."""
        results, summary = await run_benchmark(
            endpoints=["twin"],
            iterations=10,
            concurrent=5,
        )

        # Overall should be True if all endpoints are compliant
        if all(s.sla_p95_compliant and s.sla_p99_compliant for s in summary.endpoints.values()):
            assert summary.overall_sla_compliant is True

    @pytest.mark.asyncio
    async def test_run_benchmark_timestamps(self):
        """Test that benchmark records timestamps."""
        results, summary = await run_benchmark(
            endpoints=["twin"],
            iterations=5,
            concurrent=5,
        )

        assert summary.started_at is not None
        assert summary.completed_at is not None
        assert summary.duration_seconds >= 0


class TestFormatReports:
    """Tests for report formatting functions."""

    def test_format_text_report(self):
        """Test text report formatting."""
        ep_summary = EndpointSummary(
            endpoint="twin",
            total_requests=100,
            successful=98,
            failed=2,
            min_latency_ms=10.0,
            max_latency_ms=100.0,
            mean_latency_ms=45.0,
            median_latency_ms=42.0,
            p95_latency_ms=85.0,
            p99_latency_ms=95.0,
            stddev_latency_ms=15.0,
            provenance_valid_pct=99.0,
            sla_p95_compliant=True,
            sla_p99_compliant=True,
        )
        summary = BenchmarkSummary(
            endpoints={"twin": ep_summary},
            total_iterations=100,
            successful=98,
            failed=2,
            throughput_per_sec=50.0,
            duration_seconds=2.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:02Z",
            sla_targets=SLA_TARGETS,
            overall_sla_compliant=True,
        )

        report = format_text_report(summary)

        assert "P4 LATENCY BENCHMARK REPORT" in report
        assert "TWIN" in report
        assert "P95:" in report
        assert "P99:" in report
        assert "PASS" in report

    def test_format_text_report_failure(self):
        """Test text report with SLA failure."""
        ep_summary = EndpointSummary(
            endpoint="twin",
            total_requests=100,
            successful=100,
            failed=0,
            min_latency_ms=100.0,
            max_latency_ms=300.0,
            mean_latency_ms=200.0,
            median_latency_ms=200.0,
            p95_latency_ms=250.0,  # Over SLA
            p99_latency_ms=280.0,  # Over SLA
            stddev_latency_ms=50.0,
            provenance_valid_pct=100.0,
            sla_p95_compliant=False,
            sla_p99_compliant=False,
        )
        summary = BenchmarkSummary(
            endpoints={"twin": ep_summary},
            total_iterations=100,
            successful=100,
            failed=0,
            throughput_per_sec=50.0,
            duration_seconds=2.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:02Z",
            sla_targets=SLA_TARGETS,
            overall_sla_compliant=False,
        )

        report = format_text_report(summary)

        assert "FAIL" in report
        assert "NO" in report  # P95/P99 Compliant: NO

    def test_format_json_report(self):
        """Test JSON report formatting."""
        import json

        ep_summary = EndpointSummary(
            endpoint="twin",
            total_requests=100,
            successful=100,
            failed=0,
            min_latency_ms=10.0,
            max_latency_ms=100.0,
            mean_latency_ms=45.0,
            median_latency_ms=42.0,
            p95_latency_ms=85.0,
            p99_latency_ms=95.0,
            stddev_latency_ms=15.0,
            provenance_valid_pct=100.0,
            sla_p95_compliant=True,
            sla_p99_compliant=True,
        )
        summary = BenchmarkSummary(
            endpoints={"twin": ep_summary},
            total_iterations=100,
            successful=100,
            failed=0,
            throughput_per_sec=50.0,
            duration_seconds=2.0,
            started_at="2025-01-01T00:00:00Z",
            completed_at="2025-01-01T00:00:02Z",
            sla_targets=SLA_TARGETS,
            overall_sla_compliant=True,
        )
        results = [
            BenchmarkResult(
                iteration=0, endpoint="twin", claim_id="c1", decision_id=None,
                request_at=1000.0, response_at=1000.05, latency_ms=50.0,
                success=True, provenance_valid=True,
            )
        ]

        report = format_json_report(summary, results)

        # Should be valid JSON
        data = json.loads(report)

        assert "summary" in data
        assert "endpoints" in data
        assert "results" in data
        assert data["summary"]["overall_sla_compliant"] is True
        assert "twin" in data["endpoints"]
        assert len(data["results"]) == 1


class TestMainFunction:
    """Tests for main function (CLI)."""

    @pytest.mark.asyncio
    async def test_main_runs(self):
        """Test that main function can execute."""
        from scripts.benchmarks.p4_latency_benchmark import main

        with patch("sys.argv", ["p4_latency_benchmark.py", "--iterations", "5", "--concurrent", "5"]):
            with patch("sys.exit"):  # Don't exit the test
                # Just check it runs without error
                await main()

    @pytest.mark.asyncio
    async def test_main_with_json_output(self):
        """Test main with JSON output."""
        from scripts.benchmarks.p4_latency_benchmark import main

        with patch("sys.argv", ["p4_latency_benchmark.py", "--iterations", "5", "--json"]):
            with patch("sys.exit"):
                await main()

    @pytest.mark.asyncio
    async def test_main_single_endpoint(self):
        """Test main with single endpoint."""
        from scripts.benchmarks.p4_latency_benchmark import main

        with patch("sys.argv", ["p4_latency_benchmark.py", "--endpoint", "twin", "--iterations", "5"]):
            with patch("sys.exit"):
                await main()
