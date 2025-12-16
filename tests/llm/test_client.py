"""
Tests for LLM Client.

S39 - LLM Client Integration Tests
"""
import time
from unittest.mock import MagicMock, patch

import pytest

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
from app.llm.quota import QuotaExceededError, QuotaManager, QuotaType, QuotaScope, reset_quota_manager
from app.llm.fallback import FallbackHandler, reset_fallback_handler
from app.ingestion.circuit_breaker import CircuitBreaker, CircuitBreakerError


class TestLLMEnums:
    """Tests for LLM enums."""

    def test_llm_provider_values(self):
        """Test LLMProvider enum values."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.GOOGLE.value == "google"
        assert LLMProvider.LOCAL.value == "local"
        assert LLMProvider.STUB.value == "stub"


class TestLLMConfig:
    """Tests for LLMConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = LLMConfig()

        assert config.provider == LLMProvider.STUB
        assert config.default_model == "gpt-3.5-turbo"
        assert config.timeout_seconds == 30.0
        assert config.enable_circuit_breaker is True
        assert config.enable_quota is True
        assert config.enable_fallback is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            default_model="gpt-4",
            timeout_seconds=60.0,
            enable_fallback=False,
        )

        assert config.provider == LLMProvider.OPENAI
        assert config.default_model == "gpt-4"
        assert config.timeout_seconds == 60.0
        assert config.enable_fallback is False


class TestLLMRequest:
    """Tests for LLMRequest."""

    def test_create_request(self):
        """Test creating request."""
        request = LLMRequest(
            prompt="What is AI?",
            model="gpt-4",
            max_tokens=1000,
            temperature=0.5,
        )

        assert request.prompt == "What is AI?"
        assert request.model == "gpt-4"
        assert request.max_tokens == 1000
        assert request.temperature == 0.5

    def test_default_values(self):
        """Test default values."""
        request = LLMRequest(prompt="Test")

        assert request.model is None
        assert request.max_tokens == 1000
        assert request.temperature == 0.7
        assert request.system_prompt is None


class TestLLMResponse:
    """Tests for LLMResponse."""

    def test_create_response(self):
        """Test creating response."""
        response = LLMResponse(
            content="AI is artificial intelligence.",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            input_tokens=10,
            output_tokens=20,
            total_tokens=30,
            latency_ms=100.0,
        )

        assert response.content == "AI is artificial intelligence."
        assert response.model == "gpt-4"
        assert response.total_tokens == 30

    def test_to_dict(self):
        """Test converting response to dict."""
        response = LLMResponse(
            content="Response",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            input_tokens=10,
            output_tokens=20,
            total_tokens=30,
            latency_ms=100.0,
            from_cache=True,
            from_fallback=True,
            fallback_reason="circuit_open",
        )

        d = response.to_dict()

        assert d["content"] == "Response"
        assert d["model"] == "gpt-4"
        assert d["provider"] == "openai"
        assert d["from_cache"] is True
        assert d["from_fallback"] is True


class TestLLMClientStats:
    """Tests for LLMClientStats."""

    def test_avg_latency_empty(self):
        """Test average latency with no requests."""
        stats = LLMClientStats()
        assert stats.avg_latency_ms == 0.0

    def test_avg_latency(self):
        """Test average latency calculation."""
        stats = LLMClientStats(
            successful_requests=10,
            total_latency_ms=1000.0,
        )
        assert stats.avg_latency_ms == 100.0


