"""
Tests for ClaimGraph Models — S37

Tests for NodeType, ClaimState, EntityType, EdgeType, GraphNode, ClaimNode,
EntityNode, CaseNode, TopicNode, GraphEdge, Subgraph, and metrics.
"""

import pytest
from datetime import datetime, timezone

from app.claims.graph_models import (
    NodeType,
    ClaimState,
    EntityType,
    EdgeType,
    EDGE_TYPE_CONSTRAINTS,
    GraphNode,
    ClaimNode,
    EntityNode,
    CaseNode,
    TopicNode,
    GraphEdge,
    Subgraph,
    ContradictionResult,
    ClaimGraphMetrics,
    CLAIMGRAPH_SCHEMA_VERSION,
)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_all_node_types_defined(self):
        """All expected node types are defined."""
        expected = ["claim", "entity", "case", "topic"]
        actual = [t.value for t in NodeType]
        assert set(actual) == set(expected)

    def test_node_type_values(self):
        """Node type values match expected strings."""
        assert NodeType.CLAIM.value == "claim"
        assert NodeType.ENTITY.value == "entity"
        assert NodeType.CASE.value == "case"
        assert NodeType.TOPIC.value == "topic"


class TestClaimState:
    """Tests for ClaimState enum."""

    def test_all_states_defined(self):
        """All expected states are defined."""
        expected = ["pending", "verified", "false", "disputed", "inconclusive"]
        actual = [s.value for s in ClaimState]
        assert set(actual) == set(expected)

    def test_state_values(self):
        """State values match expected strings."""
        assert ClaimState.PENDING.value == "pending"
        assert ClaimState.VERIFIED.value == "verified"
        assert ClaimState.FALSE.value == "false"
        assert ClaimState.DISPUTED.value == "disputed"
        assert ClaimState.INCONCLUSIVE.value == "inconclusive"


class TestEntityType:
    """Tests for EntityType enum."""

    def test_all_entity_types_defined(self):
        """All expected entity types are defined."""
        expected = ["person", "org", "place", "event", "other"]
        actual = [t.value for t in EntityType]
        assert set(actual) == set(expected)


class TestEdgeType:
    """Tests for EdgeType enum."""

    def test_all_edge_types_defined(self):
        """All expected edge types are defined."""
        expected = [
            "support", "opposition", "dependency", "temporal",
            "causality", "refutation", "repetition", "mentions",
            "belongs_to", "tagged"
        ]
        actual = [t.value for t in EdgeType]
        assert set(actual) == set(expected)


class TestEdgeTypeConstraints:
    """Tests for edge type constraints."""

    def test_support_constraints(self):
        """Support edge is claim-to-claim."""
        c = EDGE_TYPE_CONSTRAINTS[EdgeType.SUPPORT]
        assert c["source"] == [NodeType.CLAIM]
        assert c["target"] == [NodeType.CLAIM]

    def test_opposition_constraints(self):
        """Opposition edge is claim-to-claim."""
        c = EDGE_TYPE_CONSTRAINTS[EdgeType.OPPOSITION]
        assert c["source"] == [NodeType.CLAIM]
        assert c["target"] == [NodeType.CLAIM]

    def test_mentions_constraints(self):
        """Mentions edge is claim-to-entity."""
        c = EDGE_TYPE_CONSTRAINTS[EdgeType.MENTIONS]
        assert c["source"] == [NodeType.CLAIM]
        assert c["target"] == [NodeType.ENTITY]

    def test_belongs_to_constraints(self):
        """Belongs_to edge is claim-to-case."""
        c = EDGE_TYPE_CONSTRAINTS[EdgeType.BELONGS_TO]
        assert c["source"] == [NodeType.CLAIM]
        assert c["target"] == [NodeType.CASE]

    def test_tagged_constraints(self):
        """Tagged edge is claim-to-topic."""
        c = EDGE_TYPE_CONSTRAINTS[EdgeType.TAGGED]
        assert c["source"] == [NodeType.CLAIM]
        assert c["target"] == [NodeType.TOPIC]

    def test_all_edge_types_have_constraints(self):
        """All edge types have constraints defined."""
        for edge_type in EdgeType:
            assert edge_type in EDGE_TYPE_CONSTRAINTS


