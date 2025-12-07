from __future__ import annotations

from typing import Dict

from prometheus_client import Counter, Histogram

# Métricas de ingestão newsdata.io
_requests_total = Counter(
    "newsdata_ingest_requests_total",
    "Total de requisições ao newsdata.io",
    ["source_id", "status"],
)
_errors_total = Counter(
    "newsdata_ingest_errors_total",
    "Total de erros na ingestão newsdata.io por tipo",
    ["source_id", "type"],
)
_duration_seconds = Histogram(
    "newsdata_ingest_duration_seconds",
    "Latência por requisição ao newsdata.io",
    ["source_id"],
)
_items_ingested_total = Counter(
    "newsdata_items_ingested_total",
    "Total de itens ingeridos a partir do newsdata.io",
    ["source_id"],
)


def record_request(source_id: str, status: str, duration_seconds: float | None = None) -> None:
    _requests_total.labels(source_id=source_id, status=status).inc()
    if duration_seconds is not None:
        _duration_seconds.labels(source_id=source_id).observe(duration_seconds)


def record_items(source_id: str, count: int) -> None:
    if count <= 0:
        return
    _items_ingested_total.labels(source_id=source_id).inc(count)


def record_error(source_id: str, error_type: str) -> None:
    _errors_total.labels(source_id=source_id, type=error_type).inc()


def snapshot() -> Dict[str, Dict[str, int]]:
    return {
        "requests_total": {
            f"{sample.labels['source_id']}|{sample.labels['status']}": int(sample.value)
            for sample in _requests_total.collect()[0].samples
        },
        "errors_total": {
            f"{sample.labels['source_id']}|{sample.labels['type']}": int(sample.value)
            for sample in _errors_total.collect()[0].samples
        },
    }
