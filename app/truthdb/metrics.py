"""
Metrics helpers for Truth-DB flows (S32).

Real stack first (Prometheus, if installed); falls back to in-memory counters so
tests/gates rodam sem dependências externas.
"""

from __future__ import annotations

from collections import Counter
from time import monotonic
from typing import Dict

try:
    from prometheus_client import Counter as PromCounter, Histogram

    PROM_AVAILABLE = True
except Exception:  # pragma: no cover
    PROM_AVAILABLE = False

_COUNTERS: Counter = Counter()
_LATENCIES: Dict[str, float] = {}

_PROM_COUNTERS = {}
_PROM_HIST = None

if PROM_AVAILABLE:  # pragma: no cover - optional path
    _PROM_COUNTERS["promotion_attempt"] = PromCounter(
        "truthdb_promotion_attempt_total", "Promotion attempts", ["claim_type", "env", "source"]
    )
    _PROM_COUNTERS["promotion_success"] = PromCounter(
        "truthdb_promotion_success_total", "Promotion successes", ["claim_type", "env", "source"]
    )
    _PROM_COUNTERS["flow_error"] = PromCounter(
        "truthdb_flow_error_total", "Errors in truthdb flows", ["stage", "env", "error_type"]
    )
    _PROM_COUNTERS["contestation"] = PromCounter(
        "truthdb_contestation_total", "Contestation events", ["claim_type", "env", "outcome"]
    )
    _PROM_HIST = Histogram("truthdb_flow_latency_seconds", "Latency per flow type", ["flow_type", "env"])


def _inc(name: str, labels: Dict[str, str]) -> None:
    key = ":".join([name] + list(labels.values()))
    _COUNTERS[key] += 1
    if PROM_AVAILABLE:
        _PROM_COUNTERS[name].labels(**labels).inc()


def inc_promotion_attempt(claim_type: str, env: str = "test", source: str | None = None) -> None:
    _inc("promotion_attempt", {"claim_type": claim_type, "env": env, "source": source or "unknown"})


def inc_promotion_success(claim_type: str, env: str = "test", source: str | None = None) -> None:
    _inc("promotion_success", {"claim_type": claim_type, "env": env, "source": source or "unknown"})


def inc_flow_error(stage: str, env: str = "test", error_type: str | None = None) -> None:
    _inc("flow_error", {"stage": stage, "env": env, "error_type": error_type or "generic"})


def observe_flow_latency(flow_type: str, env: str, seconds: float) -> None:
    _LATENCIES[f"{flow_type}:{env}"] = seconds
    if PROM_AVAILABLE:
        _PROM_HIST.labels(flow_type=flow_type, env=env).observe(seconds)


def inc_contestation(claim_type: str, env: str = "test", outcome: str | None = None) -> None:
    _inc("contestation", {"claim_type": claim_type, "env": env, "outcome": outcome or "pending"})


def snapshot() -> dict:
    """Expose counters and latencies for inspection in tests/gates."""
    return {"counters": dict(_COUNTERS), "latencies": dict(_LATENCIES)}


class LatencyTimer:
    """Context manager to measure latency for a flow."""

    def __init__(self, flow_type: str, env: str = "test"):
        self.flow_type = flow_type
        self.env = env
        self._start = 0.0

    def __enter__(self):
        self._start = monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        observe_flow_latency(self.flow_type, self.env, monotonic() - self._start)
        return False
