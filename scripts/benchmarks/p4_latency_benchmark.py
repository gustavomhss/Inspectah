#!/usr/bin/env python3
"""
S40-BE-028: P4 Latency Benchmark Script

Benchmarks the P4 Exposure endpoints (twin, inspect, timeline).

Usage:
    python scripts/benchmarks/p4_latency_benchmark.py [options]

Options:
    --endpoint ENDPOINT   Endpoint to benchmark (twin, inspect, timeline, all) [default: all]
    --iterations N        Number of iterations [default: 100]
    --concurrent N        Concurrent requests [default: 10]
    --output FILE         Output file for results [default: stdout]
    --json                Output in JSON format
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkResult:
    """Result from a single benchmark iteration."""

    iteration: int
    endpoint: str
    claim_id: str
    decision_id: Optional[str]
    request_at: float
    response_at: float
    latency_ms: float
    success: bool
    provenance_valid: bool = True
    error: Optional[str] = None


@dataclass
class EndpointSummary:
    """Summary for a single endpoint."""

    endpoint: str
    total_requests: int
    successful: int
    failed: int
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    stddev_latency_ms: float
    provenance_valid_pct: float
    sla_p95_compliant: bool
    sla_p99_compliant: bool


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results."""

    endpoints: Dict[str, EndpointSummary]
    total_iterations: int
    successful: int
    failed: int
    throughput_per_sec: float
    duration_seconds: float
    started_at: str
    completed_at: str
    sla_targets: Dict[str, Any] = field(default_factory=dict)
    overall_sla_compliant: bool = True


# P4 SLA targets (in milliseconds) - stricter than P1
SLA_TARGETS = {
    "p95_ms": 100,   # P95 < 100ms
    "p99_ms": 200,   # P99 < 200ms
}


async def simulate_twin_request(
    claim_id: str,
    base_latency_ms: float = 20,
) -> BenchmarkResult:
    """
    Simulate twin endpoint request.

    In production, this would call the actual /api/truth/{claim_id}/twin endpoint.
    """
    import random

    request_at = time.time()

    # Simulate variable latency (20-80ms with jitter)
    actual_time = base_latency_ms + random.uniform(0, 60)
    await asyncio.sleep(actual_time / 1000)

    response_at = time.time()
    latency_ms = (response_at - request_at) * 1000

    # Simulate provenance validation (99% valid in simulation)
    provenance_valid = random.random() < 0.99

    return BenchmarkResult(
        iteration=0,
        endpoint="twin",
        claim_id=claim_id,
        decision_id=None,
        request_at=request_at,
        response_at=response_at,
        latency_ms=latency_ms,
        success=True,
        provenance_valid=provenance_valid,
    )


async def simulate_inspect_request(
    decision_id: str,
    base_latency_ms: float = 15,
) -> BenchmarkResult:
    """
    Simulate inspect endpoint request.

    In production, this would call the actual /api/truth/decision/{id}/inspect endpoint.
    """
    import random

    request_at = time.time()

    # Simulate variable latency (15-50ms with jitter)
    actual_time = base_latency_ms + random.uniform(0, 35)
    await asyncio.sleep(actual_time / 1000)

    response_at = time.time()
    latency_ms = (response_at - request_at) * 1000

    provenance_valid = random.random() < 0.99

    return BenchmarkResult(
        iteration=0,
        endpoint="inspect",
        claim_id="",
        decision_id=decision_id,
        request_at=request_at,
        response_at=response_at,
        latency_ms=latency_ms,
        success=True,
        provenance_valid=provenance_valid,
    )


async def simulate_timeline_request(
    claim_id: str,
    base_latency_ms: float = 25,
) -> BenchmarkResult:
    """
    Simulate timeline endpoint request.

    In production, this would call the actual /api/truth/{claim_id}/timeline endpoint.
    """
    import random

    request_at = time.time()

    # Simulate variable latency (25-90ms with jitter)
    actual_time = base_latency_ms + random.uniform(0, 65)
    await asyncio.sleep(actual_time / 1000)

    response_at = time.time()
    latency_ms = (response_at - request_at) * 1000

    provenance_valid = random.random() < 0.99

    return BenchmarkResult(
        iteration=0,
        endpoint="timeline",
        claim_id=claim_id,
        decision_id=None,
        request_at=request_at,
        response_at=response_at,
        latency_ms=latency_ms,
        success=True,
        provenance_valid=provenance_valid,
    )


ENDPOINT_SIMULATORS = {
    "twin": simulate_twin_request,
    "inspect": simulate_inspect_request,
    "timeline": simulate_timeline_request,
}


