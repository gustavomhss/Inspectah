"""
S39 - Claim Graph Topology Metrics

Provides detailed topology analysis for the claim graph including:
- Centrality measures
- Cluster analysis
- Path metrics
- Health indicators
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from app.claims.graph_models import (
    ClaimGraphMetrics,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    Subgraph,
)

logger = logging.getLogger(__name__)


class TopologyHealthStatus(str, Enum):
    """Health status of the graph topology."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class NodeCentrality:
    """Centrality metrics for a single node."""
    node_id: str
    node_type: NodeType
    degree: int              # Number of connections
    in_degree: int           # Incoming edges
    out_degree: int          # Outgoing edges
    closeness: float         # Closeness centrality (0-1)
    betweenness: float       # Betweenness centrality (0-1)
    pagerank: float          # PageRank score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "degree": self.degree,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "closeness": round(self.closeness, 4),
            "betweenness": round(self.betweenness, 4),
            "pagerank": round(self.pagerank, 4),
        }


@dataclass
class ClusterMetrics:
    """Metrics for a cluster of nodes."""
    cluster_id: str
    center_node_id: str
    node_count: int
    edge_count: int
    density: float           # edges / max_possible_edges
    diameter: int            # Longest shortest path
    avg_path_length: float   # Average shortest path
    internal_edges: int      # Edges within cluster
    external_edges: int      # Edges to other clusters
    modularity: float        # How well-separated from rest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "center_node_id": self.center_node_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "density": round(self.density, 4),
            "diameter": self.diameter,
            "avg_path_length": round(self.avg_path_length, 4),
            "internal_edges": self.internal_edges,
            "external_edges": self.external_edges,
            "modularity": round(self.modularity, 4),
        }


@dataclass
class TopologyHealth:
    """Health assessment of the graph topology."""
    status: TopologyHealthStatus
    score: float             # 0-100
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "score": round(self.score, 2),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TopologyMetrics:
    """Comprehensive topology metrics for the claim graph."""
    # Basic counts
    node_count: int
    edge_count: int
    nodes_by_type: Dict[str, int]
    edges_by_type: Dict[str, int]

    # Connectivity
    connected_components: int
    largest_component_size: int
    isolated_nodes: int
    avg_degree: float
    max_degree: int

    # Density and clustering
    global_density: float
    clustering_coefficient: float
    avg_clustering: float

    # Path metrics
    avg_path_length: float
    diameter: int

    # Contradiction metrics
    contradiction_edges: int
    contradiction_rate: float

    # Domain distribution
    nodes_by_domain: Dict[str, int]

    # Health
    health: TopologyHealth

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes_by_type": self.nodes_by_type,
            "edges_by_type": self.edges_by_type,
            "connected_components": self.connected_components,
            "largest_component_size": self.largest_component_size,
            "isolated_nodes": self.isolated_nodes,
            "avg_degree": round(self.avg_degree, 4),
            "max_degree": self.max_degree,
            "global_density": round(self.global_density, 4),
            "clustering_coefficient": round(self.clustering_coefficient, 4),
            "avg_clustering": round(self.avg_clustering, 4),
            "avg_path_length": round(self.avg_path_length, 4),
            "diameter": self.diameter,
            "contradiction_edges": self.contradiction_edges,
            "contradiction_rate": round(self.contradiction_rate, 4),
            "nodes_by_domain": self.nodes_by_domain,
            "health": self.health.to_dict(),
        }

    @classmethod
    def empty(cls) -> "TopologyMetrics":
        """Create empty metrics."""
        return cls(
            node_count=0,
            edge_count=0,
            nodes_by_type={},
            edges_by_type={},
            connected_components=0,
            largest_component_size=0,
            isolated_nodes=0,
            avg_degree=0.0,
            max_degree=0,
            global_density=0.0,
            clustering_coefficient=0.0,
            avg_clustering=0.0,
            avg_path_length=0.0,
            diameter=0,
            contradiction_edges=0,
            contradiction_rate=0.0,
            nodes_by_domain={},
            health=TopologyHealth(
                status=TopologyHealthStatus.HEALTHY,
                score=100.0,
                issues=[],
                recommendations=[],
            ),
        )


