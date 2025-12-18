"""
Tests for ClaimGraph Service — S37

Tests for ClaimGraphService business logic layer.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.claims.graph_models import (
    ClaimNode,
    ClaimState,
    EdgeType,
    EntityType,
    GraphEdge,
    GraphNode,
    NodeType,
    Subgraph,
)
from app.claims.graph_service import ClaimGraphService


class TestClaimGraphServiceInit:
    """Tests for service initialization."""

    def test_init_default(self):
        """Initialize with default repository."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo:
            service = ClaimGraphService()
            assert service.repo is not None

    def test_init_custom_path(self):
        """Initialize with custom path."""
        from pathlib import Path

        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo:
            service = ClaimGraphService(db_path=Path("/custom/path.db"))
            mock_repo.assert_called_once()


class TestClaimOperations:
    """Tests for claim operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.insert_node.return_value = "claim_123"
            mock_repo.get_node.return_value = None
            mock_repo.find_nodes.return_value = []
            mock_repo.update_node.return_value = True
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_add_claim(self, service):
        """Add a new claim."""
        claim_id = service.add_claim(
            domain="politics",
            content="Test claim content",
            state=ClaimState.PENDING,
        )

        assert claim_id == "claim_123"
        service.repo.insert_node.assert_called_once()

    def test_add_claim_with_gate(self, service):
        """Add claim with gate."""
        service.add_claim(
            domain="politics",
            content="Test claim",
            gate="G1",
        )

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert node.properties.get("gate") == "G1"

    def test_add_claim_with_evidence(self, service):
        """Add claim with evidence count."""
        service.add_claim(
            domain="politics",
            content="Test claim",
            evidence_count=5,
        )

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert node.properties.get("evidence_count") == 5

    def test_get_claim_found(self, service):
        """Get existing claim."""
        mock_node = MagicMock(spec=GraphNode)
        mock_node.node_type = NodeType.CLAIM
        service.repo.get_node.return_value = mock_node

        result = service.get_claim("claim_123")

        assert result == mock_node

    def test_get_claim_not_found(self, service):
        """Get unknown claim returns None."""
        service.repo.get_node.return_value = None

        result = service.get_claim("unknown")

        assert result is None

    def test_get_claim_wrong_type(self, service):
        """Get claim returns None if wrong type."""
        mock_node = MagicMock(spec=GraphNode)
        mock_node.node_type = NodeType.ENTITY
        service.repo.get_node.return_value = mock_node

        result = service.get_claim("entity_123")

        assert result is None

    def test_update_claim_state(self, service):
        """Update claim state."""
        mock_node = MagicMock(spec=GraphNode)
        mock_node.node_type = NodeType.CLAIM
        mock_node.properties = {"state": "pending"}
        service.repo.get_node.return_value = mock_node

        result = service.update_claim_state("claim_123", ClaimState.VERIFIED)

        assert result is True
        service.repo.update_node.assert_called_once()

    def test_update_claim_state_not_found(self, service):
        """Update unknown claim returns False."""
        service.repo.get_node.return_value = None

        result = service.update_claim_state("unknown", ClaimState.VERIFIED)

        assert result is False

    def test_find_claims(self, service):
        """Find claims with filters."""
        service.find_claims(domain="politics", state=ClaimState.PENDING)

        service.repo.find_nodes.assert_called_once_with(
            node_type=NodeType.CLAIM,
            domain="politics",
            state=ClaimState.PENDING,
            gate=None,
            limit=100,
        )


class TestEntityOperations:
    """Tests for entity operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.insert_node.return_value = "entity_123"
            mock_repo.find_nodes.return_value = []
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_add_entity(self, service):
        """Add a new entity."""
        entity_id = service.add_entity(
            domain="politics",
            name="John Doe",
            entity_type=EntityType.PERSON,
        )

        assert entity_id == "entity_123"

    def test_add_entity_with_aliases(self, service):
        """Add entity with aliases."""
        service.add_entity(
            domain="politics",
            name="John Doe",
            entity_type=EntityType.PERSON,
            aliases=["JD", "Doe"],
        )

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert node.properties.get("aliases") == ["JD", "Doe"]

    def test_find_entity_by_name(self, service):
        """Find entity by name."""
        mock_entity = MagicMock(spec=GraphNode)
        mock_entity.properties = {"name": "John Doe", "aliases": []}
        service.repo.find_nodes.return_value = [mock_entity]

        result = service.find_entity_by_name("John Doe")

        assert result == mock_entity

    def test_find_entity_by_name_case_insensitive(self, service):
        """Find entity by name is case insensitive."""
        mock_entity = MagicMock(spec=GraphNode)
        mock_entity.properties = {"name": "John Doe", "aliases": []}
        service.repo.find_nodes.return_value = [mock_entity]

        result = service.find_entity_by_name("JOHN DOE")

        assert result == mock_entity

    def test_find_entity_by_alias(self, service):
        """Find entity by alias."""
        mock_entity = MagicMock(spec=GraphNode)
        mock_entity.properties = {"name": "John Doe", "aliases": ["JD"]}
        service.repo.find_nodes.return_value = [mock_entity]

        result = service.find_entity_by_name("JD")

        assert result == mock_entity

    def test_find_entity_not_found(self, service):
        """Find entity returns None if not found."""
        service.repo.find_nodes.return_value = []

        result = service.find_entity_by_name("Unknown")

        assert result is None


