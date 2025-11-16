from __future__ import annotations
import math
import os
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional


RATE_LIMIT_PER_MINUTE = int(os.environ.get("INSPECTAH_RATE_LIMIT_PER_MINUTE", "120"))
RATE_LIMIT_BURST = int(os.environ.get("INSPECTAH_RATE_LIMIT_BURST", "240"))
IDENTITY_HEADER = os.environ.get("INSPECTAH_RATE_LIMIT_HEADER", "X-Client-Id")
WINDOW_SECONDS = 60
RATE_LIMIT_POLICY = f"{RATE_LIMIT_PER_MINUTE}/min burst {RATE_LIMIT_BURST}"
_RATE_PER_SECOND = RATE_LIMIT_PER_MINUTE / WINDOW_SECONDS


@dataclass
class _Bucket:
    tokens: float
    updated_at: float


@dataclass
class RateLimitDecision:
    allowed: bool
    headers: Dict[str, str]
    retry_after: int = 0


_buckets: Dict[str, _Bucket] = {}
_lock = threading.Lock()


def reset_rate_limit_state() -> None:
    with _lock:
        _buckets.clear()


def configure_rate_limit(
    *,
    per_minute: Optional[int] = None,
    burst: Optional[int] = None,
    identity_header: Optional[str] = None,
) -> None:
    """
    Adjust the in-memory rate limit configuration.
    Intended for integration tests and controlled environments only.
    """
    global RATE_LIMIT_PER_MINUTE, RATE_LIMIT_BURST, RATE_LIMIT_POLICY, _RATE_PER_SECOND, IDENTITY_HEADER
    if per_minute is not None:
        RATE_LIMIT_PER_MINUTE = per_minute
    if burst is not None:
        RATE_LIMIT_BURST = burst
    if identity_header is not None:
        IDENTITY_HEADER = identity_header
    RATE_LIMIT_POLICY = f"{RATE_LIMIT_PER_MINUTE}/min burst {RATE_LIMIT_BURST}"
    _RATE_PER_SECOND = RATE_LIMIT_PER_MINUTE / WINDOW_SECONDS
    reset_rate_limit_state()


def _refill(bucket: _Bucket, now: float) -> None:
    elapsed = max(0.0, now - bucket.updated_at)
    bucket.tokens = min(RATE_LIMIT_BURST, bucket.tokens + elapsed * _RATE_PER_SECOND)
    bucket.updated_at = now


def check_rate_limit(identity: Optional[str]) -> RateLimitDecision:
    key = identity or "ANONYMOUS"
    now = time.monotonic()
    with _lock:
        bucket = _buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=RATE_LIMIT_BURST, updated_at=now)
            _buckets[key] = bucket
        _refill(bucket, now)
        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            allowed = True
            retry_after = 0
        else:
            allowed = False
            deficit = 1.0 - bucket.tokens
            retry_after = max(1, math.ceil(deficit / _RATE_PER_SECOND))
        remaining = max(0, int(bucket.tokens))
    reset_time = int(time.time()) + retry_after
    headers = {
        "X-RateLimit-Limit": str(RATE_LIMIT_PER_MINUTE),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time),
        "X-RateLimit-Policy": RATE_LIMIT_POLICY,
    }
    return RateLimitDecision(allowed=allowed, headers=headers, retry_after=retry_after)


__all__ = [
    "check_rate_limit",
    "reset_rate_limit_state",
    "configure_rate_limit",
    "RateLimitDecision",
    "RATE_LIMIT_PER_MINUTE",
    "RATE_LIMIT_BURST",
    "RATE_LIMIT_POLICY",
    "IDENTITY_HEADER",
]
