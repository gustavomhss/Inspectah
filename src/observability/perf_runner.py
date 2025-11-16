from __future__ import annotations
import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from field_designer.config_loader import SourceConfig, load_source_configs
from field_designer.dry_run import run_dry_run
from inspectah.metrics import reset_metrics
from inspectah.explore.api import query_items
from watchers.pipeline_runner import PipelineInvariantRunner


@dataclass
class FieldResolutionStats:
    total_fields: int
    resolved_fields: int

    @property
    def success_rate(self) -> float:
        if self.total_fields == 0:
            return 1.0
        return self.resolved_fields / self.total_fields


class PerformanceRunner:
    def __init__(
        self,
        db_path: Path,
        config_dir: Path,
        *,
        ingest_iterations: int = 6,
        query_rounds: int = 5,
        field_runs: int = 5,
    ) -> None:
        self.db_path = db_path
        self.config_dir = config_dir
        self.ingest_iterations = ingest_iterations
        self.query_rounds = query_rounds
        self.field_runs = field_runs
        self.runner = PipelineInvariantRunner(self.db_path, self.config_dir)
        self.configs = load_source_configs(self.config_dir)

    def close(self) -> None:
        self.runner.close()

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        k = (len(ordered) - 1) * (percentile / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return ordered[int(k)]
        d0 = ordered[f] * (c - k)
        d1 = ordered[c] * (k - f)
        return d0 + d1

    def _ingest_benchmark(self) -> Dict[str, Any]:
        detection_samples: List[float] = []
        successes = 0
        for index in range(self.ingest_iterations):
            mutated = (index % 3 == 2)
            start = time.perf_counter()
            try:
                self.runner.ingest(mutated=mutated)
                successes += 1
            finally:
                duration_ms = (time.perf_counter() - start) * 1000.0
                detection_samples.append(duration_ms)
        return {
            "samples_ms": detection_samples,
            "run_success_rate": successes / max(1, self.ingest_iterations),
            "p95_ms": self._percentile(detection_samples, 95),
            "p99_ms": self._percentile(detection_samples, 99),
            "runs": self.ingest_iterations,
        }

    def _query_benchmark(self) -> Dict[str, Any]:
        latencies: List[float] = []
        if not self.configs:
            return {"samples_ms": latencies, "p95_ms": 0.0, "p99_ms": 0.0, "queries": 0}
        for _ in range(self.query_rounds):
            for source_id in self.configs:
                start = time.perf_counter()
                query_items(source_id=source_id, page=1, page_size=20)
                latencies.append((time.perf_counter() - start) * 1000.0)
                start = time.perf_counter()
                query_items(q="item", page=1, page_size=10)
                latencies.append((time.perf_counter() - start) * 1000.0)
        return {
            "samples_ms": latencies,
            "p95_ms": self._percentile(latencies, 95),
            "p99_ms": self._percentile(latencies, 99),
            "queries": len(latencies),
        }

    def _field_resolution_benchmark(self) -> FieldResolutionStats:
        total_fields = 0
        resolved_fields = 0
        for _ in range(self.field_runs):
            for cfg in self.configs.values():
                result = run_dry_run(cfg, sample_size=5)
                total_fields += result.fields_total
                resolved_fields += result.fields_resolved
        return FieldResolutionStats(total_fields=total_fields, resolved_fields=resolved_fields)

    def run(self) -> Dict[str, Any]:
        reset_metrics()
        ingest_data = self._ingest_benchmark()
        field_stats = self._field_resolution_benchmark()
        query_data = self._query_benchmark()
        summary = {
            "detection_latency_p95_ms": ingest_data["p95_ms"],
            "detection_latency_p99_ms": ingest_data["p99_ms"],
            "explore_query_p95_ms": query_data["p95_ms"],
            "explore_query_p99_ms": query_data["p99_ms"],
            "run_success_rate": ingest_data["run_success_rate"],
            "field_resolution_success_under_load": field_stats.success_rate,
        }
        return {
            "summary": summary,
            "detection_latency_samples_ms": ingest_data["samples_ms"],
            "explore_query_samples_ms": query_data["samples_ms"],
            "field_resolution": {
                "total_fields": field_stats.total_fields,
                "resolved_fields": field_stats.resolved_fields,
                "success_rate": field_stats.success_rate,
            },
            "runs_executed": ingest_data["runs"],
            "queries_executed": query_data["queries"],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah performance benchmark runner")
    parser.add_argument("--config-dir", default="configs/sources", help="Diretório com configs de fonte")
    parser.add_argument("--db-path", required=True, help="Arquivo SQLite a ser usado durante o benchmark")
    parser.add_argument("--report", required=True, help="Arquivo JSON de saída")
    parser.add_argument("--ingest-iterations", type=int, default=6, help="Número de ciclos de ingestão")
    parser.add_argument("--query-rounds", type=int, default=5, help="Rodadas de consulta Explore")
    parser.add_argument("--field-runs", type=int, default=5, help="Execuções de Field Designer para carga")
    args = parser.parse_args()

    db_path = Path(args.db_path).resolve()
    config_dir = Path(args.config_dir).resolve()
    runner = PerformanceRunner(
        db_path,
        config_dir,
        ingest_iterations=args.ingest_iterations,
        query_rounds=args.query_rounds,
        field_runs=args.field_runs,
    )
    try:
        report = runner.run()
    finally:
        runner.close()
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
