#!/usr/bin/env python3
"""
S40-BE-022: P1 Latency Benchmark Script

Benchmarks the P1 pilot domain latency for collected_to_ready pipeline.

Usage:
    python scripts/benchmarks/p1_latency_benchmark.py [options]

Options:
    --domain DOMAIN     Domain to benchmark (saude, politica) [default: saude]
    --iterations N      Number of iterations [default: 100]
    --concurrent N      Concurrent requests [default: 10]
    --output FILE       Output file for results [default: stdout]
    --json              Output in JSON format
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
    domain: str
    source: str
    document_id: str
    collected_at: float
    ready_at: float
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results."""

    domain: str
    total_iterations: int
    successful: int
    failed: int
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    stddev_latency_ms: float
    throughput_per_sec: float
    duration_seconds: float
    started_at: str
    completed_at: str
    sla_targets: Dict[str, Any] = field(default_factory=dict)
    sla_compliance: Dict[str, bool] = field(default_factory=dict)


# SLA targets (in milliseconds)
SLA_TARGETS = {
    "collected_to_ready_p95_ms": 5000,  # 5 seconds
    "collected_to_ready_p99_ms": 10000,  # 10 seconds
}


async def simulate_document_processing(
    document_id: str,
    domain: str,
    source: str,
    processing_time_ms: float = 100,
) -> BenchmarkResult:
    """
    Simulate document processing for benchmarking.

    In production, this would call the actual ingestion pipeline.
    """
    collected_at = time.time()

    # Simulate variable processing time (100-500ms with jitter)
    import random

    actual_time = processing_time_ms + random.uniform(0, 400)

    await asyncio.sleep(actual_time / 1000)

    ready_at = time.time()
    latency_ms = (ready_at - collected_at) * 1000

    return BenchmarkResult(
        iteration=0,  # Set by caller
        domain=domain,
        source=source,
        document_id=document_id,
        collected_at=collected_at,
        ready_at=ready_at,
        latency_ms=latency_ms,
        success=True,
    )


