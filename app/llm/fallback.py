"""
S39 - LLM Fallback Strategies

Provides fallback mechanisms for LLM failures.
Supports model downgrade, cached responses, and degraded responses.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FallbackReason(str, Enum):
    """Reason for using fallback."""
    CIRCUIT_OPEN = "circuit_open"
    QUOTA_EXCEEDED = "quota_exceeded"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    API_ERROR = "api_error"
    MODEL_UNAVAILABLE = "model_unavailable"
    VALIDATION_ERROR = "validation_error"


class FallbackStrategy(str, Enum):
    """Available fallback strategies."""
    MODEL_DOWNGRADE = "model_downgrade"     # Try a cheaper/faster model
    CACHED_RESPONSE = "cached_response"     # Use cached response
    DEGRADED_RESPONSE = "degraded_response"  # Return minimal response
    RETRY_LATER = "retry_later"             # Queue for retry
    FAIL_FAST = "fail_fast"                 # Return error immediately


@dataclass
class FallbackResult:
    """Result of a fallback execution."""
    success: bool
    strategy_used: FallbackStrategy
    reason: FallbackReason
    response: Any
    original_model: str
    fallback_model: Optional[str] = None
    from_cache: bool = False
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "strategy_used": self.strategy_used.value,
            "reason": self.reason.value,
            "original_model": self.original_model,
            "fallback_model": self.fallback_model,
            "from_cache": self.from_cache,
            "latency_ms": self.latency_ms,
        }


@dataclass
class CachedResponse:
    """A cached LLM response."""
    cache_key: str
    prompt_hash: str
    model: str
    response: Any
    created_at: float
    ttl_seconds: int
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl_seconds


@dataclass
class FallbackConfig:
    """Configuration for fallback behavior."""
    enabled: bool = True
    strategies: List[FallbackStrategy] = field(default_factory=lambda: [
        FallbackStrategy.MODEL_DOWNGRADE,
        FallbackStrategy.CACHED_RESPONSE,
        FallbackStrategy.DEGRADED_RESPONSE,
    ])
    model_fallback_chain: Dict[str, str] = field(default_factory=lambda: {
        "gpt-4": "gpt-3.5-turbo",
        "gpt-4-turbo": "gpt-3.5-turbo",
        "claude-3-opus": "claude-3-sonnet",
        "claude-3-sonnet": "claude-3-haiku",
    })
    cache_ttl_seconds: int = 3600  # 1 hour
    max_cache_size: int = 1000


@dataclass
class FallbackStats:
    """Statistics for fallback usage."""
    total_fallbacks: int = 0
    by_reason: Dict[str, int] = field(default_factory=dict)
    by_strategy: Dict[str, int] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0
    model_downgrades: int = 0


class ResponseCache:
    """LRU cache for LLM responses."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CachedResponse] = {}
        self._access_order: List[str] = []
        self._lock = threading.Lock()

    def _make_key(self, prompt: str, model: str, params: Optional[Dict] = None) -> str:
        """Create cache key from prompt and parameters."""
        key_data = f"{model}:{prompt}"
        if params:
            key_data += f":{sorted(params.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    def get(
        self,
        prompt: str,
        model: str,
        params: Optional[Dict] = None,
    ) -> Optional[CachedResponse]:
        """Get cached response if available and not expired."""
        key = self._make_key(prompt, model, params)

        with self._lock:
            cached = self._cache.get(key)
            if cached:
                if cached.is_expired:
                    del self._cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
                    return None

                cached.hit_count += 1
                # Move to end (most recently used)
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return cached

            return None

    def put(
        self,
        prompt: str,
        model: str,
        response: Any,
        params: Optional[Dict] = None,
        ttl: Optional[int] = None,
    ) -> str:
        """Cache a response."""
        key = self._make_key(prompt, model, params)

        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size and self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]

            self._cache[key] = CachedResponse(
                cache_key=key,
                prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:16],
                model=model,
                response=response,
                created_at=time.time(),
                ttl_seconds=ttl or self.default_ttl,
            )
            self._access_order.append(key)

        return key

    def invalidate(self, key: str) -> bool:
        """Invalidate a cached response."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False

    def clear(self) -> int:
        """Clear all cached responses."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            return count

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            return len(expired_keys)