class TestLLMClient:
    """Tests for LLMClient."""

    @pytest.fixture
    def client(self):
        """Create fresh client with mocked dependencies."""
        reset_quota_manager()
        reset_fallback_handler()

        circuit_breaker = CircuitBreaker()
        quota_manager = QuotaManager()
        fallback_handler = FallbackHandler()

        client = LLMClient(
            config=LLMConfig(enable_quota=False),  # Disable quota for simpler tests
            circuit_breaker=circuit_breaker,
            quota_manager=quota_manager,
            fallback_handler=fallback_handler,
        )
        return client

    def test_create_client(self, client):
        """Test creating client."""
        assert client is not None
        assert client.config.provider == LLMProvider.STUB

    def test_initialize(self, client):
        """Test initializing client."""
        client.initialize()
        assert client._initialized is True

    def test_initialize_idempotent(self, client):
        """Test initialize is idempotent."""
        client.initialize()
        client.initialize()  # Should not raise
        assert client._initialized is True

    def test_generate_stub(self, client):
        """Test generating with stub provider."""
        request = LLMRequest(prompt="What is AI?")

        response = client.generate(request)

        assert response.content.startswith("[STUB]")
        assert response.provider == LLMProvider.STUB

    def test_generate_uses_default_model(self, client):
        """Test generate uses default model when not specified."""
        request = LLMRequest(prompt="Test")

        response = client.generate(request)

        assert response.model == client.config.default_model

    def test_generate_uses_specified_model(self, client):
        """Test generate uses specified model."""
        request = LLMRequest(prompt="Test", model="custom-model")

        # Need custom provider that returns the model
        def custom_provider(req):
            return LLMResponse(
                content="Response",
                model=req.model,
                provider=LLMProvider.STUB,
                input_tokens=10,
                output_tokens=10,
                total_tokens=20,
                latency_ms=10.0,
            )

        client.set_provider_function(custom_provider)
        response = client.generate(request)

        assert response.model == "custom-model"

    def test_generate_tracks_stats(self, client):
        """Test generate tracks statistics."""
        request = LLMRequest(prompt="Test")

        client.generate(request)
        client.generate(request)

        stats = client.get_stats()
        assert stats.total_requests == 2
        assert stats.successful_requests == 2

    def test_generate_with_quota(self):
        """Test generate respects quota."""
        quota_manager = QuotaManager()
        client = LLMClient(
            config=LLMConfig(
                enable_quota=True,
                default_token_quota=100,  # Very low quota
                enable_fallback=False,
            ),
            quota_manager=quota_manager,
        )

        request = LLMRequest(prompt="Test " * 100, max_tokens=1000)  # Will exceed quota

        with pytest.raises(QuotaExceededError):
            client.generate(request)

    def test_generate_circuit_open(self):
        """Test generate handles circuit open."""
        circuit_breaker = CircuitBreaker()
        circuit_breaker.configure("llm_stub", failure_threshold=1)

        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=True,
                enable_fallback=False,
            ),
            circuit_breaker=circuit_breaker,
        )
        client.initialize()

        # Force circuit open
        circuit_breaker.force_open("llm_stub")

        request = LLMRequest(prompt="Test")

        with pytest.raises(CircuitBreakerError):
            client.generate(request)

    def test_generate_with_fallback(self):
        """Test generate uses fallback on failure."""
        fallback_handler = FallbackHandler()
        fallback_handler.cache_response("Test prompt", "gpt-3.5-turbo", "Cached response")

        circuit_breaker = CircuitBreaker()
        circuit_breaker.configure("llm_stub", failure_threshold=1)

        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=True,
                enable_fallback=True,
                enable_quota=False,
            ),
            circuit_breaker=circuit_breaker,
            fallback_handler=fallback_handler,
        )
        client.initialize()

        # Force circuit open
        circuit_breaker.force_open("llm_stub")

        request = LLMRequest(prompt="Test prompt")
        response = client.generate(request)

        assert response.from_fallback is True

    def test_generate_provider_error_with_fallback(self):
        """Test generate handles provider error with fallback."""
        def failing_provider(req):
            raise Exception("Provider error")

        fallback_handler = FallbackHandler()
        fallback_handler.register_degraded_response("default", lambda: "Degraded")

        client = LLMClient(
            config=LLMConfig(
                enable_fallback=True,
                enable_quota=False,
            ),
            fallback_handler=fallback_handler,
            provider_fn=failing_provider,
        )

        request = LLMRequest(prompt="Test")
        response = client.generate(request)

        assert response.from_fallback is True

    def test_generate_provider_error_no_fallback(self):
        """Test generate raises on provider error without fallback."""
        def failing_provider(req):
            raise Exception("Provider error")

        client = LLMClient(
            config=LLMConfig(enable_fallback=False, enable_quota=False),
            provider_fn=failing_provider,
        )

        request = LLMRequest(prompt="Test")

        with pytest.raises(Exception, match="Provider error"):
            client.generate(request)

    def test_get_circuit_status(self, client):
        """Test getting circuit breaker status."""
        client.initialize()
        status = client.get_circuit_status()

        assert "state" in status

    def test_get_quota_status(self, client):
        """Test getting quota status."""
        status = client.get_quota_status()

        assert "limits" in status
        assert "usage" in status

    def test_is_healthy(self, client):
        """Test health check."""
        client.initialize()
        assert client.is_healthy() is True

    def test_is_healthy_circuit_open(self, client):
        """Test health check when circuit open."""
        client.initialize()
        client.circuit_breaker.force_open("llm_stub")

        assert client.is_healthy() is False

    def test_reset_circuit(self, client):
        """Test resetting circuit breaker."""
        client.initialize()
        client.circuit_breaker.force_open("llm_stub")

        client.reset_circuit()

        assert client.is_healthy() is True

    def test_set_provider_function(self, client):
        """Test setting custom provider function."""
        def custom_provider(req):
            return LLMResponse(
                content="Custom response",
                model="custom",
                provider=LLMProvider.LOCAL,
                input_tokens=5,
                output_tokens=5,
                total_tokens=10,
                latency_ms=5.0,
            )

        client.set_provider_function(custom_provider)

        request = LLMRequest(prompt="Test")
        response = client.generate(request)

        assert response.content == "Custom response"
        assert response.provider == LLMProvider.LOCAL

    def test_stats_by_model(self, client):
        """Test stats track by model."""
        def provider(req):
            return LLMResponse(
                content="Response",
                model=req.model or "default",
                provider=LLMProvider.STUB,
                input_tokens=10,
                output_tokens=10,
                total_tokens=20,
                latency_ms=10.0,
            )

        client.set_provider_function(provider)

        client.generate(LLMRequest(prompt="Test", model="model-a"))
        client.generate(LLMRequest(prompt="Test", model="model-b"))
        client.generate(LLMRequest(prompt="Test", model="model-a"))

        stats = client.get_stats()
        assert stats.by_model["model-a"] == 2
        assert stats.by_model["model-b"] == 1

    def test_stats_failed_requests(self):
        """Test stats track failed requests."""
        def failing_provider(req):
            raise Exception("Error")

        fallback_handler = FallbackHandler()
        fallback_handler.configure(
            __import__("app.llm.fallback", fromlist=["FallbackConfig"]).FallbackConfig(
                strategies=[]  # No fallback strategies
            )
        )

        client = LLMClient(
            config=LLMConfig(enable_fallback=True, enable_quota=False),
            provider_fn=failing_provider,
            fallback_handler=fallback_handler,
        )

        with pytest.raises(RuntimeError):
            client.generate(LLMRequest(prompt="Test"))

        stats = client.get_stats()
        # 2 failures: one from provider error, one from failed fallback
        assert stats.failed_requests == 2

    def test_caches_successful_response(self, client):
        """Test successful responses are cached."""
        def provider(req):
            return LLMResponse(
                content="Response",
                model="gpt-4",
                provider=LLMProvider.STUB,
                input_tokens=10,
                output_tokens=10,
                total_tokens=20,
                latency_ms=10.0,
            )

        client.set_provider_function(provider)
        client.generate(LLMRequest(prompt="Cacheable prompt"))

        # Check cache has the response
        cached = client.fallback_handler.cache.get("Cacheable prompt", "gpt-3.5-turbo")
        assert cached is not None

    def test_records_circuit_success(self, client):
        """Test successful request records success with circuit breaker."""
        client.initialize()

        # Generate some failures first
        provider_id = f"llm_{client.config.provider.value}"
        client.circuit_breaker.record_failure(provider_id)
        client.circuit_breaker.record_failure(provider_id)

        # Successful request should reset failure count
        client.generate(LLMRequest(prompt="Test"))

        stats = client.circuit_breaker.get_stats(provider_id)
        assert stats["failure_count"] == 0

    def test_records_circuit_failure(self):
        """Test failed request records failure with circuit breaker."""
        def failing_provider(req):
            raise Exception("Error")

        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=True,
                enable_fallback=False,
                enable_quota=False,
            ),
            provider_fn=failing_provider,
        )
        client.initialize()

        try:
            client.generate(LLMRequest(prompt="Test"))
        except Exception:
            pass

        provider_id = f"llm_{client.config.provider.value}"
        stats = client.circuit_breaker.get_stats(provider_id)
        assert stats["failure_count"] == 1


