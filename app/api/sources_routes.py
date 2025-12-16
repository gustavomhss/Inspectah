"""
S38-BE-010: API CRUD de Fontes

APIs para gerenciamento de fontes de dados:
- CRUD de fontes
- Dry-run para testar configuracao
- Trigger de ingestao
- Metricas de performance
- Historico de ingestao
- Health check por fonte
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.ingestion.health_monitor import HealthStatus, get_health_monitor

logger = logging.getLogger(__name__)
from app.ingestion.rate_limiter import get_rate_limiter
from app.ingestion.circuit_breaker import get_circuit_breaker


# =============================================================================
# Schemas
# =============================================================================

class SourceBase(BaseModel):
    """Schema base de fonte."""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_-]+$")
    source_type: str = Field(..., description="official, scraper, rss, api")
    url: str = Field(..., min_length=1)
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    rate_limit_rpm: int = Field(default=10, ge=1, le=100)
    enabled: bool = True


class SourceCreate(SourceBase):
    """Schema para criar fonte."""
    pass


class SourceUpdate(BaseModel):
    """Schema para atualizar fonte."""
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    rate_limit_rpm: Optional[int] = Field(default=None, ge=1, le=100)
    enabled: Optional[bool] = None


class SourceResponse(SourceBase):
    """Schema de resposta de fonte."""
    id: str
    state: str = "PROPOSED"
    last_health_status: str = "UNKNOWN"
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str = "system"

    class Config:
        from_attributes = True


class SourceDetailResponse(SourceResponse):
    """Schema de resposta detalhada de fonte."""
    health_stats: Optional[Dict[str, Any]] = None
    rate_limit_stats: Optional[Dict[str, Any]] = None
    circuit_breaker_stats: Optional[Dict[str, Any]] = None
    recent_runs: List[Dict[str, Any]] = Field(default_factory=list)


class DryRunRequest(BaseModel):
    """Schema para dry-run de fonte."""
    url: Optional[str] = None  # Override da URL
    limit: int = Field(default=5, ge=1, le=20)


class DryRunResponse(BaseModel):
    """Resultado do dry-run."""
    success: bool
    source_id: str
    documents_found: int
    sample_documents: List[Dict[str, Any]]
    latency_ms: float
    error_message: Optional[str] = None


class TriggerIngestionRequest(BaseModel):
    """Schema para trigger de ingestao."""
    force: bool = False
    limit: Optional[int] = Field(default=None, ge=1, le=1000)


class TriggerIngestionResponse(BaseModel):
    """Resultado do trigger de ingestao."""
    run_id: str
    status: str
    triggered_at: datetime


class SourceMetricsResponse(BaseModel):
    """Metricas de uma fonte."""
    source_id: str
    period: str  # 1h, 24h, 7d
    total_documents: int
    documents_per_hour: float
    avg_latency_ms: float
    success_rate: float
    error_count: int
    last_ingestion: Optional[datetime]


class IngestionHistoryItem(BaseModel):
    """Item do historico de ingestao."""
    run_id: str
    status: str
    trigger: str
    started_at: datetime
    finished_at: Optional[datetime]
    documents_processed: int
    error_message: Optional[str]
    duration_seconds: Optional[float]


class IngestionHistoryResponse(BaseModel):
    """Resposta do historico de ingestao."""
    source_id: str
    runs: List[IngestionHistoryItem]
    pagination: Dict[str, int]


class HealthCheckResponse(BaseModel):
    """Resposta do health check."""
    source_id: str
    status: str
    latency_ms: float
    checked_at: datetime
    consecutive_successes: int
    consecutive_failures: int
    uptime_percent: float
    error_message: Optional[str] = None


# =============================================================================
# In-Memory Store (placeholder para repository real)
# =============================================================================

_sources_store: Dict[str, Dict[str, Any]] = {}
_runs_store: Dict[str, List[Dict[str, Any]]] = {}


def _generate_id() -> str:
    import uuid
    return f"src_{uuid.uuid4().hex[:12]}"


def _generate_run_id() -> str:
    import uuid
    return f"run_{uuid.uuid4().hex[:12]}"


# =============================================================================
# Router
# =============================================================================

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
def list_sources(
    source_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    state: Optional[str] = Query(None, description="Filtrar por estado"),
    enabled: Optional[bool] = Query(None, description="Filtrar por habilitado"),
    q: Optional[str] = Query(None, description="Busca por nome/slug"),
) -> List[SourceResponse]:
    """Lista todas as fontes com filtros opcionais."""
    sources = list(_sources_store.values())

    if source_type:
        sources = [s for s in sources if s.get("source_type") == source_type]
    if state:
        sources = [s for s in sources if s.get("state") == state]
    if enabled is not None:
        sources = [s for s in sources if s.get("enabled") == enabled]
    if q:
        q_lower = q.lower()
        sources = [
            s for s in sources
            if q_lower in s.get("name", "").lower() or q_lower in s.get("slug", "").lower()
        ]

    return [SourceResponse(**s) for s in sources]


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate) -> SourceResponse:
    """Cria uma nova fonte."""
    # Verificar slug unico
    for s in _sources_store.values():
        if s.get("slug") == payload.slug:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Source with slug '{payload.slug}' already exists"
            )

    now = datetime.now(timezone.utc)
    source_id = _generate_id()

    source = {
        "id": source_id,
        **payload.model_dump(),
        "state": "PROPOSED",
        "last_health_status": "UNKNOWN",
        "last_health_check": None,
        "created_at": now,
        "updated_at": now,
        "created_by": "admin",
    }

    _sources_store[source_id] = source
    _runs_store[source_id] = []

    # Configurar rate limiter e health monitor
    rate_limiter = get_rate_limiter()
    rate_limiter.configure(source_id, requests_per_minute=payload.rate_limit_rpm)

    health_monitor = get_health_monitor()
    health_monitor.register_source(
        source_id=source_id,
        probe_url=payload.url,
        interval_seconds=300,
    )

    return SourceResponse(**source)


@router.get("/{source_id}", response_model=SourceDetailResponse)
def get_source(source_id: str) -> SourceDetailResponse:
    """Retorna detalhes de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    # Agregar stats
    health_monitor = get_health_monitor()
    rate_limiter = get_rate_limiter()
    circuit_breaker = get_circuit_breaker()

    health_stats = health_monitor.get_stats(source_id)
    rate_limit_stats = rate_limiter.get_stats(source_id)
    circuit_stats = circuit_breaker.get_stats(source_id)

    # Ultimos runs
    runs = _runs_store.get(source_id, [])[-5:]

    return SourceDetailResponse(
        **source,
        health_stats=health_stats,
        rate_limit_stats=rate_limit_stats,
        circuit_breaker_stats=circuit_stats,
        recent_runs=runs,
    )


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: str, payload: SourceUpdate) -> SourceResponse:
    """Atualiza uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    source.update(update_data)
    source["updated_at"] = datetime.now(timezone.utc)

    # Atualizar rate limiter se necessario
    if "rate_limit_rpm" in update_data:
        rate_limiter = get_rate_limiter()
        rate_limiter.configure(source_id, requests_per_minute=update_data["rate_limit_rpm"])

    _sources_store[source_id] = source
    return SourceResponse(**source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: str) -> None:
    """Remove uma fonte."""
    if source_id not in _sources_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    del _sources_store[source_id]
    if source_id in _runs_store:
        del _runs_store[source_id]


@router.post("/{source_id}/status", response_model=SourceResponse)
def change_source_status(
    source_id: str,
    target_state: str = Query(..., description="Novo estado"),
    reason: str = Query("", description="Motivo da mudanca"),
) -> SourceResponse:
    """Muda o estado de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    valid_states = ["PROPOSED", "TESTING", "ACTIVE", "UNDER_REVIEW", "SUSPECT", "DISABLED_TEMP", "DISABLED_PERM"]
    if target_state not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state. Must be one of: {valid_states}"
        )

    source["state"] = target_state
    source["updated_at"] = datetime.now(timezone.utc)
    _sources_store[source_id] = source

    return SourceResponse(**source)


