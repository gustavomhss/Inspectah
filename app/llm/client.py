"""
S39 - LLM Client with Circuit Breaker, Quota, and Fallback

Resilient LLM client that handles failures gracefully with:
- Circuit breaker for provider failures
- Token and request quotas
- Automatic fallback to cheaper models or cached responses
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.ingestion.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    get_circuit_breaker,
)
from app.llm.quota import (
    QuotaExceededError,
    QuotaManager,
    QuotaScope,
    QuotaType,
    get_quota_manager,
)
from app.llm.fallback import (
    FallbackHandler,
    FallbackReason,
    FallbackResult,
    FallbackStrategy,
    get_fallback_handler,
)

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    STUB = "stub"


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    provider: LLMProvider = LLMProvider.STUB
    default_model: str = "gpt-3.5-turbo"
    timeout_seconds: float = 30.0
    max_retries: int = 2
    enable_circuit_breaker: bool = True
    enable_quota: bool = True
    enable_fallback: bool = True
    # Circuit breaker settings
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    # Default quotas (tokens per hour)
    default_token_quota: int = 100000
    default_request_quota: int = 1000


@dataclass
class LLMRequest:
    """An LLM request."""
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    provider: LLMProvider
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    from_cache: bool = False
    from_fallback: bool = False
    fallback_reason: Optional[str] = None
    request_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider.value,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "from_cache": self.from_cache,
            "from_fallback": self.from_fallback,
            "fallback_reason": self.fallback_reason,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LLMClientStats:
    """Statistics for LLM client."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    fallback_requests: int = 0
    cached_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0.0
    by_model: Dict[str, int] = field(default_factory=dict)
    by_provider: Dict[str, int] = field(default_factory=dict)

    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests


