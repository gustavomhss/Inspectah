"""
Métricas auxiliares para SF3 (admin/ingest/ui) com pré-semeadura para /metrics.
"""

from __future__ import annotations

import time

from prometheus_client import Counter, Gauge

# Admin/UI metrics
_admin_requests = Counter(
    "admin_ui_requests_total",
    "Total de requisições da UI/Admin por rota/status",
    ["route", "status"],
)
_admin_dashboard_age = Gauge(
    "dashboard_freshness_seconds",
    "Freshness (seconds) de painéis",
    ["dashboard"],
)


def record_admin_request(route: str, status: int) -> None:
    _admin_requests.labels(route=route, status=str(status)).inc()
    if route.startswith("/admin"):
        _admin_dashboard_age.labels(dashboard="sf3_obs_overview").set(0)


def seed_defaults() -> None:
    """
    Pré-cria séries para evitar painéis/alertas vazios.
    """
    _admin_requests.labels(route="/admin/health", status="200").inc(0)
    _admin_dashboard_age.labels(dashboard="sf3_obs_overview").set(0)


# Semeia ao importar
seed_defaults()
