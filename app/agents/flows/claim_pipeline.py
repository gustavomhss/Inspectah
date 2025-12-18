"""
Claim Pipeline — S37

Integrates claim extraction and processing with ClaimGraph.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.claims.graph_models import ClaimState, EdgeType, EntityType
from app.claims.graph_service import ClaimGraphService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedClaim:
    """Claim data extracted from sources."""

    content: str
    domain: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    evidence_count: int = 0
    entities: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaimPipelineResult:
    """Result of processing a claim through the pipeline."""

    claim_id: str
    status: str  # "created", "updated", "duplicate", "failed"
    entity_ids: List[str] = field(default_factory=list)
    relation_ids: List[str] = field(default_factory=list)
    error: Optional[str] = None


class ClaimPipeline:
    """
    Pipeline for processing claims and integrating with ClaimGraph.

    Flow:
    1. Receive extracted claim
    2. Check for duplicates
    3. Add to ClaimGraph
    4. Extract and link entities
    5. Infer relations (temporal, entity-based)
    """

    def __init__(self, graph_service: Optional[ClaimGraphService] = None):
        self.graph = graph_service or ClaimGraphService()
        self._entity_cache: Dict[str, str] = {}  # name -> entity_id

    def process_claim(self, claim: ExtractedClaim) -> ClaimPipelineResult:
        """
        Process a single claim through the pipeline.

        Args:
            claim: Extracted claim data

        Returns:
            ClaimPipelineResult with IDs and status
        """
        try:
            # 1. Add claim to graph
            claim_id = self.graph.add_claim(
                domain=claim.domain,
                content=claim.content,
                state=ClaimState.PENDING,
                evidence_count=claim.evidence_count,
                extra_properties={
                    "source_id": claim.source_id,
                    "source_url": claim.source_url,
                    "confidence": claim.confidence,
                    "extracted_at": claim.extracted_at.isoformat(),
                    **claim.metadata,
                },
            )
            logger.info(f"Created claim {claim_id} in domain {claim.domain}")

            # 2. Process entities
            entity_ids = self._process_entities(claim_id, claim.domain, claim.entities)

            # 3. Infer relations with existing claims
            relation_ids = self._infer_relations(claim_id, claim.domain)

            return ClaimPipelineResult(
                claim_id=claim_id,
                status="created",
                entity_ids=entity_ids,
                relation_ids=relation_ids,
            )

        except Exception as e:
            logger.error(f"Failed to process claim: {e}")
            return ClaimPipelineResult(
                claim_id="",
                status="failed",
                error=str(e),
            )

    def process_batch(
        self, claims: List[ExtractedClaim]
    ) -> List[ClaimPipelineResult]:
        """
        Process multiple claims in batch.

        Args:
            claims: List of extracted claims

        Returns:
            List of results for each claim
        """
        results = []
        for claim in claims:
            result = self.process_claim(claim)
            results.append(result)
        return results

    def _process_entities(
        self,
        claim_id: str,
        domain: str,
        entities: List[Dict[str, str]],
    ) -> List[str]:
        """Extract entities and link them to the claim."""
        entity_ids = []

        for entity_data in entities:
            name = entity_data.get("name", "")
            entity_type_str = entity_data.get("type", "other")

            if not name:
                continue

            # Map string type to EntityType enum
            type_map = {
                "person": EntityType.PERSON,
                "organization": EntityType.ORGANIZATION,
                "org": EntityType.ORGANIZATION,
                "place": EntityType.PLACE,
                "location": EntityType.PLACE,
                "event": EntityType.EVENT,
            }
            entity_type = type_map.get(entity_type_str.lower(), EntityType.OTHER)

            # Check cache first
            cache_key = f"{domain}:{name.lower()}"
            if cache_key in self._entity_cache:
                entity_id = self._entity_cache[cache_key]
            else:
                # Try to find existing entity
                existing = self.graph.find_entity_by_name(name, domain=domain)
                if existing:
                    entity_id = existing.id
                else:
                    # Create new entity
                    entity_id = self.graph.add_entity(
                        domain=domain,
                        name=name,
                        entity_type=entity_type,
                    )
                    logger.info(f"Created entity {entity_id}: {name}")
                self._entity_cache[cache_key] = entity_id

            # Link claim to entity
            try:
                self.graph.link_claim_to_entity(claim_id, entity_id)
                entity_ids.append(entity_id)
            except Exception as e:
                logger.warning(f"Failed to link claim to entity: {e}")

        return entity_ids

    def _infer_relations(
        self, claim_id: str, domain: str
    ) -> List[str]:
        """
        Infer relations with existing claims based on:
        - Shared entities
        - Temporal proximity
        - Content similarity (future)
        """
        relation_ids = []

        # Get recent claims in same domain
        recent_claims = self.graph.find_claims(domain=domain, limit=50)

        # Get the new claim's entities
        new_claim = self.graph.repo.get_node(claim_id)
        if not new_claim:
            return relation_ids

        new_claim_edges = self.graph.repo.find_edges(
            source_id=claim_id, edge_type=EdgeType.MENTIONS
        )
        new_entity_ids = {e.target_id for e in new_claim_edges}

        for other_claim in recent_claims:
            if other_claim.id == claim_id:
                continue

            # Check for shared entities
            other_edges = self.graph.repo.find_edges(
                source_id=other_claim.id, edge_type=EdgeType.MENTIONS
            )
            other_entity_ids = {e.target_id for e in other_edges}

            shared_entities = new_entity_ids & other_entity_ids
            if shared_entities:
                # Claims share entities - likely related
                # Add temporal relation based on creation time
                try:
                    if new_claim.created_at > other_claim.created_at:
                        edge_id = self.graph.add_temporal_relation(
                            other_claim.id, claim_id
                        )
                    else:
                        edge_id = self.graph.add_temporal_relation(
                            claim_id, other_claim.id
                        )
                    relation_ids.append(edge_id)
                    logger.debug(
                        f"Created temporal relation between {claim_id} and {other_claim.id}"
                    )
                except Exception:
                    # May already exist or other constraint violation
                    logger.debug(f"Failed to create temporal relation between {claim_id} and {other_claim.id}, skipping", exc_info=True)
                    pass

        return relation_ids

    def link_claim_to_case(
        self, claim_id: str, case_id: str
    ) -> str:
        """Link a processed claim to a case."""
        return self.graph.link_claim_to_case(claim_id, case_id)

    def link_claim_to_topic(
        self, claim_id: str, topic_id: str
    ) -> str:
        """Tag a processed claim with a topic."""
        return self.graph.link_claim_to_topic(claim_id, topic_id)

    def add_contradiction(
        self,
        claim_a_id: str,
        claim_b_id: str,
        strength: float = 1.0,
    ) -> str:
        """Mark two claims as contradicting each other."""
        return self.graph.add_opposition_relation(claim_a_id, claim_b_id, weight=strength)

    def add_support(
        self,
        supporting_claim_id: str,
        supported_claim_id: str,
        strength: float = 1.0,
    ) -> str:
        """Mark one claim as supporting another."""
        return self.graph.add_support_relation(
            supporting_claim_id, supported_claim_id, weight=strength
        )


# Singleton instance for convenience
_default_pipeline: Optional[ClaimPipeline] = None


def get_claim_pipeline() -> ClaimPipeline:
    """Get or create the default claim pipeline instance."""
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = ClaimPipeline()
    return _default_pipeline


def process_extracted_claims(
    claims_data: List[Dict[str, Any]],
    domain: str,
) -> List[ClaimPipelineResult]:
    """
    Convenience function to process extracted claims.

    Args:
        claims_data: List of claim dictionaries with keys:
            - content (required)
            - source_id, source_url (optional)
            - confidence (optional, default 1.0)
            - evidence_count (optional, default 0)
            - entities (optional, list of {name, type})
        domain: Domain for all claims

    Returns:
        List of processing results
    """
    pipeline = get_claim_pipeline()
    claims = [
        ExtractedClaim(
            content=c["content"],
            domain=domain,
            source_id=c.get("source_id"),
            source_url=c.get("source_url"),
            confidence=c.get("confidence", 1.0),
            evidence_count=c.get("evidence_count", 0),
            entities=c.get("entities", []),
            metadata=c.get("metadata", {}),
        )
        for c in claims_data
    ]
    return pipeline.process_batch(claims)
