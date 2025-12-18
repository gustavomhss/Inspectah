"""
Tests for Claim Graph Topology Metrics.

S39 - Topology Analysis Tests
"""
import pytest
from datetime import datetime, timezone

from app.claims.graph_models import (
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    Subgraph,
)
from app.claims.topology_metrics import (
    TopologyHealthStatus,
    NodeCentrality,
    ClusterMetrics,
    TopologyHealth,
    TopologyMetrics,
    TopologyAnalyzer,
    get_topology_analyzer,
    reset_topology_analyzer,
)


# ============================================================================
# Helper Functions
# ============================================================================

def _now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def _make_node(
    node_id: str,
    node_type: NodeType,
    domain: str = "test",
    properties: dict = None,
) -> GraphNode:
    """Create a GraphNode with proper structure."""
    now = _now()
    return GraphNode(
        id=node_id,
        node_type=node_type,
        domain=domain,
        created_at=now,
        updated_at=now,
        properties=properties or {},
    )


def _make_edge(
    source_id: str,
    target_id: str,
    edge_type: EdgeType,
    weight: float = 0.5,
    edge_id: str = None,
) -> GraphEdge:
    """Create a GraphEdge with proper structure."""
    return GraphEdge(
        id=edge_id or f"e_{source_id}_{target_id}",
        source_id=source_id,
        target_id=target_id,
        edge_type=edge_type,
        weight=weight,
        created_at=_now(),
        properties={},
    )


def _make_subgraph(
    center_id: str,
    nodes: list,
    edges: list,
    depth: int = 1,
) -> Subgraph:
    """Create a Subgraph with proper structure."""
    return Subgraph(
        center_id=center_id,
        nodes=nodes,
        edges=edges,
        depth=depth,
    )


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_nodes():
    """Create sample graph nodes."""
    return [
        _make_node("n1", NodeType.CLAIM, "politica", {"text": "claim 1"}),
        _make_node("n2", NodeType.CLAIM, "politica", {"text": "claim 2"}),
        _make_node("n3", NodeType.ENTITY, "economia", {"name": "Entity"}),
        _make_node("n4", NodeType.TOPIC, "saude", {"name": "Topic"}),
        _make_node("n5", NodeType.CLAIM, "politica", {"text": "claim 3"}),
    ]


@pytest.fixture
def sample_edges():
    """Create sample graph edges."""
    return [
        _make_edge("n1", "n2", EdgeType.SUPPORT, 0.8),
        _make_edge("n2", "n3", EdgeType.MENTIONS, 0.5),
        _make_edge("n1", "n4", EdgeType.TAGGED, 0.6),
        _make_edge("n3", "n5", EdgeType.MENTIONS, 0.7),
        _make_edge("n4", "n5", EdgeType.TAGGED, 0.4),
    ]


@pytest.fixture
def connected_nodes():
    """Create a fully connected graph."""
    return [_make_node(f"c{i}", NodeType.CLAIM) for i in range(5)]


@pytest.fixture
def connected_edges():
    """Create edges for a fully connected graph."""
    edges = []
    for i in range(5):
        for j in range(i + 1, 5):
            edges.append(_make_edge(f"c{i}", f"c{j}", EdgeType.SUPPORT, 0.5))
    return edges


@pytest.fixture
def contradicting_edges():
    """Create edges with high contradiction rate."""
    return [
        _make_edge("n1", "n2", EdgeType.OPPOSITION, 0.9),
        _make_edge("n2", "n5", EdgeType.OPPOSITION, 0.8),
        _make_edge("n1", "n5", EdgeType.SUPPORT, 0.7),
    ]


@pytest.fixture
def analyzer():
    """Create fresh analyzer."""
    reset_topology_analyzer()
    return TopologyAnalyzer()


# ============================================================================
# Test TopologyHealthStatus
# ============================================================================

