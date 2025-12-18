"""
S39-W4: OpenTelemetry Tracing Setup (T-OBS-TRACE-001)

Distributed tracing configuration for the Inspectah API.
"""

import os
from typing import Optional
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

# Configuration
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "localhost:4317")
SERVICE_NAME_VALUE = os.getenv("SERVICE_NAME", "inspectah-api")
SERVICE_VERSION_VALUE = os.getenv("SERVICE_VERSION", "s39")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Global tracer
_tracer: Optional[trace.Tracer] = None


def setup_tracing(app=None, engine=None, redis_client=None) -> trace.Tracer:
    """
    Initialize OpenTelemetry tracing.

    Args:
        app: FastAPI application instance
        engine: SQLAlchemy engine for DB tracing
        redis_client: Redis client for cache tracing

    Returns:
        Configured tracer instance
    """
    global _tracer

    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: SERVICE_NAME_VALUE,
        SERVICE_VERSION: SERVICE_VERSION_VALUE,
        "deployment.environment": ENVIRONMENT,
        "sprint": "s39",
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    if os.getenv("TRACING_ENABLED", "true").lower() == "true":
        exporter = OTLPSpanExporter(
            endpoint=OTLP_ENDPOINT,
            insecure=ENVIRONMENT == "development",
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    # Set as global provider
    trace.set_tracer_provider(provider)

    # Set up B3 propagation for cross-service tracing
    set_global_textmap(B3MultiFormat())

    # Instrument FastAPI if provided
    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    # Instrument HTTP clients
    HTTPXClientInstrumentor().instrument()

    # Instrument SQLAlchemy if engine provided
    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine)

    # Instrument Redis if client provided
    if redis_client is not None:
        RedisInstrumentor().instrument()

    # Get tracer
    _tracer = trace.get_tracer(SERVICE_NAME_VALUE, SERVICE_VERSION_VALUE)

    return _tracer


def get_tracer() -> trace.Tracer:
    """Get the configured tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer(SERVICE_NAME_VALUE, SERVICE_VERSION_VALUE)
    return _tracer


@contextmanager
def trace_span(name: str, attributes: Optional[dict] = None):
    """
    Context manager for creating trace spans.

    Usage:
        with trace_span("process_claim", {"claim_id": claim_id}):
            # processing logic
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        try:
            yield span
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def add_span_attribute(key: str, value):
    """Add attribute to current span."""
    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict] = None):
    """Add event to current span."""
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


def set_span_error(error: Exception):
    """Mark current span as error."""
    span = trace.get_current_span()
    if span:
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))
        span.record_exception(error)


# Custom span decorators for common operations
def trace_claim_processing(func):
    """Decorator for tracing claim processing functions."""
    def wrapper(*args, **kwargs):
        claim_id = kwargs.get("claim_id") or (args[0] if args else "unknown")
        with trace_span("claim.process", {"claim.id": claim_id}):
            return func(*args, **kwargs)
    return wrapper


def trace_signal_update(func):
    """Decorator for tracing signal update functions."""
    def wrapper(*args, **kwargs):
        signal_id = kwargs.get("signal_id") or (args[0] if args else "unknown")
        with trace_span("signal.update", {"signal.id": signal_id}):
            return func(*args, **kwargs)
    return wrapper


def trace_explanation_generation(func):
    """Decorator for tracing explanation generation."""
    def wrapper(*args, **kwargs):
        claim_id = kwargs.get("claim_id") or (args[0] if args else "unknown")
        with trace_span("explanation.generate", {"claim.id": claim_id}):
            return func(*args, **kwargs)
    return wrapper


def trace_llm_call(func):
    """Decorator for tracing LLM API calls."""
    def wrapper(*args, **kwargs):
        model = kwargs.get("model", "unknown")
        with trace_span("llm.call", {"llm.model": model}) as span:
            result = func(*args, **kwargs)
            if hasattr(result, "usage"):
                span.set_attribute("llm.tokens_used", result.usage.total_tokens)
            return result
    return wrapper


def trace_db_query(func):
    """Decorator for tracing database queries."""
    def wrapper(*args, **kwargs):
        query_type = kwargs.get("query_type", "select")
        shard = kwargs.get("shard", 0)
        with trace_span("db.query", {"db.query_type": query_type, "db.shard": shard}):
            return func(*args, **kwargs)
    return wrapper


def trace_kafka_publish(func):
    """Decorator for tracing Kafka message publishing."""
    def wrapper(*args, **kwargs):
        topic = kwargs.get("topic") or (args[0] if args else "unknown")
        with trace_span("kafka.publish", {"kafka.topic": topic}):
            return func(*args, **kwargs)
    return wrapper


def trace_websocket_message(func):
    """Decorator for tracing WebSocket message handling."""
    def wrapper(*args, **kwargs):
        message_type = kwargs.get("message_type", "unknown")
        with trace_span("websocket.message", {"websocket.message_type": message_type}):
            return func(*args, **kwargs)
    return wrapper


# Span context utilities
def get_trace_context() -> dict:
    """Get current trace context for propagation."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        ctx = span.get_span_context()
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
            "trace_flags": ctx.trace_flags,
        }
    return {}


def inject_trace_headers(headers: dict) -> dict:
    """Inject trace context into HTTP headers for propagation."""
    ctx = get_trace_context()
    if ctx:
        headers["X-B3-TraceId"] = ctx["trace_id"]
        headers["X-B3-SpanId"] = ctx["span_id"]
        headers["X-B3-Sampled"] = "1" if ctx["trace_flags"] else "0"
    return headers
