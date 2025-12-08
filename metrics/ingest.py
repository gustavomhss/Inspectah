from __future__ import annotations

from prometheus_client import Counter, Histogram

_requests = Counter(
    "ingest_requests_total",
    "Total de requisições de ingestão por status/fonte",
    ["status", "source"],
)
_errors = Counter(
    "ingest_errors_total",
    "Total de erros de ingestão por tipo/fonte",
    ["type", "source"],
)
_items = Counter(
    "ingest_items_ingested_total",
    "Total de itens ingeridos por fonte",
    ["source"],
)
_duration = Histogram(
    "ingest_duration_seconds",
    "Duração por requisição de ingestão",
    ["source"],
    buckets=(0.1, 0.5, 1, 2, 5, 10),
)


def record_request(status: str, source: str, duration_seconds: float | None = None) -> None:
    _requests.labels(status=status, source=source).inc()
    if duration_seconds is not None:
        _duration.labels(source=source).observe(duration_seconds)


def record_error(error_type: str, source: str) -> None:
    _errors.labels(type=error_type, source=source).inc()


def record_items(source: str, count: int) -> None:
    if count > 0:
        _items.labels(source=source).inc(count)
