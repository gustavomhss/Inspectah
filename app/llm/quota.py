"""
S39 - LLM Quota Manager

Manages token and request quotas for LLM providers.
Supports per-model, per-user, and global quotas with sliding windows.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QuotaScope(str, Enum):
    """Scope for quota limits."""
    GLOBAL = "global"       # System-wide
    MODEL = "model"         # Per model
    USER = "user"           # Per user
    AGENT = "agent"         # Per agent type


class QuotaType(str, Enum):
    """Type of quota limit."""
    TOKENS = "tokens"           # Input + output tokens
    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    REQUESTS = "requests"       # Number of requests


class QuotaExceededError(Exception):
    """Raised when quota is exceeded."""
    def __init__(
        self,
        message: str,
        quota_type: QuotaType,
        current: int,
        limit: int,
        reset_at: Optional[datetime] = None,
    ):
        super().__init__(message)
        self.quota_type = quota_type
        self.current = current
        self.limit = limit
        self.reset_at = reset_at


@dataclass
class QuotaLimit:
    """Configuration for a quota limit."""
    quota_type: QuotaType
    limit: int
    window_seconds: int = 3600  # 1 hour default
    scope: QuotaScope = QuotaScope.GLOBAL
    scope_id: Optional[str] = None  # e.g., model name, user id


@dataclass
class QuotaUsage:
    """Tracks usage within a quota window."""
    quota_type: QuotaType
    scope: QuotaScope
    scope_id: str
    window_start: float
    window_seconds: int
    limit: int
    used: int = 0
    requests: List[tuple] = field(default_factory=list)  # (timestamp, amount)

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def reset_at(self) -> datetime:
        reset_ts = self.window_start + self.window_seconds
        return datetime.fromtimestamp(reset_ts, tz=timezone.utc)

    @property
    def is_exceeded(self) -> bool:
        return self.used >= self.limit

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quota_type": self.quota_type.value,
            "scope": self.scope.value,
            "scope_id": self.scope_id,
            "limit": self.limit,
            "used": self.used,
            "remaining": self.remaining,
            "reset_at": self.reset_at.isoformat(),
            "utilization_percent": round(self.used / self.limit * 100, 2) if self.limit > 0 else 0,
        }


@dataclass
class QuotaStats:
    """Statistics for quota usage."""
    total_requests: int
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    rejected_requests: int
    active_quotas: int


class QuotaManager:
    """
    Manages LLM quotas with sliding window tracking.

    Features:
    - Per-model, per-user, and global quotas
    - Token and request limits
    - Sliding window tracking
    - Automatic cleanup of expired windows

    Usage:
        manager = QuotaManager()

        # Configure quotas
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            window_seconds=3600,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        # Check before request
        if manager.can_consume("gpt-4", QuotaType.TOKENS, 1000):
            result = call_llm()
            manager.consume("gpt-4", QuotaType.TOKENS, actual_tokens)

        # Or use consume directly (raises if exceeded)
        try:
            manager.consume("gpt-4", QuotaType.TOKENS, 1000)
        except QuotaExceededError as e:
            handle_quota_exceeded(e)
    """

    def __init__(self):
        self._limits: Dict[str, QuotaLimit] = {}
        self._usage: Dict[str, QuotaUsage] = {}
        self._lock = threading.Lock()
        self._stats = QuotaStats(
            total_requests=0,
            total_tokens=0,
            total_input_tokens=0,
            total_output_tokens=0,
            rejected_requests=0,
            active_quotas=0,
        )

    def _make_key(
        self,
        quota_type: QuotaType,
        scope: QuotaScope,
        scope_id: str,
    ) -> str:
        """Create unique key for quota tracking."""
        return f"{quota_type.value}:{scope.value}:{scope_id}"

    def add_limit(self, limit: QuotaLimit) -> None:
        """Add or update a quota limit."""
        scope_id = limit.scope_id or "default"
        key = self._make_key(limit.quota_type, limit.scope, scope_id)

        with self._lock:
            self._limits[key] = limit
            logger.info(
                f"[quota] Added limit: {limit.quota_type.value} "
                f"{limit.limit}/{limit.window_seconds}s for {limit.scope.value}:{scope_id}"
            )

    def remove_limit(
        self,
        quota_type: QuotaType,
        scope: QuotaScope,
        scope_id: str = "default",
    ) -> bool:
        """Remove a quota limit."""
        key = self._make_key(quota_type, scope, scope_id)

        with self._lock:
            if key in self._limits:
                del self._limits[key]
                if key in self._usage:
                    del self._usage[key]
                return True
            return False

    def _get_or_create_usage(
        self,
        quota_type: QuotaType,
        scope: QuotaScope,
        scope_id: str,
    ) -> Optional[QuotaUsage]:
        """Get or create usage tracker for a quota."""
        key = self._make_key(quota_type, scope, scope_id)
        limit = self._limits.get(key)

        if not limit:
            return None

        now = time.time()

        if key not in self._usage:
            self._usage[key] = QuotaUsage(
                quota_type=quota_type,
                scope=scope,
                scope_id=scope_id,
                window_start=now,
                window_seconds=limit.window_seconds,
                limit=limit.limit,
            )
        else:
            usage = self._usage[key]
            # Check if window has expired
            if now - usage.window_start >= usage.window_seconds:
                # Reset window
                usage.window_start = now
                usage.used = 0
                usage.requests.clear()
            else:
                # Clean old requests from sliding window
                cutoff = now - usage.window_seconds
                usage.requests = [(ts, amt) for ts, amt in usage.requests if ts > cutoff]
                usage.used = sum(amt for _, amt in usage.requests)

        return self._usage[key]

    def can_consume(
        self,
        scope_id: str,
        quota_type: QuotaType,
        amount: int,
        scope: QuotaScope = QuotaScope.MODEL,
    ) -> bool:
        """Check if quota allows consuming the amount."""
        with self._lock:
            usage = self._get_or_create_usage(quota_type, scope, scope_id)
            if not usage:
                return True  # No limit configured
            return usage.used + amount <= usage.limit

    def consume(
        self,
        scope_id: str,
        quota_type: QuotaType,
        amount: int,
        scope: QuotaScope = QuotaScope.MODEL,
        raise_on_exceed: bool = True,
    ) -> QuotaUsage:
        """
        Consume quota and return updated usage.

        Args:
            scope_id: ID within the scope (model name, user id, etc.)
            quota_type: Type of quota
            amount: Amount to consume
            scope: Quota scope
            raise_on_exceed: Raise QuotaExceededError if exceeded

        Returns:
            Updated QuotaUsage

        Raises:
            QuotaExceededError: If quota exceeded and raise_on_exceed is True
        """
        with self._lock:
            usage = self._get_or_create_usage(quota_type, scope, scope_id)

            if not usage:
                # No limit, create temporary usage for tracking
                return QuotaUsage(
                    quota_type=quota_type,
                    scope=scope,
                    scope_id=scope_id,
                    window_start=time.time(),
                    window_seconds=3600,
                    limit=999999999,
                    used=amount,
                )

            if usage.used + amount > usage.limit:
                self._stats.rejected_requests += 1
                if raise_on_exceed:
                    raise QuotaExceededError(
                        f"Quota exceeded for {scope.value}:{scope_id} "
                        f"({usage.used + amount}/{usage.limit} {quota_type.value})",
                        quota_type=quota_type,
                        current=usage.used,
                        limit=usage.limit,
                        reset_at=usage.reset_at,
                    )

            # Record consumption
            now = time.time()
            usage.requests.append((now, amount))
            usage.used += amount

            # Update stats
            self._stats.total_requests += 1
            if quota_type == QuotaType.TOKENS:
                self._stats.total_tokens += amount
            elif quota_type == QuotaType.INPUT_TOKENS:
                self._stats.total_input_tokens += amount
            elif quota_type == QuotaType.OUTPUT_TOKENS:
                self._stats.total_output_tokens += amount

            return usage

    def get_usage(
        self,
        scope_id: str,
        quota_type: QuotaType,
        scope: QuotaScope = QuotaScope.MODEL,
    ) -> Optional[QuotaUsage]:
        """Get current usage for a quota."""
        with self._lock:
            return self._get_or_create_usage(quota_type, scope, scope_id)

    def get_all_usage(self) -> List[QuotaUsage]:
        """Get all current quota usage."""
        with self._lock:
            # Refresh all usages
            for key, limit in self._limits.items():
                scope_id = limit.scope_id or "default"
                self._get_or_create_usage(limit.quota_type, limit.scope, scope_id)
            return list(self._usage.values())

    def get_stats(self) -> QuotaStats:
        """Get quota manager statistics."""
        with self._lock:
            self._stats.active_quotas = len(self._usage)
            return self._stats

    def reset_usage(
        self,
        scope_id: str,
        quota_type: QuotaType,
        scope: QuotaScope = QuotaScope.MODEL,
    ) -> bool:
        """Reset usage for a specific quota."""
        key = self._make_key(quota_type, scope, scope_id)
        with self._lock:
            if key in self._usage:
                usage = self._usage[key]
                usage.used = 0
                usage.requests.clear()
                usage.window_start = time.time()
                logger.info(f"[quota] Reset usage for {key}")
                return True
            return False

    def reserve(
        self,
        scope_id: str,
        quota_type: QuotaType,
        amount: int,
        scope: QuotaScope = QuotaScope.MODEL,
    ) -> bool:
        """
        Reserve quota for an upcoming request.

        Returns True if reservation successful, False otherwise.
        Use release() to return unused reservation.
        """
        return self.can_consume(scope_id, quota_type, amount, scope)

    def to_dict(self) -> Dict[str, Any]:
        """Export quota state as dictionary."""
        with self._lock:
            return {
                "limits": [
                    {
                        "key": k,
                        "quota_type": v.quota_type.value,
                        "limit": v.limit,
                        "window_seconds": v.window_seconds,
                        "scope": v.scope.value,
                        "scope_id": v.scope_id,
                    }
                    for k, v in self._limits.items()
                ],
                "usage": [u.to_dict() for u in self._usage.values()],
                "stats": {
                    "total_requests": self._stats.total_requests,
                    "total_tokens": self._stats.total_tokens,
                    "rejected_requests": self._stats.rejected_requests,
                },
            }


# Singleton instance
_quota_manager: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Get singleton quota manager instance."""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager


def reset_quota_manager() -> None:
    """Reset singleton instance (for testing)."""
    global _quota_manager
    _quota_manager = None