# =============================================================================
# Dry-Run
# =============================================================================

@router.post("/{source_id}/dry-run", response_model=DryRunResponse)
async def dry_run_source(source_id: str, payload: DryRunRequest) -> DryRunResponse:
    """
    Executa dry-run de uma fonte para testar configuracao.

    Nao persiste dados, apenas retorna amostra de documentos.
    """
    import time

    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    start_time = time.time()
    url = payload.url or source.get("url")
    source_type = source.get("source_type")

    try:
        # Simular fetch baseado no tipo
        sample_docs = []

        if source_type == "official":
            # Usar integrador oficial
            from app.ingestion.providers.gov_br import GovBrClient
            client = GovBrClient()
            docs = await client.search_datasets(query="dados", rows=payload.limit)
            sample_docs = [
                {"title": d.title, "url": d.url, "type": "dataset"}
                for d in docs[:payload.limit]
            ]

        elif source_type == "scraper":
            # Indicar que scraper precisa ser executado manualmente
            sample_docs = [
                {"info": "Scraper dry-run requires manual execution", "url": url}
            ]

        else:
            # Tentar fetch generico
            import httpx
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(url, timeout=10, follow_redirects=True)
                if response.status_code == 200:
                    sample_docs = [
                        {"status": "reachable", "content_length": len(response.text)}
                    ]
                else:
                    raise Exception(f"HTTP {response.status_code}")

        latency_ms = (time.time() - start_time) * 1000

        return DryRunResponse(
            success=True,
            source_id=source_id,
            documents_found=len(sample_docs),
            sample_documents=sample_docs,
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.exception("dry_run_source failed for %s", source_id)
        latency_ms = (time.time() - start_time) * 1000
        return DryRunResponse(
            success=False,
            source_id=source_id,
            documents_found=0,
            sample_documents=[],
            latency_ms=latency_ms,
            error_message="Source validation failed. Check logs for details.",
        )


# =============================================================================
# Trigger Ingestion
# =============================================================================

@router.post("/{source_id}/trigger", response_model=TriggerIngestionResponse)
def trigger_ingestion(source_id: str, payload: TriggerIngestionRequest) -> TriggerIngestionResponse:
    """Dispara ingestao para uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    if not source.get("enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source is disabled"
        )

    # Verificar circuit breaker
    circuit_breaker = get_circuit_breaker()
    if not circuit_breaker.is_available(source_id) and not payload.force:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Source circuit is open. Use force=true to override."
        )

    now = datetime.now(timezone.utc)
    run_id = _generate_run_id()

    run = {
        "run_id": run_id,
        "status": "PENDING",
        "trigger": "MANUAL",
        "started_at": now,
        "finished_at": None,
        "documents_processed": 0,
        "error_message": None,
    }

    if source_id not in _runs_store:
        _runs_store[source_id] = []
    _runs_store[source_id].append(run)

    # TODO: Disparar ingestao async (celery/background task)

    return TriggerIngestionResponse(
        run_id=run_id,
        status="PENDING",
        triggered_at=now,
    )


# =============================================================================
# Metrics
# =============================================================================

@router.get("/{source_id}/metrics", response_model=SourceMetricsResponse)
def get_source_metrics(
    source_id: str,
    period: str = Query("24h", description="Periodo: 1h, 24h, 7d"),
) -> SourceMetricsResponse:
    """Retorna metricas de performance de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    # Calcular metricas baseado nos runs
    runs = _runs_store.get(source_id, [])

    # Filtrar por periodo
    now = datetime.now(timezone.utc)
    if period == "1h":
        cutoff = now - timedelta(hours=1)
    elif period == "24h":
        cutoff = now - timedelta(hours=24)
    elif period == "7d":
        cutoff = now - timedelta(days=7)
    else:
        cutoff = now - timedelta(hours=24)

    recent_runs = [
        r for r in runs
        if r.get("started_at") and r["started_at"] >= cutoff
    ]

    total_docs = sum(r.get("documents_processed", 0) for r in recent_runs)
    success_runs = [r for r in recent_runs if r.get("status") == "COMPLETED"]
    error_runs = [r for r in recent_runs if r.get("status") == "FAILED"]

    # Calcular metricas
    hours = {"1h": 1, "24h": 24, "7d": 168}.get(period, 24)
    docs_per_hour = total_docs / hours if hours > 0 else 0

    success_rate = len(success_runs) / len(recent_runs) if recent_runs else 1.0

    # Latencia do health monitor
    health_monitor = get_health_monitor()
    stats = health_monitor.get_stats(source_id)
    avg_latency = stats.get("avg_latency_ms", 0) if stats else 0

    last_ingestion = None
    if runs:
        last_run = runs[-1]
        last_ingestion = last_run.get("finished_at") or last_run.get("started_at")

    return SourceMetricsResponse(
        source_id=source_id,
        period=period,
        total_documents=total_docs,
        documents_per_hour=docs_per_hour,
        avg_latency_ms=avg_latency,
        success_rate=success_rate,
        error_count=len(error_runs),
        last_ingestion=last_ingestion,
    )


# =============================================================================
# History
# =============================================================================

@router.get("/{source_id}/history", response_model=IngestionHistoryResponse)
def get_ingestion_history(
    source_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> IngestionHistoryResponse:
    """Retorna historico de ingestao de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    runs = _runs_store.get(source_id, [])

    # Ordenar por data (mais recente primeiro) e paginar
    sorted_runs = sorted(
        runs,
        key=lambda r: r.get("started_at") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    paginated = sorted_runs[offset:offset + limit]

    items = []
    for run in paginated:
        started = run.get("started_at")
        finished = run.get("finished_at")
        duration = None
        if started and finished:
            duration = (finished - started).total_seconds()

        items.append(IngestionHistoryItem(
            run_id=run.get("run_id", ""),
            status=run.get("status", "UNKNOWN"),
            trigger=run.get("trigger", "UNKNOWN"),
            started_at=started or datetime.now(timezone.utc),
            finished_at=finished,
            documents_processed=run.get("documents_processed", 0),
            error_message=run.get("error_message"),
            duration_seconds=duration,
        ))

    return IngestionHistoryResponse(
        source_id=source_id,
        runs=items,
        pagination={"limit": limit, "offset": offset, "total": len(runs)},
    )


# =============================================================================
# Health Check
# =============================================================================

@router.get("/{source_id}/health", response_model=HealthCheckResponse)
def get_source_health(source_id: str) -> HealthCheckResponse:
    """Retorna status de saude de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    health_monitor = get_health_monitor()
    stats = health_monitor.get_stats(source_id)

    if not stats:
        return HealthCheckResponse(
            source_id=source_id,
            status="UNKNOWN",
            latency_ms=0,
            checked_at=datetime.now(timezone.utc),
            consecutive_successes=0,
            consecutive_failures=0,
            uptime_percent=100.0,
        )

    return HealthCheckResponse(
        source_id=source_id,
        status=stats.get("status", "UNKNOWN"),
        latency_ms=stats.get("avg_latency_ms", 0),
        checked_at=datetime.fromisoformat(stats["last_check"]) if stats.get("last_check") else datetime.now(timezone.utc),
        consecutive_successes=stats.get("consecutive_successes", 0),
        consecutive_failures=stats.get("consecutive_failures", 0),
        uptime_percent=stats.get("uptime_percent", 100.0),
        error_message=stats.get("error_message"),
    )


@router.post("/{source_id}/health", response_model=HealthCheckResponse)
def trigger_health_check(source_id: str) -> HealthCheckResponse:
    """Dispara health check manual de uma fonte."""
    source = _sources_store.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found"
        )

    health_monitor = get_health_monitor()
    status_result = health_monitor.check_source(source_id)

    # Atualizar fonte
    source["last_health_status"] = status_result.value.upper()
    source["last_health_check"] = datetime.now(timezone.utc)
    _sources_store[source_id] = source

    return get_source_health(source_id)
