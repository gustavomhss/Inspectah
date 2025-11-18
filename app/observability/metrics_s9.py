from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

MetricKey = Tuple[str, ...]

_user_queries_total: Dict[MetricKey, int] = defaultdict(int)
_user_latency: Dict[MetricKey, List[float]] = defaultdict(list)
_admin_actions_total: Dict[MetricKey, int] = defaultdict(int)
_errors_total: Dict[MetricKey, int] = defaultdict(int)


def record_user_query(info_type: str, scenario_id: str, outcome: str, duration_seconds: float) -> None:
    key = (info_type or "unknown", scenario_id or "unknown", outcome or "unknown")
    _user_queries_total[key] += 1
    latency_key = (info_type or "unknown", scenario_id or "unknown")
    _user_latency[latency_key].append(duration_seconds)


def record_admin_action(action: str) -> None:
    key = (action,)
    _admin_actions_total[key] += 1


def record_error(route: str, kind: str) -> None:
    key = (route or "unknown", kind or "unknown")
    _errors_total[key] += 1


def get_metrics_snapshot() -> Dict[str, object]:
    return {
        "user_queries_total": _format_counter(_user_queries_total),
        "user_latency_seconds": _format_latency(_user_latency),
        "admin_actions_total": _format_counter(_admin_actions_total),
        "errors_total": _format_counter(_errors_total),
    }


def reset() -> None:
    _user_queries_total.clear()
    _user_latency.clear()
    _admin_actions_total.clear()
    _errors_total.clear()


def _format_counter(counter: Dict[MetricKey, int]) -> List[Dict[str, object]]:
    data: List[Dict[str, object]] = []
    for key, value in counter.items():
        record = {f"label_{idx}": part for idx, part in enumerate(key)}
        record["value"] = value
        data.append(record)
    return data


def _format_latency(latency: Dict[MetricKey, List[float]]) -> List[Dict[str, object]]:
    data: List[Dict[str, object]] = []
    for key, samples in latency.items():
        entry = {f"label_{idx}": part for idx, part in enumerate(key)}
        entry.update(_latency_stats(samples))
        data.append(entry)
    return data


def _latency_stats(samples: List[float]) -> Dict[str, float]:
    if not samples:
        return {"count": 0, "p50": 0.0, "p95": 0.0}
    ordered = sorted(samples)
    return {
        "count": len(ordered),
        "p50": _percentile(ordered, 50),
        "p95": _percentile(ordered, 95),
    }


def _percentile(samples: List[float], percentile: float) -> float:
    if not samples:
        return 0.0
    if len(samples) == 1:
        return samples[0]
    rank = percentile / 100 * (len(samples) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(samples) - 1)
    weight = rank - lower
    return samples[lower] * (1 - weight) + samples[upper] * weight
