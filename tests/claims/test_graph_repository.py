"""
Tests for ClaimGraph Repository — S37

Tests for ClaimGraphRepository persistence operations.
"""

import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.claims.graph_models import (
    ClaimNode,
    ClaimState,
    EdgeType,
    EntityNode,
    EntityType,
    GraphEdge,
    GraphNode,
    NodeType,
    TopicNode,
)
from app.claims.graph_repository import ClaimGraphRepository


class TestClaimGraphRepositoryInit:
    """Tests for repository initialization."""

    def test_init_default_path(self):
        """Initialize with default path."""
        with patch.object(ClaimGraphRepository, "_ensure_db"):
            repo = ClaimGraphRepository()
            assert repo.db_path is not None

    def test_init_custom_path(self):
        """Initialize with custom path."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as f:
            with patch.object(ClaimGraphRepository, "_ensure_db"):
                repo = ClaimGraphRepository(db_path=Path(f.name))
                assert repo.db_path == Path(f.name)


class TestNodeOperations:
    """Tests for node CRUD operations."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with temp database."""
        db_path = tmp_path / "test.sqlite"
        # Create simple schema
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE claimgraph_nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                domain TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE claimgraph_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL,
                created_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(ClaimGraphRepository, "_ensure_db"):
            repo = ClaimGraphRepository(db_path=db_path)
            return repo

    def test_insert_node(self, repo):
        """Insert a node."""
        node = ClaimNode.create(
            domain="test",
            content="Test claim",
            state=ClaimState.PENDING,
        )

        node_id = repo.insert_node(node)
        assert node_id == node.id

    def test_get_node(self, repo):
        """Get node by ID."""
        node = ClaimNode.create(
            domain="test",
            content="Test claim",
        )
        repo.insert_node(node)

        found = repo.get_node(node.id)
        assert found is not None
        assert found.id == node.id
        assert found.node_type == NodeType.CLAIM

    def test_get_node_not_found(self, repo):
        """Get unknown node returns None."""
        found = repo.get_node("unknown_id")
        assert found is None

    def test_find_nodes_all(self, repo):
        """Find all nodes."""
        for i in range(3):
            node = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(node)

        nodes = repo.find_nodes()
        assert len(nodes) == 3

    def test_find_nodes_by_type(self, repo):
        """Find nodes by type."""
        claim = ClaimNode.create(domain="test", content="Claim")
        entity = EntityNode.create(domain="test", name="Entity", entity_type=EntityType.PERSON)

        repo.insert_node(claim)
        repo.insert_node(entity)

        claims = repo.find_nodes(node_type=NodeType.CLAIM)
        entities = repo.find_nodes(node_type=NodeType.ENTITY)

        assert len(claims) == 1
        assert len(entities) == 1

    def test_find_nodes_by_domain(self, repo):
        """Find nodes by domain."""
        node1 = ClaimNode.create(domain="politics", content="Claim 1")
        node2 = ClaimNode.create(domain="health", content="Claim 2")

        repo.insert_node(node1)
        repo.insert_node(node2)

        politics = repo.find_nodes(domain="politics")
        health = repo.find_nodes(domain="health")

        assert len(politics) == 1
        assert len(health) == 1

    def test_find_nodes_limit(self, repo):
        """Find nodes respects limit."""
        for i in range(10):
            node = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(node)

        nodes = repo.find_nodes(limit=5)
        assert len(nodes) == 5

    def test_find_nodes_offset(self, repo):
        """Find nodes respects offset."""
        for i in range(10):
            node = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(node)

        nodes = repo.find_nodes(limit=5, offset=5)
        assert len(nodes) == 5

    def test_update_node(self, repo):
        """Update node properties."""
        node = ClaimNode.create(
            domain="test",
            content="Original",
            state=ClaimState.PENDING,
        )
        repo.insert_node(node)

        new_props = {"content": "Updated", "state": "verified"}
        updated = repo.update_node(node.id, new_props)

        assert updated is True

        found = repo.get_node(node.id)
        assert found.properties["content"] == "Updated"

    def test_update_node_not_found(self, repo):
        """Update unknown node returns False."""
        updated = repo.update_node("unknown_id", {})
        assert updated is False

    def test_delete_node(self, repo):
        """Delete a node."""
        node = ClaimNode.create(domain="test", content="To delete")
        repo.insert_node(node)

        deleted = repo.delete_node(node.id)
        assert deleted is True

        found = repo.get_node(node.id)
        assert found is None

    def test_delete_node_not_found(self, repo):
        """Delete unknown node returns False."""
        deleted = repo.delete_node("unknown_id")
        assert deleted is False

    def test_count_nodes_all(self, repo):
        """Count all nodes."""
        for i in range(5):
            node = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(node)

        count = repo.count_nodes()
        assert count == 5

    def test_count_nodes_by_type(self, repo):
        """Count nodes by type."""
        for i in range(3):
            claim = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(claim)

        entity = EntityNode.create(domain="test", name="Entity", entity_type=EntityType.PERSON)
        repo.insert_node(entity)

        claim_count = repo.count_nodes(node_type=NodeType.CLAIM)
        entity_count = repo.count_nodes(node_type=NodeType.ENTITY)

        assert claim_count == 3
        assert entity_count == 1


