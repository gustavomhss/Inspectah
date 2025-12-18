"""
S38-BE-051: API Contracts v1

Contratos de API para integracao externa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

CONTRACT_VERSION = "1.0.0"


# Generic types
T = TypeVar("T")


class ContractStatus(str, Enum):
    """Status de resposta."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class ErrorContract:
    """Contrato de erro padrao."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "field": self.field,
            "trace_id": self.trace_id,
        }


@dataclass
class PaginationContract:
    """Contrato de paginacao."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationContract":
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }


@dataclass
class ResponseEnvelope(Generic[T]):
    """Envelope padrao de resposta."""
    status: ContractStatus
    data: Optional[T] = None
    errors: List[ErrorContract] = field(default_factory=list)
    pagination: Optional[PaginationContract] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status.value,
            "meta": {
                "version": CONTRACT_VERSION,
                "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                **self.meta,
            },
        }

        if self.data is not None:
            if hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            elif isinstance(self.data, list):
                result["data"] = [
                    d.to_dict() if hasattr(d, "to_dict") else d
                    for d in self.data
                ]
            else:
                result["data"] = self.data

        if self.errors:
            result["errors"] = [e.to_dict() for e in self.errors]

        if self.pagination:
            result["pagination"] = self.pagination.to_dict()

        return result


# Domain Contracts

@dataclass
class ClaimContract:
    """Contrato de Claim para API externa."""
    id: str
    text: str
    source_id: Optional[str]
    verdict: Optional[str]
    confidence: Optional[float]
    created_at: str
    updated_at: str
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    evidence_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "source_id": self.source_id,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "entities": self.entities,
            "topics": self.topics,
            "evidence_count": self.evidence_count,
        }


@dataclass
class SourceContract:
    """Contrato de Source para API externa."""
    id: str
    name: str
    slug: str
    source_type: str
    url: str
    enabled: bool
    state: str
    health_status: str
    credibility_score: Optional[float]
    created_at: str
    last_ingestion_at: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "source_type": self.source_type,
            "url": self.url,
            "enabled": self.enabled,
            "state": self.state,
            "health_status": self.health_status,
            "credibility_score": self.credibility_score,
            "created_at": self.created_at,
            "last_ingestion_at": self.last_ingestion_at,
        }


@dataclass
class SignalContract:
    """Contrato de Signal para API externa."""
    type: str
    scope: str
    scope_id: Optional[str]
    value: float
    confidence: float
    level: str
    calculated_at: str
    expires_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "scope": self.scope,
            "scope_id": self.scope_id,
            "value": self.value,
            "confidence": self.confidence,
            "level": self.level,
            "calculated_at": self.calculated_at,
            "expires_at": self.expires_at,
        }


@dataclass
class PolicyContract:
    """Contrato de Policy para API externa."""
    id: str
    name: str
    domain: str
    version: int
    status: str
    min_confidence: float
    min_sources: int
    sensitive: bool
    created_at: str
    activated_at: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "version": self.version,
            "status": self.status,
            "min_confidence": self.min_confidence,
            "min_sources": self.min_sources,
            "sensitive": self.sensitive,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
        }


@dataclass
class VerdictContract:
    """Contrato de Verdict para API externa."""
    claim_id: str
    verdict: str
    confidence: float
    reasoning: str
    evidence_ids: List[str]
    sources_count: int
    decided_at: str
    decided_by: str
    policy_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_ids": self.evidence_ids,
            "sources_count": self.sources_count,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
            "policy_id": self.policy_id,
        }


@dataclass
class RelationContract:
    """Contrato de Relation entre claims."""
    source_claim_id: str
    target_claim_id: str
    relation_type: str
    confidence: float
    method: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_claim_id": self.source_claim_id,
            "target_claim_id": self.target_claim_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "method": self.method,
            "created_at": self.created_at,
        }


# Contract validation

class ContractValidator:
    """Validador de contratos."""

    @staticmethod
    def validate_claim(data: Dict[str, Any]) -> List[ErrorContract]:
        errors = []
        if not data.get("id"):
            errors.append(ErrorContract("MISSING_FIELD", "id is required", field="id"))
        if not data.get("text"):
            errors.append(ErrorContract("MISSING_FIELD", "text is required", field="text"))
        return errors

    @staticmethod
    def validate_source(data: Dict[str, Any]) -> List[ErrorContract]:
        errors = []
        if not data.get("name"):
            errors.append(ErrorContract("MISSING_FIELD", "name is required", field="name"))
        if not data.get("url"):
            errors.append(ErrorContract("MISSING_FIELD", "url is required", field="url"))
        if not data.get("source_type"):
            errors.append(ErrorContract("MISSING_FIELD", "source_type is required", field="source_type"))
        return errors


# Response helpers

def success_response(
    data: Any,
    pagination: Optional[PaginationContract] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Cria resposta de sucesso."""
    envelope = ResponseEnvelope(
        status=ContractStatus.SUCCESS,
        data=data,
        pagination=pagination,
        meta=meta or {},
    )
    return envelope.to_dict()


def error_response(
    errors: List[ErrorContract],
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Cria resposta de erro."""
    envelope = ResponseEnvelope(
        status=ContractStatus.ERROR,
        errors=errors,
        meta=meta or {},
    )
    return envelope.to_dict()


def partial_response(
    data: Any,
    errors: List[ErrorContract],
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Cria resposta parcial (sucesso com avisos)."""
    envelope = ResponseEnvelope(
        status=ContractStatus.PARTIAL,
        data=data,
        errors=errors,
        meta=meta or {},
    )
    return envelope.to_dict()
