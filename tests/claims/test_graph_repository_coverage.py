"""
Extended tests for ClaimGraph Repository — S37

Additional tests to reach 97%+ coverage.
"""

import pytest
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from app.claims.graph_repository import ClaimGraphRepository, DEFAULT_DB_PATH
from app.claims.graph_models import (
    ClaimState,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
)


class TestGraphRepositoryEdgeCases:
    """Test edge cases and error paths."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_graph.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return ClaimGraphRepository(db_path=temp_db)

    def test_count_edges_with_domain_and_type(self, repo):
        """Test counting edges with domain and type filters."""
        # Create nodes in specific domain
        node1 = GraphNode(
            id="n1",
            node_type=NodeType.CLAIM,
            domain="politics",
            properties={}
        )
        node2 = GraphNode(
            id="n2",
            node_type=NodeType.CLAIM,
            domain="politics",
            properties={}
        )
        repo.insert_node(node1)
        repo.insert_node(node2)

        # Create edge
        edge = GraphEdge(
            id="e1",
            source_id="n1",
            target_id="n2",
            edge_type=EdgeType.SUPPORT,
        )
        repo.insert_edge(edge)

        # Count with domain and type
        count = repo.count_edges(edge_type=EdgeType.SUPPORT, domain="politics")
        assert count == 1

    def test_count_edges_with_domain_no_type(self, repo):
        """Test counting edges with domain filter only."""
        # Create nodes
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        # Create edges of different types
        edge1 = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORT)
        edge2 = GraphEdge(id="e2", source_id="n2", target_id="n1", edge_type=EdgeType.OPPOSITION)
        repo.insert_edge(edge1)
        repo.insert_edge(edge2)

        count = repo.count_edges(domain="test")
        assert count == 2

    def test_count_edges_no_filters(self, repo):
        """Test counting all edges."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="d1", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="d2", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        edge = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORT)
        repo.insert_edge(edge)

        count = repo.count_edges()
        assert count >= 1

    def test_count_edges_by_type_only(self, repo):
        """Test counting edges by type only."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="d1", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="d1", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        edge1 = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORT)
        edge2 = GraphEdge(id="e2", source_id="n2", target_id="n1", edge_type=EdgeType.OPPOSITION)
        repo.insert_edge(edge1)
        repo.insert_edge(edge2)

        count = repo.count_edges(edge_type=EdgeType.SUPPORT)
        assert count >= 1

    def test_get_cluster_nonexistent_center(self, repo):
        """Test get_cluster with nonexistent center node."""
        nodes, edges = repo.get_cluster("nonexistent", depth=2)

        assert nodes == []
        assert edges == []

    def test_get_cluster_depth_zero(self, repo):
        """Test get_cluster with depth 0."""
        node = GraphNode(id="center", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node)

        nodes, edges = repo.get_cluster("center", depth=0)

        assert len(nodes) == 1
        assert nodes[0].id == "center"
        assert edges == []

    def test_get_cluster_filters_edges_correctly(self, repo):
        """Test get_cluster only includes edges between discovered nodes."""
        # Create a cluster: center -> n1, center -> n2, n1 -> external
        center = GraphNode(id="center", node_type=NodeType.CLAIM, domain="test", properties={})
        n1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        n2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="test", properties={})
        external = GraphNode(id="external", node_type=NodeType.CLAIM, domain="test", properties={})

        for node in [center, n1, n2, external]:
            repo.insert_node(node)

        # Edges
        repo.insert_edge(GraphEdge(id="e1", source_id="center", target_id="n1", edge_type=EdgeType.SUPPORT))
        repo.insert_edge(GraphEdge(id="e2", source_id="center", target_id="n2", edge_type=EdgeType.SUPPORT))
        repo.insert_edge(GraphEdge(id="e3", source_id="n1", target_id="external", edge_type=EdgeType.SUPPORT))

        # Get cluster with depth 1 (should not include external)
        nodes, edges = repo.get_cluster("center", depth=1)

        node_ids = {n.id for n in nodes}
        assert "external" not in node_ids

        # Edges should only be between center, n1, n2
        for edge in edges:
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_find_nodes_with_state_filter(self, repo):
        """Test finding nodes with state filter."""
        node1 = GraphNode(
            id="n1",
            node_type=NodeType.CLAIM,
            domain="test",
            properties={"state": ClaimState.VALIDATED.value}
        )
        node2 = GraphNode(
            id="n2",
            node_type=NodeType.CLAIM,
            domain="test",
            properties={"state": ClaimState.REJECTED.value}
        )
        repo.insert_node(node1)
        repo.insert_node(node2)

        results = repo.find_nodes(state=ClaimState.VALIDATED)

        assert len(results) == 1
        assert results[0].id == "n1"

    def test_find_nodes_with_gate_filter(self, repo):
        """Test finding nodes with gate filter."""
        node1 = GraphNode(
            id="n1",
            node_type=NodeType.CLAIM,
            domain="test",
            properties={"gate": "gate1"}
        )
        node2 = GraphNode(
            id="n2",
            node_type=NodeType.CLAIM,
            domain="test",
            properties={"gate": "gate2"}
        )
        repo.insert_node(node1)
        repo.insert_node(node2)

        results = repo.find_nodes(gate="gate1")

        assert len(results) == 1
        assert results[0].id == "n1"

    def test_find_nodes_with_offset(self, repo):
        """Test finding nodes with offset."""
        for i in range(5):
            node = GraphNode(id=f"n{i}", node_type=NodeType.CLAIM, domain="test", properties={})
            repo.insert_node(node)

        results = repo.find_nodes(offset=2, limit=10)

        # Should skip first 2 (ordered by created_at DESC)
        assert len(results) <= 3

    def test_update_node_returns_false_for_nonexistent(self, repo):
        """Test update_node returns False for nonexistent node."""
        updated = repo.update_node("nonexistent", {"new": "data"})

        assert updated is False

    def test_delete_node_returns_false_for_nonexistent(self, repo):
        """Test delete_node returns False for nonexistent node."""
        deleted = repo.delete_node("nonexistent")

        assert deleted is False

    def test_delete_edge_returns_false_for_nonexistent(self, repo):
        """Test delete_edge returns False for nonexistent edge."""
        deleted = repo.delete_edge("nonexistent")

        assert deleted is False

    def test_get_metrics_no_domain(self, repo):
        """Test getting metrics without domain filter."""
        # Create mixed nodes
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="d1", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.ENTITY, domain="d2", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        edge = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.OPPOSITION)
        repo.insert_edge(edge)

        metrics = repo.get_metrics()

        assert metrics.node_count >= 2
        assert metrics.edge_count >= 1
        assert metrics.contradiction_rate > 0

    def test_get_metrics_with_domain(self, repo):
        """Test getting metrics with domain filter."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="politics", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="politics", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        edge = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORT)
        repo.insert_edge(edge)

        metrics = repo.get_metrics(domain="politics")

        assert metrics.claim_count >= 2
        assert metrics.edge_count >= 1

    def test_get_metrics_density_single_node(self, repo):
        """Test density calculation with single node."""
        node = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node)

        metrics = repo.get_metrics()

        assert metrics.cluster_density == 0.0  # No edges possible

    def test_get_metrics_empty_graph(self, repo):
        """Test metrics on empty graph."""
        metrics = repo.get_metrics()

        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.cluster_density == 0.0
        assert metrics.contradiction_rate == 0.0

    def test_get_contradictions_as_target(self, repo):
        """Test getting contradictions where claim is target."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)

        # n1 opposes n2 (so n2 is the target)
        edge = GraphEdge(
            id="e1",
            source_id="n1",
            target_id="n2",
            edge_type=EdgeType.OPPOSITION,
            weight=0.9
        )
        repo.insert_edge(edge)

        # Get contradictions for n2 (as target)
        results = repo.get_contradictions("n2")

        assert len(results) == 1
        assert results[0].opposing_claim_id == "n1"
        assert results[0].strength == 0.9

    def test_get_contradictions_filters_by_strength(self, repo):
        """Test get_contradictions filters by min_strength."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="test", properties={})
        node3 = GraphNode(id="n3", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)
        repo.insert_node(node3)

        # Weak and strong oppositions
        repo.insert_edge(GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.OPPOSITION, weight=0.3))
        repo.insert_edge(GraphEdge(id="e2", source_id="n1", target_id="n3", edge_type=EdgeType.OPPOSITION, weight=0.8))

        results = repo.get_contradictions("n1", min_strength=0.5)

        assert len(results) == 1  # Only the strong one
        assert results[0].opposing_claim_id == "n3"

    def test_count_nodes_multiple_filters(self, repo):
        """Test counting nodes with multiple filters."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="politics", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.ENTITY, domain="politics", properties={})
        node3 = GraphNode(id="n3", node_type=NodeType.CLAIM, domain="economy", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)
        repo.insert_node(node3)

        count = repo.count_nodes(node_type=NodeType.CLAIM, domain="politics")

        assert count == 1

    def test_get_timeline(self, repo):
        """Test getting timeline of claims for a topic."""
        # Create topic node
        topic = GraphNode(id="topic1", node_type=NodeType.TOPIC, domain="test", properties={})
        repo.insert_node(topic)

        # Create claims at different times
        import time
        claim1 = GraphNode(id="c1", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(claim1)
        time.sleep(0.01)
        claim2 = GraphNode(id="c2", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(claim2)

        # Tag claims with topic
        repo.insert_edge(GraphEdge(id="e1", source_id="c1", target_id="topic1", edge_type=EdgeType.TAGGED))
        repo.insert_edge(GraphEdge(id="e2", source_id="c2", target_id="topic1", edge_type=EdgeType.TAGGED))

        timeline = repo.get_timeline("topic1", limit=100)

        assert len(timeline) == 2
        # Should be ordered by created_at ASC
        assert timeline[0].id == "c1"
        assert timeline[1].id == "c2"

    def test_get_edge_not_found(self, repo):
        """Test getting nonexistent edge."""
        result = repo.get_edge("nonexistent")

        assert result is None

    def test_find_edges_multiple_filters(self, repo):
        """Test finding edges with multiple filters."""
        node1 = GraphNode(id="n1", node_type=NodeType.CLAIM, domain="test", properties={})
        node2 = GraphNode(id="n2", node_type=NodeType.CLAIM, domain="test", properties={})
        node3 = GraphNode(id="n3", node_type=NodeType.CLAIM, domain="test", properties={})
        repo.insert_node(node1)
        repo.insert_node(node2)
        repo.insert_node(node3)

        edge1 = GraphEdge(id="e1", source_id="n1", target_id="n2", edge_type=EdgeType.SUPPORT)
        edge2 = GraphEdge(id="e2", source_id="n1", target_id="n3", edge_type=EdgeType.OPPOSITION)
        edge3 = GraphEdge(id="e3", source_id="n2", target_id="n3", edge_type=EdgeType.SUPPORT)
        repo.insert_edge(edge1)
        repo.insert_edge(edge2)
        repo.insert_edge(edge3)

        # Find edges from n1 with SUPPORT type
        results = repo.find_edges(source_id="n1", edge_type=EdgeType.SUPPORT)

        assert len(results) == 1
        assert results[0].id == "e1"