class TestTopologyHealthStatus:
    """Tests for TopologyHealthStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert TopologyHealthStatus.HEALTHY.value == "healthy"
        assert TopologyHealthStatus.DEGRADED.value == "degraded"
        assert TopologyHealthStatus.WARNING.value == "warning"
        assert TopologyHealthStatus.CRITICAL.value == "critical"


# ============================================================================
# Test NodeCentrality
# ============================================================================

class TestNodeCentrality:
    """Tests for NodeCentrality dataclass."""

    def test_create_centrality(self):
        """Test creating centrality."""
        centrality = NodeCentrality(
            node_id="n1",
            node_type=NodeType.CLAIM,
            degree=5,
            in_degree=2,
            out_degree=3,
            closeness=0.75,
            betweenness=0.5,
            pagerank=0.125,
        )

        assert centrality.node_id == "n1"
        assert centrality.degree == 5
        assert centrality.closeness == 0.75

    def test_to_dict(self):
        """Test converting centrality to dict."""
        centrality = NodeCentrality(
            node_id="n1",
            node_type=NodeType.CLAIM,
            degree=5,
            in_degree=2,
            out_degree=3,
            closeness=0.756789,
            betweenness=0.512345,
            pagerank=0.125678,
        )

        d = centrality.to_dict()

        assert d["node_id"] == "n1"
        assert d["node_type"] == "claim"
        assert d["degree"] == 5
        assert d["closeness"] == 0.7568  # Rounded
        assert d["betweenness"] == 0.5123
        assert d["pagerank"] == 0.1257


# ============================================================================
# Test ClusterMetrics
# ============================================================================

class TestClusterMetrics:
    """Tests for ClusterMetrics dataclass."""

    def test_create_cluster_metrics(self):
        """Test creating cluster metrics."""
        metrics = ClusterMetrics(
            cluster_id="cluster_1",
            center_node_id="n1",
            node_count=10,
            edge_count=15,
            density=0.333,
            diameter=3,
            avg_path_length=1.5,
            internal_edges=12,
            external_edges=5,
            modularity=0.45,
        )

        assert metrics.cluster_id == "cluster_1"
        assert metrics.node_count == 10
        assert metrics.density == 0.333

    def test_to_dict(self):
        """Test converting cluster metrics to dict."""
        metrics = ClusterMetrics(
            cluster_id="cluster_1",
            center_node_id="n1",
            node_count=10,
            edge_count=15,
            density=0.333456,
            diameter=3,
            avg_path_length=1.567890,
            internal_edges=12,
            external_edges=5,
            modularity=0.456789,
        )

        d = metrics.to_dict()

        assert d["cluster_id"] == "cluster_1"
        assert d["density"] == 0.3335  # Rounded
        assert d["avg_path_length"] == 1.5679
        assert d["modularity"] == 0.4568


# ============================================================================
# Test TopologyHealth
# ============================================================================

class TestTopologyHealth:
    """Tests for TopologyHealth dataclass."""

    def test_create_health(self):
        """Test creating health assessment."""
        health = TopologyHealth(
            status=TopologyHealthStatus.HEALTHY,
            score=95.5,
            issues=[],
            recommendations=[],
        )

        assert health.status == TopologyHealthStatus.HEALTHY
        assert health.score == 95.5
        assert len(health.issues) == 0

    def test_health_with_issues(self):
        """Test health with issues."""
        health = TopologyHealth(
            status=TopologyHealthStatus.WARNING,
            score=65.0,
            issues=["Low connectivity", "High isolated nodes"],
            recommendations=["Add more edges", "Link isolated claims"],
        )

        assert health.status == TopologyHealthStatus.WARNING
        assert len(health.issues) == 2
        assert "Low connectivity" in health.issues

    def test_to_dict(self):
        """Test converting health to dict."""
        health = TopologyHealth(
            status=TopologyHealthStatus.DEGRADED,
            score=55.678,
            issues=["Issue 1"],
            recommendations=["Fix it"],
        )

        d = health.to_dict()

        assert d["status"] == "degraded"
        assert d["score"] == 55.68  # Rounded
        assert d["issues"] == ["Issue 1"]
        assert "timestamp" in d

    def test_health_default_timestamp(self):
        """Test health default timestamp."""
        health = TopologyHealth(
            status=TopologyHealthStatus.HEALTHY,
            score=100.0,
            issues=[],
            recommendations=[],
        )

        assert health.timestamp is not None
        assert health.timestamp.tzinfo == timezone.utc


# ============================================================================
# Test TopologyMetrics
# ============================================================================

class TestTopologyMetrics:
    """Tests for TopologyMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating topology metrics."""
        health = TopologyHealth(
            status=TopologyHealthStatus.HEALTHY,
            score=100.0,
            issues=[],
            recommendations=[],
        )
        metrics = TopologyMetrics(
            node_count=100,
            edge_count=200,
            nodes_by_type={"claim": 50, "entity": 30, "topic": 20},
            edges_by_type={"support": 100, "opposition": 50, "mentions": 50},
            connected_components=3,
            largest_component_size=80,
            isolated_nodes=5,
            avg_degree=4.0,
            max_degree=15,
            global_density=0.04,
            clustering_coefficient=0.35,
            avg_clustering=0.40,
            avg_path_length=2.5,
            diameter=6,
            contradiction_edges=50,
            contradiction_rate=0.333,
            nodes_by_domain={"politica": 40, "economia": 30, "saude": 30},
            health=health,
        )

        assert metrics.node_count == 100
        assert metrics.connected_components == 3

    def test_to_dict(self):
        """Test converting metrics to dict."""
        health = TopologyHealth(
            status=TopologyHealthStatus.HEALTHY,
            score=100.0,
            issues=[],
            recommendations=[],
        )
        metrics = TopologyMetrics(
            node_count=100,
            edge_count=200,
            nodes_by_type={"claim": 50},
            edges_by_type={"support": 100},
            connected_components=3,
            largest_component_size=80,
            isolated_nodes=5,
            avg_degree=4.123456,
            max_degree=15,
            global_density=0.041234,
            clustering_coefficient=0.351234,
            avg_clustering=0.401234,
            avg_path_length=2.512345,
            diameter=6,
            contradiction_edges=50,
            contradiction_rate=0.333456,
            nodes_by_domain={"politica": 40},
            health=health,
        )

        d = metrics.to_dict()

        assert d["node_count"] == 100
        assert d["avg_degree"] == 4.1235  # Rounded
        assert d["global_density"] == 0.0412
        assert "health" in d

    def test_empty_metrics(self):
        """Test creating empty metrics."""
        metrics = TopologyMetrics.empty()

        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.connected_components == 0
        assert metrics.health.status == TopologyHealthStatus.HEALTHY
        assert metrics.health.score == 100.0


# ============================================================================
# Test TopologyAnalyzer - Basic
# ============================================================================

class TestTopologyAnalyzerBasic:
    """Basic tests for TopologyAnalyzer."""

    def test_create_analyzer(self, analyzer):
        """Test creating analyzer."""
        assert analyzer is not None
        assert analyzer.health_thresholds is not None

    def test_custom_thresholds(self):
        """Test analyzer with custom thresholds."""
        thresholds = {
            "min_connectivity": 0.5,
            "max_isolated": 0.1,
            "min_density": 0.01,
            "max_contradiction_rate": 0.2,
        }
        analyzer = TopologyAnalyzer(health_thresholds=thresholds)

        assert analyzer.health_thresholds["min_connectivity"] == 0.5

    def test_analyze_empty_graph(self, analyzer):
        """Test analyzing empty graph."""
        metrics = analyzer.analyze([], [])

        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.health.status == TopologyHealthStatus.HEALTHY


# ============================================================================
# Test TopologyAnalyzer - Analysis
# ============================================================================

class TestTopologyAnalyzerAnalysis:
    """Tests for TopologyAnalyzer.analyze()."""

    def test_analyze_basic(self, analyzer, sample_nodes, sample_edges):
        """Test basic analysis."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.node_count == 5
        assert metrics.edge_count == 5

    def test_analyze_nodes_by_type(self, analyzer, sample_nodes, sample_edges):
        """Test nodes by type counting."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.nodes_by_type["claim"] == 3
        assert metrics.nodes_by_type["entity"] == 1
        assert metrics.nodes_by_type["topic"] == 1

    def test_analyze_edges_by_type(self, analyzer, sample_nodes, sample_edges):
        """Test edges by type counting."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.edges_by_type["support"] == 1
        assert metrics.edges_by_type["mentions"] == 2
        assert metrics.edges_by_type["tagged"] == 2

    def test_analyze_nodes_by_domain(self, analyzer, sample_nodes, sample_edges):
        """Test nodes by domain counting."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.nodes_by_domain["politica"] == 3
        assert metrics.nodes_by_domain["economia"] == 1
        assert metrics.nodes_by_domain["saude"] == 1

    def test_analyze_connectivity(self, analyzer, sample_nodes, sample_edges):
        """Test connectivity analysis."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.connected_components >= 1
        assert metrics.largest_component_size >= 1

    def test_analyze_fully_connected(self, analyzer, connected_nodes, connected_edges):
        """Test analysis of fully connected graph."""
        metrics = analyzer.analyze(connected_nodes, connected_edges)

        assert metrics.connected_components == 1
        assert metrics.largest_component_size == 5
        assert metrics.isolated_nodes == 0

    def test_analyze_isolated_nodes(self, analyzer):
        """Test analysis with isolated nodes."""
        nodes = [
            _make_node("n1", NodeType.CLAIM),
            _make_node("n2", NodeType.CLAIM),
            _make_node("n3", NodeType.CLAIM),
        ]
        edges = [
            _make_edge("n1", "n2", EdgeType.SUPPORT, 0.5),
        ]

        metrics = analyzer.analyze(nodes, edges)

        assert metrics.isolated_nodes == 1  # n3 is isolated

    def test_analyze_degree_stats(self, analyzer, sample_nodes, sample_edges):
        """Test degree statistics."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.avg_degree > 0
        assert metrics.max_degree > 0

    def test_analyze_density(self, analyzer, connected_nodes, connected_edges):
        """Test density calculation."""
        metrics = analyzer.analyze(connected_nodes, connected_edges)

        # Fully connected graph should have density ~1
        # But edges are directed, so actual density is lower
        assert metrics.global_density > 0.4

    def test_analyze_clustering(self, analyzer, sample_nodes, sample_edges):
        """Test clustering coefficient calculation."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.clustering_coefficient >= 0
        assert metrics.avg_clustering >= 0

    def test_analyze_path_metrics(self, analyzer, sample_nodes, sample_edges):
        """Test path metrics estimation."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        assert metrics.avg_path_length >= 0
        assert metrics.diameter >= 0

    def test_analyze_contradiction_rate(self, analyzer, sample_nodes, contradicting_edges):
        """Test contradiction rate calculation."""
        metrics = analyzer.analyze(sample_nodes, contradicting_edges)

        assert metrics.contradiction_edges == 2
        assert metrics.contradiction_rate > 0.5  # 2 out of 3 are opposition


# ============================================================================
# Test TopologyAnalyzer - Centrality
# ============================================================================

class TestTopologyAnalyzerCentrality:
    """Tests for TopologyAnalyzer.calculate_centrality()."""

    def test_calculate_centrality(self, analyzer, sample_nodes, sample_edges):
        """Test centrality calculation."""
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        assert centrality is not None
        assert centrality.node_id == "n1"
        assert centrality.node_type == NodeType.CLAIM

    def test_centrality_degree(self, analyzer, sample_nodes, sample_edges):
        """Test degree in centrality."""
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        # n1 connects to n2 and n4
        assert centrality.out_degree == 2
        assert centrality.degree >= 2

    def test_centrality_unknown_node(self, analyzer, sample_nodes, sample_edges):
        """Test centrality for unknown node."""
        centrality = analyzer.calculate_centrality("unknown", sample_nodes, sample_edges)

        assert centrality is None

    def test_centrality_closeness(self, analyzer, sample_nodes, sample_edges):
        """Test closeness centrality."""
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        assert 0 <= centrality.closeness <= 1

    def test_centrality_betweenness(self, analyzer, sample_nodes, sample_edges):
        """Test betweenness centrality."""
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        assert 0 <= centrality.betweenness <= 1

    def test_centrality_pagerank(self, analyzer, sample_nodes, sample_edges):
        """Test PageRank score."""
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        assert centrality.pagerank >= 0

    def test_centrality_isolated_node(self, analyzer):
        """Test centrality for isolated node."""
        nodes = [
            _make_node("n1", NodeType.CLAIM),
            _make_node("n2", NodeType.CLAIM),
        ]
        edges = []

        centrality = analyzer.calculate_centrality("n1", nodes, edges)

        assert centrality.degree == 0
        assert centrality.closeness == 0.0


# ============================================================================
# Test TopologyAnalyzer - Cluster Analysis
# ============================================================================

class TestTopologyAnalyzerCluster:
    """Tests for TopologyAnalyzer.analyze_cluster()."""

    def test_analyze_cluster(self, analyzer, sample_nodes, sample_edges):
        """Test cluster analysis."""
        subgraph = _make_subgraph(
            center_id="n1",
            nodes=sample_nodes[:3],
            edges=[e for e in sample_edges if e.source_id in {"n1", "n2", "n3"} and e.target_id in {"n1", "n2", "n3"}],
        )

        metrics = analyzer.analyze_cluster(subgraph, sample_edges)

        assert metrics.cluster_id.startswith("cluster_")
        assert metrics.center_node_id == "n1"
        assert metrics.node_count == 3

    def test_cluster_density(self, analyzer, connected_nodes, connected_edges):
        """Test cluster density calculation."""
        subgraph = _make_subgraph(
            center_id="c0",
            nodes=connected_nodes[:3],
            edges=[
                e for e in connected_edges
                if e.source_id in {"c0", "c1", "c2"} and e.target_id in {"c0", "c1", "c2"}
            ],
        )

        metrics = analyzer.analyze_cluster(subgraph, connected_edges)

        assert metrics.density > 0

    def test_cluster_internal_external_edges(self, analyzer, sample_nodes, sample_edges):
        """Test internal vs external edge counting."""
        subgraph = _make_subgraph(
            center_id="n1",
            nodes=sample_nodes[:2],  # n1, n2
            edges=[sample_edges[0]],  # n1 -> n2
        )

        metrics = analyzer.analyze_cluster(subgraph, sample_edges)

        assert metrics.internal_edges >= 1
        assert metrics.external_edges >= 0

    def test_cluster_modularity(self, analyzer, sample_nodes, sample_edges):
        """Test modularity calculation."""
        subgraph = _make_subgraph(
            center_id="n1",
            nodes=sample_nodes[:3],
            edges=[sample_edges[0], sample_edges[1]],
        )

        metrics = analyzer.analyze_cluster(subgraph, sample_edges)

        # Modularity can be positive or negative
        assert isinstance(metrics.modularity, float)


# ============================================================================
# Test TopologyAnalyzer - Health Assessment
# ============================================================================

class TestTopologyAnalyzerHealth:
    """Tests for TopologyAnalyzer.assess_health()."""

    def test_healthy_graph(self, analyzer):
        """Test healthy graph assessment."""
        metrics = {
            "connectivity": 0.9,
            "isolated_fraction": 0.05,
            "density": 0.1,
            "contradiction_rate": 0.1,
        }

        health = analyzer.assess_health(metrics)

        assert health.status == TopologyHealthStatus.HEALTHY
        assert health.score >= 80
        assert len(health.issues) == 0

    def test_low_connectivity(self, analyzer):
        """Test low connectivity detection."""
        metrics = {
            "connectivity": 0.05,  # Below threshold
            "isolated_fraction": 0.1,
            "density": 0.01,
            "contradiction_rate": 0.1,
        }

        health = analyzer.assess_health(metrics)

        assert health.score < 100
        assert any("connectivity" in issue.lower() for issue in health.issues)
        assert any("relations" in rec.lower() for rec in health.recommendations)

    def test_high_isolated_fraction(self, analyzer):
        """Test high isolated nodes detection."""
        metrics = {
            "connectivity": 0.5,
            "isolated_fraction": 0.3,  # Above threshold
            "density": 0.01,
            "contradiction_rate": 0.1,
        }

        health = analyzer.assess_health(metrics)

        assert health.score < 100
        assert any("isolated" in issue.lower() for issue in health.issues)

    def test_low_density(self, analyzer):
        """Test low density detection."""
        metrics = {
            "connectivity": 0.5,
            "isolated_fraction": 0.1,
            "density": 0.0001,  # Below threshold
            "contradiction_rate": 0.1,
        }

        health = analyzer.assess_health(metrics)

        assert health.score < 100
        assert any("density" in issue.lower() for issue in health.issues)

    def test_high_contradiction_rate(self, analyzer):
        """Test high contradiction rate detection."""
        metrics = {
            "connectivity": 0.5,
            "isolated_fraction": 0.1,
            "density": 0.01,
            "contradiction_rate": 0.5,  # Above threshold
        }

        health = analyzer.assess_health(metrics)

        assert health.score < 100
        assert any("contradiction" in issue.lower() for issue in health.issues)

    def test_warning_status(self, analyzer):
        """Test warning status threshold."""
        metrics = {
            "connectivity": 0.05,  # -20
            "isolated_fraction": 0.1,
            "density": 0.0001,  # -10 (below min_density threshold)
            "contradiction_rate": 0.1,
        }
        # Total penalty: -20 -10 = -30, score = 70 -> WARNING (60 <= score < 80)

        health = analyzer.assess_health(metrics)

        assert health.status == TopologyHealthStatus.WARNING
        assert 60 <= health.score < 80

    def test_degraded_status(self, analyzer):
        """Test degraded status threshold."""
        metrics = {
            "connectivity": 0.05,  # -20
            "isolated_fraction": 0.3,  # -15
            "density": 0.0001,  # -10
            "contradiction_rate": 0.1,
        }

        health = analyzer.assess_health(metrics)

        assert health.status == TopologyHealthStatus.DEGRADED
        assert 40 <= health.score < 60

    def test_critical_status(self, analyzer):
        """Test critical status threshold."""
        metrics = {
            "connectivity": 0.05,  # -20
            "isolated_fraction": 0.3,  # -15
            "density": 0.0001,  # -10
            "contradiction_rate": 0.5,  # -25
        }

        health = analyzer.assess_health(metrics)

        assert health.status == TopologyHealthStatus.CRITICAL
        assert health.score < 40

    def test_score_minimum_zero(self, analyzer):
        """Test score doesn't go below zero."""
        metrics = {
            "connectivity": 0.0,
            "isolated_fraction": 1.0,
            "density": 0.0,
            "contradiction_rate": 1.0,
        }

        health = analyzer.assess_health(metrics)

        assert health.score >= 0


