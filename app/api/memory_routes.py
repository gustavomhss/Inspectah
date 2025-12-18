"""
S38-BE-043: Memory Controller API Routes

Endpoints para gerenciamento de memoria de contexto.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.context.memory_controller import (
    MemoryController,
    MemoryEntry,
    MemoryScope,
    MemoryStats,
    MemoryType,
    RetentionPolicy,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

# Global controller instance
_controller: Optional[MemoryController] = None


def _get_controller() -> MemoryController:
    global _controller
    if _controller is None:
        _controller = MemoryController()
    return _controller


# Request/Response models

class RememberRequest(BaseModel):
    """Request para armazenar memoria."""
    scope: str = Field(description="Escopo: session, agent, flow, case, user, global")
    scope_id: str
    key: str
    value: Any
    memory_type: str = Field(default="context", description="Tipo: context, fact, decision, observation, summary, reference")
    retention: str = Field(default="medium", description="Retencao: ephemeral, short, medium, long, permanent")
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class RecallRequest(BaseModel):
    """Request para recuperar memorias."""
    scope: str
    scope_id: str
    key: Optional[str] = None
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    limit: int = Field(default=100, le=500)
    include_expired: bool = False


class ForgetRequest(BaseModel):
    """Request para esquecer memorias."""
    scope: str
    scope_id: str
    key: Optional[str] = None


class MemoryEntryResponse(BaseModel):
    """Resposta com entrada de memoria."""
    entry_id: str
    scope: str
    scope_id: str
    memory_type: str
    key: str
    value: Any
    retention: str
    created_at: str
    expires_at: str
    accessed_at: str
    access_count: int
    importance: float
    tags: List[str]
    is_expired: bool


class StatsResponse(BaseModel):
    """Resposta com estatisticas."""
    total_entries: int
    active_entries: int
    expired_entries: int
    by_scope: Dict[str, int]
    by_type: Dict[str, int]
    by_retention: Dict[str, int]
    total_access_count: int
    avg_importance: float


# Helper functions

def _parse_scope(scope_str: str) -> MemoryScope:
    try:
        return MemoryScope(scope_str)
    except ValueError:
        raise HTTPException(400, f"Invalid scope: {scope_str}")


def _parse_memory_type(type_str: str) -> MemoryType:
    try:
        return MemoryType(type_str)
    except ValueError:
        raise HTTPException(400, f"Invalid memory type: {type_str}")


def _parse_retention(retention_str: str) -> RetentionPolicy:
    try:
        return RetentionPolicy(retention_str)
    except ValueError:
        raise HTTPException(400, f"Invalid retention: {retention_str}")


def _to_response(entry: MemoryEntry) -> MemoryEntryResponse:
    return MemoryEntryResponse(
        entry_id=entry.entry_id,
        scope=entry.scope.value,
        scope_id=entry.scope_id,
        memory_type=entry.memory_type.value,
        key=entry.key,
        value=entry.value,
        retention=entry.retention.value,
        created_at=entry.created_at.isoformat(),
        expires_at=entry.expires_at.isoformat(),
        accessed_at=entry.accessed_at.isoformat(),
        access_count=entry.access_count,
        importance=entry.importance,
        tags=entry.tags,
        is_expired=entry.is_expired(),
    )


# Endpoints

@router.post("/remember", response_model=MemoryEntryResponse)
async def remember(body: RememberRequest):
    """
    Armazena uma memoria.

    Escopos disponiveis:
    - session: Memoria de sessao (curto prazo)
    - agent: Memoria do agente
    - flow: Memoria do fluxo
    - case: Memoria do caso
    - user: Memoria do usuario
    - global: Memoria global
    """
    controller = _get_controller()

    entry = controller.remember(
        scope=_parse_scope(body.scope),
        scope_id=body.scope_id,
        key=body.key,
        value=body.value,
        memory_type=_parse_memory_type(body.memory_type),
        retention=_parse_retention(body.retention),
        importance=body.importance,
        tags=body.tags,
        metadata=body.metadata,
    )

    return _to_response(entry)


@router.post("/recall", response_model=List[MemoryEntryResponse])
async def recall(body: RecallRequest):
    """
    Recupera memorias.

    Filtros aplicaveis:
    - key: Chave especifica
    - memory_type: Tipo de memoria
    - tags: Tags para busca
    - min_importance: Importancia minima
    """
    controller = _get_controller()

    memory_type = None
    if body.memory_type:
        memory_type = _parse_memory_type(body.memory_type)

    entries = controller.recall(
        scope=_parse_scope(body.scope),
        scope_id=body.scope_id,
        key=body.key,
        memory_type=memory_type,
        tags=body.tags,
        min_importance=body.min_importance,
        limit=body.limit,
        include_expired=body.include_expired,
    )

    return [_to_response(e) for e in entries]


@router.get("/recall/{scope}/{scope_id}")
async def recall_get(
    scope: str,
    scope_id: str,
    key: Optional[str] = Query(None),
    memory_type: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
):
    """Recupera memorias via GET."""
    controller = _get_controller()

    mt = _parse_memory_type(memory_type) if memory_type else None

    entries = controller.recall(
        scope=_parse_scope(scope),
        scope_id=scope_id,
        key=key,
        memory_type=mt,
        limit=limit,
    )

    return {
        "scope": scope,
        "scope_id": scope_id,
        "entries": [_to_response(e) for e in entries],
        "total": len(entries),
    }


@router.post("/forget")
async def forget(body: ForgetRequest):
    """
    Esquece memorias.

    Se key nao especificada, remove todas do escopo.
    """
    controller = _get_controller()

    count = controller.forget(
        scope=_parse_scope(body.scope),
        scope_id=body.scope_id,
        key=body.key,
    )

    return {
        "success": True,
        "forgotten_count": count,
        "scope": body.scope,
        "scope_id": body.scope_id,
        "key": body.key,
    }


@router.get("/context/{scope}/{scope_id}")
async def get_context(
    scope: str,
    scope_id: str,
    include_types: Optional[str] = Query(None, description="Tipos separados por virgula"),
    max_entries: int = Query(50, le=200),
):
    """
    Constroi contexto de memoria.

    Retorna contexto formatado para uso em agentes/fluxos.
    """
    controller = _get_controller()

    types = None
    if include_types:
        types = [_parse_memory_type(t.strip()) for t in include_types.split(",")]

    context = controller.build_context(
        scope=_parse_scope(scope),
        scope_id=scope_id,
        include_types=types,
        max_entries=max_entries,
    )

    return {
        "context_id": context.context_id,
        "scope": context.scope.value,
        "scope_id": context.scope_id,
        "entry_count": context.entry_count,
        "entries": {k: _to_response(v).model_dump() for k, v in context.entries.items()},
    }


@router.post("/summarize/{scope}/{scope_id}")
async def summarize(scope: str, scope_id: str):
    """
    Cria resumo das memorias de um escopo.

    O resumo e armazenado como nova memoria.
    """
    controller = _get_controller()

    entry = controller.summarize(
        scope=_parse_scope(scope),
        scope_id=scope_id,
    )

    return _to_response(entry)


@router.get("/export/{scope}/{scope_id}")
async def export_context(scope: str, scope_id: str):
    """Exporta contexto para serializacao."""
    controller = _get_controller()
    return controller.export_context(
        scope=_parse_scope(scope),
        scope_id=scope_id,
    )


@router.post("/import/{scope}/{scope_id}")
async def import_context(
    scope: str,
    scope_id: str,
    data: Dict[str, Any],
):
    """Importa contexto de dados serializados."""
    controller = _get_controller()

    count = controller.import_context(
        data=data,
        scope=_parse_scope(scope),
        scope_id=scope_id,
    )

    return {"success": True, "imported_count": count}


@router.post("/cleanup")
async def cleanup_expired():
    """Remove todas as entradas expiradas."""
    controller = _get_controller()
    count = controller.cleanup_expired()
    return {"success": True, "cleaned_count": count}


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Retorna estatisticas de uso de memoria."""
    controller = _get_controller()
    stats = controller.get_stats()
    return StatsResponse(
        total_entries=stats.total_entries,
        active_entries=stats.active_entries,
        expired_entries=stats.expired_entries,
        by_scope=stats.by_scope,
        by_type=stats.by_type,
        by_retention=stats.by_retention,
        total_access_count=stats.total_access_count,
        avg_importance=stats.avg_importance,
    )