class TestGraphNode:
    """Tests for GraphNode base class."""

    def test_create_node(self):
        """Create base graph node."""
        node = GraphNode.create(
            node_type=NodeType.CLAIM,
            domain="politics",
            properties={"key": "value"},
        )
        assert node.id.startswith("cgn_")
        assert node.node_type == NodeType.CLAIM
        assert node.domain == "politics"
        assert node.properties == {"key": "value"}
        assert isinstance(node.created_at, datetime)
        assert isinstance(node.updated_at, datetime)

    def test_create_node_no_properties(self):
        """Create node without properties."""
        node = GraphNode.create(
            node_type=NodeType.ENTITY,
            domain="health",
        )
        assert node.properties == {}

    def test_unique_node_ids(self):
        """Each node gets unique ID."""
        n1 = GraphNode.create(NodeType.CLAIM, "d1")
        n2 = GraphNode.create(NodeType.CLAIM, "d1")
        assert n1.id != n2.id


class TestClaimNode:
    """Tests for ClaimNode class."""

    def test_create_claim_node(self):
        """Create claim node."""
        claim = ClaimNode.create(
            domain="politics",
            content="Test claim content",
            state=ClaimState.PENDING,
            gate="G1",
            evidence_count=5,
        )
        assert claim.id.startswith("clm_")
        assert claim.node_type == NodeType.CLAIM
        assert claim.domain == "politics"
        assert claim.content == "Test claim content"
        assert claim.state == ClaimState.PENDING
        assert claim.gate == "G1"
        assert claim.evidence_count == 5

    def test_create_claim_node_defaults(self):
        """Create claim node with defaults."""
        claim = ClaimNode.create(
            domain="health",
            content="Health claim",
        )
        assert claim.state == ClaimState.PENDING
        assert claim.gate is None
        assert claim.evidence_count == 0

    def test_create_claim_node_extra_properties(self):
        """Create claim node with extra properties."""
        claim = ClaimNode.create(
            domain="politics",
            content="Test",
            extra_properties={"source": "twitter", "reach": 1000},
        )
        assert claim.properties["source"] == "twitter"
        assert claim.properties["reach"] == 1000

    def test_claim_node_state_verified(self):
        """Claim node with verified state."""
        claim = ClaimNode.create(
            domain="politics",
            content="Verified claim",
            state=ClaimState.VERIFIED,
        )
        assert claim.state == ClaimState.VERIFIED

    def test_claim_node_post_init_fixes_type(self):
        """Post init ensures node_type is CLAIM."""
        now = datetime.now(timezone.utc)
        claim = ClaimNode(
            id="test_123",
            node_type=NodeType.ENTITY,  # Wrong type
            domain="test",
            created_at=now,
            updated_at=now,
            properties={},
        )
        assert claim.node_type == NodeType.CLAIM  # Fixed by __post_init__


class TestEntityNode:
    """Tests for EntityNode class."""

    def test_create_entity_person(self):
        """Create person entity node."""
        entity = EntityNode.create(
            domain="politics",
            name="John Doe",
            entity_type=EntityType.PERSON,
            aliases=["JD", "Johnny"],
        )
        assert entity.id.startswith("ent_")
        assert entity.node_type == NodeType.ENTITY
        assert entity.name == "John Doe"
        assert entity.entity_type == EntityType.PERSON
        assert entity.aliases == ["JD", "Johnny"]

    def test_create_entity_organization(self):
        """Create organization entity node."""
        entity = EntityNode.create(
            domain="business",
            name="Acme Corp",
            entity_type=EntityType.ORGANIZATION,
        )
        assert entity.entity_type == EntityType.ORGANIZATION
        assert entity.aliases == []

    def test_create_entity_place(self):
        """Create place entity node."""
        entity = EntityNode.create(
            domain="geography",
            name="New York",
            entity_type=EntityType.PLACE,
        )
        assert entity.entity_type == EntityType.PLACE

    def test_entity_node_post_init_fixes_type(self):
        """Post init ensures node_type is ENTITY."""
        now = datetime.now(timezone.utc)
        entity = EntityNode(
            id="test_123",
            node_type=NodeType.CLAIM,  # Wrong type
            domain="test",
            created_at=now,
            updated_at=now,
            properties={},
        )
        assert entity.node_type == NodeType.ENTITY


class TestCaseNode:
    """Tests for CaseNode class."""

    def test_create_case_node(self):
        """Create case node."""
        case = CaseNode.create(
            domain="politics",
            title="Election Fraud Claims",
            status="open",
        )
        assert case.id.startswith("cas_")
        assert case.node_type == NodeType.CASE
        assert case.title == "Election Fraud Claims"
        assert case.status == "open"

    def test_create_case_default_status(self):
        """Create case with default status."""
        case = CaseNode.create(
            domain="health",
            title="Vaccine Misinformation",
        )
        assert case.status == "open"

    def test_case_node_post_init_fixes_type(self):
        """Post init ensures node_type is CASE."""
        now = datetime.now(timezone.utc)
        case = CaseNode(
            id="test_123",
            node_type=NodeType.CLAIM,
            domain="test",
            created_at=now,
            updated_at=now,
            properties={},
        )
        assert case.node_type == NodeType.CASE