# ============================================================================
# Test TopologyAnalyzer - Private Methods
# ============================================================================

class TestTopologyAnalyzerPrivate:
    """Tests for private helper methods."""

    def test_build_adjacency_list(self, analyzer, sample_nodes, sample_edges):
        """Test adjacency list building."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)

        assert "n1" in adj
        assert "n2" in adj["n1"]  # n1 -> n2
        assert "n1" in adj["n2"]  # Undirected, so reverse too

    def test_calculate_degrees(self, analyzer, sample_nodes, sample_edges):
        """Test degree calculation."""
        in_deg, out_deg = analyzer._calculate_degrees(sample_nodes, sample_edges)

        assert out_deg["n1"] == 2  # n1 -> n2, n1 -> n4
        assert in_deg["n2"] == 1  # n1 -> n2

    def test_count_by_type(self, analyzer, sample_nodes):
        """Test counting by type."""
        counts = analyzer._count_by_type(sample_nodes)

        assert counts["claim"] == 3
        assert counts["entity"] == 1
        assert counts["topic"] == 1

    def test_count_edges_by_type(self, analyzer, sample_edges):
        """Test counting edges by type."""
        counts = analyzer._count_edges_by_type(sample_edges)

        assert counts["support"] == 1
        assert counts["mentions"] == 2

    def test_count_by_domain(self, analyzer, sample_nodes):
        """Test counting by domain."""
        counts = analyzer._count_by_domain(sample_nodes)

        assert counts["politica"] == 3
        assert counts["economia"] == 1

    def test_find_connected_components(self, analyzer, sample_nodes, sample_edges):
        """Test finding connected components."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        components = analyzer._find_connected_components(sample_nodes, adj)

        assert len(components) >= 1
        # All nodes should be in some component
        all_nodes = set()
        for comp in components:
            all_nodes.update(comp)
        assert len(all_nodes) == len(sample_nodes)

    def test_find_connected_components_multiple(self, analyzer):
        """Test finding multiple components."""
        nodes = [
            _make_node("a1", NodeType.CLAIM),
            _make_node("a2", NodeType.CLAIM),
            _make_node("b1", NodeType.CLAIM),
            _make_node("b2", NodeType.CLAIM),
        ]
        edges = [
            _make_edge("a1", "a2", EdgeType.SUPPORT, 0.5),
            _make_edge("b1", "b2", EdgeType.SUPPORT, 0.5),
        ]

        adj = analyzer._build_adjacency_list(nodes, edges)
        components = analyzer._find_connected_components(nodes, adj)

        assert len(components) == 2

    def test_calculate_clustering_coefficient(self, analyzer, sample_nodes, sample_edges):
        """Test clustering coefficient calculation."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        coef = analyzer._calculate_clustering_coefficient(sample_nodes, adj)

        assert len(coef) == len(sample_nodes)
        for val in coef.values():
            assert 0 <= val <= 1

    def test_clustering_coefficient_isolated(self, analyzer):
        """Test clustering for isolated node."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        adj = {"n1": set()}

        coef = analyzer._calculate_clustering_coefficient(nodes, adj)

        assert coef["n1"] == 0.0

    def test_estimate_path_metrics(self, analyzer, sample_nodes, sample_edges):
        """Test path metrics estimation."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        avg_path, diameter = analyzer._estimate_path_metrics(sample_nodes, adj)

        assert avg_path >= 0
        assert diameter >= 0

    def test_estimate_path_metrics_single_node(self, analyzer):
        """Test path metrics with single node."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        adj = {"n1": set()}

        avg_path, diameter = analyzer._estimate_path_metrics(nodes, adj)

        assert avg_path == 0.0
        assert diameter == 0

    def test_bfs_distances(self, analyzer, sample_nodes, sample_edges):
        """Test BFS distance calculation."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        distances = analyzer._bfs_distances("n1", adj)

        assert distances["n1"] == 0
        assert all(d >= 0 for d in distances.values())

    def test_calculate_closeness(self, analyzer, sample_nodes, sample_edges):
        """Test closeness calculation."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        closeness = analyzer._calculate_closeness("n1", sample_nodes, adj)

        assert 0 <= closeness <= 1

    def test_calculate_closeness_isolated(self, analyzer):
        """Test closeness for isolated node."""
        nodes = [
            _make_node("n1", NodeType.CLAIM),
            _make_node("n2", NodeType.CLAIM),
        ]
        adj = {"n1": set(), "n2": set()}

        closeness = analyzer._calculate_closeness("n1", nodes, adj)

        assert closeness == 0.0

    def test_calculate_betweenness(self, analyzer, sample_nodes, sample_edges):
        """Test betweenness calculation."""
        adj = analyzer._build_adjacency_list(sample_nodes, sample_edges)
        betweenness = analyzer._calculate_betweenness("n1", sample_nodes, adj)

        assert 0 <= betweenness <= 1

    def test_calculate_pagerank(self, analyzer, sample_nodes, sample_edges):
        """Test PageRank calculation."""
        pagerank = analyzer._calculate_pagerank("n1", sample_nodes, sample_edges)

        assert pagerank >= 0

    def test_calculate_pagerank_empty(self, analyzer):
        """Test PageRank with empty graph."""
        pagerank = analyzer._calculate_pagerank("n1", [], [])

        assert pagerank == 0.0