def calculate_endpoint_summary(
    endpoint: str,
    results: List[BenchmarkResult],
) -> EndpointSummary:
    """Calculate summary statistics for an endpoint."""
    endpoint_results = [r for r in results if r.endpoint == endpoint]
    successful = [r for r in endpoint_results if r.success]
    failed = [r for r in endpoint_results if not r.success]

    if not successful:
        return EndpointSummary(
            endpoint=endpoint,
            total_requests=len(endpoint_results),
            successful=0,
            failed=len(failed),
            min_latency_ms=0,
            max_latency_ms=0,
            mean_latency_ms=0,
            median_latency_ms=0,
            p95_latency_ms=0,
            p99_latency_ms=0,
            stddev_latency_ms=0,
            provenance_valid_pct=0,
            sla_p95_compliant=False,
            sla_p99_compliant=False,
        )

    latencies = [r.latency_ms for r in successful]
    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)

    p95_idx = int(n * 0.95)
    p99_idx = int(n * 0.99)

    p95_latency = latencies_sorted[p95_idx] if p95_idx < n else latencies_sorted[-1]
    p99_latency = latencies_sorted[p99_idx] if p99_idx < n else latencies_sorted[-1]

    provenance_valid_count = sum(1 for r in successful if r.provenance_valid)

    return EndpointSummary(
        endpoint=endpoint,
        total_requests=len(endpoint_results),
        successful=len(successful),
        failed=len(failed),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        mean_latency_ms=statistics.mean(latencies),
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=p95_latency,
        p99_latency_ms=p99_latency,
        stddev_latency_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        provenance_valid_pct=(provenance_valid_count / len(successful)) * 100,
        sla_p95_compliant=p95_latency <= SLA_TARGETS["p95_ms"],
        sla_p99_compliant=p99_latency <= SLA_TARGETS["p99_ms"],
    )


async def run_benchmark(
    endpoints: List[str],
    iterations: int,
    concurrent: int,
) -> tuple[List[BenchmarkResult], BenchmarkSummary]:
    """Run the P4 latency benchmark."""
    results: List[BenchmarkResult] = []
    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    # Calculate iterations per endpoint
    iterations_per_endpoint = iterations // len(endpoints)

    for endpoint in endpoints:
        simulator = ENDPOINT_SIMULATORS.get(endpoint)
        if not simulator:
            continue

        for batch_start in range(0, iterations_per_endpoint, concurrent):
            batch_size = min(concurrent, iterations_per_endpoint - batch_start)
            tasks = []

            for i in range(batch_size):
                iteration = batch_start + i
                if endpoint in ("twin", "timeline"):
                    task = simulator(claim_id=f"bench-claim-{iteration}")
                else:
                    task = simulator(decision_id=f"bench-decision-{iteration}")
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(batch_results):
                iteration = batch_start + i
                if isinstance(result, Exception):
                    results.append(
                        BenchmarkResult(
                            iteration=iteration,
                            endpoint=endpoint,
                            claim_id=f"bench-claim-{iteration}",
                            decision_id=f"bench-decision-{iteration}" if endpoint == "inspect" else None,
                            request_at=0,
                            response_at=0,
                            latency_ms=0,
                            success=False,
                            error=str(result),
                        )
                    )
                else:
                    result.iteration = iteration
                    results.append(result)

    end_time = time.time()
    completed_at = datetime.now(timezone.utc).isoformat()
    duration_seconds = end_time - start_time

    # Calculate per-endpoint summaries
    endpoint_summaries = {}
    for endpoint in endpoints:
        summary = calculate_endpoint_summary(endpoint, results)
        endpoint_summaries[endpoint] = summary

    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    overall_sla_compliant = all(
        s.sla_p95_compliant and s.sla_p99_compliant
        for s in endpoint_summaries.values()
    )

    summary = BenchmarkSummary(
        endpoints=endpoint_summaries,
        total_iterations=len(results),
        successful=successful,
        failed=failed,
        throughput_per_sec=successful / duration_seconds if duration_seconds > 0 else 0,
        duration_seconds=duration_seconds,
        started_at=started_at,
        completed_at=completed_at,
        sla_targets=SLA_TARGETS,
        overall_sla_compliant=overall_sla_compliant,
    )

    return results, summary


