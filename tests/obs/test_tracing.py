"""
S39-W4: Tests for OpenTelemetry Tracing (T-OBS-TRACE-001)

Tests for the distributed tracing module.
"""

import pytest
from unittest.mock import MagicMock, patch

# Mock OpenTelemetry before importing the module
import sys

# Create mock modules
mock_trace = MagicMock()
mock_trace.StatusCode = MagicMock()
mock_trace.StatusCode.ERROR = 'ERROR'
mock_trace.StatusCode.OK = 'OK'
mock_trace.Status = MagicMock()

class MockSpanContext:
    is_valid = True
    trace_id = 0x1234567890abcdef1234567890abcdef
    span_id = 0x1234567890abcdef
    trace_flags = 1

mock_span = MagicMock()
mock_span.is_recording.return_value = True
mock_span.get_span_context.return_value = MockSpanContext()

mock_tracer = MagicMock()
mock_tracer.start_as_current_span.return_value.__enter__ = MagicMock(return_value=mock_span)
mock_tracer.start_as_current_span.return_value.__exit__ = MagicMock(return_value=False)

mock_trace.get_tracer.return_value = mock_tracer
mock_trace.get_current_span.return_value = mock_span
mock_trace.set_tracer_provider = MagicMock()

# Patch the modules
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = mock_trace
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()
sys.modules['opentelemetry.exporter'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()
sys.modules['opentelemetry.instrumentation'] = MagicMock()
sys.modules['opentelemetry.instrumentation.fastapi'] = MagicMock()
sys.modules['opentelemetry.instrumentation.httpx'] = MagicMock()
sys.modules['opentelemetry.instrumentation.sqlalchemy'] = MagicMock()
sys.modules['opentelemetry.instrumentation.redis'] = MagicMock()
sys.modules['opentelemetry.propagate'] = MagicMock()
sys.modules['opentelemetry.propagators'] = MagicMock()
sys.modules['opentelemetry.propagators.b3'] = MagicMock()


class TestTracingSetup:
    """Tests for tracing setup functions."""

    def test_setup_tracing_returns_tracer(self):
        """Test that setup_tracing returns a tracer instance."""
        from app.observability.tracing import setup_tracing

        tracer = setup_tracing()
        assert tracer is not None

    def test_get_tracer_returns_tracer(self):
        """Test that get_tracer returns a tracer instance."""
        from app.observability.tracing import get_tracer

        tracer = get_tracer()
        assert tracer is not None


class TestTraceSpan:
    """Tests for trace_span context manager."""

    def test_trace_span_creates_span(self):
        """Test that trace_span creates a span."""
        from app.observability.tracing import trace_span

        with trace_span("test_operation") as span:
            assert span is not None

    def test_trace_span_with_attributes(self):
        """Test trace_span with attributes."""
        from app.observability.tracing import trace_span

        attributes = {"key": "value", "number": 42}
        with trace_span("test_operation", attributes):
            pass

    def test_trace_span_handles_exception(self):
        """Test that trace_span handles exceptions properly."""
        from app.observability.tracing import trace_span

        with pytest.raises(ValueError):
            with trace_span("failing_operation"):
                raise ValueError("Test error")


class TestSpanHelpers:
    """Tests for span helper functions."""

    def test_add_span_attribute(self):
        """Test adding attribute to current span."""
        from app.observability.tracing import add_span_attribute

        add_span_attribute("test_key", "test_value")
        # Should not raise

    def test_add_span_event(self):
        """Test adding event to current span."""
        from app.observability.tracing import add_span_event

        add_span_event("test_event", {"key": "value"})
        # Should not raise

    def test_add_span_event_without_attributes(self):
        """Test adding event without attributes."""
        from app.observability.tracing import add_span_event

        add_span_event("simple_event")
        # Should not raise

    def test_set_span_error(self):
        """Test setting span error status."""
        from app.observability.tracing import set_span_error

        error = Exception("Test error")
        set_span_error(error)
        # Should not raise


class TestTraceDecorators:
    """Tests for trace decorators."""

    def test_trace_claim_processing_decorator(self):
        """Test trace_claim_processing decorator."""
        from app.observability.tracing import trace_claim_processing

        @trace_claim_processing
        def process_claim(claim_id: str):
            return f"processed_{claim_id}"

        result = process_claim("claim_123")
        assert result == "processed_claim_123"

    def test_trace_signal_update_decorator(self):
        """Test trace_signal_update decorator."""
        from app.observability.tracing import trace_signal_update

        @trace_signal_update
        def update_signal(signal_id: str):
            return f"updated_{signal_id}"

        result = update_signal("signal_456")
        assert result == "updated_signal_456"

    def test_trace_explanation_generation_decorator(self):
        """Test trace_explanation_generation decorator."""
        from app.observability.tracing import trace_explanation_generation

        @trace_explanation_generation
        def generate_explanation(claim_id: str):
            return {"claim_id": claim_id, "explanation": "test"}

        result = generate_explanation("claim_789")
        assert result["claim_id"] == "claim_789"

    def test_trace_llm_call_decorator(self):
        """Test trace_llm_call decorator."""
        from app.observability.tracing import trace_llm_call

        @trace_llm_call
        def call_llm(model: str = "gpt-4"):
            result = MagicMock()
            result.usage = MagicMock(total_tokens=100)
            return result

        result = call_llm(model="gpt-4")
        assert result is not None

    def test_trace_db_query_decorator(self):
        """Test trace_db_query decorator."""
        from app.observability.tracing import trace_db_query

        @trace_db_query
        def run_query(query_type: str = "select", shard: int = 0):
            return {"rows": []}

        result = run_query(query_type="select", shard=1)
        assert result["rows"] == []

    def test_trace_kafka_publish_decorator(self):
        """Test trace_kafka_publish decorator."""
        from app.observability.tracing import trace_kafka_publish

        @trace_kafka_publish
        def publish_message(topic: str):
            return True

        result = publish_message("signals")
        assert result is True

    def test_trace_websocket_message_decorator(self):
        """Test trace_websocket_message decorator."""
        from app.observability.tracing import trace_websocket_message

        @trace_websocket_message
        def handle_message(message_type: str = "signal_update"):
            return {"handled": True}

        result = handle_message(message_type="signal_update")
        assert result["handled"] is True


class TestTraceContextUtils:
    """Tests for trace context utilities."""

    def test_get_trace_context_with_patch(self):
        """Test getting trace context with patched span."""
        from app.observability.tracing import get_trace_context

        # The function should return a dict (empty or with context)
        with patch('app.observability.tracing.trace') as mock_trace:
            mock_ctx = MagicMock()
            mock_ctx.is_valid = False
            mock_span = MagicMock()
            mock_span.get_span_context.return_value = mock_ctx
            mock_trace.get_current_span.return_value = mock_span

            ctx = get_trace_context()
            assert isinstance(ctx, dict)

    def test_get_trace_context_with_valid_span(self):
        """Test getting trace context with valid span."""
        from app.observability.tracing import get_trace_context

        with patch('app.observability.tracing.trace') as mock_trace:
            mock_ctx = MagicMock()
            mock_ctx.is_valid = True
            mock_ctx.trace_id = 0x1234567890abcdef1234567890abcdef
            mock_ctx.span_id = 0x1234567890abcdef
            mock_ctx.trace_flags = 1
            mock_span = MagicMock()
            mock_span.get_span_context.return_value = mock_ctx
            mock_trace.get_current_span.return_value = mock_span

            ctx = get_trace_context()
            assert isinstance(ctx, dict)
            assert "trace_id" in ctx
            assert "span_id" in ctx
            assert "trace_flags" in ctx

    def test_inject_trace_headers(self):
        """Test injecting trace headers."""
        from app.observability.tracing import inject_trace_headers

        with patch('app.observability.tracing.get_trace_context') as mock_get_ctx:
            mock_get_ctx.return_value = {
                "trace_id": "1234567890abcdef1234567890abcdef",
                "span_id": "1234567890abcdef",
                "trace_flags": 1,
            }

            headers = {"Authorization": "Bearer token"}
            result = inject_trace_headers(headers)

            assert "Authorization" in result
            assert "X-B3-TraceId" in result
            assert "X-B3-SpanId" in result

    def test_inject_trace_headers_empty_context(self):
        """Test injecting trace headers with empty context."""
        from app.observability.tracing import inject_trace_headers

        with patch('app.observability.tracing.get_trace_context') as mock_get_ctx:
            mock_get_ctx.return_value = {}

            headers = {"Authorization": "Bearer token"}
            result = inject_trace_headers(headers)

            assert "Authorization" in result
            # No B3 headers since context is empty
            assert "X-B3-TraceId" not in result


class TestTracingConfiguration:
    """Tests for tracing configuration."""

    def test_tracing_module_constants(self):
        """Test that tracing module has expected constants."""
        from app.observability import tracing

        assert hasattr(tracing, 'OTLP_ENDPOINT')
        assert hasattr(tracing, 'SERVICE_NAME_VALUE')
        assert hasattr(tracing, 'SERVICE_VERSION_VALUE')
        assert hasattr(tracing, 'ENVIRONMENT')

    def test_service_name_default(self):
        """Test default service name."""
        from app.observability import tracing

        assert tracing.SERVICE_NAME_VALUE == "inspectah-api"

    def test_service_version_default(self):
        """Test default service version."""
        from app.observability import tracing

        assert tracing.SERVICE_VERSION_VALUE == "s39"