# ============================================================================
# Test Singleton
# ============================================================================

class TestSingleton:
    """Tests for singleton functions."""

    def test_get_topology_analyzer(self):
        """Test getting singleton."""
        reset_topology_analyzer()
        analyzer1 = get_topology_analyzer()
        analyzer2 = get_topology_analyzer()

        assert analyzer1 is analyzer2

    def test_reset_topology_analyzer(self):
        """Test resetting singleton."""
        analyzer1 = get_topology_analyzer()
        reset_topology_analyzer()
        analyzer2 = get_topology_analyzer()

        assert analyzer1 is not analyzer2


# ============================================================================
# Integration Tests
# ============================================================================

class TestTopologyIntegration:
    """Integration tests for topology analysis."""

    def test_full_analysis_workflow(self, analyzer, sample_nodes, sample_edges):
        """Test complete analysis workflow."""
        # Analyze graph
        metrics = analyzer.analyze(sample_nodes, sample_edges)

        # Get centrality for key node
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        # Create subgraph and analyze cluster
        subgraph = _make_subgraph(
            center_id="n1",
            nodes=sample_nodes[:3],
            edges=[sample_edges[0], sample_edges[1]],
        )
        cluster_metrics = analyzer.analyze_cluster(subgraph, sample_edges)

        # Verify all outputs
        assert metrics.node_count == 5
        assert centrality is not None
        assert cluster_metrics.node_count == 3

    def test_large_graph_performance(self, analyzer):
        """Test performance with larger graph."""
        # Create larger graph
        nodes = [_make_node(f"n{i}", NodeType.CLAIM) for i in range(100)]
        edges = [
            _make_edge(f"n{i}", f"n{(i+1) % 100}", EdgeType.SUPPORT, 0.5)
            for i in range(100)
        ]

        # Should complete without timeout
        metrics = analyzer.analyze(nodes, edges)

        assert metrics.node_count == 100
        assert metrics.edge_count == 100

    def test_serialization_roundtrip(self, analyzer, sample_nodes, sample_edges):
        """Test that all outputs can be serialized."""
        metrics = analyzer.analyze(sample_nodes, sample_edges)
        centrality = analyzer.calculate_centrality("n1", sample_nodes, sample_edges)

        # Convert to dict
        metrics_dict = metrics.to_dict()
        centrality_dict = centrality.to_dict()

        # Verify structure
        assert "node_count" in metrics_dict
        assert "health" in metrics_dict
        assert "node_id" in centrality_dict