class TestTopicNode:
    """Tests for TopicNode class."""

    def test_create_topic_node(self):
        """Create topic node."""
        topic = TopicNode.create(
            domain="politics",
            name="Elections",
            keywords=["vote", "ballot", "polls"],
        )
        assert topic.id.startswith("top_")
        assert topic.node_type == NodeType.TOPIC
        assert topic.name == "Elections"
        assert topic.keywords == ["vote", "ballot", "polls"]

    def test_create_topic_no_keywords(self):
        """Create topic without keywords."""
        topic = TopicNode.create(
            domain="health",
            name="Vaccines",
        )
        assert topic.keywords == []

    def test_topic_node_post_init_fixes_type(self):
        """Post init ensures node_type is TOPIC."""
        now = datetime.now(timezone.utc)
        topic = TopicNode(
            id="test_123",
            node_type=NodeType.CLAIM,
            domain="test",
            created_at=now,
            updated_at=now,
            properties={},
        )
        assert topic.node_type == NodeType.TOPIC


class TestGraphEdge:
    """Tests for GraphEdge class."""

    def test_create_edge(self):
        """Create graph edge."""
        edge = GraphEdge.create(
            source_id="clm_123",
            target_id="clm_456",
            edge_type=EdgeType.SUPPORT,
            weight=0.8,
            properties={"confidence": 0.9},
        )
        assert edge.id.startswith("edg_")
        assert edge.source_id == "clm_123"
        assert edge.target_id == "clm_456"
        assert edge.edge_type == EdgeType.SUPPORT
        assert edge.weight == 0.8
        assert edge.confidence == 0.9
        assert isinstance(edge.created_at, datetime)

    def test_create_edge_no_weight(self):
        """Create edge without weight."""
        edge = GraphEdge.create(
            source_id="clm_123",
            target_id="clm_456",
            edge_type=EdgeType.OPPOSITION,
        )
        assert edge.weight is None

    def test_create_edge_self_loop_raises(self):
        """Self-loop raises error."""
        with pytest.raises(ValueError, match="Self-loops are not allowed"):
            GraphEdge.create(
                source_id="clm_123",
                target_id="clm_123",
                edge_type=EdgeType.SUPPORT,
            )

    def test_edge_weight_validation_too_low(self):
        """Weight below 0 raises error."""
        with pytest.raises(ValueError, match="Edge weight must be between"):
            GraphEdge(
                id="test",
                source_id="s",
                target_id="t",
                edge_type=EdgeType.SUPPORT,
                weight=-0.1,
            )

    def test_edge_weight_validation_too_high(self):
        """Weight above 1 raises error."""
        with pytest.raises(ValueError, match="Edge weight must be between"):
            GraphEdge(
                id="test",
                source_id="s",
                target_id="t",
                edge_type=EdgeType.SUPPORT,
                weight=1.1,
            )

    def test_edge_weight_boundary_valid(self):
        """Weight at boundaries is valid."""
        edge0 = GraphEdge.create("s", "t1", EdgeType.SUPPORT, weight=0.0)
        edge1 = GraphEdge.create("s", "t2", EdgeType.SUPPORT, weight=1.0)
        assert edge0.weight == 0.0
        assert edge1.weight == 1.0

    def test_edge_properties(self):
        """Edge property accessors."""
        edge = GraphEdge.create(
            source_id="s",
            target_id="t",
            edge_type=EdgeType.REFUTATION,
            properties={
                "confidence": 0.85,
                "source_trace": "trace_123",
                "reason": "Contradicts evidence",
            },
        )
        assert edge.confidence == 0.85
        assert edge.source_trace == "trace_123"
        assert edge.reason == "Contradicts evidence"

    def test_unique_edge_ids(self):
        """Each edge gets unique ID."""
        e1 = GraphEdge.create("s", "t1", EdgeType.SUPPORT)
        e2 = GraphEdge.create("s", "t2", EdgeType.SUPPORT)
        assert e1.id != e2.id


