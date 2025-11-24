from __future__ import annotations

import time
import urllib.request
from typing import Optional

from .models import SourceHealthStatus
from .service import get_source_detail, register_healthcheck


def run_healthcheck(source_id: str) -> Optional[dict]:
    """Executa um health-check simples baseado no endpoint da fonte."""
    source = get_source_detail(source_id)
    if not source:
        return None
    start = time.perf_counter()
    status = SourceHealthStatus.OK
    error = None
    endpoint = source.endpoint or source.meta.get("url_base", source.endpoint)

    # Suporte a endpoints mock para ambientes sem rede
    if endpoint and endpoint.startswith("mock://"):
        marker = endpoint.replace("mock://", "")
        if marker == "fail":
            status = SourceHealthStatus.FAIL
            error = "mock failure"
        elif marker == "degraded":
            status = SourceHealthStatus.DEGRADED
        latency_ms = int((time.perf_counter() - start) * 1000)
        check = register_healthcheck(source_id, status=status, latency_ms=latency_ms, error=error)
        return check.__dict__

    try:
        req = urllib.request.Request(endpoint, method="GET")
        req.add_header("User-Agent", "Inspectah-Healthcheck")
        if source.auth_type != "none":
            req.add_header("X-Auth-Type", source.auth_type)
        with urllib.request.urlopen(req, timeout=max(1, source.timeout_ms / 1000)) as resp:  # nosec B310
            if getattr(resp, "status", 200) >= 500:
                status = SourceHealthStatus.DEGRADED
            if getattr(resp, "status", 200) >= 400:
                status = SourceHealthStatus.FAIL
    except Exception as exc:  # pragma: no cover - robustez
        status = SourceHealthStatus.FAIL
        error = str(exc)
    latency_ms = int((time.perf_counter() - start) * 1000)
    check = register_healthcheck(source_id, status=status, latency_ms=latency_ms, error=error)
    return check.__dict__