class TopologyAnalyzer:
    """
    Analyzes claim graph topology and computes metrics.

    Features:
    - Node and edge statistics
    - Centrality calculations
    - Cluster detection
    - Health assessment

    Usage:
        analyzer = TopologyAnalyzer()

        # Analyze entire graph
        metrics = analyzer.analyze(nodes, edges)

        # Calculate centrality for specific node
        centrality = analyzer.calculate_centrality(node_id, nodes, edges)

        # Get health assessment
        health = analyzer.assess_health(metrics)
    """

    def __init__(
        self,
        health_thresholds: Optional[Dict[str, float]] = None,
    ):
        self.health_thresholds = health_thresholds or {
            "min_connectivity": 0.1,     # Min fraction of nodes connected
            "max_isolated": 0.2,         # Max fraction of isolated nodes
            "min_density": 0.001,        # Min global density
            "max_contradiction_rate": 0.3,  # Max contradiction rate
        }

    def analyze(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> TopologyMetrics:
        """
        Perform complete topology analysis.

        Args:
            nodes: List of graph nodes
            edges: List of graph edges

        Returns:
            TopologyMetrics with all computed metrics
        """
        if not nodes:
            return TopologyMetrics.empty()

        # Build adjacency structures
        adj_list = self._build_adjacency_list(nodes, edges)
        in_degree, out_degree = self._calculate_degrees(nodes, edges)

        # Basic counts
        node_count = len(nodes)
        edge_count = len(edges)
        nodes_by_type = self._count_by_type(nodes)
        edges_by_type = self._count_edges_by_type(edges)
        nodes_by_domain = self._count_by_domain(nodes)

        # Connectivity
        components = self._find_connected_components(nodes, adj_list)
        connected_components = len(components)
        largest_component_size = max(len(c) for c in components) if components else 0
        isolated_nodes = sum(1 for n in nodes if in_degree.get(n.id, 0) + out_degree.get(n.id, 0) == 0)

        # Degree statistics
        degrees = [in_degree.get(n.id, 0) + out_degree.get(n.id, 0) for n in nodes]
        avg_degree = sum(degrees) / node_count if node_count > 0 else 0.0
        max_degree = max(degrees) if degrees else 0

        # Density
        max_edges = node_count * (node_count - 1) if node_count > 1 else 1
        global_density = edge_count / max_edges if max_edges > 0 else 0.0

        # Clustering
        clustering_coef = self._calculate_clustering_coefficient(nodes, adj_list)
        avg_clustering = sum(clustering_coef.values()) / len(clustering_coef) if clustering_coef else 0.0

        # Path metrics (approximated for large graphs)
        avg_path_length, diameter = self._estimate_path_metrics(nodes, adj_list)

        # Contradiction metrics
        contradiction_edges = sum(1 for e in edges if e.edge_type == EdgeType.OPPOSITION)
        claim_edges = sum(1 for e in edges if e.edge_type in {EdgeType.SUPPORT, EdgeType.OPPOSITION})
        contradiction_rate = contradiction_edges / claim_edges if claim_edges > 0 else 0.0

        # Health assessment
        metrics_for_health = {
            "connectivity": (largest_component_size / node_count) if node_count > 0 else 0,
            "isolated_fraction": isolated_nodes / node_count if node_count > 0 else 0,
            "density": global_density,
            "contradiction_rate": contradiction_rate,
        }
        health = self.assess_health(metrics_for_health)

        return TopologyMetrics(
            node_count=node_count,
            edge_count=edge_count,
            nodes_by_type=nodes_by_type,
            edges_by_type=edges_by_type,
            connected_components=connected_components,
            largest_component_size=largest_component_size,
            isolated_nodes=isolated_nodes,
            avg_degree=avg_degree,
            max_degree=max_degree,
            global_density=global_density,
            clustering_coefficient=sum(clustering_coef.values()) / len(nodes) if nodes else 0.0,
            avg_clustering=avg_clustering,
            avg_path_length=avg_path_length,
            diameter=diameter,
            contradiction_edges=contradiction_edges,
            contradiction_rate=contradiction_rate,
            nodes_by_domain=nodes_by_domain,
            health=health,
        )

    def calculate_centrality(
        self,
        node_id: str,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> Optional[NodeCentrality]:
        """Calculate centrality metrics for a specific node."""
        node = next((n for n in nodes if n.id == node_id), None)
        if not node:
            return None

        adj_list = self._build_adjacency_list(nodes, edges)
        in_degree, out_degree = self._calculate_degrees(nodes, edges)

        # Degree
        degree = in_degree.get(node_id, 0) + out_degree.get(node_id, 0)

        # Closeness (simplified)
        closeness = self._calculate_closeness(node_id, nodes, adj_list)

        # Betweenness (simplified approximation)
        betweenness = self._calculate_betweenness(node_id, nodes, adj_list)

        # PageRank (simplified)
        pagerank = self._calculate_pagerank(node_id, nodes, edges)

        return NodeCentrality(
            node_id=node_id,
            node_type=node.node_type,
            degree=degree,
            in_degree=in_degree.get(node_id, 0),
            out_degree=out_degree.get(node_id, 0),
            closeness=closeness,
            betweenness=betweenness,
            pagerank=pagerank,
        )

    def analyze_cluster(
        self,
        subgraph: Subgraph,
        all_edges: List[GraphEdge],
    ) -> ClusterMetrics:
        """Analyze metrics for a cluster/subgraph."""
        node_ids = {n.id for n in subgraph.nodes}

        # Count internal vs external edges
        internal_edges = 0
        external_edges = 0

        for edge in all_edges:
            source_in = edge.source_id in node_ids
            target_in = edge.target_id in node_ids

            if source_in and target_in:
                internal_edges += 1
            elif source_in or target_in:
                external_edges += 1

        # Density
        n = subgraph.node_count
        max_edges = n * (n - 1) if n > 1 else 1
        density = internal_edges / max_edges if max_edges > 0 else 0.0

        # Path metrics within cluster
        adj_list = self._build_adjacency_list(subgraph.nodes, subgraph.edges)
        avg_path, diameter = self._estimate_path_metrics(subgraph.nodes, adj_list)

        # Modularity (simplified)
        total_edges = internal_edges + external_edges
        expected = (internal_edges / total_edges) ** 2 if total_edges > 0 else 0
        actual = internal_edges / total_edges if total_edges > 0 else 0
        modularity = actual - expected

        return ClusterMetrics(
            cluster_id=f"cluster_{subgraph.center_id[:8]}",
            center_node_id=subgraph.center_id,
            node_count=n,
            edge_count=subgraph.edge_count,
            density=density,
            diameter=diameter,
            avg_path_length=avg_path,
            internal_edges=internal_edges,
            external_edges=external_edges,
            modularity=modularity,
        )

    def get_top_central_nodes(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        top_n: int = 10,
        metric: str = "degree",
    ) -> List[NodeCentrality]:
        """
        Get top N nodes by centrality metric.

        Args:
            nodes: List of graph nodes
            edges: List of graph edges
            top_n: Number of top nodes to return
            metric: Centrality metric to sort by (degree, closeness, betweenness, pagerank)

        Returns:
            List of NodeCentrality sorted by the specified metric
        """
        if not nodes:
            return []

        # Calculate centrality for all nodes
        centralities = []
        for node in nodes:
            centrality = self.calculate_centrality(node.id, nodes, edges)
            if centrality:
                centralities.append(centrality)

        # Sort by metric
        if metric == "closeness":
            centralities.sort(key=lambda c: c.closeness, reverse=True)
        elif metric == "betweenness":
            centralities.sort(key=lambda c: c.betweenness, reverse=True)
        elif metric == "pagerank":
            centralities.sort(key=lambda c: c.pagerank, reverse=True)
        else:  # default to degree
            centralities.sort(key=lambda c: c.degree, reverse=True)

        return centralities[:top_n]

    def validate_graph(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> List[str]:
        """
        Validate graph integrity.

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        node_ids = {n.id for n in nodes}

        # Check for orphan edges
        for edge in edges:
            if edge.source_id not in node_ids:
                issues.append(f"Edge {edge.id} references missing source node: {edge.source_id}")
            if edge.target_id not in node_ids:
                issues.append(f"Edge {edge.id} references missing target node: {edge.target_id}")

        # Check for duplicate edges
        seen_edges = set()
        for edge in edges:
            key = (edge.source_id, edge.target_id, edge.edge_type)
            if key in seen_edges:
                issues.append(f"Duplicate edge: {edge.source_id} -> {edge.target_id} ({edge.edge_type})")
            seen_edges.add(key)

        # Check for self-loops
        for edge in edges:
            if edge.source_id == edge.target_id:
                issues.append(f"Self-loop detected: {edge.source_id}")

        return issues

    def assess_health(
        self,
        metrics: Dict[str, float],
    ) -> TopologyHealth:
        """
        Assess health of the graph topology.

        Args:
            metrics: Dictionary with connectivity, isolated_fraction, density, contradiction_rate

        Returns:
            TopologyHealth assessment
        """
        issues = []
        recommendations = []
        score = 100.0

        # Check connectivity
        connectivity = metrics.get("connectivity", 0)
        if connectivity < self.health_thresholds["min_connectivity"]:
            issues.append(f"Low connectivity: {connectivity:.2%}")
            recommendations.append("Increase claim-to-claim relations")
            score -= 20

        # Check isolated nodes
        isolated_fraction = metrics.get("isolated_fraction", 0)
        if isolated_fraction > self.health_thresholds["max_isolated"]:
            issues.append(f"High isolated nodes: {isolated_fraction:.2%}")
            recommendations.append("Link isolated claims to related topics/entities")
            score -= 15

        # Check density
        density = metrics.get("density", 0)
        if density < self.health_thresholds["min_density"]:
            issues.append(f"Low density: {density:.4f}")
            recommendations.append("Add more edges between related claims")
            score -= 10

        # Check contradiction rate
        contradiction_rate = metrics.get("contradiction_rate", 0)
        if contradiction_rate > self.health_thresholds["max_contradiction_rate"]:
            issues.append(f"High contradiction rate: {contradiction_rate:.2%}")
            recommendations.append("Review contradicting claims for resolution")
            score -= 25

        # Determine status
        if score >= 80:
            status = TopologyHealthStatus.HEALTHY
        elif score >= 60:
            status = TopologyHealthStatus.WARNING
        elif score >= 40:
            status = TopologyHealthStatus.DEGRADED
        else:
            status = TopologyHealthStatus.CRITICAL

        return TopologyHealth(
            status=status,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations,
        )

    def _build_adjacency_list(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> Dict[str, Set[str]]:
        """Build undirected adjacency list."""
        adj: Dict[str, Set[str]] = {n.id: set() for n in nodes}
        for edge in edges:
            if edge.source_id in adj:
                adj[edge.source_id].add(edge.target_id)
            if edge.target_id in adj:
                adj[edge.target_id].add(edge.source_id)
        return adj

    def _calculate_degrees(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Calculate in-degree and out-degree for each node."""
        in_degree: Dict[str, int] = {n.id: 0 for n in nodes}
        out_degree: Dict[str, int] = {n.id: 0 for n in nodes}

        for edge in edges:
            if edge.source_id in out_degree:
                out_degree[edge.source_id] += 1
            if edge.target_id in in_degree:
                in_degree[edge.target_id] += 1

        return in_degree, out_degree

    def _count_by_type(self, nodes: List[GraphNode]) -> Dict[str, int]:
        """Count nodes by type."""
        counts: Dict[str, int] = defaultdict(int)
        for node in nodes:
            counts[node.node_type.value] += 1
        return dict(counts)

    def _count_edges_by_type(self, edges: List[GraphEdge]) -> Dict[str, int]:
        """Count edges by type."""
        counts: Dict[str, int] = defaultdict(int)
        for edge in edges:
            counts[edge.edge_type.value] += 1
        return dict(counts)

    def _count_by_domain(self, nodes: List[GraphNode]) -> Dict[str, int]:
        """Count nodes by domain."""
        counts: Dict[str, int] = defaultdict(int)
        for node in nodes:
            counts[node.domain] += 1
        return dict(counts)

    def _find_connected_components(
        self,
        nodes: List[GraphNode],
        adj_list: Dict[str, Set[str]],
    ) -> List[Set[str]]:
        """Find connected components using DFS."""
        visited: Set[str] = set()
        components: List[Set[str]] = []

        for node in nodes:
            if node.id not in visited:
                component: Set[str] = set()
                stack = [node.id]

                while stack:
                    current = stack.pop()
                    if current in visited:
                        continue
                    visited.add(current)
                    component.add(current)
                    stack.extend(adj_list.get(current, set()) - visited)

                components.append(component)

        return components

    def _calculate_clustering_coefficient(
        self,
        nodes: List[GraphNode],
        adj_list: Dict[str, Set[str]],
    ) -> Dict[str, float]:
        """Calculate local clustering coefficient for each node."""
        coefficients: Dict[str, float] = {}

        for node in nodes:
            neighbors = adj_list.get(node.id, set())
            k = len(neighbors)

            if k < 2:
                coefficients[node.id] = 0.0
                continue

            # Count edges between neighbors
            edges_between = 0
            neighbors_list = list(neighbors)
            for i, n1 in enumerate(neighbors_list):
                for n2 in neighbors_list[i+1:]:
                    if n2 in adj_list.get(n1, set()):
                        edges_between += 1

            max_edges = k * (k - 1) / 2
            coefficients[node.id] = edges_between / max_edges if max_edges > 0 else 0.0

        return coefficients

    def _estimate_path_metrics(
        self,
        nodes: List[GraphNode],
        adj_list: Dict[str, Set[str]],
    ) -> Tuple[float, int]:
        """Estimate average path length and diameter (sample-based for large graphs)."""
        if len(nodes) <= 1:
            return 0.0, 0

        # Sample nodes for large graphs
        sample_size = min(50, len(nodes))
        sample_nodes = nodes[:sample_size]

        total_path_length = 0
        path_count = 0
        max_path = 0

        for start_node in sample_nodes:
            # BFS from start_node
            distances = self._bfs_distances(start_node.id, adj_list)

            for dist in distances.values():
                if dist > 0 and dist < float('inf'):
                    total_path_length += dist
                    path_count += 1
                    max_path = max(max_path, dist)

        avg_path = total_path_length / path_count if path_count > 0 else 0.0
        return avg_path, max_path

    def _bfs_distances(
        self,
        start_id: str,
        adj_list: Dict[str, Set[str]],
    ) -> Dict[str, int]:
        """Calculate distances from start node using BFS."""
        distances: Dict[str, int] = {start_id: 0}
        queue = [start_id]
        idx = 0

        while idx < len(queue):
            current = queue[idx]
            idx += 1

            for neighbor in adj_list.get(current, set()):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        return distances

    def _calculate_closeness(
        self,
        node_id: str,
        nodes: List[GraphNode],
        adj_list: Dict[str, Set[str]],
    ) -> float:
        """Calculate closeness centrality for a node."""
        distances = self._bfs_distances(node_id, adj_list)
        reachable = [d for d in distances.values() if d > 0]

        if not reachable:
            return 0.0

        avg_distance = sum(reachable) / len(reachable)
        return 1.0 / avg_distance if avg_distance > 0 else 0.0

    def _calculate_betweenness(
        self,
        node_id: str,
        nodes: List[GraphNode],
        adj_list: Dict[str, Set[str]],
    ) -> float:
        """Simplified betweenness centrality approximation."""
        # For simplicity, return a value based on degree
        degree = len(adj_list.get(node_id, set()))
        max_degree = max(len(neighbors) for neighbors in adj_list.values()) if adj_list else 1
        return degree / max_degree if max_degree > 0 else 0.0

    def _calculate_pagerank(
        self,
        node_id: str,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        damping: float = 0.85,
        iterations: int = 10,
    ) -> float:
        """
        Optimized PageRank calculation.

        Uses pre-built incoming edge map for O(n * iterations) instead of O(n * e * iterations).
        """
        n = len(nodes)
        if n == 0:
            return 0.0

        # Initialize scores
        scores = {node.id: 1.0 / n for node in nodes}

        # Pre-build out-degree map and incoming edges map
        out_degree: Dict[str, int] = defaultdict(int)
        incoming: Dict[str, List[str]] = defaultdict(list)

        for edge in edges:
            out_degree[edge.source_id] += 1
            incoming[edge.target_id].append(edge.source_id)

        # Iterate - now O(n * iterations) since we pre-built incoming map
        for _ in range(iterations):
            new_scores: Dict[str, float] = {}
            for node in nodes:
                incoming_score = 0.0
                for source_id in incoming.get(node.id, []):
                    source_out = out_degree.get(source_id, 1)
                    incoming_score += scores.get(source_id, 0) / source_out

                new_scores[node.id] = (1 - damping) / n + damping * incoming_score

            scores = new_scores

        return scores.get(node_id, 0.0)


# Singleton instance
_topology_analyzer: Optional[TopologyAnalyzer] = None


def get_topology_analyzer() -> TopologyAnalyzer:
    """Get singleton topology analyzer instance."""
    global _topology_analyzer
    if _topology_analyzer is None:
        _topology_analyzer = TopologyAnalyzer()
    return _topology_analyzer


def reset_topology_analyzer() -> None:
    """Reset singleton instance (for testing)."""
    global _topology_analyzer
    _topology_analyzer = None