class TestEdgeOperations:
    """Tests for edge CRUD operations."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with temp database."""
        db_path = tmp_path / "test.sqlite"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE claimgraph_nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                domain TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE claimgraph_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL,
                created_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(ClaimGraphRepository, "_ensure_db"):
            repo = ClaimGraphRepository(db_path=db_path)
            return repo

    def test_insert_edge(self, repo):
        """Insert an edge."""
        edge = GraphEdge.create(
            source_id="node_1",
            target_id="node_2",
            edge_type=EdgeType.SUPPORT,
        )

        edge_id = repo.insert_edge(edge)
        assert edge_id == edge.id

    def test_get_edge(self, repo):
        """Get edge by ID."""
        edge = GraphEdge.create(
            source_id="node_1",
            target_id="node_2",
            edge_type=EdgeType.OPPOSITION,
            weight=0.8,
        )
        repo.insert_edge(edge)

        found = repo.get_edge(edge.id)
        assert found is not None
        assert found.id == edge.id
        assert found.edge_type == EdgeType.OPPOSITION

    def test_get_edge_not_found(self, repo):
        """Get unknown edge returns None."""
        found = repo.get_edge("unknown_id")
        assert found is None

    def test_find_edges_all(self, repo):
        """Find all edges."""
        for i in range(3):
            edge = GraphEdge.create(
                source_id=f"source_{i}",
                target_id=f"target_{i}",
                edge_type=EdgeType.MENTIONS,
            )
            repo.insert_edge(edge)

        edges = repo.find_edges()
        assert len(edges) == 3

    def test_find_edges_by_source(self, repo):
        """Find edges by source."""
        e1 = GraphEdge.create("source_A", "target_1", EdgeType.SUPPORT)
        e2 = GraphEdge.create("source_A", "target_2", EdgeType.SUPPORT)
        e3 = GraphEdge.create("source_B", "target_1", EdgeType.SUPPORT)

        repo.insert_edge(e1)
        repo.insert_edge(e2)
        repo.insert_edge(e3)

        edges = repo.find_edges(source_id="source_A")
        assert len(edges) == 2

    def test_find_edges_by_target(self, repo):
        """Find edges by target."""
        e1 = GraphEdge.create("source_1", "target_A", EdgeType.SUPPORT)
        e2 = GraphEdge.create("source_2", "target_A", EdgeType.SUPPORT)
        e3 = GraphEdge.create("source_1", "target_B", EdgeType.SUPPORT)

        repo.insert_edge(e1)
        repo.insert_edge(e2)
        repo.insert_edge(e3)

        edges = repo.find_edges(target_id="target_A")
        assert len(edges) == 2

    def test_find_edges_by_type(self, repo):
        """Find edges by type."""
        e1 = GraphEdge.create("s1", "t1", EdgeType.SUPPORT)
        e2 = GraphEdge.create("s2", "t2", EdgeType.OPPOSITION)

        repo.insert_edge(e1)
        repo.insert_edge(e2)

        support = repo.find_edges(edge_type=EdgeType.SUPPORT)
        opposition = repo.find_edges(edge_type=EdgeType.OPPOSITION)

        assert len(support) == 1
        assert len(opposition) == 1

    def test_delete_edge(self, repo):
        """Delete an edge."""
        edge = GraphEdge.create("s", "t", EdgeType.MENTIONS)
        repo.insert_edge(edge)

        deleted = repo.delete_edge(edge.id)
        assert deleted is True

        found = repo.get_edge(edge.id)
        assert found is None

    def test_count_edges_all(self, repo):
        """Count all edges."""
        for i in range(4):
            edge = GraphEdge.create(f"s{i}", f"t{i}", EdgeType.SUPPORT)
            repo.insert_edge(edge)

        count = repo.count_edges()
        assert count == 4

    def test_count_edges_by_type(self, repo):
        """Count edges by type."""
        for i in range(3):
            repo.insert_edge(GraphEdge.create(f"s{i}", f"t{i}", EdgeType.SUPPORT))
        for i in range(2):
            repo.insert_edge(GraphEdge.create(f"x{i}", f"y{i}", EdgeType.OPPOSITION))

        support_count = repo.count_edges(edge_type=EdgeType.SUPPORT)
        opposition_count = repo.count_edges(edge_type=EdgeType.OPPOSITION)

        assert support_count == 3
        assert opposition_count == 2


