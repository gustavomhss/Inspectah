"""
ClaimGraph Service — S37

Business logic layer for ClaimGraph operations.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.claims.graph_models import (
    CaseNode,
    ClaimGraphMetrics,
    ClaimNode,
    ClaimState,
    ContradictionResult,
    EdgeType,
    EntityNode,
    EntityType,
    GraphEdge,
    GraphNode,
    NodeType,
    Subgraph,
    TopicNode,
)
from app.claims.graph_repository import ClaimGraphRepository


class ClaimGraphService:
    """Service for ClaimGraph operations."""

    def __init__(self, db_path: Optional[Path] = None):
        self.repo = ClaimGraphRepository(db_path=db_path)

    # ==================== CLAIM OPERATIONS ====================

    def add_claim(
        self,
        domain: str,
        content: str,
        state: ClaimState = ClaimState.PENDING,
        gate: Optional[str] = None,
        evidence_count: int = 0,
        extra_properties: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a new claim to the graph.

        Args:
            domain: Domain this claim belongs to (e.g., 'pilot_politics')
            content: The claim text/content
            state: Initial state of the claim
            gate: Gate level (G1, G2, G3) if applicable
            evidence_count: Number of supporting evidences
            extra_properties: Additional properties

        Returns:
            The ID of the created claim node
        """
        claim = ClaimNode.create(
            domain=domain,
            content=content,
            state=state,
            gate=gate,
            evidence_count=evidence_count,
            extra_properties=extra_properties,
        )
        return self.repo.insert_node(claim)

    def get_claim(self, claim_id: str) -> Optional[GraphNode]:
        """Get a claim by ID."""
        node = self.repo.get_node(claim_id)
        if node and node.node_type == NodeType.CLAIM:
            return node
        return None

    def update_claim_state(self, claim_id: str, new_state: ClaimState) -> bool:
        """Update a claim's state."""
        node = self.repo.get_node(claim_id)
        if not node or node.node_type != NodeType.CLAIM:
            return False
        props = node.properties.copy()
        props["state"] = new_state.value
        return self.repo.update_node(claim_id, props)

    def find_claims(
        self,
        domain: Optional[str] = None,
        state: Optional[ClaimState] = None,
        gate: Optional[str] = None,
        limit: int = 100,
    ) -> List[GraphNode]:
        """Find claims with optional filters."""
        return self.repo.find_nodes(
            node_type=NodeType.CLAIM,
            domain=domain,
            state=state,
            gate=gate,
            limit=limit,
        )

    # ==================== ENTITY OPERATIONS ====================

    def add_entity(
        self,
        domain: str,
        name: str,
        entity_type: EntityType,
        aliases: Optional[List[str]] = None,
    ) -> str:
        """Add a new entity to the graph."""
        entity = EntityNode.create(
            domain=domain,
            name=name,
            entity_type=entity_type,
            aliases=aliases,
        )
        return self.repo.insert_node(entity)

    def find_entity_by_name(
        self, name: str, domain: Optional[str] = None
    ) -> Optional[GraphNode]:
        """Find an entity by name (case-insensitive)."""
        nodes = self.repo.find_nodes(node_type=NodeType.ENTITY, domain=domain, limit=1000)
        name_lower = name.lower()
        for node in nodes:
            node_name = node.properties.get("name", "")
            if node_name.lower() == name_lower:
                return node
            # Check aliases
            aliases = node.properties.get("aliases", [])
            for alias in aliases:
                if alias.lower() == name_lower:
                    return node
        return None

    # ==================== CASE OPERATIONS ====================

    def add_case(
        self,
        domain: str,
        title: str,
        status: str = "open",
    ) -> str:
        """Add a new case/theme to the graph."""
        case = CaseNode.create(domain=domain, title=title, status=status)
        return self.repo.insert_node(case)

    # ==================== TOPIC OPERATIONS ====================

    def add_topic(
        self,
        domain: str,
        name: str,
        keywords: Optional[List[str]] = None,
    ) -> str:
        """Add a new topic to the graph."""
        topic = TopicNode.create(domain=domain, name=name, keywords=keywords)
        return self.repo.insert_node(topic)

    # ==================== RELATION OPERATIONS ====================

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: EdgeType,
        weight: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a relation between two nodes.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of relation (support, opposition, etc.)
            weight: Optional weight (0.0 to 1.0) for weighted relations
            properties: Additional edge properties

        Returns:
            The ID of the created edge

        Raises:
            ValueError: If self-loop or invalid node types
        """
        # Validate nodes exist
        source = self.repo.get_node(source_id)
        target = self.repo.get_node(target_id)

        if not source:
            raise ValueError(f"Source node {source_id} not found")
        if not target:
            raise ValueError(f"Target node {target_id} not found")

        edge = GraphEdge.create(
            source_id=source_id,
            target_id=target_id,
            edge_type=relation_type,
            weight=weight,
            properties=properties,
        )
        return self.repo.insert_edge(edge)

    def link_claim_to_entity(
        self, claim_id: str, entity_id: str
    ) -> str:
        """Link a claim to an entity it mentions."""
        return self.add_relation(claim_id, entity_id, EdgeType.MENTIONS)

    def link_claim_to_case(self, claim_id: str, case_id: str) -> str:
        """Link a claim to a case it belongs to."""
        return self.add_relation(claim_id, case_id, EdgeType.BELONGS_TO)

    def link_claim_to_topic(self, claim_id: str, topic_id: str) -> str:
        """Tag a claim with a topic."""
        return self.add_relation(claim_id, topic_id, EdgeType.TAGGED)

    def add_support_relation(
        self, supporting_claim_id: str, supported_claim_id: str, weight: float = 1.0
    ) -> str:
        """Add a support relation between two claims."""
        return self.add_relation(
            supporting_claim_id, supported_claim_id, EdgeType.SUPPORT, weight=weight
        )

    def add_opposition_relation(
        self, claim_a_id: str, claim_b_id: str, weight: float = 1.0
    ) -> str:
        """Add an opposition/contradiction relation between two claims."""
        return self.add_relation(
            claim_a_id, claim_b_id, EdgeType.OPPOSITION, weight=weight
        )

    def add_temporal_relation(
        self, earlier_claim_id: str, later_claim_id: str
    ) -> str:
        """Add a temporal ordering relation (earlier -> later)."""
        return self.add_relation(
            earlier_claim_id, later_claim_id, EdgeType.TEMPORAL
        )

    # ==================== QUERY OPERATIONS ====================

    def get_cluster(
        self, node_id: str, depth: int = 2
    ) -> Subgraph:
        """
        Get a subgraph centered on a node.

        Args:
            node_id: Center node ID
            depth: How many hops to expand (default 2)

        Returns:
            Subgraph containing nodes and edges
        """
        nodes, edges = self.repo.get_cluster(node_id, depth=depth)
        return Subgraph(
            nodes=nodes,
            edges=edges,
            center_id=node_id,
            depth=depth,
        )

    def get_contradictions(
        self, claim_id: str, min_strength: float = 0.0
    ) -> List[ContradictionResult]:
        """
        Get claims that contradict the given claim.

        Args:
            claim_id: ID of the claim to find contradictions for
            min_strength: Minimum contradiction strength (0.0 to 1.0)

        Returns:
            List of contradiction results ordered by strength
        """
        return self.repo.get_contradictions(claim_id, min_strength=min_strength)

    def get_timeline(self, topic_id: str, limit: int = 100) -> List[GraphNode]:
        """
        Get claims related to a topic in chronological order.

        Args:
            topic_id: ID of the topic
            limit: Maximum number of claims to return

        Returns:
            List of claim nodes ordered by creation time
        """
        return self.repo.get_timeline(topic_id, limit=limit)

    # ==================== METRICS ====================

    def get_metrics(self, domain: Optional[str] = None) -> ClaimGraphMetrics:
        """
        Get aggregate metrics for the graph.

        Args:
            domain: Optional domain filter

        Returns:
            ClaimGraphMetrics with counts and rates
        """
        return self.repo.get_metrics(domain=domain)

    # ==================== BATCH OPERATIONS ====================

    def bulk_add_claims(
        self, claims_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple claims in batch.

        Args:
            claims_data: List of dicts with claim properties
                Required: domain, content
                Optional: state, gate, evidence_count, extra_properties

        Returns:
            List of created claim IDs
        """
        ids = []
        for data in claims_data:
            claim_id = self.add_claim(
                domain=data["domain"],
                content=data["content"],
                state=ClaimState(data.get("state", "pending")),
                gate=data.get("gate"),
                evidence_count=data.get("evidence_count", 0),
                extra_properties=data.get("extra_properties"),
            )
            ids.append(claim_id)
        return ids

    def infer_temporal_relations(
        self, claim_ids: List[str]
    ) -> List[str]:
        """
        Automatically create temporal relations based on creation time.

        Args:
            claim_ids: List of claim IDs to process

        Returns:
            List of created edge IDs
        """
        # Get nodes and sort by creation time
        nodes = []
        for cid in claim_ids:
            node = self.repo.get_node(cid)
            if node and node.node_type == NodeType.CLAIM:
                nodes.append(node)

        nodes.sort(key=lambda n: n.created_at)

        edge_ids = []
        for i in range(len(nodes) - 1):
            # Only link if same domain
            if nodes[i].domain == nodes[i + 1].domain:
                edge_id = self.add_temporal_relation(nodes[i].id, nodes[i + 1].id)
                edge_ids.append(edge_id)

        return edge_ids