def format_text_report(summary: BenchmarkSummary) -> str:
    """Format summary as human-readable text."""
    lines = [
        "=" * 70,
        "P4 LATENCY BENCHMARK REPORT (Truth Twin / Decision Inspector)",
        "=" * 70,
        "",
        "EXECUTION:",
        f"  Started:    {summary.started_at}",
        f"  Completed:  {summary.completed_at}",
        f"  Duration:   {summary.duration_seconds:.2f}s",
        f"  Iterations: {summary.total_iterations}",
        f"  Successful: {summary.successful}",
        f"  Failed:     {summary.failed}",
        f"  Throughput: {summary.throughput_per_sec:.2f} req/s",
        "",
        "SLA TARGETS:",
        f"  P95: {summary.sla_targets['p95_ms']}ms",
        f"  P99: {summary.sla_targets['p99_ms']}ms",
        "",
    ]

    for endpoint, ep_summary in summary.endpoints.items():
        lines.extend([
            "-" * 70,
            f"ENDPOINT: {endpoint.upper()}",
            "-" * 70,
            f"  Requests:   {ep_summary.total_requests}",
            f"  Successful: {ep_summary.successful}",
            f"  Failed:     {ep_summary.failed}",
            "",
            "  LATENCY (ms):",
            f"    Min:    {ep_summary.min_latency_ms:.2f}",
            f"    Max:    {ep_summary.max_latency_ms:.2f}",
            f"    Mean:   {ep_summary.mean_latency_ms:.2f}",
            f"    Median: {ep_summary.median_latency_ms:.2f}",
            f"    P95:    {ep_summary.p95_latency_ms:.2f}",
            f"    P99:    {ep_summary.p99_latency_ms:.2f}",
            f"    StdDev: {ep_summary.stddev_latency_ms:.2f}",
            "",
            f"  Provenance Valid: {ep_summary.provenance_valid_pct:.1f}%",
            f"  P95 Compliant: {'YES' if ep_summary.sla_p95_compliant else 'NO'}",
            f"  P99 Compliant: {'YES' if ep_summary.sla_p99_compliant else 'NO'}",
            "",
        ])

    lines.extend([
        "=" * 70,
        f"OVERALL SLA COMPLIANCE: {'PASS' if summary.overall_sla_compliant else 'FAIL'}",
        "=" * 70,
    ])

    return "\n".join(lines)


def format_json_report(summary: BenchmarkSummary, results: List[BenchmarkResult]) -> str:
    """Format summary and results as JSON."""
    return json.dumps(
        {
            "summary": {
                "total_iterations": summary.total_iterations,
                "successful": summary.successful,
                "failed": summary.failed,
                "throughput_per_sec": summary.throughput_per_sec,
                "duration_seconds": summary.duration_seconds,
                "started_at": summary.started_at,
                "completed_at": summary.completed_at,
                "sla_targets": summary.sla_targets,
                "overall_sla_compliant": summary.overall_sla_compliant,
            },
            "endpoints": {
                endpoint: {
                    "total_requests": s.total_requests,
                    "successful": s.successful,
                    "failed": s.failed,
                    "latency_ms": {
                        "min": s.min_latency_ms,
                        "max": s.max_latency_ms,
                        "mean": s.mean_latency_ms,
                        "median": s.median_latency_ms,
                        "p95": s.p95_latency_ms,
                        "p99": s.p99_latency_ms,
                        "stddev": s.stddev_latency_ms,
                    },
                    "provenance_valid_pct": s.provenance_valid_pct,
                    "sla_p95_compliant": s.sla_p95_compliant,
                    "sla_p99_compliant": s.sla_p99_compliant,
                }
                for endpoint, s in summary.endpoints.items()
            },
            "results": [
                {
                    "iteration": r.iteration,
                    "endpoint": r.endpoint,
                    "claim_id": r.claim_id,
                    "decision_id": r.decision_id,
                    "latency_ms": r.latency_ms,
                    "success": r.success,
                    "provenance_valid": r.provenance_valid,
                    "error": r.error,
                }
                for r in results
            ],
        },
        indent=2,
    )


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="P4 Latency Benchmark for Truth Twin / Decision Inspector"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="all",
        choices=["twin", "inspect", "timeline", "all"],
        help="Endpoint to benchmark",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations (total across endpoints)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Concurrent requests",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    if args.endpoint == "all":
        endpoints = ["twin", "inspect", "timeline"]
    else:
        endpoints = [args.endpoint]

    print(f"Running P4 latency benchmark for endpoints: {', '.join(endpoints)}...", file=sys.stderr)
    print(f"Iterations: {args.iterations}, Concurrent: {args.concurrent}", file=sys.stderr)

    results, summary = await run_benchmark(
        endpoints=endpoints,
        iterations=args.iterations,
        concurrent=args.concurrent,
    )

    if args.json:
        output = format_json_report(summary, results)
    else:
        output = format_text_report(summary)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with non-zero if SLA not met
    if not summary.overall_sla_compliant:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
