"""
S38-BE-034: Claims Relations API Routes

Endpoints para gerenciamento de relacoes entre claims.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.claims.relation_inference import Claim, RelationInferenceService
from app.claims.relation_types import (
    ClassificationResult,
    ClaimCluster,
    ClaimRelation,
    InferenceMethod,
    RelationConfig,
    RelationType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])

# Global service instance
_inference_service: Optional[RelationInferenceService] = None


def _get_inference_service() -> RelationInferenceService:
    """Get or create inference service."""
    global _inference_service
    if _inference_service is None:
        _inference_service = RelationInferenceService()
    return _inference_service


# Request/Response models

class ClaimInput(BaseModel):
    """Claim para analise de relacao."""
    id: str
    text: str
    embedding: Optional[List[float]] = None
    entities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class RelationRequest(BaseModel):
    """Request para inferir relacoes."""
    source_claim: ClaimInput
    candidate_claims: List[ClaimInput]
    max_results: int = Field(default=10, le=50)
    config: Optional[Dict[str, float]] = None


class SimilarityRequest(BaseModel):
    """Request para buscar similares."""
    query_claim: ClaimInput
    all_claims: List[ClaimInput]
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    limit: int = Field(default=10, le=100)


class ClaimRelationResponse(BaseModel):
    """Relacao entre claims na resposta."""
    source_claim_id: str
    target_claim_id: str
    relation_type: str
    confidence: float
    method: str
    indicators: Dict[str, Any]


class InferRelationsResponse(BaseModel):
    """Resposta de inferencia de relacoes."""
    relations: List[ClaimRelationResponse]
    total: int
    processing_time_ms: float


class SimilarClaimResponse(BaseModel):
    """Claim similar na resposta."""
    claim_id: str
    text: str
    similarity: float


class FindSimilarResponse(BaseModel):
    """Resposta de busca de similares."""
    similar_claims: List[SimilarClaimResponse]
    total: int
    threshold: float


class ClusterResponse(BaseModel):
    """Cluster de claims."""
    cluster_id: str
    representative_id: str
    member_ids: List[str]
    size: int
    avg_similarity: float
    topic: Optional[str] = None


class ClusteringResponse(BaseModel):
    """Resposta de clustering."""
    clusters: List[ClusterResponse]
    total_clusters: int
    total_claims: int


# Endpoints

@router.post("/relations/infer", response_model=InferRelationsResponse)
async def infer_relations(body: RelationRequest):
    """
    Infere relacoes semanticas entre um claim fonte e candidatos.

    Tipos de relacao:
    - supports: Claim A apoia claim B
    - contradicts: Claim A contradiz claim B
    - related: Claims relacionados tematicamente
    - duplicate: Claims duplicados ou muito similares
    - refines: Claim A especifica claim B
    - generalizes: Claim A generaliza claim B
    """
    import time
    start = time.time()

    service = _get_inference_service()

    # Apply custom config if provided
    if body.config:
        config = RelationConfig(
            similarity_threshold=body.config.get("similarity_threshold", 0.7),
            contradiction_threshold=body.config.get("contradiction_threshold", 0.6),
            duplicate_threshold=body.config.get("duplicate_threshold", 0.95),
            support_threshold=body.config.get("support_threshold", 0.85),
            confidence_threshold=body.config.get("confidence_threshold", 0.7),
        )
        service.config = config

    # Convert to internal Claim objects
    source = _to_claim(body.source_claim)
    candidates = [_to_claim(c) for c in body.candidate_claims]

    # Infer relations
    relations = service.infer_relations(source, candidates, body.max_results)

    elapsed_ms = (time.time() - start) * 1000

    return InferRelationsResponse(
        relations=[
            ClaimRelationResponse(
                source_claim_id=r.source_claim_id,
                target_claim_id=r.target_claim_id,
                relation_type=r.relation_type.value,
                confidence=r.confidence,
                method=r.method.value,
                indicators=r.indicators,
            )
            for r in relations
        ],
        total=len(relations),
        processing_time_ms=elapsed_ms,
    )


@router.post("/relations/similar", response_model=FindSimilarResponse)
async def find_similar_claims(body: SimilarityRequest):
    """
    Encontra claims similares ao claim de consulta.

    Usa similaridade de embeddings ou fallback para Jaccard.
    """
    service = _get_inference_service()

    query = _to_claim(body.query_claim)
    all_claims = [_to_claim(c) for c in body.all_claims]

    results = service.find_similar(query, all_claims, body.threshold, body.limit)

    return FindSimilarResponse(
        similar_claims=[
            SimilarClaimResponse(
                claim_id=claim.id,
                text=claim.text,
                similarity=sim,
            )
            for claim, sim in results
        ],
        total=len(results),
        threshold=body.threshold,
    )


@router.get("/relations/types")
async def list_relation_types():
    """Lista tipos de relacao disponiveis."""
    return {
        "relation_types": [
            {"type": rt.value, "description": _get_relation_description(rt)}
            for rt in RelationType
        ],
        "inference_methods": [
            {"method": m.value, "description": _get_method_description(m)}
            for m in InferenceMethod
        ],
    }


@router.get("/relations/config")
async def get_relation_config():
    """Retorna configuracao atual de inferencia."""
    service = _get_inference_service()
    config = service.config

    return {
        "similarity_threshold": config.similarity_threshold,
        "contradiction_threshold": config.contradiction_threshold,
        "duplicate_threshold": config.duplicate_threshold,
        "support_threshold": config.support_threshold,
        "confidence_threshold": config.confidence_threshold,
        "negation_boost": config.negation_boost,
        "max_relations_per_claim": config.max_relations_per_claim,
    }


@router.put("/relations/config")
async def update_relation_config(config: Dict[str, float]):
    """Atualiza configuracao de inferencia."""
    service = _get_inference_service()

    new_config = RelationConfig(
        similarity_threshold=config.get("similarity_threshold", service.config.similarity_threshold),
        contradiction_threshold=config.get("contradiction_threshold", service.config.contradiction_threshold),
        duplicate_threshold=config.get("duplicate_threshold", service.config.duplicate_threshold),
        support_threshold=config.get("support_threshold", service.config.support_threshold),
        confidence_threshold=config.get("confidence_threshold", service.config.confidence_threshold),
        negation_boost=config.get("negation_boost", service.config.negation_boost),
        max_relations_per_claim=int(config.get("max_relations_per_claim", service.config.max_relations_per_claim)),
    )

    service.config = new_config

    return {"success": True, "config": {
        "similarity_threshold": new_config.similarity_threshold,
        "contradiction_threshold": new_config.contradiction_threshold,
        "duplicate_threshold": new_config.duplicate_threshold,
        "support_threshold": new_config.support_threshold,
        "confidence_threshold": new_config.confidence_threshold,
        "negation_boost": new_config.negation_boost,
        "max_relations_per_claim": new_config.max_relations_per_claim,
    }}


@router.post("/cluster", response_model=ClusteringResponse)
async def cluster_claims(
    claims: List[ClaimInput],
    similarity_threshold: float = Query(0.8, ge=0.5, le=1.0),
):
    """
    Agrupa claims similares em clusters.

    Algoritmo simples de clustering por similaridade.
    """
    service = _get_inference_service()

    # Convert claims
    claim_objs = [_to_claim(c) for c in claims]

    # Simple single-linkage clustering
    clusters = _cluster_claims(service, claim_objs, similarity_threshold)

    return ClusteringResponse(
        clusters=[
            ClusterResponse(
                cluster_id=c.cluster_id,
                representative_id=c.representative_id,
                member_ids=c.member_ids,
                size=c.size,
                avg_similarity=c.avg_similarity,
                topic=c.topic,
            )
            for c in clusters
        ],
        total_clusters=len(clusters),
        total_claims=len(claims),
    )


@router.post("/deduplicate")
async def deduplicate_claims(
    claims: List[ClaimInput],
    threshold: float = Query(0.95, ge=0.8, le=1.0),
):
    """
    Remove claims duplicados da lista.

    Retorna lista de claims unicos e grupos de duplicados.
    """
    service = _get_inference_service()

    claim_objs = [_to_claim(c) for c in claims]

    # Find duplicates
    seen = set()
    unique = []
    duplicates = []

    for i, claim in enumerate(claim_objs):
        if claim.id in seen:
            continue

        is_duplicate = False
        for j, other in enumerate(claim_objs):
            if i >= j or other.id in seen:
                continue

            sim = service._compute_similarity(claim, other)
            if sim >= threshold:
                is_duplicate = True
                seen.add(other.id)
                duplicates.append({
                    "original_id": claim.id,
                    "duplicate_id": other.id,
                    "similarity": sim,
                })

        if not is_duplicate:
            unique.append(claim.id)
            seen.add(claim.id)

    return {
        "unique_count": len(unique),
        "duplicate_count": len(duplicates),
        "unique_ids": unique,
        "duplicates": duplicates,
        "threshold": threshold,
    }


# Helper functions

def _to_claim(claim_input: ClaimInput) -> Claim:
    """Convert ClaimInput to internal Claim."""
    return Claim(
        id=claim_input.id,
        text=claim_input.text,
        embedding=claim_input.embedding,
        entities=claim_input.entities or [],
        metadata=claim_input.metadata or {},
    )


def _get_relation_description(rt: RelationType) -> str:
    """Get description for relation type."""
    descriptions = {
        RelationType.SUPPORTS: "Claim A apoia ou corrobora claim B",
        RelationType.CONTRADICTS: "Claim A contradiz ou refuta claim B",
        RelationType.RELATED: "Claims relacionados tematicamente",
        RelationType.DUPLICATE: "Claims duplicados ou muito similares",
        RelationType.REFINES: "Claim A especifica ou detalha claim B",
        RelationType.GENERALIZES: "Claim A generaliza claim B",
    }
    return descriptions.get(rt, "")


def _get_method_description(m: InferenceMethod) -> str:
    """Get description for inference method."""
    descriptions = {
        InferenceMethod.MANUAL: "Anotacao manual por humano",
        InferenceMethod.EMBEDDING: "Similaridade por embedding vetorial",
        InferenceMethod.LLM: "Classificacao por modelo de linguagem",
        InferenceMethod.RULE: "Regra heuristica baseada em padroes",
        InferenceMethod.ENTITY: "Match de entidades nomeadas",
    }
    return descriptions.get(m, "")


def _cluster_claims(
    service: RelationInferenceService,
    claims: List[Claim],
    threshold: float,
) -> List[ClaimCluster]:
    """Simple single-linkage clustering."""
    from uuid import uuid4

    if not claims:
        return []

    # Compute similarity matrix
    n = len(claims)
    assigned = [-1] * n
    clusters: List[List[int]] = []

    for i in range(n):
        if assigned[i] >= 0:
            continue

        # Start new cluster
        cluster_idx = len(clusters)
        clusters.append([i])
        assigned[i] = cluster_idx

        # Find all similar claims
        for j in range(i + 1, n):
            if assigned[j] >= 0:
                continue

            sim = service._compute_similarity(claims[i], claims[j])
            if sim >= threshold:
                clusters[cluster_idx].append(j)
                assigned[j] = cluster_idx

    # Convert to ClaimCluster objects
    result = []
    for cluster_indices in clusters:
        if not cluster_indices:
            continue

        member_ids = [claims[i].id for i in cluster_indices]

        # Compute avg similarity within cluster
        avg_sim = 1.0
        if len(cluster_indices) > 1:
            sims = []
            for i, idx_i in enumerate(cluster_indices):
                for idx_j in cluster_indices[i + 1:]:
                    sims.append(service._compute_similarity(
                        claims[idx_i], claims[idx_j]
                    ))
            avg_sim = sum(sims) / len(sims) if sims else 1.0

        result.append(ClaimCluster(
            cluster_id=f"cluster_{uuid4().hex[:8]}",
            representative_id=member_ids[0],  # First as representative
            member_ids=member_ids,
            avg_similarity=avg_sim,
        ))

    return result


# =============================================================================
# S40-BE-012: ClaimGraph Export Endpoint
# =============================================================================

class ClaimGraphExportResponse(BaseModel):
    """Response for ClaimGraph export."""
    version: str
    export_id: str
    domain: str
    claims: List[Dict[str, Any]]
    edges: Optional[List[Dict[str, Any]]] = None
    pagination: Optional[Dict[str, Any]] = None
    exported_at: str
    metadata: Optional[Dict[str, Any]] = None


@router.get("/export", response_model=ClaimGraphExportResponse)
async def export_claimgraph(
    domain: str = Query(..., description="Domain to export"),
    format: str = Query("v1", description="Export format version"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    include_signals: bool = Query(True, description="Include NO-GO signals"),
):
    """
    Export ClaimGraph data (S40-BE-012).

    Returns claims for the specified domain in ClaimGraph export format v1.
    Supports pagination for large datasets.
    """
    from app.claims.export import export_claimgraph_v1
    from app.claims.graph_models import ClaimNode

    if format != "v1":
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    # In production, this would fetch from database
    # For now, return empty export structure
    claims: List[ClaimNode] = []

    export = export_claimgraph_v1(
        claims=claims,
        domain=domain,
        page=page,
        page_size=page_size,
        include_signals=include_signals,
    )

    export_dict = export.to_dict()

    return ClaimGraphExportResponse(
        version=export_dict["version"],
        export_id=export_dict["export_id"],
        domain=export_dict["domain"],
        claims=export_dict["claims"],
        edges=export_dict.get("edges"),
        pagination=export_dict.get("pagination"),
        exported_at=export_dict["exported_at"],
        metadata=export_dict.get("metadata"),
    )


# =============================================================================
# S40-BE-016: NO-GO Signals Endpoint
# =============================================================================

class NOGOSignalResponse(BaseModel):
    """NO-GO signal in API response."""
    signal_id: str
    type: str
    severity: str
    reason: str
    detected_at: str
    resolved: bool
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_reason: Optional[str] = None


class ClaimSignalsResponse(BaseModel):
    """Response for claim signals."""
    claim_id: str
    signals: List[NOGOSignalResponse]
    has_blocking: bool
    total: int


@router.get("/{claim_id}/signals", response_model=ClaimSignalsResponse)
async def get_claim_signals(
    claim_id: str,
    include_resolved: bool = Query(False, description="Include resolved signals"),
):
    """
    Get NO-GO signals for a claim (S40-BE-016).

    Returns all active (and optionally resolved) NO-GO signals for the specified claim.
    """
    from app.claims.signals import get_signal_repository

    repo = get_signal_repository()
    signals = repo.get_by_claim(claim_id, include_resolved=include_resolved)

    return ClaimSignalsResponse(
        claim_id=claim_id,
        signals=[
            NOGOSignalResponse(
                signal_id=s.signal_id,
                type=s.type.value,
                severity=s.severity.value,
                reason=s.reason,
                detected_at=s.detected_at.isoformat(),
                resolved=s.resolved,
                resolved_at=s.resolved_at.isoformat() if s.resolved_at else None,
                resolved_by=s.resolved_by,
                resolution_reason=s.resolution_reason,
            )
            for s in signals
        ],
        has_blocking=repo.has_blocking_signals(claim_id),
        total=len(signals),
    )
