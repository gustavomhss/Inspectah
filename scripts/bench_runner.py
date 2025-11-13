#!/usr/bin/env python3
"""Synthetic benchmark runner for Inspectah components."""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Dict, List

random.seed(1337)

OPERATIONS = [
    "api_create",
    "api_explore",
    "vault_manifest",
    "ingestor_step",
    "fts_query",
    "export_job",
]

SCENARIOS = {
    "light": 10,
    "medium": 50,
    "heavy": 120,
}


def simulate_latency(operation: str, load: str) -> float:
    base = {
        "api_create": 80,
        "api_explore": 60,
        "vault_manifest": 90,
        "ingestor_step": 120,
        "fts_query": 70,
        "export_job": 110,
    }[operation]
    multiplier = {
        "light": 0.9,
        "medium": 1.1,
        "heavy": 1.4,
    }[load]
    jitter = random.uniform(-10, 15)
    return max(10.0, base * multiplier + jitter)


def run_scenario(name: str, rps: int, iterations: int = 100) -> Dict[str, Dict[str, float]]:
    measurements: Dict[str, List[float]] = {op: [] for op in OPERATIONS}
    for _ in range(iterations):
        for op in OPERATIONS:
            measurements[op].append(simulate_latency(op, name))
    summary = {}
    for op, values in measurements.items():
        sorted_vals = sorted(values)
        summary[op] = {
            "p50": percentile(sorted_vals, 50),
            "p75": percentile(sorted_vals, 75),
            "p95": percentile(sorted_vals, 95),
            "p99": percentile(sorted_vals, 99),
            "throughput_ops_per_sec": rps,
        }
    return summary


def percentile(values: List[float], pct: int) -> float:
    if not values:
        return 0.0
    k = (len(values) - 1) * pct / 100
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


def record_latency_series(results: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, List[float]]:
    series = {}
    for scenario, ops in results.items():
        for op, stats in ops.items():
            key = f"{scenario}_{op}"
            series[key] = [stats["p50"], stats["p95"], stats["p99"]]
    return series


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah benchmark runner")
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--series", type=Path, required=True)
    args = parser.parse_args()

    bench_results: Dict[str, Dict[str, Dict[str, float]]] = {}
    for scenario, rps in SCENARIOS.items():
        bench_results[scenario] = run_scenario(scenario, rps)

    args.raw.parent.mkdir(parents=True, exist_ok=True)
    args.raw.write_text(json.dumps(bench_results, indent=2), encoding="utf-8")

    series = record_latency_series(bench_results)
    args.series.write_text(json.dumps(series, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