class TestLLMClientCoverage:
    """Additional tests for full coverage."""

    def test_quota_exceeded_with_fallback(self):
        """Test quota exceeded triggers fallback."""
        from app.llm.quota import QuotaLimit

        quota_manager = QuotaManager()
        quota_manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=10,  # Very low limit
            window_seconds=3600,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
        ))

        fallback_handler = FallbackHandler()
        fallback_handler.cache_response("Test prompt", "gpt-3.5-turbo", "Cached")

        client = LLMClient(
            config=LLMConfig(
                enable_quota=True,
                enable_fallback=True,
                default_token_quota=10,  # Low quota
            ),
            quota_manager=quota_manager,
            fallback_handler=fallback_handler,
        )
        client._initialized = True  # Skip initialization

        request = LLMRequest(prompt="Test prompt", max_tokens=1000)
        response = client.generate(request)

        assert response.from_fallback is True
        assert response.fallback_reason == "quota_exceeded"

    def test_token_adjustment_when_actual_exceeds_estimated(self):
        """Test token quota adjustment when actual > estimated."""
        from app.llm.quota import QuotaLimit

        quota_manager = QuotaManager()
        quota_manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            window_seconds=3600,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
        ))

        def provider_with_high_tokens(req):
            return LLMResponse(
                content="Response",
                model=req.model or "gpt-3.5-turbo",
                provider=LLMProvider.STUB,
                input_tokens=5000,  # High token count
                output_tokens=5000,
                total_tokens=10000,  # Much higher than estimated
                latency_ms=10.0,
            )

        client = LLMClient(
            config=LLMConfig(enable_quota=True, enable_circuit_breaker=False),
            quota_manager=quota_manager,
            provider_fn=provider_with_high_tokens,
        )
        client._initialized = True

        request = LLMRequest(prompt="Short", max_tokens=100)  # Low estimate
        response = client.generate(request)

        assert response.total_tokens == 10000

    def test_circuit_breaker_disabled(self):
        """Test with circuit breaker disabled."""
        def provider(req):
            return LLMResponse(
                content="Response",
                model="model",
                provider=LLMProvider.STUB,
                input_tokens=10,
                output_tokens=10,
                total_tokens=20,
                latency_ms=10.0,
            )

        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=False,
                enable_quota=False,
            ),
            provider_fn=provider,
        )

        response = client.generate(LLMRequest(prompt="Test"))
        assert response.content == "Response"

    def test_quota_disabled_circuit_enabled(self):
        """Test with quota disabled but circuit enabled."""
        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=True,
                enable_quota=False,
            ),
        )
        client.initialize()

        response = client.generate(LLMRequest(prompt="Test"))
        assert response is not None

    def test_get_circuit_status_not_configured(self):
        """Test circuit status when provider not configured."""
        client = LLMClient()
        # Don't initialize - circuit breaker returns None for unknown source
        status = client.get_circuit_status()
        # When not configured, get_stats returns None, so we return {"state": "unknown"}
        # But circuit breaker always returns closed for unknown sources
        assert "state" in status or status == {"state": "unknown"}

    def test_fallback_increments_stats(self):
        """Test fallback properly increments stats."""
        fallback_handler = FallbackHandler()
        fallback_handler.cache_response("prompt", "gpt-3.5-turbo", "cached")

        circuit_breaker = CircuitBreaker()
        circuit_breaker.configure("llm_stub", failure_threshold=1)
        circuit_breaker.force_open("llm_stub")

        client = LLMClient(
            config=LLMConfig(
                enable_circuit_breaker=True,
                enable_fallback=True,
                enable_quota=False,
            ),
            circuit_breaker=circuit_breaker,
            fallback_handler=fallback_handler,
        )
        client._initialized = True

        response = client.generate(LLMRequest(prompt="prompt"))

        stats = client.get_stats()
        assert stats.fallback_requests == 1
        assert response.from_cache is True

    def test_estimate_tokens_with_system_prompt(self):
        """Test token estimation includes system prompt."""
        client = LLMClient(config=LLMConfig(enable_quota=False))

        request_without = LLMRequest(prompt="Hello world", max_tokens=100)
        request_with = LLMRequest(
            prompt="Hello world",
            max_tokens=100,
            system_prompt="You are a helpful assistant that explains things clearly.",
        )

        estimate_without = client._estimate_tokens(request_without)
        estimate_with = client._estimate_tokens(request_with)

        assert estimate_with > estimate_without


class TestSingleton:
    """Tests for singleton functions."""

    def test_get_llm_client(self):
        """Test getting singleton."""
        reset_llm_client()
        client1 = get_llm_client()
        client2 = get_llm_client()

        assert client1 is client2

    def test_reset_llm_client(self):
        """Test resetting singleton."""
        client1 = get_llm_client()
        reset_llm_client()
        client2 = get_llm_client()

        assert client1 is not client2
