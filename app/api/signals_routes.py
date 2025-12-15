"""
S38-BE-033: Signals API Routes

Endpoints para sinais on-demand do mercado de verdade.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.signals import (
    CacheInvalidationService,
    EventType,
    InvalidationEvent,
    InstrumentedCacheService,
    MemoryCacheBackend,
    SignalRequest,
    SignalScope,
    SignalService,
    SignalType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/signals", tags=["signals"])

# Global instances (will be replaced with DI in production)
_cache_service: Optional[InstrumentedCacheService] = None
_signal_service: Optional[SignalService] = None
_invalidation_service: Optional[CacheInvalidationService] = None


def _get_services():
    """Get or create service instances."""
    global _cache_service, _signal_service, _invalidation_service

    if _cache_service is None:
        _cache_service = InstrumentedCacheService(MemoryCacheBackend())
        _signal_service = SignalService(cache_service=_cache_service)
        _invalidation_service = CacheInvalidationService(_cache_service)

    return _signal_service, _cache_service, _invalidation_service


# Request/Response models

class SignalRequestBody(BaseModel):
    """Request para buscar sinais."""
    signal_types: List[str] = Field(
        default_factory=list,
        description="Tipos de sinais (vazio = todos)"
    )
    scope: str = Field(default="global", description="Escopo: global, topic, entity, source, claim")
    scope_ids: Optional[List[str]] = Field(default=None, description="IDs dos escopos")
    force_refresh: bool = Field(default=False, description="Forcar recalculo ignorando cache")
    include_metadata: bool = Field(default=False, description="Incluir metadata detalhado")


class SignalValueResponse(BaseModel):
    """Valor de sinal na resposta."""
    signal_type: str
    scope: str
    scope_id: Optional[str]
    value: float
    confidence: float
    level: str
    sample_size: int
    calculated_at: str
    expires_at: str
    metadata: Optional[Dict[str, Any]] = None


class SignalBatchResponse(BaseModel):
    """Resposta com batch de sinais."""
    batch_id: str
    signals: List[SignalValueResponse]
    alerts: List[Dict[str, Any]]
    calculation_time_ms: float
    cache_stats: Optional[Dict[str, Any]] = None


class InvalidationRequest(BaseModel):
    """Request para invalidar cache."""
    event_type: str = Field(default="manual_invalidation")
    scope: str = Field(default="global")
    scope_id: Optional[str] = None
    signal_types: Optional[List[str]] = None


class CacheStatsResponse(BaseModel):
    """Estatisticas de cache."""
    hits: int
    misses: int
    sets: int
    deletes: int
    hit_rate: float


# Endpoints

@router.get("", response_model=SignalBatchResponse)
async def get_signals(
    signal_types: Optional[str] = Query(None, description="Tipos separados por virgula"),
    scope: str = Query("global", description="Escopo"),
    scope_id: Optional[str] = Query(None, description="ID do escopo"),
    force_refresh: bool = Query(False, description="Forcar recalculo"),
):
    """
    Busca sinais on-demand.

    Se signal_types nao especificado, retorna todos os tipos.
    """
    signal_service, cache_service, _ = _get_services()

    # Parse signal types
    types_to_fetch: List[SignalType] = []
    if signal_types:
        for t in signal_types.split(","):
            try:
                types_to_fetch.append(SignalType(t.strip()))
            except ValueError:
                raise HTTPException(400, f"Invalid signal type: {t}")
    else:
        types_to_fetch = list(SignalType)

    # Parse scope
    try:
        parsed_scope = SignalScope(scope)
    except ValueError:
        raise HTTPException(400, f"Invalid scope: {scope}")

    # Build request
    request = SignalRequest(
        signal_types=types_to_fetch,
        scope=parsed_scope,
        scope_ids=[scope_id] if scope_id else None,
        force_refresh=force_refresh,
        include_metadata=True,
    )

    # Get signals
    batch = await signal_service.get_signals(request)
    alerts = signal_service.check_alerts(batch.signals)

    # Build response
    signals_response = []
    for s in batch.signals:
        config = signal_service.configs.get(s.signal_type)
        level = s.get_level(config) if config else "unknown"
        signals_response.append(SignalValueResponse(
            signal_type=s.signal_type.value,
            scope=s.scope.value,
            scope_id=s.scope_id,
            value=s.value,
            confidence=s.confidence,
            level=level,
            sample_size=s.sample_size,
            calculated_at=s.calculated_at.isoformat(),
            expires_at=s.expires_at.isoformat(),
            metadata=s.metadata if s.metadata else None,
        ))

    alerts_response = [
        {
            "id": a.alert_id,
            "signal_type": a.signal_type.value,
            "level": a.level,
            "value": a.value,
            "threshold": a.threshold,
            "message": a.message,
        }
        for a in alerts
    ]

    return SignalBatchResponse(
        batch_id=batch.batch_id,
        signals=signals_response,
        alerts=alerts_response,
        calculation_time_ms=batch.calculation_time_ms,
        cache_stats=cache_service.get_stats(),
    )


@router.post("", response_model=SignalBatchResponse)
async def query_signals(body: SignalRequestBody):
    """
    Busca sinais com filtros complexos via POST.
    """
    signal_service, cache_service, _ = _get_services()

    # Parse signal types
    types_to_fetch: List[SignalType] = []
    if body.signal_types:
        for t in body.signal_types:
            try:
                types_to_fetch.append(SignalType(t))
            except ValueError:
                raise HTTPException(400, f"Invalid signal type: {t}")
    else:
        types_to_fetch = list(SignalType)

    # Parse scope
    try:
        parsed_scope = SignalScope(body.scope)
    except ValueError:
        raise HTTPException(400, f"Invalid scope: {body.scope}")

    # Build request
    request = SignalRequest(
        signal_types=types_to_fetch,
        scope=parsed_scope,
        scope_ids=body.scope_ids,
        force_refresh=body.force_refresh,
        include_metadata=body.include_metadata,
    )

    batch = await signal_service.get_signals(request)
    alerts = signal_service.check_alerts(batch.signals)

    signals_response = []
    for s in batch.signals:
        config = signal_service.configs.get(s.signal_type)
        level = s.get_level(config) if config else "unknown"
        signals_response.append(SignalValueResponse(
            signal_type=s.signal_type.value,
            scope=s.scope.value,
            scope_id=s.scope_id,
            value=s.value,
            confidence=s.confidence,
            level=level,
            sample_size=s.sample_size,
            calculated_at=s.calculated_at.isoformat(),
            expires_at=s.expires_at.isoformat(),
            metadata=s.metadata if body.include_metadata else None,
        ))

    alerts_response = [
        {
            "id": a.alert_id,
            "signal_type": a.signal_type.value,
            "level": a.level,
            "value": a.value,
            "threshold": a.threshold,
            "message": a.message,
        }
        for a in alerts
    ]

    return SignalBatchResponse(
        batch_id=batch.batch_id,
        signals=signals_response,
        alerts=alerts_response,
        calculation_time_ms=batch.calculation_time_ms,
        cache_stats=cache_service.get_stats() if body.include_metadata else None,
    )


@router.get("/dashboard")
async def get_dashboard_signals():
    """
    Retorna sinais formatados para dashboard.

    Endpoint otimizado para visualizacao.
    """
    signal_service, _, _ = _get_services()
    return await signal_service.get_dashboard_signals()


@router.get("/types")
async def list_signal_types():
    """Lista tipos de sinais disponiveis e suas configuracoes."""
    from app.signals import SignalConfig

    configs = SignalConfig.default_configs()
    return {
        "types": [
            {
                "type": t.value,
                "priority": configs[t].priority.value,
                "cache_ttl_seconds": configs[t].cache_ttl_seconds,
                "thresholds": configs[t].thresholds,
            }
            for t in SignalType
        ],
        "scopes": [s.value for s in SignalScope],
    }


@router.post("/invalidate")
async def invalidate_cache(body: InvalidationRequest):
    """
    Invalida cache de sinais.

    Uso em casos de manutencao ou apos atualizacoes importantes.
    """
    _, cache_service, invalidation_service = _get_services()

    try:
        event_type = EventType(body.event_type)
    except ValueError:
        event_type = EventType.MANUAL_INVALIDATION

    try:
        scope = SignalScope(body.scope)
    except ValueError:
        raise HTTPException(400, f"Invalid scope: {body.scope}")

    # Parse affected signal types
    affected_types = None
    if body.signal_types:
        affected_types = []
        for t in body.signal_types:
            try:
                affected_types.append(SignalType(t))
            except ValueError:
                raise HTTPException(400, f"Invalid signal type: {t}")

    event = InvalidationEvent(
        event_type=event_type,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        scope=scope,
        scope_id=body.scope_id,
        affected_types=affected_types,
    )

    count = await invalidation_service.process_event(event)

    return {
        "success": True,
        "invalidated_count": count,
        "event_type": event_type.value,
        "scope": scope.value,
        "scope_id": body.scope_id,
    }


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Retorna estatisticas de cache."""
    _, cache_service, _ = _get_services()
    stats = cache_service.get_stats()
    return CacheStatsResponse(**stats)


@router.get("/cache/events")
async def get_invalidation_events(limit: int = Query(50, le=200)):
    """Retorna eventos de invalidacao recentes."""
    _, _, invalidation_service = _get_services()
    events = invalidation_service.get_recent_events(limit)
    return {"events": events, "count": len(events)}


@router.delete("/cache")
async def clear_cache():
    """Limpa todo o cache de sinais."""
    _, _, invalidation_service = _get_services()
    count = await invalidation_service.invalidate_all()
    return {"success": True, "cleared_count": count}
