from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class _Series:
    values: List[float]

    def add(self, value: float) -> None:
        if value >= 0:
            self.values.append(value)

    def summary(self) -> Dict[str, float]:
        if not self.values:
            return {"count": 0, "min": 0.0, "max": 0.0, "avg": 0.0}
        total = sum(self.values)
        return {
            "count": len(self.values),
            "min": min(self.values),
            "max": max(self.values),
            "avg": total / len(self.values),
        }


_run_latencies = _Series([])
_explore_latencies = _Series([])
_explore_requests_total = 0
_explore_rate_limited_total = 0
_explore_queries_total = 0
_ingest_items_total = 0
_ingest_errors_total = 0


def reset_metrics() -> None:
    _run_latencies.values.clear()
    _explore_latencies.values.clear()
    global _explore_requests_total, _explore_rate_limited_total, _explore_queries_total, _ingest_items_total, _ingest_errors_total
    _explore_requests_total = 0
    _explore_rate_limited_total = 0
    _explore_queries_total = 0
    _ingest_items_total = 0
    _ingest_errors_total = 0


def record_run_latency(value_ms: float) -> None:
    _run_latencies.add(value_ms)


def record_explore_query_latency(value_ms: float) -> None:
    _explore_latencies.add(value_ms)


def record_explore_request(rate_limited: bool) -> None:
    global _explore_requests_total, _explore_rate_limited_total
    _explore_requests_total += 1
    if rate_limited:
        _explore_rate_limited_total += 1


def record_explore_query() -> None:
    global _explore_queries_total
    _explore_queries_total += 1


def record_ingest_event(items_ingested: int, *, error: bool, source_id: str | None = None) -> None:
    del source_id  # source is captured by logs; metrics remain aggregate
    global _ingest_items_total, _ingest_errors_total
    if items_ingested > 0:
        _ingest_items_total += items_ingested
    if error:
        _ingest_errors_total += 1


def get_snapshot() -> Dict[str, Dict[str, float]]:
    return {
        "inspectah_run_latency_ms": _run_latencies.summary(),
        "inspectah_explore_query_latency_ms": _explore_latencies.summary(),
        "inspectah_explore_requests_total": {
            "count": float(_explore_requests_total),
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
        },
        "inspectah_explore_rate_limited_total": {
            "count": float(_explore_rate_limited_total),
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
        },
        "inspectah_explore_queries_total": {
            "count": float(_explore_queries_total),
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
        },
        "inspectah_ingest_items_total": {
            "count": float(_ingest_items_total),
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
        },
        "inspectah_ingest_errors_total": {
            "count": float(_ingest_errors_total),
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
        },
    }


__all__ = [
    "record_run_latency",
    "record_explore_query_latency",
    "record_explore_request",
    "record_explore_query",
    "record_ingest_event",
    "get_snapshot",
    "reset_metrics",
]
