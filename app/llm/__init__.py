"""
S39 - LLM Module

Provides resilient LLM integration with:
- Circuit breaker for provider failures
- Token and request quota management
- Automatic fallback strategies
"""

from app.llm.quota import (
    QuotaScope,
    QuotaType,
    QuotaExceededError,
    QuotaLimit,
    QuotaUsage,
    QuotaStats,
    QuotaManager,
    get_quota_manager,
    reset_quota_manager,
)
from app.llm.fallback import (
    FallbackReason,
    FallbackStrategy,
    FallbackResult,
    FallbackConfig,
    FallbackStats,
    FallbackHandler,
    ResponseCache,
    CachedResponse,
    get_fallback_handler,
    reset_fallback_handler,
)
from app.llm.client import (
    LLMProvider,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMClientStats,
    LLMClient,
    get_llm_client,
    reset_llm_client,
)

__all__ = [
    # Quota
    "QuotaScope",
    "QuotaType",
    "QuotaExceededError",
    "QuotaLimit",
    "QuotaUsage",
    "QuotaStats",
    "QuotaManager",
    "get_quota_manager",
    "reset_quota_manager",
    # Fallback
    "FallbackReason",
    "FallbackStrategy",
    "FallbackResult",
    "FallbackConfig",
    "FallbackStats",
    "FallbackHandler",
    "ResponseCache",
    "CachedResponse",
    "get_fallback_handler",
    "reset_fallback_handler",
    # Client
    "LLMProvider",
    "LLMConfig",
    "LLMRequest",
    "LLMResponse",
    "LLMClientStats",
    "LLMClient",
    "get_llm_client",
    "reset_llm_client",
]
