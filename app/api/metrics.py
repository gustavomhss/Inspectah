"""
S40-BE-027: P4 API Latency Metrics.

Prometheus metrics for P4 exposure endpoints with thread safety
and defensive programming.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

try:
    from prometheus_client import Counter, Histogram, Gauge
except ImportError:
    # Stub implementations for testing
    class _StubMetric:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def observe(self, value):
            pass
        def inc(self, value=1):
            pass
        def set(self, value):
            pass

    Counter = _StubMetric  # type: ignore
    Histogram = _StubMetric  # type: ignore
    Gauge = _StubMetric  # type: ignore

logger = logging.getLogger(__name__)

# Valid P4 endpoint names
P4_VALID_ENDPOINTS = frozenset({"twin", "inspect", "timeline"})

# Maximum latency samples to keep in memory per endpoint
P4_MAX_SAMPLES = 10000

# Thread lock for in-memory stats
_p4_stats_lock = threading.Lock()

# P4 endpoint latency histogram (S40-BE-027)
# Buckets optimized for sub-100ms SLA target
p4_endpoint_latency_ms = Histogram(
    "p4_endpoint_latency_ms",
    "P4 endpoint response latency in milliseconds",
    ["endpoint", "status"],
    buckets=(5, 10, 25, 50, 75, 100, 150, 200, 500, 1000),
)

# P4 request counter
p4_requests_total = Counter(
    "p4_requests_total",
    "Total P4 endpoint requests",
    ["endpoint", "status"],
)

# P4 provenance validation counter
p4_provenance_valid = Counter(
    "p4_provenance_valid_total",
    "P4 responses with valid provenance",
    ["endpoint"],
)

p4_provenance_invalid = Counter(
    "p4_provenance_invalid_total",
    "P4 responses without valid provenance",
    ["endpoint"],
)

# Current P4 latency gauge (for dashboards)
p4_current_latency_ms = Gauge(
    "p4_current_latency_ms",
    "Current P4 endpoint latency (last request)",
    ["endpoint"],
)


def _sanitize_endpoint(endpoint: str) -> str:
    """Sanitize endpoint name for safe metric labels."""
    if not endpoint:
        return "unknown"
    # Only allow alphanumeric, underscore, and forward slash
    sanitized = "".join(c if c.isalnum() or c in "_/" else "_" for c in endpoint)
    return sanitized[:64]  # Limit length


def _sanitize_latency(latency_ms: float) -> float:
    """Sanitize latency value to reasonable bounds."""
    if latency_ms is None:
        return 0.0
    try:
        lat = float(latency_ms)
        # Cap at 1 hour (3600000ms) as a sanity check
        return max(0.0, min(lat, 3600000.0))
    except (TypeError, ValueError):
        return 0.0


def record_p4_request(
    endpoint: str,
    latency_ms: float,
    status: str = "success",
    provenance_valid: bool = True,
) -> None:
    """
    Record a P4 endpoint request.

    Args:
        endpoint: Endpoint name (twin, inspect, timeline)
        latency_ms: Response latency in milliseconds
        status: Request status (success, error)
        provenance_valid: Whether response had valid provenance
    """
    # Sanitize inputs
    safe_endpoint = _sanitize_endpoint(endpoint)
    safe_latency = _sanitize_latency(latency_ms)
    safe_status = status if status in ("success", "error") else "unknown"

    # Record latency
    p4_endpoint_latency_ms.labels(endpoint=safe_endpoint, status=safe_status).observe(safe_latency)

    # Record request count
    p4_requests_total.labels(endpoint=safe_endpoint, status=safe_status).inc()

    # Record provenance validation
    if provenance_valid:
        p4_provenance_valid.labels(endpoint=safe_endpoint).inc()
    else:
        p4_provenance_invalid.labels(endpoint=safe_endpoint).inc()

    # Update current latency gauge
    p4_current_latency_ms.labels(endpoint=safe_endpoint).set(safe_latency)

    logger.debug(f"[p4_metrics] {safe_endpoint}: {safe_latency}ms, status={safe_status}, provenance={provenance_valid}")


# In-memory tracking for statistics (testing/debugging)
_p4_latencies: Dict[str, List[float]] = {}
_p4_requests: Dict[str, int] = {}


def record_p4_latency(endpoint: str, latency_ms: float) -> None:
    """
    Record P4 latency (in-memory for stats).

    Thread-safe with automatic memory management.

    Args:
        endpoint: Endpoint name
        latency_ms: Latency value in milliseconds
    """
    if not endpoint:
        endpoint = "unknown"

    with _p4_stats_lock:
        if endpoint not in _p4_latencies:
            _p4_latencies[endpoint] = []

        latencies = _p4_latencies[endpoint]
        latencies.append(float(latency_ms))

        # Memory management: trim old samples if exceeding max
        if len(latencies) > P4_MAX_SAMPLES:
            # Keep the most recent samples
            _p4_latencies[endpoint] = latencies[-P4_MAX_SAMPLES:]

        if endpoint not in _p4_requests:
            _p4_requests[endpoint] = 0
        _p4_requests[endpoint] += 1


def _calculate_percentile(sorted_values: List[float], percentile: float) -> float:
    """
    Calculate percentile from sorted values.

    Uses floor-based index for consistency with Prometheus.

    Args:
        sorted_values: Pre-sorted list of values
        percentile: Percentile (0-1), e.g., 0.95 for P95

    Returns:
        Percentile value
    """
    if not sorted_values:
        return 0.0
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    # Calculate index, bounded to valid range
    idx = min(int(n * percentile), n - 1)
    return sorted_values[idx]


def get_p4_stats(endpoint: Optional[str] = None) -> Dict[str, Any]:
    """
    Get P4 latency statistics.

    Thread-safe statistics calculation.

    Args:
        endpoint: Optional endpoint filter

    Returns:
        Dict with statistics (min, max, mean, p50, p95, p99)
    """
    import statistics

    # Get snapshot of data under lock
    with _p4_stats_lock:
        if endpoint:
            endpoints = [endpoint] if endpoint in _p4_latencies else []
        else:
            endpoints = list(_p4_latencies.keys())

        # Create defensive copies for each endpoint
        endpoint_data: Dict[str, List[float]] = {}
        for ep in endpoints:
            latencies = _p4_latencies.get(ep, [])
            if latencies:
                endpoint_data[ep] = list(latencies)

    # Calculate stats outside the lock (expensive operations)
    result: Dict[str, Any] = {}
    for ep, latencies_copy in endpoint_data.items():
        if not latencies_copy:
            continue

        sorted_latencies = sorted(latencies_copy)
        n = len(sorted_latencies)

        result[ep] = {
            "count": n,
            "min_ms": min(latencies_copy),
            "max_ms": max(latencies_copy),
            "mean_ms": statistics.mean(latencies_copy),
            "median_ms": statistics.median(latencies_copy),
            "p95_ms": _calculate_percentile(sorted_latencies, 0.95),
            "p99_ms": _calculate_percentile(sorted_latencies, 0.99),
        }

    return result


def reset_p4_stats() -> None:
    """Reset P4 statistics (for testing). Thread-safe."""
    global _p4_latencies, _p4_requests
    with _p4_stats_lock:
        _p4_latencies = {}
        _p4_requests = {}


def check_p4_sla_compliance(latency_ms: float, target_ms: float = 100) -> bool:
    """
    Check if latency meets P4 SLA target.

    Args:
        latency_ms: Measured latency in milliseconds
        target_ms: SLA target (default 100ms)

    Returns:
        True if compliant, False otherwise
    """
    try:
        return float(latency_ms) <= float(target_ms)
    except (TypeError, ValueError):
        return False


def get_p4_request_count(endpoint: Optional[str] = None) -> Dict[str, int]:
    """
    Get request counts per endpoint.

    Thread-safe.

    Args:
        endpoint: Optional endpoint filter

    Returns:
        Dict mapping endpoint names to request counts
    """
    with _p4_stats_lock:
        if endpoint:
            count = _p4_requests.get(endpoint, 0)
            return {endpoint: count} if count > 0 else {}
        return dict(_p4_requests)


# SLA targets (in milliseconds)
P4_SLA_TARGETS = {
    "p95_ms": 100,  # P95 < 100ms
    "p99_ms": 200,  # P99 < 200ms
}


def get_p4_sla_status() -> Dict[str, Any]:
    """
    Get P4 SLA compliance status.

    Returns:
        Dict with SLA targets, compliance status per endpoint, and overall status.
    """
    stats = get_p4_stats()
    request_counts = get_p4_request_count()

    compliance: Dict[str, Dict[str, Any]] = {}
    for endpoint, ep_stats in stats.items():
        p95 = ep_stats.get("p95_ms", 0)
        p99 = ep_stats.get("p99_ms", 0)
        p95_target = P4_SLA_TARGETS["p95_ms"]
        p99_target = P4_SLA_TARGETS["p99_ms"]

        compliance[endpoint] = {
            "p95_compliant": p95 <= p95_target,
            "p99_compliant": p99 <= p99_target,
            "p95_ms": p95,
            "p99_ms": p99,
            "p95_headroom_ms": p95_target - p95,
            "p99_headroom_ms": p99_target - p99,
            "request_count": request_counts.get(endpoint, 0),
            "sample_count": ep_stats.get("count", 0),
        }

    # Calculate overall compliance
    if compliance:
        all_compliant = all(
            c.get("p95_compliant", False) and c.get("p99_compliant", False)
            for c in compliance.values()
        )
        violations = [
            ep for ep, c in compliance.items()
            if not c.get("p95_compliant", True) or not c.get("p99_compliant", True)
        ]
    else:
        all_compliant = True
        violations = []

    return {
        "targets": dict(P4_SLA_TARGETS),  # Defensive copy
        "compliance": compliance,
        "overall_compliant": all_compliant,
        "violations": violations,
        "total_endpoints": len(compliance),
    }