class TestCaseOperations:
    """Tests for case operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.insert_node.return_value = "case_123"
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_add_case(self, service):
        """Add a new case."""
        case_id = service.add_case(
            domain="politics",
            title="Election Fraud Case",
        )

        assert case_id == "case_123"

    def test_add_case_with_status(self, service):
        """Add case with status."""
        service.add_case(
            domain="politics",
            title="Test Case",
            status="closed",
        )

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert node.properties.get("status") == "closed"


class TestTopicOperations:
    """Tests for topic operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.insert_node.return_value = "topic_123"
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_add_topic(self, service):
        """Add a new topic."""
        topic_id = service.add_topic(
            domain="politics",
            name="Elections",
        )

        assert topic_id == "topic_123"

    def test_add_topic_with_keywords(self, service):
        """Add topic with keywords."""
        service.add_topic(
            domain="politics",
            name="Elections",
            keywords=["vote", "ballot", "candidate"],
        )

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert "vote" in node.properties.get("keywords", [])


class TestRelationOperations:
    """Tests for relation operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_node.return_value = MagicMock(spec=GraphNode)
            mock_repo.insert_edge.return_value = "edge_123"
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_add_relation(self, service):
        """Add a relation between nodes."""
        edge_id = service.add_relation(
            source_id="claim_1",
            target_id="claim_2",
            relation_type=EdgeType.SUPPORT,
        )

        assert edge_id == "edge_123"

    def test_add_relation_with_weight(self, service):
        """Add weighted relation."""
        service.add_relation(
            source_id="claim_1",
            target_id="claim_2",
            relation_type=EdgeType.OPPOSITION,
            weight=0.8,
        )

        call_args = service.repo.insert_edge.call_args
        edge = call_args[0][0]
        assert edge.weight == 0.8

    def test_add_relation_source_not_found(self, service):
        """Add relation raises if source not found."""
        service.repo.get_node.side_effect = [None, MagicMock()]

        with pytest.raises(ValueError, match="Source node.*not found"):
            service.add_relation("unknown", "target", EdgeType.SUPPORT)

    def test_add_relation_target_not_found(self, service):
        """Add relation raises if target not found."""
        service.repo.get_node.side_effect = [MagicMock(), None]

        with pytest.raises(ValueError, match="Target node.*not found"):
            service.add_relation("source", "unknown", EdgeType.SUPPORT)

    def test_link_claim_to_entity(self, service):
        """Link claim to entity."""
        edge_id = service.link_claim_to_entity("claim_1", "entity_1")

        assert edge_id == "edge_123"

    def test_link_claim_to_case(self, service):
        """Link claim to case."""
        edge_id = service.link_claim_to_case("claim_1", "case_1")

        assert edge_id == "edge_123"

    def test_link_claim_to_topic(self, service):
        """Link claim to topic."""
        edge_id = service.link_claim_to_topic("claim_1", "topic_1")

        assert edge_id == "edge_123"

    def test_add_support_relation(self, service):
        """Add support relation."""
        service.add_support_relation("claim_1", "claim_2", weight=0.9)

        call_args = service.repo.insert_edge.call_args
        edge = call_args[0][0]
        assert edge.edge_type == EdgeType.SUPPORT

    def test_add_opposition_relation(self, service):
        """Add opposition relation."""
        service.add_opposition_relation("claim_1", "claim_2")

        call_args = service.repo.insert_edge.call_args
        edge = call_args[0][0]
        assert edge.edge_type == EdgeType.OPPOSITION

    def test_add_temporal_relation(self, service):
        """Add temporal relation."""
        service.add_temporal_relation("earlier_claim", "later_claim")

        call_args = service.repo.insert_edge.call_args
        edge = call_args[0][0]
        assert edge.edge_type == EdgeType.TEMPORAL


class TestQueryOperations:
    """Tests for query operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_get_cluster(self, service):
        """Get cluster returns subgraph."""
        mock_nodes = [MagicMock(spec=GraphNode)]
        mock_edges = [MagicMock(spec=GraphEdge)]
        service.repo.get_cluster.return_value = (mock_nodes, mock_edges)

        result = service.get_cluster("center_id", depth=2)

        assert isinstance(result, Subgraph)
        assert result.center_id == "center_id"
        assert result.depth == 2

    def test_get_contradictions(self, service):
        """Get contradictions."""
        mock_contradictions = [MagicMock()]
        service.repo.get_contradictions.return_value = mock_contradictions

        result = service.get_contradictions("claim_1", min_strength=0.5)

        assert result == mock_contradictions
        service.repo.get_contradictions.assert_called_once_with(
            "claim_1", min_strength=0.5
        )

    def test_get_timeline(self, service):
        """Get timeline."""
        mock_nodes = [MagicMock(spec=GraphNode)]
        service.repo.get_timeline.return_value = mock_nodes

        result = service.get_timeline("topic_1", limit=50)

        assert result == mock_nodes
        service.repo.get_timeline.assert_called_once_with("topic_1", limit=50)


