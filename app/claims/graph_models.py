"""
ClaimGraph Models — S37

Schema: claimgraph_schema_v1

Defines node and edge types for the ClaimGraph relational structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from uuid import uuid4


def _generate_id(prefix: str = "cgn") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class NodeType(str, Enum):
    """Types of nodes in the ClaimGraph."""

    CLAIM = "claim"
    ENTITY = "entity"
    CASE = "case"
    TOPIC = "topic"


class ClaimState(str, Enum):
    """Possible states for a claim node."""

    PENDING = "pending"
    VERIFIED = "verified"
    FALSE = "false"
    DISPUTED = "disputed"
    INCONCLUSIVE = "inconclusive"


class EntityType(str, Enum):
    """Types of entities."""

    PERSON = "person"
    ORGANIZATION = "org"
    PLACE = "place"
    EVENT = "event"
    OTHER = "other"


class EdgeType(str, Enum):
    """Types of edges (relations) in the ClaimGraph."""

    SUPPORT = "support"
    OPPOSITION = "opposition"
    DEPENDENCY = "dependency"
    TEMPORAL = "temporal"
    CAUSALITY = "causality"
    REFUTATION = "refutation"
    REPETITION = "repetition"
    MENTIONS = "mentions"
    BELONGS_TO = "belongs_to"
    TAGGED = "tagged"


# Edge type constraints: which node types can be source/target
EDGE_TYPE_CONSTRAINTS: Dict[EdgeType, Dict[str, List[NodeType]]] = {
    EdgeType.SUPPORT: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.OPPOSITION: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.DEPENDENCY: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.TEMPORAL: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.CAUSALITY: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.REFUTATION: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.REPETITION: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CLAIM],
    },
    EdgeType.MENTIONS: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.ENTITY],
    },
    EdgeType.BELONGS_TO: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.CASE],
    },
    EdgeType.TAGGED: {
        "source": [NodeType.CLAIM],
        "target": [NodeType.TOPIC],
    },
}


@dataclass
class GraphNode:
    """Base node in the ClaimGraph."""

    id: str
    node_type: NodeType
    domain: str
    created_at: datetime
    updated_at: datetime
    properties: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        node_type: NodeType,
        domain: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "GraphNode":
        """Create a new node with auto-generated ID and timestamps."""
        now = datetime.now(timezone.utc)
        return cls(
            id=_generate_id("cgn"),
            node_type=node_type,
            domain=domain,
            created_at=now,
            updated_at=now,
            properties=properties or {},
        )


@dataclass
class ClaimNode(GraphNode):
    """Claim node with typed properties."""

    def __post_init__(self):
        if self.node_type != NodeType.CLAIM:
            self.node_type = NodeType.CLAIM

    @property
    def content(self) -> Optional[str]:
        return self.properties.get("content")

    @property
    def state(self) -> Optional[ClaimState]:
        state_val = self.properties.get("state")
        return ClaimState(state_val) if state_val else None

    @property
    def gate(self) -> Optional[str]:
        return self.properties.get("gate")

    @property
    def evidence_count(self) -> int:
        return self.properties.get("evidence_count", 0)

    @classmethod
    def create(
        cls,
        domain: str,
        content: str,
        state: ClaimState = ClaimState.PENDING,
        gate: Optional[str] = None,
        evidence_count: int = 0,
        extra_properties: Optional[Dict[str, Any]] = None,
    ) -> "ClaimNode":
        """Create a new claim node."""
        now = datetime.now(timezone.utc)
        props = {
            "content": content,
            "state": state.value,
            "gate": gate,
            "evidence_count": evidence_count,
            **(extra_properties or {}),
        }
        node = cls(
            id=_generate_id("clm"),
            node_type=NodeType.CLAIM,
            domain=domain,
            created_at=now,
            updated_at=now,
            properties=props,
        )
        return node


@dataclass
class EntityNode(GraphNode):
    """Entity node (person, org, place)."""

    def __post_init__(self):
        if self.node_type != NodeType.ENTITY:
            self.node_type = NodeType.ENTITY

    @property
    def name(self) -> Optional[str]:
        return self.properties.get("name")

    @property
    def entity_type(self) -> Optional[EntityType]:
        et = self.properties.get("entity_type")
        return EntityType(et) if et else None

    @property
    def aliases(self) -> List[str]:
        return self.properties.get("aliases", [])

    @classmethod
    def create(
        cls,
        domain: str,
        name: str,
        entity_type: EntityType,
        aliases: Optional[List[str]] = None,
    ) -> "EntityNode":
        """Create a new entity node."""
        now = datetime.now(timezone.utc)
        props = {
            "name": name,
            "entity_type": entity_type.value,
            "aliases": aliases or [],
        }
        return cls(
            id=_generate_id("ent"),
            node_type=NodeType.ENTITY,
            domain=domain,
            created_at=now,
            updated_at=now,
            properties=props,
        )


@dataclass
class CaseNode(GraphNode):
    """Case/theme node for grouping claims."""

    def __post_init__(self):
        if self.node_type != NodeType.CASE:
            self.node_type = NodeType.CASE

    @property
    def title(self) -> Optional[str]:
        return self.properties.get("title")

    @property
    def status(self) -> Optional[str]:
        return self.properties.get("status")

    @classmethod
    def create(
        cls,
        domain: str,
        title: str,
        status: str = "open",
    ) -> "CaseNode":
        """Create a new case node."""
        now = datetime.now(timezone.utc)
        props = {
            "title": title,
            "status": status,
        }
        return cls(
            id=_generate_id("cas"),
            node_type=NodeType.CASE,
            domain=domain,
            created_at=now,
            updated_at=now,
            properties=props,
        )


@dataclass
class TopicNode(GraphNode):
    """Topic node for subject classification."""

    def __post_init__(self):
        if self.node_type != NodeType.TOPIC:
            self.node_type = NodeType.TOPIC

    @property
    def name(self) -> Optional[str]:
        return self.properties.get("name")

    @property
    def keywords(self) -> List[str]:
        return self.properties.get("keywords", [])

    @classmethod
    def create(
        cls,
        domain: str,
        name: str,
        keywords: Optional[List[str]] = None,
    ) -> "TopicNode":
        """Create a new topic node."""
        now = datetime.now(timezone.utc)
        props = {
            "name": name,
            "keywords": keywords or [],
        }
        return cls(
            id=_generate_id("top"),
            node_type=NodeType.TOPIC,
            domain=domain,
            created_at=now,
            updated_at=now,
            properties=props,
        )


@dataclass
class GraphEdge:
    """Edge (relation) between nodes in the ClaimGraph."""

    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: Optional[float] = None
    created_at: datetime = field(default_factory=_utcnow)
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.weight is not None and not (0.0 <= self.weight <= 1.0):
            raise ValueError(f"Edge weight must be between 0.0 and 1.0, got {self.weight}")

    @classmethod
    def create(
        cls,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        weight: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "GraphEdge":
        """Create a new edge with auto-generated ID."""
        if source_id == target_id:
            raise ValueError("Self-loops are not allowed")
        return cls(
            id=_generate_id("edg"),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            created_at=_utcnow(),
            properties=properties or {},
        )

    @property
    def confidence(self) -> Optional[float]:
        return self.properties.get("confidence")

    @property
    def source_trace(self) -> Optional[str]:
        return self.properties.get("source_trace")

    @property
    def reason(self) -> Optional[str]:
        return self.properties.get("reason")


@dataclass
class Subgraph:
    """A subset of the ClaimGraph returned by cluster queries."""

    nodes: List[GraphNode]
    edges: List[GraphEdge]
    center_id: str
    depth: int

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def get_density(self) -> float:
        """Calculate cluster density: edges / (nodes * (nodes-1))."""
        n = self.node_count
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1)
        return self.edge_count / max_edges

    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Filter nodes by type."""
        return [n for n in self.nodes if n.node_type == node_type]

    def get_edges_by_type(self, edge_type: EdgeType) -> List[GraphEdge]:
        """Filter edges by type."""
        return [e for e in self.edges if e.edge_type == edge_type]


@dataclass
class ContradictionResult:
    """Result of get_contradictions query."""

    claim_id: str
    opposing_claim_id: str
    strength: float
    edge_id: str


@dataclass
class ClaimGraphMetrics:
    """Aggregate metrics for ClaimGraph."""

    node_count: int
    edge_count: int
    claim_count: int
    entity_count: int
    case_count: int
    topic_count: int
    cluster_density: float
    contradiction_rate: float
    temporal_span_days: Optional[float] = None

    @classmethod
    def empty(cls) -> "ClaimGraphMetrics":
        return cls(
            node_count=0,
            edge_count=0,
            claim_count=0,
            entity_count=0,
            case_count=0,
            topic_count=0,
            cluster_density=0.0,
            contradiction_rate=0.0,
            temporal_span_days=None,
        )


# Schema version constant
CLAIMGRAPH_SCHEMA_VERSION = "claimgraph_schema_v1"