class FallbackHandler:
    """
    Handles LLM fallback strategies.

    Provides multiple fallback mechanisms:
    - Model downgrade: Try a cheaper/faster model
    - Cached response: Use previously cached response
    - Degraded response: Return minimal/default response
    - Retry later: Queue for background retry

    Usage:
        handler = FallbackHandler()

        # Configure
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.MODEL_DOWNGRADE, FallbackStrategy.CACHED_RESPONSE],
            model_fallback_chain={"gpt-4": "gpt-3.5-turbo"},
        ))

        # Handle fallback
        result = handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="What is the capital of France?",
            call_fn=lambda m, p: llm.generate(model=m, prompt=p),
        )
    """

    def __init__(self, config: Optional[FallbackConfig] = None):
        self.config = config or FallbackConfig()
        self.cache = ResponseCache(
            max_size=self.config.max_cache_size,
            default_ttl=self.config.cache_ttl_seconds,
        )
        self._stats = FallbackStats()
        self._lock = threading.Lock()
        self._degraded_responses: Dict[str, Callable[[], Any]] = {}

    def configure(self, config: FallbackConfig) -> None:
        """Update configuration."""
        self.config = config
        self.cache.max_size = config.max_cache_size
        self.cache.default_ttl = config.cache_ttl_seconds

    def register_degraded_response(
        self,
        key: str,
        response_fn: Callable[[], Any],
    ) -> None:
        """Register a degraded response generator."""
        self._degraded_responses[key] = response_fn

    def handle_fallback(
        self,
        reason: FallbackReason,
        model: str,
        prompt: str,
        call_fn: Optional[Callable[[str, str], Any]] = None,
        params: Optional[Dict] = None,
        degraded_key: Optional[str] = None,
    ) -> FallbackResult:
        """
        Handle a fallback scenario.

        Args:
            reason: Why fallback is needed
            model: Original model that failed
            prompt: The prompt to process
            call_fn: Function to call with (model, prompt)
            params: Additional parameters
            degraded_key: Key for degraded response generator

        Returns:
            FallbackResult with outcome
        """
        start = time.time()

        if not self.config.enabled:
            return FallbackResult(
                success=False,
                strategy_used=FallbackStrategy.FAIL_FAST,
                reason=reason,
                response=None,
                original_model=model,
                latency_ms=(time.time() - start) * 1000,
            )

        # Update stats
        with self._lock:
            self._stats.total_fallbacks += 1
            self._stats.by_reason[reason.value] = (
                self._stats.by_reason.get(reason.value, 0) + 1
            )

        # Try strategies in order
        for strategy in self.config.strategies:
            result = self._try_strategy(
                strategy=strategy,
                reason=reason,
                model=model,
                prompt=prompt,
                call_fn=call_fn,
                params=params,
                degraded_key=degraded_key,
            )
            if result.success:
                result.latency_ms = (time.time() - start) * 1000
                with self._lock:
                    self._stats.by_strategy[strategy.value] = (
                        self._stats.by_strategy.get(strategy.value, 0) + 1
                    )
                return result

        # All strategies failed
        return FallbackResult(
            success=False,
            strategy_used=FallbackStrategy.FAIL_FAST,
            reason=reason,
            response=None,
            original_model=model,
            latency_ms=(time.time() - start) * 1000,
            metadata={"error": "All fallback strategies failed"},
        )

    def _try_strategy(
        self,
        strategy: FallbackStrategy,
        reason: FallbackReason,
        model: str,
        prompt: str,
        call_fn: Optional[Callable[[str, str], Any]],
        params: Optional[Dict],
        degraded_key: Optional[str],
    ) -> FallbackResult:
        """Try a single fallback strategy."""

        if strategy == FallbackStrategy.MODEL_DOWNGRADE:
            return self._try_model_downgrade(
                reason, model, prompt, call_fn, params
            )

        elif strategy == FallbackStrategy.CACHED_RESPONSE:
            return self._try_cached_response(
                reason, model, prompt, params
            )

        elif strategy == FallbackStrategy.DEGRADED_RESPONSE:
            return self._try_degraded_response(
                reason, model, degraded_key
            )

        elif strategy == FallbackStrategy.FAIL_FAST:
            return FallbackResult(
                success=False,
                strategy_used=strategy,
                reason=reason,
                response=None,
                original_model=model,
            )

        return FallbackResult(
            success=False,
            strategy_used=strategy,
            reason=reason,
            response=None,
            original_model=model,
        )

    def _try_model_downgrade(
        self,
        reason: FallbackReason,
        model: str,
        prompt: str,
        call_fn: Optional[Callable[[str, str], Any]],
        params: Optional[Dict],
    ) -> FallbackResult:
        """Try using a fallback model."""
        fallback_model = self.config.model_fallback_chain.get(model)

        if not fallback_model or not call_fn:
            return FallbackResult(
                success=False,
                strategy_used=FallbackStrategy.MODEL_DOWNGRADE,
                reason=reason,
                response=None,
                original_model=model,
            )

        try:
            response = call_fn(fallback_model, prompt)
            with self._lock:
                self._stats.model_downgrades += 1

            # Cache successful response
            self.cache.put(prompt, fallback_model, response, params)

            return FallbackResult(
                success=True,
                strategy_used=FallbackStrategy.MODEL_DOWNGRADE,
                reason=reason,
                response=response,
                original_model=model,
                fallback_model=fallback_model,
            )
        except Exception as e:
            logger.warning(f"Model downgrade failed: {e}")
            return FallbackResult(
                success=False,
                strategy_used=FallbackStrategy.MODEL_DOWNGRADE,
                reason=reason,
                response=None,
                original_model=model,
                fallback_model=fallback_model,
                metadata={"error": str(e)},
            )

    def _try_cached_response(
        self,
        reason: FallbackReason,
        model: str,
        prompt: str,
        params: Optional[Dict],
    ) -> FallbackResult:
        """Try using a cached response."""
        # Try exact match first
        cached = self.cache.get(prompt, model, params)

        if cached:
            with self._lock:
                self._stats.cache_hits += 1
            return FallbackResult(
                success=True,
                strategy_used=FallbackStrategy.CACHED_RESPONSE,
                reason=reason,
                response=cached.response,
                original_model=model,
                from_cache=True,
                metadata={"cache_key": cached.cache_key},
            )

        # Try fallback model cache
        fallback_model = self.config.model_fallback_chain.get(model)
        if fallback_model:
            cached = self.cache.get(prompt, fallback_model, params)
            if cached:
                with self._lock:
                    self._stats.cache_hits += 1
                return FallbackResult(
                    success=True,
                    strategy_used=FallbackStrategy.CACHED_RESPONSE,
                    reason=reason,
                    response=cached.response,
                    original_model=model,
                    fallback_model=fallback_model,
                    from_cache=True,
                    metadata={"cache_key": cached.cache_key},
                )

        with self._lock:
            self._stats.cache_misses += 1

        return FallbackResult(
            success=False,
            strategy_used=FallbackStrategy.CACHED_RESPONSE,
            reason=reason,
            response=None,
            original_model=model,
        )

    def _try_degraded_response(
        self,
        reason: FallbackReason,
        model: str,
        degraded_key: Optional[str],
    ) -> FallbackResult:
        """Try returning a degraded response."""
        response_fn = None

        if degraded_key and degraded_key in self._degraded_responses:
            response_fn = self._degraded_responses[degraded_key]
        elif "default" in self._degraded_responses:
            response_fn = self._degraded_responses["default"]

        if response_fn:
            try:
                response = response_fn()
                return FallbackResult(
                    success=True,
                    strategy_used=FallbackStrategy.DEGRADED_RESPONSE,
                    reason=reason,
                    response=response,
                    original_model=model,
                    metadata={"degraded": True},
                )
            except Exception as e:
                logger.warning(f"Degraded response failed: {e}")

        return FallbackResult(
            success=False,
            strategy_used=FallbackStrategy.DEGRADED_RESPONSE,
            reason=reason,
            response=None,
            original_model=model,
        )

    def cache_response(
        self,
        prompt: str,
        model: str,
        response: Any,
        params: Optional[Dict] = None,
        ttl: Optional[int] = None,
    ) -> str:
        """Manually cache a response for future fallback."""
        return self.cache.put(prompt, model, response, params, ttl)

    def get_stats(self) -> FallbackStats:
        """Get fallback statistics."""
        with self._lock:
            return FallbackStats(
                total_fallbacks=self._stats.total_fallbacks,
                by_reason=dict(self._stats.by_reason),
                by_strategy=dict(self._stats.by_strategy),
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                model_downgrades=self._stats.model_downgrades,
            )

    def get_fallback_model(self, model: str) -> Optional[str]:
        """Get the fallback model for a given model."""
        return self.config.model_fallback_chain.get(model)

    def cleanup_cache(self) -> int:
        """Clean up expired cache entries."""
        return self.cache.cleanup_expired()


# Singleton instance
_fallback_handler: Optional[FallbackHandler] = None


def get_fallback_handler() -> FallbackHandler:
    """Get singleton fallback handler instance."""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler()
    return _fallback_handler


def reset_fallback_handler() -> None:
    """Reset singleton instance (for testing)."""
    global _fallback_handler
    _fallback_handler = None