class TestGraphQueries:
    """Tests for graph query operations."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with temp database."""
        db_path = tmp_path / "test.sqlite"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE claimgraph_nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                domain TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE claimgraph_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL,
                created_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(ClaimGraphRepository, "_ensure_db"):
            repo = ClaimGraphRepository(db_path=db_path)
            return repo

    def test_get_cluster_single_node(self, repo):
        """Get cluster with single node."""
        node = ClaimNode.create(domain="test", content="Center")
        repo.insert_node(node)

        nodes, edges = repo.get_cluster(node.id, depth=1)

        assert len(nodes) == 1
        assert len(edges) == 0

    def test_get_cluster_with_edges(self, repo):
        """Get cluster with connected nodes."""
        center = ClaimNode.create(domain="test", content="Center")
        neighbor1 = ClaimNode.create(domain="test", content="Neighbor 1")
        neighbor2 = ClaimNode.create(domain="test", content="Neighbor 2")

        repo.insert_node(center)
        repo.insert_node(neighbor1)
        repo.insert_node(neighbor2)

        edge1 = GraphEdge.create(center.id, neighbor1.id, EdgeType.SUPPORT)
        edge2 = GraphEdge.create(center.id, neighbor2.id, EdgeType.SUPPORT)

        repo.insert_edge(edge1)
        repo.insert_edge(edge2)

        nodes, edges = repo.get_cluster(center.id, depth=1)

        assert len(nodes) == 3
        assert len(edges) == 2

    def test_get_cluster_depth_limit(self, repo):
        """Get cluster respects depth limit."""
        n1 = ClaimNode.create(domain="test", content="N1")
        n2 = ClaimNode.create(domain="test", content="N2")
        n3 = ClaimNode.create(domain="test", content="N3")

        repo.insert_node(n1)
        repo.insert_node(n2)
        repo.insert_node(n3)

        repo.insert_edge(GraphEdge.create(n1.id, n2.id, EdgeType.SUPPORT))
        repo.insert_edge(GraphEdge.create(n2.id, n3.id, EdgeType.SUPPORT))

        # Depth 1 should only get n1 and n2
        nodes, edges = repo.get_cluster(n1.id, depth=1)
        assert len(nodes) == 2

        # Depth 2 should get all
        nodes, edges = repo.get_cluster(n1.id, depth=2)
        assert len(nodes) == 3

    def test_get_contradictions(self, repo):
        """Get contradicting claims."""
        c1 = ClaimNode.create(domain="test", content="Claim 1")
        c2 = ClaimNode.create(domain="test", content="Claim 2 (opposes)")

        repo.insert_node(c1)
        repo.insert_node(c2)

        edge = GraphEdge.create(c1.id, c2.id, EdgeType.OPPOSITION, weight=0.9)
        repo.insert_edge(edge)

        contradictions = repo.get_contradictions(c1.id)

        assert len(contradictions) == 1
        assert contradictions[0].opposing_claim_id == c2.id
        assert contradictions[0].strength == 0.9

    def test_get_contradictions_min_strength(self, repo):
        """Get contradictions with minimum strength."""
        c1 = ClaimNode.create(domain="test", content="Claim 1")
        c2 = ClaimNode.create(domain="test", content="Weak opposition")
        c3 = ClaimNode.create(domain="test", content="Strong opposition")

        repo.insert_node(c1)
        repo.insert_node(c2)
        repo.insert_node(c3)

        repo.insert_edge(GraphEdge.create(c1.id, c2.id, EdgeType.OPPOSITION, weight=0.3))
        repo.insert_edge(GraphEdge.create(c1.id, c3.id, EdgeType.OPPOSITION, weight=0.9))

        strong = repo.get_contradictions(c1.id, min_strength=0.5)

        assert len(strong) == 1
        assert strong[0].opposing_claim_id == c3.id

    def test_get_timeline(self, repo):
        """Get claims timeline by topic."""
        topic = TopicNode.create(domain="test", name="Politics")
        repo.insert_node(topic)

        for i in range(3):
            claim = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(claim)
            repo.insert_edge(GraphEdge.create(claim.id, topic.id, EdgeType.TAGGED))

        timeline = repo.get_timeline(topic.id)

        assert len(timeline) == 3