class TestSubgraph:
    """Tests for Subgraph class."""

    def test_subgraph_counts(self):
        """Subgraph node and edge counts."""
        nodes = [
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.ENTITY, "d1"),
        ]
        edges = [
            GraphEdge.create(nodes[0].id, nodes[1].id, EdgeType.SUPPORT),
        ]
        subgraph = Subgraph(
            nodes=nodes,
            edges=edges,
            center_id=nodes[0].id,
            depth=1,
        )
        assert subgraph.node_count == 3
        assert subgraph.edge_count == 1

    def test_subgraph_density_empty(self):
        """Density of single node subgraph is 0."""
        nodes = [GraphNode.create(NodeType.CLAIM, "d1")]
        subgraph = Subgraph(nodes=nodes, edges=[], center_id=nodes[0].id, depth=0)
        assert subgraph.get_density() == 0.0

    def test_subgraph_density_calculation(self):
        """Calculate density correctly."""
        nodes = [
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
        ]
        edges = [
            GraphEdge.create(nodes[0].id, nodes[1].id, EdgeType.SUPPORT),
            GraphEdge.create(nodes[1].id, nodes[2].id, EdgeType.SUPPORT),
            GraphEdge.create(nodes[0].id, nodes[2].id, EdgeType.SUPPORT),
        ]
        subgraph = Subgraph(nodes=nodes, edges=edges, center_id=nodes[0].id, depth=1)
        # max_edges = 3 * 2 = 6, actual = 3, density = 0.5
        assert subgraph.get_density() == 0.5

    def test_subgraph_get_nodes_by_type(self):
        """Filter nodes by type."""
        nodes = [
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.ENTITY, "d1"),
            GraphNode.create(NodeType.CASE, "d1"),
        ]
        subgraph = Subgraph(nodes=nodes, edges=[], center_id=nodes[0].id, depth=1)

        claims = subgraph.get_nodes_by_type(NodeType.CLAIM)
        entities = subgraph.get_nodes_by_type(NodeType.ENTITY)
        cases = subgraph.get_nodes_by_type(NodeType.CASE)
        topics = subgraph.get_nodes_by_type(NodeType.TOPIC)

        assert len(claims) == 2
        assert len(entities) == 1
        assert len(cases) == 1
        assert len(topics) == 0

    def test_subgraph_get_edges_by_type(self):
        """Filter edges by type."""
        nodes = [
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
            GraphNode.create(NodeType.CLAIM, "d1"),
        ]
        edges = [
            GraphEdge.create(nodes[0].id, nodes[1].id, EdgeType.SUPPORT),
            GraphEdge.create(nodes[1].id, nodes[2].id, EdgeType.OPPOSITION),
            GraphEdge.create(nodes[0].id, nodes[2].id, EdgeType.SUPPORT),
        ]
        subgraph = Subgraph(nodes=nodes, edges=edges, center_id=nodes[0].id, depth=1)

        support_edges = subgraph.get_edges_by_type(EdgeType.SUPPORT)
        opposition_edges = subgraph.get_edges_by_type(EdgeType.OPPOSITION)
        dependency_edges = subgraph.get_edges_by_type(EdgeType.DEPENDENCY)

        assert len(support_edges) == 2
        assert len(opposition_edges) == 1
        assert len(dependency_edges) == 0


class TestContradictionResult:
    """Tests for ContradictionResult class."""

    def test_create_contradiction_result(self):
        """Create contradiction result."""
        result = ContradictionResult(
            claim_id="clm_123",
            opposing_claim_id="clm_456",
            strength=0.9,
            edge_id="edg_789",
        )
        assert result.claim_id == "clm_123"
        assert result.opposing_claim_id == "clm_456"
        assert result.strength == 0.9
        assert result.edge_id == "edg_789"


class TestClaimGraphMetrics:
    """Tests for ClaimGraphMetrics class."""

    def test_create_metrics(self):
        """Create metrics."""
        metrics = ClaimGraphMetrics(
            node_count=100,
            edge_count=250,
            claim_count=60,
            entity_count=30,
            case_count=5,
            topic_count=5,
            cluster_density=0.42,
            contradiction_rate=0.15,
            temporal_span_days=30.5,
        )
        assert metrics.node_count == 100
        assert metrics.edge_count == 250
        assert metrics.claim_count == 60
        assert metrics.entity_count == 30
        assert metrics.case_count == 5
        assert metrics.topic_count == 5
        assert metrics.cluster_density == 0.42
        assert metrics.contradiction_rate == 0.15
        assert metrics.temporal_span_days == 30.5

    def test_empty_metrics(self):
        """Create empty metrics."""
        metrics = ClaimGraphMetrics.empty()
        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.claim_count == 0
        assert metrics.entity_count == 0
        assert metrics.case_count == 0
        assert metrics.topic_count == 0
        assert metrics.cluster_density == 0.0
        assert metrics.contradiction_rate == 0.0
        assert metrics.temporal_span_days is None


class TestSchemaVersion:
    """Tests for schema version constant."""

    def test_schema_version(self):
        """Schema version is defined."""
        assert CLAIMGRAPH_SCHEMA_VERSION == "claimgraph_schema_v1"
