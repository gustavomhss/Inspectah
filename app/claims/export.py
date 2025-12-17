"""
Sprint 40: ClaimGraph Export functionality.

Tasks: S40-BE-011, S40-BE-013
Export and ingest ClaimGraph data for P2->P3 pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.claims.graph_models import ClaimNode, GraphEdge, EdgeType, ClaimState

logger = logging.getLogger(__name__)


def _generate_export_id() -> str:
    """Generate a unique export ID."""
    return str(uuid4())


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass
class ClaimPrior:
    """Prior probabilistic estimate for a claim."""

    probability: float  # 0-1
    confidence: float  # 0-1
    source: str  # model, expert, crowd, official, hybrid
    model_version: Optional[str] = None
    computed_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probability": self.probability,
            "confidence": self.confidence,
            "source": self.source,
            "model_version": self.model_version,
            "computed_at": self.computed_at.isoformat(),
        }


@dataclass
class EvidenceItem:
    """Evidence item in the evidence trail."""

    evidence_id: str
    type: str  # source, fact_check, expert_opinion, official_data, etc.
    stance: str  # supports, refutes, neutral, unclear
    weight: float = 0.5
    url: Optional[str] = None
    snippet: Optional[str] = None
    collected_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "type": self.type,
            "stance": self.stance,
            "weight": self.weight,
            "url": self.url,
            "snippet": self.snippet,
            "collected_at": self.collected_at.isoformat(),
        }


@dataclass
class NOGOSignal:
    """NO-GO signal (S40-BE-014)."""

    type: str  # INCONSISTENCY, SUSPICION, ABUSE
    severity: str  # low, medium, high, critical
    reason: str
    detected_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "reason": self.reason,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class ClaimExportItem:
    """A claim formatted for export."""

    claim_id: str
    text: str
    prior: ClaimPrior
    evidence_trail: List[EvidenceItem]
    current_state: str
    created_at: datetime
    normalized_text: Optional[str] = None
    signals: List[NOGOSignal] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    source_refs: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "claim_id": self.claim_id,
            "text": self.text,
            "prior": self.prior.to_dict(),
            "evidence_trail": [e.to_dict() for e in self.evidence_trail],
            "current_state": self.current_state,
            "created_at": self.created_at.isoformat(),
        }
        if self.normalized_text:
            result["normalized_text"] = self.normalized_text
        if self.signals:
            result["signals"] = [s.to_dict() for s in self.signals]
        if self.relations:
            result["relations"] = self.relations
        if self.source_refs:
            result["source_refs"] = self.source_refs
        if self.updated_at:
            result["updated_at"] = self.updated_at.isoformat()
        return result


@dataclass
class ClaimGraphExport:
    """Complete ClaimGraph export (S40-BE-011)."""

    version: str = "1.0"
    export_id: str = field(default_factory=_generate_export_id)
    domain: str = ""
    claims: List[ClaimExportItem] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    exported_at: datetime = field(default_factory=_utcnow)
    pagination: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "version": self.version,
            "export_id": self.export_id,
            "domain": self.domain,
            "claims": [c.to_dict() for c in self.claims],
            "exported_at": self.exported_at.isoformat(),
        }
        if self.edges:
            result["edges"] = self.edges
        if self.pagination:
            result["pagination"] = self.pagination
        if self.metadata:
            result["metadata"] = self.metadata
        return result


def _map_claim_state(state: ClaimState) -> str:
    """Map ClaimState to export format."""
    mapping = {
        ClaimState.PENDING: "CLAIMED",
        ClaimState.VERIFIED: "ESTABLISHED_FACT",
        ClaimState.FALSE: "RETRACTED",
        ClaimState.DISPUTED: "UNDER_DISPUTE",
        ClaimState.INCONCLUSIVE: "UNDER_REVIEW",
    }
    return mapping.get(state, "UNKNOWN")


def _map_edge_type(edge_type: EdgeType) -> str:
    """Map EdgeType to export relation type."""
    mapping = {
        EdgeType.SUPPORT: "supports",
        EdgeType.OPPOSITION: "contradicts",
        EdgeType.REFUTATION: "contradicts",
        EdgeType.DEPENDENCY: "implies",
        EdgeType.CAUSALITY: "implies",
        EdgeType.TEMPORAL: "derived_from",
        EdgeType.REPETITION: "derived_from",
    }
    return mapping.get(edge_type, "supports")


def export_claimgraph_v1(
    claims: List[ClaimNode],
    edges: Optional[List[GraphEdge]] = None,
    domain: str = "default",
    page: int = 1,
    page_size: int = 100,
    include_signals: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> ClaimGraphExport:
    """
    Export ClaimGraph to v1 format (S40-BE-011).

    Args:
        claims: List of ClaimNode objects to export
        edges: Optional list of GraphEdge objects
        domain: Domain of the export
        page: Current page number
        page_size: Number of claims per page
        include_signals: Whether to include NO-GO signals
        metadata: Optional metadata to include

    Returns:
        ClaimGraphExport object ready for serialization
    """
    # Convert claims to export format
    export_claims: List[ClaimExportItem] = []

    for claim in claims:
        # Create default prior if not present
        prior_data = claim.properties.get("prior", {})
        prior = ClaimPrior(
            probability=prior_data.get("probability", 0.5),
            confidence=prior_data.get("confidence", 0.5),
            source=prior_data.get("source", "model"),
            model_version=prior_data.get("model_version"),
        )

        # Get evidence trail
        evidence_data = claim.properties.get("evidence_trail", [])
        evidence_trail = [
            EvidenceItem(
                evidence_id=e.get("evidence_id", f"ev_{i}"),
                type=e.get("type", "source"),
                stance=e.get("stance", "unclear"),
                weight=e.get("weight", 0.5),
                url=e.get("url"),
                snippet=e.get("snippet"),
            )
            for i, e in enumerate(evidence_data)
        ]

        # Get signals
        signals: List[NOGOSignal] = []
        if include_signals:
            signal_data = claim.properties.get("signals", [])
            signals = [
                NOGOSignal(
                    type=s.get("type", "SUSPICION"),
                    severity=s.get("severity", "low"),
                    reason=s.get("reason", ""),
                )
                for s in signal_data
            ]

        # Map state
        state = claim.state
        export_state = _map_claim_state(state) if state else "UNKNOWN"

        # Create export item
        export_item = ClaimExportItem(
            claim_id=claim.id,
            text=claim.content or "",
            prior=prior,
            evidence_trail=evidence_trail,
            current_state=export_state,
            created_at=claim.created_at,
            normalized_text=claim.properties.get("normalized_text"),
            signals=signals,
            source_refs=claim.properties.get("source_refs", []),
            updated_at=claim.updated_at,
        )
        export_claims.append(export_item)

    # Convert edges
    export_edges: List[Dict[str, Any]] = []
    if edges:
        for edge in edges:
            export_edge = {
                "edge_id": edge.id,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "relation_type": _map_edge_type(edge.edge_type),
                "weight": edge.weight or 0.5,
            }
            if edge.properties:
                export_edge["metadata"] = edge.properties
            export_edges.append(export_edge)

    # Create pagination info
    total_claims = len(claims)
    total_pages = (total_claims + page_size - 1) // page_size if page_size > 0 else 1
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_claims": total_claims,
        "total_pages": total_pages,
        "has_next": page < total_pages,
    }

    # Create export
    export = ClaimGraphExport(
        domain=domain,
        claims=export_claims,
        edges=export_edges,
        pagination=pagination,
        metadata=metadata or {},
    )

    logger.info(f"Exported {len(export_claims)} claims for domain {domain}")

    return export


def ingest_claimgraph_export(
    export_data: Dict[str, Any],
    validate: bool = True,
) -> List[ClaimExportItem]:
    """
    Ingest a ClaimGraph export (S40-BE-013).

    Args:
        export_data: Dict from ClaimGraphExport.to_dict() or JSON
        validate: Whether to validate the data

    Returns:
        List of ClaimExportItem objects

    Raises:
        ValueError: If validation fails
    """
    if validate:
        # Basic validation
        if export_data.get("version") != "1.0":
            raise ValueError(f"Unsupported export version: {export_data.get('version')}")
        if "claims" not in export_data:
            raise ValueError("Missing 'claims' field in export")

    claims: List[ClaimExportItem] = []

    for claim_data in export_data.get("claims", []):
        # Parse prior
        prior_data = claim_data.get("prior", {})
        prior = ClaimPrior(
            probability=prior_data.get("probability", 0.5),
            confidence=prior_data.get("confidence", 0.5),
            source=prior_data.get("source", "model"),
            model_version=prior_data.get("model_version"),
        )

        # Parse evidence trail
        evidence_trail = []
        for e in claim_data.get("evidence_trail", []):
            evidence_trail.append(
                EvidenceItem(
                    evidence_id=e.get("evidence_id", ""),
                    type=e.get("type", "source"),
                    stance=e.get("stance", "unclear"),
                    weight=e.get("weight", 0.5),
                    url=e.get("url"),
                    snippet=e.get("snippet"),
                )
            )

        # Parse signals
        signals = []
        for s in claim_data.get("signals", []):
            signals.append(
                NOGOSignal(
                    type=s.get("type", "SUSPICION"),
                    severity=s.get("severity", "low"),
                    reason=s.get("reason", ""),
                )
            )

        # Create claim item
        claim = ClaimExportItem(
            claim_id=claim_data.get("claim_id", ""),
            text=claim_data.get("text", ""),
            prior=prior,
            evidence_trail=evidence_trail,
            current_state=claim_data.get("current_state", "UNKNOWN"),
            created_at=datetime.fromisoformat(claim_data.get("created_at", _utcnow().isoformat())),
            normalized_text=claim_data.get("normalized_text"),
            signals=signals,
            relations=claim_data.get("relations", []),
            source_refs=claim_data.get("source_refs", []),
        )
        claims.append(claim)

    logger.info(f"Ingested {len(claims)} claims from export")

    return claims