# ============================================================================
# Test Top Central Nodes
# ============================================================================

class TestTopCentralNodes:
    """Tests for get_top_central_nodes method."""

    @pytest.fixture
    def analyzer(self):
        reset_topology_analyzer()
        return TopologyAnalyzer()

    def test_top_central_empty_graph(self, analyzer):
        """Test top central nodes with empty graph."""
        result = analyzer.get_top_central_nodes([], [], top_n=5)
        assert result == []

    def test_top_central_by_degree(self, analyzer):
        """Test top central nodes sorted by degree."""
        # Create a star topology with n1 at center
        center = _make_node("center", NodeType.CLAIM)
        periphery = [_make_node(f"p{i}", NodeType.CLAIM) for i in range(5)]
        nodes = [center] + periphery

        edges = [
            _make_edge("center", f"p{i}", EdgeType.SUPPORT)
            for i in range(5)
        ]

        result = analyzer.get_top_central_nodes(nodes, edges, top_n=3, metric="degree")

        assert len(result) == 3
        assert result[0].node_id == "center"  # Highest degree
        assert result[0].degree == 5

    def test_top_central_by_pagerank(self, analyzer):
        """Test top central nodes sorted by pagerank."""
        nodes = [_make_node(f"n{i}", NodeType.CLAIM) for i in range(5)]
        edges = [
            _make_edge("n0", "n1", EdgeType.SUPPORT),
            _make_edge("n0", "n2", EdgeType.SUPPORT),
            _make_edge("n1", "n3", EdgeType.SUPPORT),
            _make_edge("n2", "n3", EdgeType.SUPPORT),
            _make_edge("n3", "n4", EdgeType.SUPPORT),
        ]

        result = analyzer.get_top_central_nodes(nodes, edges, top_n=3, metric="pagerank")

        assert len(result) == 3
        # All nodes have pagerank values
        for node in result:
            assert node.pagerank >= 0

    def test_top_central_by_closeness(self, analyzer):
        """Test top central nodes sorted by closeness."""
        nodes = [_make_node(f"n{i}", NodeType.CLAIM) for i in range(4)]
        edges = [
            _make_edge("n0", "n1", EdgeType.SUPPORT),
            _make_edge("n1", "n2", EdgeType.SUPPORT),
            _make_edge("n2", "n3", EdgeType.SUPPORT),
            _make_edge("n0", "n2", EdgeType.SUPPORT),  # shortcut
        ]

        result = analyzer.get_top_central_nodes(nodes, edges, top_n=2, metric="closeness")

        assert len(result) == 2
        # Middle nodes should have higher closeness
        for node in result:
            assert node.closeness >= 0

    def test_top_central_by_betweenness(self, analyzer):
        """Test top central nodes sorted by betweenness."""
        nodes = [_make_node(f"n{i}", NodeType.CLAIM) for i in range(4)]
        edges = [
            _make_edge("n0", "n1", EdgeType.SUPPORT),
            _make_edge("n1", "n2", EdgeType.SUPPORT),
            _make_edge("n2", "n3", EdgeType.SUPPORT),
        ]

        result = analyzer.get_top_central_nodes(nodes, edges, top_n=2, metric="betweenness")

        assert len(result) == 2

    def test_top_n_limit(self, analyzer):
        """Test that top_n limits results."""
        nodes = [_make_node(f"n{i}", NodeType.CLAIM) for i in range(10)]
        edges = []

        result = analyzer.get_top_central_nodes(nodes, edges, top_n=3)

        assert len(result) == 3


