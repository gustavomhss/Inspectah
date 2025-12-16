"""
S38-BE-042: Policies API Routes

Endpoints para gerenciamento de versoes de policies.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.policies.models import PromotionPolicyConfig
from app.policies.version_service import (
    ChangeType,
    PolicyAuditEntry,
    PolicyStatus,
    PolicyVersion,
    PolicyVersionService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])

# Global service instance
_version_service: Optional[PolicyVersionService] = None


def _get_service() -> PolicyVersionService:
    global _version_service
    if _version_service is None:
        _version_service = PolicyVersionService()
    return _version_service


# Request/Response models

class PolicyConfigInput(BaseModel):
    """Configuracao de policy para criacao/update."""
    name: str
    domain: str
    min_confidence: float = Field(ge=0.0, le=1.0)
    min_sources: int = Field(ge=0)
    require_debunk: bool = False
    require_human: bool = False
    sensitive: bool = False
    default_decision: str = "HOLD"
    metadata: Optional[Dict[str, Any]] = None


class CreateVersionRequest(BaseModel):
    """Request para criar nova versao."""
    config: PolicyConfigInput
    changelog: str = ""
    parent_version_id: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request para aprovar versao."""
    comments: str = ""


class RollbackRequest(BaseModel):
    """Request para rollback."""
    target_version_id: str
    reason: str


class PolicyVersionResponse(BaseModel):
    """Resposta com dados de versao."""
    version_id: str
    policy_id: str
    version_number: int
    config: Dict[str, Any]
    status: str
    created_at: str
    created_by: str
    approved_at: Optional[str]
    approved_by: Optional[str]
    activated_at: Optional[str]
    changelog: str


class AuditEntryResponse(BaseModel):
    """Resposta de entrada de audit."""
    audit_id: str
    policy_id: str
    version_id: str
    change_type: str
    changed_at: str
    changed_by: str
    old_status: Optional[str]
    new_status: Optional[str]
    details: Dict[str, Any]


# Helper functions

def _to_response(version: PolicyVersion) -> PolicyVersionResponse:
    return PolicyVersionResponse(
        version_id=version.version_id,
        policy_id=version.policy_id,
        version_number=version.version_number,
        config={
            "name": version.config.name,
            "domain": version.config.domain,
            "min_confidence": version.config.min_confidence,
            "min_sources": version.config.min_sources,
            "require_debunk": version.config.require_debunk,
            "require_human": version.config.require_human,
            "sensitive": version.config.sensitive,
            "default_decision": version.config.default_decision,
        },
        status=version.status.value,
        created_at=version.created_at.isoformat(),
        created_by=version.created_by,
        approved_at=version.approved_at.isoformat() if version.approved_at else None,
        approved_by=version.approved_by,
        activated_at=version.activated_at.isoformat() if version.activated_at else None,
        changelog=version.changelog,
    )


def _to_audit_response(entry: PolicyAuditEntry) -> AuditEntryResponse:
    return AuditEntryResponse(
        audit_id=entry.audit_id,
        policy_id=entry.policy_id,
        version_id=entry.version_id,
        change_type=entry.change_type.value,
        changed_at=entry.changed_at.isoformat(),
        changed_by=entry.changed_by,
        old_status=entry.old_status.value if entry.old_status else None,
        new_status=entry.new_status.value if entry.new_status else None,
        details=entry.details,
    )


# Endpoints

@router.post("/versions", response_model=PolicyVersionResponse)
async def create_version(
    body: CreateVersionRequest,
    created_by: str = Query(..., description="Usuario criador"),
):
    """
    Cria nova versao de policy.

    A versao e criada em status DRAFT.
    """
    service = _get_service()

    config = PromotionPolicyConfig(
        name=body.config.name,
        domain=body.config.domain,
        min_confidence=body.config.min_confidence,
        min_sources=body.config.min_sources,
        require_debunk=body.config.require_debunk,
        require_human=body.config.require_human,
        sensitive=body.config.sensitive,
        default_decision=body.config.default_decision,
        metadata=body.config.metadata or {},
    )

    try:
        version = service.create_version(
            config=config,
            created_by=created_by,
            changelog=body.changelog,
            parent_version_id=body.parent_version_id,
        )
        return _to_response(version)
    except ValueError as e:
        logger.warning("create_version validation error: %s", e)
        raise HTTPException(400, {"error": "validation_error", "message": "Invalid policy configuration"})


@router.get("/versions/{version_id}", response_model=PolicyVersionResponse)
async def get_version(version_id: str):
    """Retorna uma versao especifica."""
    service = _get_service()
    version = service.repository.get_version(version_id)

    if not version:
        raise HTTPException(404, f"Version {version_id} not found")

    return _to_response(version)


