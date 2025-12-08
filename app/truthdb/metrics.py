from __future__ import annotations

from collections import Counter
from time import monotonic
from typing import Dict

from prometheus_client import Counter as PromCounter, Histogram

# In-memory counters para testes e snapshot usado pelos testes existentes.
_local: Counter[str] = Counter()

_transitions = PromCounter(
    "truth_promotion_transitions_total",
    "Truth promotion transitions",
    ["from", "to", "result", "role"],
)
_failures = PromCounter(
    "truth_promotion_failures_total",
    "Truth promotion failures",
    ["reason"],
)
_latency = Histogram(
    "truth_promotion_latency_seconds",
    "Latency per promotion transition",
    ["from", "to"],
    buckets=(0.1, 0.5, 1, 2, 5, 10),
)


def inc_promotion_attempt(claim_type: str, env: str = "test") -> None:
    _local[f"promotion_attempt:{claim_type}:{env}"] += 1


def inc_promotion_success(claim_type: str, env: str = "test") -> None:
    _local[f"promotion_success:{claim_type}:{env}"] += 1


def inc_contestation(claim_type: str, env: str = "test", outcome: str = "pending") -> None:
    _local[f"contestation:{claim_type}:{env}:{outcome}"] += 1


def inc_flow_error(stage: str, env: str = "test", error_type: str = "unknown") -> None:
    _local[f"flow_error:{stage}:{env}:{error_type}"] += 1


def record_transition(from_state: str, to_state: str, result: str, role: str) -> None:
    _transitions.labels(from_state, to_state, result, role).inc()


def record_failure(reason: str) -> None:
    _failures.labels(reason=reason).inc()
    _local[f"truth_failure:{reason}"] += 1


def observe_latency(from_state: str, to_state: str, seconds: float) -> None:
    _latency.labels(from_state, to_state).observe(seconds)


def snapshot() -> Dict[str, Dict[str, int]]:
    """Compat helper para testes legados."""
    return {"counters": dict(_local)}


class LatencyTimer:
    """Context manager para medir latência e não quebrar chamadas legadas."""

    def __init__(self, from_state: str | None = None, to_state: str | None = None, flow_type: str | None = None, env: str = "test"):
        self.from_state = from_state
        self.to_state = to_state
        self.flow_type = flow_type
        self.env = env
        self._start = 0.0

    def __enter__(self):
        self._start = monotonic()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = max(monotonic() - self._start, 0.0)
        # Se não veio from/to, ainda assim registra em contador local para rastrear.
        if self.from_state and self.to_state:
            observe_latency(self.from_state, self.to_state, elapsed)
        else:
            _local[f"latency:{self.flow_type or 'generic'}:{self.env}"] += 1
        return False