# ============================================================================
# Test Graph Validation
# ============================================================================

class TestGraphValidation:
    """Tests for validate_graph method."""

    @pytest.fixture
    def analyzer(self):
        reset_topology_analyzer()
        return TopologyAnalyzer()

    def test_validate_valid_graph(self, analyzer):
        """Test validation of a valid graph."""
        nodes = [
            _make_node("n1", NodeType.CLAIM),
            _make_node("n2", NodeType.CLAIM),
        ]
        edges = [_make_edge("n1", "n2", EdgeType.SUPPORT)]

        issues = analyzer.validate_graph(nodes, edges)
        assert len(issues) == 0

    def test_validate_orphan_source(self, analyzer):
        """Test detection of edge with missing source node."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        edges = [_make_edge("missing", "n1", EdgeType.SUPPORT)]

        issues = analyzer.validate_graph(nodes, edges)

        assert len(issues) == 1
        assert "missing source node" in issues[0]

    def test_validate_orphan_target(self, analyzer):
        """Test detection of edge with missing target node."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        edges = [_make_edge("n1", "missing", EdgeType.SUPPORT)]

        issues = analyzer.validate_graph(nodes, edges)

        assert len(issues) == 1
        assert "missing target node" in issues[0]

    def test_validate_duplicate_edges(self, analyzer):
        """Test detection of duplicate edges."""
        nodes = [
            _make_node("n1", NodeType.CLAIM),
            _make_node("n2", NodeType.CLAIM),
        ]
        edges = [
            _make_edge("n1", "n2", EdgeType.SUPPORT, edge_id="e1"),
            _make_edge("n1", "n2", EdgeType.SUPPORT, edge_id="e2"),  # duplicate
        ]

        issues = analyzer.validate_graph(nodes, edges)

        assert len(issues) == 1
        assert "Duplicate edge" in issues[0]

    def test_validate_self_loops(self, analyzer):
        """Test detection of self-loops."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        edges = [_make_edge("n1", "n1", EdgeType.SUPPORT)]

        issues = analyzer.validate_graph(nodes, edges)

        assert len(issues) == 1
        assert "Self-loop" in issues[0]

    def test_validate_multiple_issues(self, analyzer):
        """Test detection of multiple issues."""
        nodes = [_make_node("n1", NodeType.CLAIM)]
        edges = [
            _make_edge("missing", "n1", EdgeType.SUPPORT),  # orphan source
            _make_edge("n1", "n1", EdgeType.SUPPORT),       # self-loop
        ]

        issues = analyzer.validate_graph(nodes, edges)

        assert len(issues) == 2

    def test_validate_empty_graph(self, analyzer):
        """Test validation of empty graph."""
        issues = analyzer.validate_graph([], [])
        assert len(issues) == 0