class TestMetrics:
    """Tests for metrics operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_get_metrics(self, service):
        """Get metrics."""
        mock_metrics = MagicMock()
        service.repo.get_metrics.return_value = mock_metrics

        result = service.get_metrics()

        assert result == mock_metrics

    def test_get_metrics_by_domain(self, service):
        """Get metrics by domain."""
        service.get_metrics(domain="politics")

        service.repo.get_metrics.assert_called_once_with(domain="politics")


class TestBatchOperations:
    """Tests for batch operations."""

    @pytest.fixture
    def service(self):
        """Create service with mock repo."""
        with patch("app.claims.graph_service.ClaimGraphRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.insert_node.side_effect = lambda n: n.id
            mock_repo.get_node.return_value = MagicMock(
                spec=GraphNode,
                node_type=NodeType.CLAIM,
                domain="test",
                created_at=datetime.now(timezone.utc),
            )
            mock_repo.insert_edge.return_value = "edge_123"
            service = ClaimGraphService()
            service.repo = mock_repo
            return service

    def test_bulk_add_claims(self, service):
        """Bulk add claims."""
        claims_data = [
            {"domain": "test", "content": "Claim 1"},
            {"domain": "test", "content": "Claim 2"},
            {"domain": "test", "content": "Claim 3"},
        ]

        ids = service.bulk_add_claims(claims_data)

        assert len(ids) == 3
        assert service.repo.insert_node.call_count == 3

    def test_bulk_add_claims_with_state(self, service):
        """Bulk add claims with state."""
        claims_data = [
            {"domain": "test", "content": "Claim", "state": "verified"},
        ]

        service.bulk_add_claims(claims_data)

        call_args = service.repo.insert_node.call_args
        node = call_args[0][0]
        assert node.properties.get("state") == "verified"

    def test_infer_temporal_relations(self, service):
        """Infer temporal relations."""
        # Create mock nodes with different timestamps
        node1 = MagicMock(spec=GraphNode)
        node1.id = "claim_1"
        node1.node_type = NodeType.CLAIM
        node1.domain = "test"
        node1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        node2 = MagicMock(spec=GraphNode)
        node2.id = "claim_2"
        node2.node_type = NodeType.CLAIM
        node2.domain = "test"
        node2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)

        # First two calls for infer_temporal_relations, then two more for add_relation validation
        service.repo.get_node.side_effect = [node1, node2, node1, node2]

        edge_ids = service.infer_temporal_relations(["claim_1", "claim_2"])

        assert len(edge_ids) == 1

    def test_infer_temporal_relations_different_domains(self, service):
        """No temporal relations between different domains."""
        node1 = MagicMock(spec=GraphNode)
        node1.id = "claim_1"
        node1.node_type = NodeType.CLAIM
        node1.domain = "politics"
        node1.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        node2 = MagicMock(spec=GraphNode)
        node2.id = "claim_2"
        node2.node_type = NodeType.CLAIM
        node2.domain = "health"
        node2.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)

        service.repo.get_node.side_effect = [node1, node2]

        edge_ids = service.infer_temporal_relations(["claim_1", "claim_2"])

        # No edges created because different domains
        assert len(edge_ids) == 0
