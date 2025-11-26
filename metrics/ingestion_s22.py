from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

runs_total: Dict[Tuple[str, str], int] = defaultdict(int)
runs_fail_total: Dict[str, int] = defaultdict(int)
last_success_ts: Dict[str, float] = {}
last_failure_ts: Dict[str, float] = {}
latency_ms: Dict[str, List[int]] = defaultdict(list)


def reset() -> None:
    runs_total.clear()
    runs_fail_total.clear()
    last_success_ts.clear()
    last_failure_ts.clear()
    latency_ms.clear()


def record_run(source_id: str, status: str, trigger: str | None = None) -> None:
    runs_total[(source_id, status)] += 1
    if status in {"FAIL", "PARTIAL_SUCCESS"}:
        runs_fail_total[source_id] += 1


def record_latency(source_id: str, value_ms: int) -> None:
    latency_ms[source_id].append(value_ms)


def mark_success(source_id: str, ts: float) -> None:
    last_success_ts[source_id] = ts


def mark_failure(source_id: str, ts: float) -> None:
    last_failure_ts[source_id] = ts
    runs_fail_total[source_id] += 1


def summary() -> dict:
    return {
        "runs_total": {f"{k[0]}|{k[1]}": v for k, v in runs_total.items()},
        "runs_fail_total": dict(runs_fail_total),
        "last_success_ts": dict(last_success_ts),
        "last_failure_ts": dict(last_failure_ts),
    }