@router.post("/versions/{version_id}/submit")
async def submit_for_review(
    version_id: str,
    submitted_by: str = Query(..., description="Usuario que submete"),
):
    """Submete versao para revisao."""
    service = _get_service()

    try:
        version = service.submit_for_review(version_id, submitted_by)
        return _to_response(version)
    except ValueError as e:
        logger.warning("submit_for_review error for %s: %s", version_id, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Cannot submit version for review"})


@router.post("/versions/{version_id}/approve")
async def approve_version(
    version_id: str,
    body: ApprovalRequest,
    approved_by: str = Query(..., description="Usuario aprovador"),
):
    """Aprova versao de policy."""
    service = _get_service()

    try:
        version = service.approve(version_id, approved_by, body.comments)
        return _to_response(version)
    except ValueError as e:
        logger.warning("approve error for %s: %s", version_id, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Cannot approve version"})


@router.post("/versions/{version_id}/activate")
async def activate_version(
    version_id: str,
    activated_by: str = Query(..., description="Usuario que ativa"),
):
    """Ativa versao de policy."""
    service = _get_service()

    try:
        version = service.activate(version_id, activated_by)
        return _to_response(version)
    except ValueError as e:
        logger.warning("activate error for %s: %s", version_id, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Cannot activate version"})


@router.post("/versions/{version_id}/deactivate")
async def deactivate_version(
    version_id: str,
    deactivated_by: str = Query(..., description="Usuario que desativa"),
    reason: str = Query("", description="Motivo"),
):
    """Desativa versao de policy."""
    service = _get_service()

    try:
        version = service.deactivate(version_id, deactivated_by, reason)
        return _to_response(version)
    except ValueError as e:
        logger.warning("deactivate error for %s: %s", version_id, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Cannot deactivate version"})


@router.get("/active/{domain}")
async def get_active_policy(domain: str):
    """Retorna policy ativa para um dominio."""
    service = _get_service()
    config = service.get_active_policy(domain)

    if not config:
        raise HTTPException(404, f"No active policy for domain {domain}")

    return {
        "name": config.name,
        "domain": config.domain,
        "min_confidence": config.min_confidence,
        "min_sources": config.min_sources,
        "require_debunk": config.require_debunk,
        "require_human": config.require_human,
        "sensitive": config.sensitive,
        "default_decision": config.default_decision,
    }


@router.get("/history/{domain}")
async def get_version_history(
    domain: str,
    name: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    """Retorna historico de versoes de um dominio."""
    service = _get_service()
    versions = service.get_version_history(domain, name)

    return {
        "domain": domain,
        "versions": [_to_response(v) for v in versions[:limit]],
        "total": len(versions),
    }


@router.post("/rollback/{domain}")
async def rollback(
    domain: str,
    body: RollbackRequest,
    rolled_back_by: str = Query(..., description="Usuario"),
):
    """Faz rollback para uma versao anterior."""
    service = _get_service()

    try:
        version = service.rollback(
            domain=domain,
            target_version_id=body.target_version_id,
            rolled_back_by=rolled_back_by,
            reason=body.reason,
        )
        return _to_response(version)
    except ValueError as e:
        logger.warning("rollback error for domain %s: %s", domain, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Rollback failed"})


@router.get("/compare")
async def compare_versions(
    version_a: str = Query(...),
    version_b: str = Query(...),
):
    """Compara duas versoes de policy."""
    service = _get_service()

    try:
        comparison = service.compare_versions(version_a, version_b)
        return {
            "version_a": comparison.version_a,
            "version_b": comparison.version_b,
            "differences": comparison.differences,
            "summary": comparison.summary,
        }
    except ValueError as e:
        logger.warning("compare_versions error for %s vs %s: %s", version_a, version_b, e)
        raise HTTPException(400, {"error": "validation_error", "message": "Cannot compare versions"})


@router.get("/audit", response_model=List[AuditEntryResponse])
async def get_audit_log(
    policy_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """Retorna audit log de policies."""
    service = _get_service()
    entries = service.get_audit_log(policy_id, limit)
    return [_to_audit_response(e) for e in entries]


@router.get("/statuses")
async def list_statuses():
    """Lista status possiveis de versao."""
    return {
        "statuses": [
            {"status": s.value, "description": _get_status_description(s)}
            for s in PolicyStatus
        ],
        "change_types": [
            {"type": c.value, "description": _get_change_description(c)}
            for c in ChangeType
        ],
    }


def _get_status_description(status: PolicyStatus) -> str:
    descriptions = {
        PolicyStatus.DRAFT: "Em elaboracao",
        PolicyStatus.PENDING_REVIEW: "Aguardando revisao",
        PolicyStatus.APPROVED: "Aprovada, pronta para ativar",
        PolicyStatus.ACTIVE: "Em producao",
        PolicyStatus.DEPRECATED: "Descontinuada",
        PolicyStatus.ARCHIVED: "Arquivada",
    }
    return descriptions.get(status, "")


def _get_change_description(change: ChangeType) -> str:
    descriptions = {
        ChangeType.CREATE: "Criacao de versao",
        ChangeType.UPDATE: "Atualizacao de status",
        ChangeType.ACTIVATE: "Ativacao em producao",
        ChangeType.DEACTIVATE: "Desativacao",
        ChangeType.DEPRECATE: "Descontinuacao",
        ChangeType.ARCHIVE: "Arquivamento",
        ChangeType.ROLLBACK: "Rollback para versao anterior",
    }
    return descriptions.get(change, "")