class LLMClient:
    """
    Resilient LLM client with circuit breaker, quota management, and fallback.

    Features:
    - Circuit breaker: Prevents cascading failures when provider is down
    - Quota management: Enforces token and request limits
    - Fallback: Automatic model downgrade or cached responses
    - Observability: Detailed stats and logging

    Usage:
        client = LLMClient(config=LLMConfig(
            provider=LLMProvider.OPENAI,
            default_model="gpt-4",
            enable_fallback=True,
        ))

        # Simple generation
        response = client.generate(LLMRequest(
            prompt="What is the capital of France?",
        ))

        # With custom model
        response = client.generate(LLMRequest(
            prompt="Explain quantum computing",
            model="gpt-4",
            max_tokens=2000,
        ))
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        quota_manager: Optional[QuotaManager] = None,
        fallback_handler: Optional[FallbackHandler] = None,
        provider_fn: Optional[Callable[[LLMRequest], LLMResponse]] = None,
    ):
        self.config = config or LLMConfig()
        self.circuit_breaker = circuit_breaker or get_circuit_breaker()
        self.quota_manager = quota_manager or get_quota_manager()
        self.fallback_handler = fallback_handler or get_fallback_handler()
        self._provider_fn = provider_fn or self._stub_provider
        self._stats = LLMClientStats()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize client with configured settings."""
        if self._initialized:
            return

        # Configure circuit breaker for provider
        provider_id = f"llm_{self.config.provider.value}"
        self.circuit_breaker.configure(
            source_id=provider_id,
            failure_threshold=self.config.failure_threshold,
            timeout_seconds=self.config.recovery_timeout,
        )

        # Configure default quotas
        if self.config.enable_quota:
            self.quota_manager.add_limit(
                __import__("app.llm.quota", fromlist=["QuotaLimit"]).QuotaLimit(
                    quota_type=QuotaType.TOKENS,
                    limit=self.config.default_token_quota,
                    window_seconds=3600,
                    scope=QuotaScope.GLOBAL,
                    scope_id="default",
                )
            )
            self.quota_manager.add_limit(
                __import__("app.llm.quota", fromlist=["QuotaLimit"]).QuotaLimit(
                    quota_type=QuotaType.REQUESTS,
                    limit=self.config.default_request_quota,
                    window_seconds=3600,
                    scope=QuotaScope.GLOBAL,
                    scope_id="default",
                )
            )

        self._initialized = True
        logger.info(f"LLMClient initialized with provider={self.config.provider.value}")

    def generate(
        self,
        request: LLMRequest,
        user_id: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate LLM response with full resilience features.

        Args:
            request: The LLM request
            user_id: Optional user ID for quota tracking

        Returns:
            LLMResponse with generated content

        Raises:
            QuotaExceededError: If quota exceeded and no fallback available
            CircuitBreakerError: If circuit open and no fallback available
        """
        if not self._initialized:
            self.initialize()

        start = time.time()
        model = request.model or self.config.default_model
        provider_id = f"llm_{self.config.provider.value}"

        self._stats.total_requests += 1
        self._stats.by_model[model] = self._stats.by_model.get(model, 0) + 1
        self._stats.by_provider[self.config.provider.value] = (
            self._stats.by_provider.get(self.config.provider.value, 0) + 1
        )

        # Check quota before making request
        if self.config.enable_quota:
            estimated_tokens = self._estimate_tokens(request)
            try:
                self.quota_manager.consume(
                    scope_id="default",
                    quota_type=QuotaType.TOKENS,
                    amount=estimated_tokens,
                    scope=QuotaScope.GLOBAL,
                )
            except QuotaExceededError as e:
                logger.warning(f"Quota exceeded: {e}")
                if self.config.enable_fallback:
                    return self._handle_fallback(
                        request=request,
                        reason=FallbackReason.QUOTA_EXCEEDED,
                        model=model,
                        start_time=start,
                    )
                raise

        # Check circuit breaker
        if self.config.enable_circuit_breaker:
            if not self.circuit_breaker.is_available(provider_id):
                logger.warning(f"Circuit open for {provider_id}")
                if self.config.enable_fallback:
                    return self._handle_fallback(
                        request=request,
                        reason=FallbackReason.CIRCUIT_OPEN,
                        model=model,
                        start_time=start,
                    )
                raise CircuitBreakerError(f"Circuit open for {provider_id}")

        # Make the actual request
        try:
            response = self._call_provider(request, model)

            # Record success
            if self.config.enable_circuit_breaker:
                self.circuit_breaker.record_success(provider_id)

            # Update actual token usage
            if self.config.enable_quota:
                actual_tokens = response.total_tokens
                # Adjust for estimated vs actual (we already consumed estimated)
                estimated = self._estimate_tokens(request)
                if actual_tokens > estimated:
                    self.quota_manager.consume(
                        scope_id="default",
                        quota_type=QuotaType.TOKENS,
                        amount=actual_tokens - estimated,
                        scope=QuotaScope.GLOBAL,
                        raise_on_exceed=False,
                    )

            # Cache response for future fallback
            if self.config.enable_fallback:
                self.fallback_handler.cache_response(
                    prompt=request.prompt,
                    model=model,
                    response=response.content,
                )

            # Update stats
            self._stats.successful_requests += 1
            self._stats.total_input_tokens += response.input_tokens
            self._stats.total_output_tokens += response.output_tokens
            self._stats.total_latency_ms += response.latency_ms

            return response

        except Exception as e:
            logger.error(f"LLM request failed: {e}")

            # Record failure
            if self.config.enable_circuit_breaker:
                self.circuit_breaker.record_failure(provider_id, str(e))

            self._stats.failed_requests += 1

            # Try fallback
            if self.config.enable_fallback:
                return self._handle_fallback(
                    request=request,
                    reason=FallbackReason.API_ERROR,
                    model=model,
                    start_time=start,
                )

            raise

    def _call_provider(self, request: LLMRequest, model: str) -> LLMResponse:
        """Call the actual LLM provider."""
        start = time.time()

        # Use injected provider function
        request_with_model = LLMRequest(
            prompt=request.prompt,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            metadata=request.metadata,
        )

        response = self._provider_fn(request_with_model)
        response.latency_ms = (time.time() - start) * 1000
        return response

    def _stub_provider(self, request: LLMRequest) -> LLMResponse:
        """Stub provider for testing."""
        # Simulate some latency
        time.sleep(0.01)

        input_tokens = len(request.prompt.split()) * 2  # Rough estimate
        output_tokens = min(request.max_tokens, 50)

        return LLMResponse(
            content=f"[STUB] Response for: {request.prompt[:100]}...",
            model=request.model or self.config.default_model,
            provider=self.config.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            latency_ms=10.0,
        )

    def _handle_fallback(
        self,
        request: LLMRequest,
        reason: FallbackReason,
        model: str,
        start_time: float,
    ) -> LLMResponse:
        """Handle fallback scenario."""
        def call_fn(fallback_model: str, prompt: str) -> str:
            fb_request = LLMRequest(
                prompt=prompt,
                model=fallback_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            fb_response = self._call_provider(fb_request, fallback_model)
            return fb_response.content

        result = self.fallback_handler.handle_fallback(
            reason=reason,
            model=model,
            prompt=request.prompt,
            call_fn=call_fn,
        )

        latency = (time.time() - start_time) * 1000

        if result.success:
            self._stats.fallback_requests += 1
            if result.from_cache:
                self._stats.cached_requests += 1

            return LLMResponse(
                content=result.response if isinstance(result.response, str) else str(result.response),
                model=result.fallback_model or model,
                provider=self.config.provider,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency,
                from_cache=result.from_cache,
                from_fallback=True,
                fallback_reason=reason.value,
            )

        # Fallback failed
        self._stats.failed_requests += 1
        raise RuntimeError(
            f"LLM request failed and fallback unsuccessful. Reason: {reason.value}"
        )

    def _estimate_tokens(self, request: LLMRequest) -> int:
        """Estimate tokens for a request."""
        # Rough estimation: ~1.3 tokens per word
        prompt_tokens = int(len(request.prompt.split()) * 1.3)
        if request.system_prompt:
            prompt_tokens += int(len(request.system_prompt.split()) * 1.3)
        return prompt_tokens + request.max_tokens

    def get_stats(self) -> LLMClientStats:
        """Get client statistics."""
        return self._stats

    def get_circuit_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        provider_id = f"llm_{self.config.provider.value}"
        stats = self.circuit_breaker.get_stats(provider_id)
        return stats or {"state": "unknown"}

    def get_quota_status(self) -> Dict[str, Any]:
        """Get quota status."""
        return self.quota_manager.to_dict()

    def is_healthy(self) -> bool:
        """Check if client is healthy."""
        provider_id = f"llm_{self.config.provider.value}"
        return self.circuit_breaker.is_available(provider_id)

    def reset_circuit(self) -> None:
        """Reset circuit breaker."""
        provider_id = f"llm_{self.config.provider.value}"
        self.circuit_breaker.reset(provider_id)

    def set_provider_function(self, fn: Callable[[LLMRequest], LLMResponse]) -> None:
        """Set custom provider function."""
        self._provider_fn = fn


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get singleton LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client() -> None:
    """Reset singleton instance (for testing)."""
    global _llm_client
    _llm_client = None