class TestMetrics:
    """Tests for metrics operations."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with temp database."""
        db_path = tmp_path / "test.sqlite"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE claimgraph_nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                domain TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE claimgraph_edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL,
                created_at TEXT NOT NULL,
                properties TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(ClaimGraphRepository, "_ensure_db"):
            repo = ClaimGraphRepository(db_path=db_path)
            return repo

    def test_get_metrics_empty(self, repo):
        """Get metrics for empty graph."""
        metrics = repo.get_metrics()

        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.cluster_density == 0.0

    def test_get_metrics_with_data(self, repo):
        """Get metrics with data."""
        for i in range(5):
            claim = ClaimNode.create(domain="test", content=f"Claim {i}")
            repo.insert_node(claim)

        entity = EntityNode.create(domain="test", name="Entity", entity_type=EntityType.PERSON)
        repo.insert_node(entity)

        metrics = repo.get_metrics()

        assert metrics.node_count == 6
        assert metrics.claim_count == 5
        assert metrics.entity_count == 1

    def test_get_metrics_contradiction_rate(self, repo):
        """Get metrics with contradiction rate."""
        c1 = ClaimNode.create(domain="test", content="C1")
        c2 = ClaimNode.create(domain="test", content="C2")
        c3 = ClaimNode.create(domain="test", content="C3")

        repo.insert_node(c1)
        repo.insert_node(c2)
        repo.insert_node(c3)

        # 1 opposition, 2 support edges
        repo.insert_edge(GraphEdge.create(c1.id, c2.id, EdgeType.OPPOSITION))
        repo.insert_edge(GraphEdge.create(c1.id, c3.id, EdgeType.SUPPORT))
        repo.insert_edge(GraphEdge.create(c2.id, c3.id, EdgeType.SUPPORT))

        metrics = repo.get_metrics()

        assert metrics.edge_count == 3
        assert metrics.contradiction_rate == pytest.approx(1/3)

    def test_get_metrics_by_domain(self, repo):
        """Get metrics filtered by domain."""
        for i in range(3):
            claim = ClaimNode.create(domain="politics", content=f"Claim {i}")
            repo.insert_node(claim)

        for i in range(2):
            claim = ClaimNode.create(domain="health", content=f"Claim {i}")
            repo.insert_node(claim)

        politics_metrics = repo.get_metrics(domain="politics")
        health_metrics = repo.get_metrics(domain="health")

        assert politics_metrics.claim_count == 3
        assert health_metrics.claim_count == 2
