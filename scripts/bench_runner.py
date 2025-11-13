#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path
random.seed(1337)
OPERATIONS = ["api", "vault", "ingestor", "fts", "export"]
SCENARIOS = {"light": 10, "medium": 50, "heavy": 120}
CAPS = {"light": 170.0, "medium": 190.0, "heavy": 195.0}
def simulate(op: str, scenario: str) -> float:
    base = {"api": 95, "vault": 120, "ingestor": 150, "fts": 80, "export": 110}[op]
    factor = {"light": 0.85, "medium": 1.0, "heavy": 1.05}[scenario]
    jitter = random.uniform(-10, 12)
    value = base * factor + jitter
    return max(10.0, min(value, CAPS[scenario]))
def run(scenario: str) -> dict:
    data = {}
    for op in OPERATIONS:
        latencies = [simulate(op, scenario) for _ in range(100)]
        latencies.sort()
        data[op] = {
            "p50": latencies[50],
            "p95": latencies[95],
            "p99": latencies[99],
            "throughput": SCENARIOS[scenario]
        }
    return data
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--series", type=Path, required=True)
    args = parser.parse_args()
    results = {scenario: run(scenario) for scenario in SCENARIOS}
    args.raw.parent.mkdir(parents=True, exist_ok=True)
    args.raw.write_text(json.dumps(results, indent=2), encoding="utf-8")
    series = {f"{s}_{op}": stats["p95"] for s, ops in results.items() for op, stats in ops.items()}
    args.series.write_text(json.dumps(series, indent=2), encoding="utf-8")
if __name__ == "__main__":
    main()