@router.get("/scopes")
async def list_scopes():
    """Lista escopos e tipos disponiveis."""
    return {
        "scopes": [
            {"scope": s.value, "description": _get_scope_description(s)}
            for s in MemoryScope
        ],
        "memory_types": [
            {"type": t.value, "description": _get_type_description(t)}
            for t in MemoryType
        ],
        "retention_policies": [
            {"policy": r.value, "description": _get_retention_description(r)}
            for r in RetentionPolicy
        ],
    }


def _get_scope_description(scope: MemoryScope) -> str:
    descriptions = {
        MemoryScope.SESSION: "Memoria de sessao (curto prazo)",
        MemoryScope.AGENT: "Memoria do agente",
        MemoryScope.FLOW: "Memoria do fluxo de trabalho",
        MemoryScope.CASE: "Memoria do caso de investigacao",
        MemoryScope.USER: "Memoria do usuario",
        MemoryScope.GLOBAL: "Memoria global do sistema",
    }
    return descriptions.get(scope, "")


def _get_type_description(mtype: MemoryType) -> str:
    descriptions = {
        MemoryType.CONTEXT: "Contexto atual",
        MemoryType.FACT: "Fato aprendido",
        MemoryType.DECISION: "Decisao tomada",
        MemoryType.OBSERVATION: "Observacao",
        MemoryType.SUMMARY: "Resumo",
        MemoryType.REFERENCE: "Referencia a outros dados",
    }
    return descriptions.get(mtype, "")


def _get_retention_description(retention: RetentionPolicy) -> str:
    descriptions = {
        RetentionPolicy.EPHEMERAL: "Deletar ao fim da sessao (~1h)",
        RetentionPolicy.SHORT: "Reter por 1 dia",
        RetentionPolicy.MEDIUM: "Reter por 7 dias",
        RetentionPolicy.LONG: "Reter por 30 dias",
        RetentionPolicy.PERMANENT: "Nunca deletar",
    }
    return descriptions.get(retention, "")