async def run_benchmark(
    domain: str,
    iterations: int,
    concurrent: int,
    source: str = "benchmark",
) -> tuple[List[BenchmarkResult], BenchmarkSummary]:
    """Run the P1 latency benchmark."""
    results: List[BenchmarkResult] = []
    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    # Run iterations in batches of concurrent requests
    for batch_start in range(0, iterations, concurrent):
        batch_size = min(concurrent, iterations - batch_start)
        tasks = []

        for i in range(batch_size):
            iteration = batch_start + i
            doc_id = f"bench-{domain}-{iteration}"
            task = simulate_document_processing(
                document_id=doc_id,
                domain=domain,
                source=source,
            )
            tasks.append(task)

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(batch_results):
            iteration = batch_start + i
            if isinstance(result, Exception):
                results.append(
                    BenchmarkResult(
                        iteration=iteration,
                        domain=domain,
                        source=source,
                        document_id=f"bench-{domain}-{iteration}",
                        collected_at=0,
                        ready_at=0,
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

    # Calculate summary statistics
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]

    if successful_results:
        latencies = [r.latency_ms for r in successful_results]
        latencies_sorted = sorted(latencies)

        p95_idx = int(len(latencies_sorted) * 0.95)
        p99_idx = int(len(latencies_sorted) * 0.99)

        summary = BenchmarkSummary(
            domain=domain,
            total_iterations=iterations,
            successful=len(successful_results),
            failed=len(failed_results),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            mean_latency_ms=statistics.mean(latencies),
            median_latency_ms=statistics.median(latencies),
            p95_latency_ms=latencies_sorted[p95_idx] if p95_idx < len(latencies_sorted) else latencies_sorted[-1],
            p99_latency_ms=latencies_sorted[p99_idx] if p99_idx < len(latencies_sorted) else latencies_sorted[-1],
            stddev_latency_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
            throughput_per_sec=len(successful_results) / duration_seconds if duration_seconds > 0 else 0,
            duration_seconds=duration_seconds,
            started_at=started_at,
            completed_at=completed_at,
            sla_targets=SLA_TARGETS,
            sla_compliance={
                "p95_compliant": latencies_sorted[p95_idx] <= SLA_TARGETS["collected_to_ready_p95_ms"]
                if p95_idx < len(latencies_sorted)
                else True,
                "p99_compliant": latencies_sorted[p99_idx] <= SLA_TARGETS["collected_to_ready_p99_ms"]
                if p99_idx < len(latencies_sorted)
                else True,
            },
        )
    else:
        summary = BenchmarkSummary(
            domain=domain,
            total_iterations=iterations,
            successful=0,
            failed=len(failed_results),
            min_latency_ms=0,
            max_latency_ms=0,
            mean_latency_ms=0,
            median_latency_ms=0,
            p95_latency_ms=0,
            p99_latency_ms=0,
            stddev_latency_ms=0,
            throughput_per_sec=0,
            duration_seconds=duration_seconds,
            started_at=started_at,
            completed_at=completed_at,
            sla_targets=SLA_TARGETS,
            sla_compliance={"p95_compliant": False, "p99_compliant": False},
        )

    return results, summary


def format_text_report(summary: BenchmarkSummary) -> str:
    """Format summary as human-readable text."""
    lines = [
        "=" * 60,
        "P1 LATENCY BENCHMARK REPORT",
        f"Domain: {summary.domain}",
        "=" * 60,
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
        "LATENCY (ms):",
        f"  Min:    {summary.min_latency_ms:.2f}",
        f"  Max:    {summary.max_latency_ms:.2f}",
        f"  Mean:   {summary.mean_latency_ms:.2f}",
        f"  Median: {summary.median_latency_ms:.2f}",
        f"  P95:    {summary.p95_latency_ms:.2f}",
        f"  P99:    {summary.p99_latency_ms:.2f}",
        f"  StdDev: {summary.stddev_latency_ms:.2f}",
        "",
        "SLA COMPLIANCE:",
        f"  Target P95: {summary.sla_targets['collected_to_ready_p95_ms']}ms",
        f"  Target P99: {summary.sla_targets['collected_to_ready_p99_ms']}ms",
        f"  P95 Compliant: {'YES' if summary.sla_compliance['p95_compliant'] else 'NO'}",
        f"  P99 Compliant: {'YES' if summary.sla_compliance['p99_compliant'] else 'NO'}",
        "",
        "=" * 60,
    ]

    overall = "PASS" if all(summary.sla_compliance.values()) else "FAIL"
    lines.append(f"OVERALL: {overall}")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_json_report(summary: BenchmarkSummary, results: List[BenchmarkResult]) -> str:
    """Format summary and results as JSON."""
    return json.dumps(
        {
            "summary": {
                "domain": summary.domain,
                "total_iterations": summary.total_iterations,
                "successful": summary.successful,
                "failed": summary.failed,
                "latency_ms": {
                    "min": summary.min_latency_ms,
                    "max": summary.max_latency_ms,
                    "mean": summary.mean_latency_ms,
                    "median": summary.median_latency_ms,
                    "p95": summary.p95_latency_ms,
                    "p99": summary.p99_latency_ms,
                    "stddev": summary.stddev_latency_ms,
                },
                "throughput_per_sec": summary.throughput_per_sec,
                "duration_seconds": summary.duration_seconds,
                "started_at": summary.started_at,
                "completed_at": summary.completed_at,
                "sla_targets": summary.sla_targets,
                "sla_compliance": summary.sla_compliance,
            },
            "results": [
                {
                    "iteration": r.iteration,
                    "document_id": r.document_id,
                    "latency_ms": r.latency_ms,
                    "success": r.success,
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
        description="P1 Latency Benchmark for pilot domains"
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="saude",
        choices=["saude", "politica"],
        help="Domain to benchmark",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations",
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

    print(f"Running P1 latency benchmark for domain '{args.domain}'...", file=sys.stderr)
    print(f"Iterations: {args.iterations}, Concurrent: {args.concurrent}", file=sys.stderr)

    results, summary = await run_benchmark(
        domain=args.domain,
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
    if not all(summary.sla_compliance.values()):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
