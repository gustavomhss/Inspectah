"""
ClaimGraph Repository — S37

Data access layer for ClaimGraph nodes and edges.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from app.claims.graph_models import (
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
)

# Default database path
DEFAULT_DB_PATH = Path("out/databases/s37_claimgraph.sqlite")


class ClaimGraphRepository:
    """Repository for ClaimGraph persistence operations."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Ensure database exists and has schema applied."""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            migration_path = Path("db/migrations/027_sprint37_claimgraph.sql")
            if migration_path.exists():
                with open(migration_path) as f:
                    sql = f.read()
                with self._get_connection() as conn:
                    conn.executescript(sql)

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ==================== NODE OPERATIONS ====================

    def insert_node(self, node: GraphNode) -> str:
        """Insert a node into the graph. Returns node ID."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO claimgraph_nodes (id, node_type, domain, created_at, updated_at, properties)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    node.id,
                    node.node_type.value,
                    node.domain,
                    node.created_at.isoformat(),
                    node.updated_at.isoformat(),
                    json.dumps(node.properties),
                ),
            )
        return node.id

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM claimgraph_nodes WHERE id = ?", (node_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_node(row)

    def find_nodes(
        self,
        node_type: Optional[NodeType] = None,
        domain: Optional[str] = None,
        state: Optional[ClaimState] = None,
        gate: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[GraphNode]:
        """Find nodes with optional filters."""
        conditions = []
        params: List[Any] = []

        if node_type:
            conditions.append("node_type = ?")
            params.append(node_type.value)
        if domain:
            conditions.append("domain = ?")
            params.append(domain)
        if state:
            conditions.append("json_extract(properties, '$.state') = ?")
            params.append(state.value)
        if gate:
            conditions.append("json_extract(properties, '$.gate') = ?")
            params.append(gate)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM claimgraph_nodes
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params,
            ).fetchall()
        return [self._row_to_node(row) for row in rows]

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """Update node properties. Returns True if updated."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE claimgraph_nodes
                SET properties = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(properties), datetime.now(timezone.utc).replace(tzinfo=None).isoformat(), node_id),
            )
        return cursor.rowcount > 0

    def delete_node(self, node_id: str) -> bool:
        """Delete a node (cascades to edges). Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM claimgraph_nodes WHERE id = ?", (node_id,)
            )
        return cursor.rowcount > 0

    def count_nodes(
        self,
        node_type: Optional[NodeType] = None,
        domain: Optional[str] = None,
    ) -> int:
        """Count nodes with optional filters."""
        conditions = []
        params: List[Any] = []

        if node_type:
            conditions.append("node_type = ?")
            params.append(node_type.value)
        if domain:
            conditions.append("domain = ?")
            params.append(domain)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_connection() as conn:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM claimgraph_nodes WHERE {where_clause}",
                params,
            ).fetchone()
        return row["cnt"] if row else 0

    # ==================== EDGE OPERATIONS ====================

    def insert_edge(self, edge: GraphEdge) -> str:
        """Insert an edge into the graph. Returns edge ID."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO claimgraph_edges (id, source_id, target_id, edge_type, weight, created_at, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.id,
                    edge.source_id,
                    edge.target_id,
                    edge.edge_type.value,
                    edge.weight,
                    edge.created_at.isoformat(),
                    json.dumps(edge.properties),
                ),
            )
        return edge.id

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM claimgraph_edges WHERE id = ?", (edge_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_edge(row)

    def find_edges(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        edge_type: Optional[EdgeType] = None,
        limit: int = 100,
    ) -> List[GraphEdge]:
        """Find edges with optional filters."""
        conditions = []
        params: List[Any] = []

        if source_id:
            conditions.append("source_id = ?")
            params.append(source_id)
        if target_id:
            conditions.append("target_id = ?")
            params.append(target_id)
        if edge_type:
            conditions.append("edge_type = ?")
            params.append(edge_type.value)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM claimgraph_edges
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [self._row_to_edge(row) for row in rows]

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM claimgraph_edges WHERE id = ?", (edge_id,)
            )
        return cursor.rowcount > 0

    def count_edges(
        self,
        edge_type: Optional[EdgeType] = None,
        domain: Optional[str] = None,
    ) -> int:
        """Count edges with optional filters."""
        if domain:
            # Join with nodes to filter by domain
            with self._get_connection() as conn:
                if edge_type:
                    row = conn.execute(
                        """
                        SELECT COUNT(*) as cnt FROM claimgraph_edges e
                        JOIN claimgraph_nodes n ON e.source_id = n.id
                        WHERE n.domain = ? AND e.edge_type = ?
                        """,
                        (domain, edge_type.value),
                    ).fetchone()
                else:
                    row = conn.execute(
                        """
                        SELECT COUNT(*) as cnt FROM claimgraph_edges e
                        JOIN claimgraph_nodes n ON e.source_id = n.id
                        WHERE n.domain = ?
                        """,
                        (domain,),
                    ).fetchone()
        else:
            with self._get_connection() as conn:
                if edge_type:
                    row = conn.execute(
                        "SELECT COUNT(*) as cnt FROM claimgraph_edges WHERE edge_type = ?",
                        (edge_type.value,),
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT COUNT(*) as cnt FROM claimgraph_edges"
                    ).fetchone()
        return row["cnt"] if row else 0

    # ==================== GRAPH QUERIES ====================

    def get_cluster(
        self, center_id: str, depth: int = 2
    ) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """
        Get a subgraph centered on a node, expanding to given depth.

        Optimized with recursive CTE to fetch all nodes and edges in 2 queries
        instead of N+1 queries per node.
        """
        with self._get_connection() as conn:
            # Use recursive CTE to find all connected node IDs within depth
            node_rows = conn.execute(
                """
                WITH RECURSIVE connected_nodes(id, depth) AS (
                    -- Base case: start with center node
                    SELECT ?, 0
                    WHERE EXISTS (SELECT 1 FROM claimgraph_nodes WHERE id = ?)

                    UNION

                    -- Recursive case: expand to connected nodes
                    SELECT
                        CASE
                            WHEN e.source_id = cn.id THEN e.target_id
                            ELSE e.source_id
                        END,
                        cn.depth + 1
                    FROM connected_nodes cn
                    JOIN claimgraph_edges e ON e.source_id = cn.id OR e.target_id = cn.id
                    WHERE cn.depth < ?
                )
                SELECT DISTINCT n.*
                FROM claimgraph_nodes n
                JOIN connected_nodes cn ON n.id = cn.id
                """,
                (center_id, center_id, depth),
            ).fetchall()

            nodes = [self._row_to_node(row) for row in node_rows]
            node_ids = {node.id for node in nodes}

            if not node_ids:
                return [], []

            # Fetch all edges between the discovered nodes in one query
            placeholders = ",".join("?" * len(node_ids))
            edge_rows = conn.execute(
                f"""
                SELECT * FROM claimgraph_edges
                WHERE source_id IN ({placeholders})
                   OR target_id IN ({placeholders})
                """,
                list(node_ids) + list(node_ids),
            ).fetchall()

            edges = [
                self._row_to_edge(row)
                for row in edge_rows
                if row["source_id"] in node_ids and row["target_id"] in node_ids
            ]

        return nodes, edges

    def get_contradictions(
        self, claim_id: str, min_strength: float = 0.0
    ) -> List[ContradictionResult]:
        """Get claims that oppose/contradict the given claim."""
        results: List[ContradictionResult] = []

        with self._get_connection() as conn:
            # Find opposition edges where claim is source
            rows = conn.execute(
                """
                SELECT id, target_id, weight FROM claimgraph_edges
                WHERE source_id = ? AND edge_type = 'opposition'
                AND (weight IS NULL OR weight >= ?)
                ORDER BY weight DESC
                """,
                (claim_id, min_strength),
            ).fetchall()
            for row in rows:
                results.append(
                    ContradictionResult(
                        claim_id=claim_id,
                        opposing_claim_id=row["target_id"],
                        strength=row["weight"] or 1.0,
                        edge_id=row["id"],
                    )
                )

            # Find opposition edges where claim is target
            rows = conn.execute(
                """
                SELECT id, source_id, weight FROM claimgraph_edges
                WHERE target_id = ? AND edge_type = 'opposition'
                AND (weight IS NULL OR weight >= ?)
                ORDER BY weight DESC
                """,
                (claim_id, min_strength),
            ).fetchall()
            for row in rows:
                results.append(
                    ContradictionResult(
                        claim_id=claim_id,
                        opposing_claim_id=row["source_id"],
                        strength=row["weight"] or 1.0,
                        edge_id=row["id"],
                    )
                )

        return results

    def get_timeline(
        self, topic_id: str, limit: int = 100
    ) -> List[GraphNode]:
        """Get claims tagged with a topic, ordered by creation time."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT n.* FROM claimgraph_nodes n
                JOIN claimgraph_edges e ON n.id = e.source_id
                WHERE e.target_id = ? AND e.edge_type = 'tagged'
                AND n.node_type = 'claim'
                ORDER BY n.created_at ASC
                LIMIT ?
                """,
                (topic_id, limit),
            ).fetchall()
        return [self._row_to_node(row) for row in rows]

    # ==================== METRICS ====================

    def get_metrics(self, domain: Optional[str] = None) -> ClaimGraphMetrics:
        """Get aggregate metrics for the graph."""
        with self._get_connection() as conn:
            if domain:
                node_counts = conn.execute(
                    """
                    SELECT node_type, COUNT(*) as cnt
                    FROM claimgraph_nodes WHERE domain = ?
                    GROUP BY node_type
                    """,
                    (domain,),
                ).fetchall()
                edge_count = conn.execute(
                    """
                    SELECT COUNT(*) as cnt FROM claimgraph_edges e
                    JOIN claimgraph_nodes n ON e.source_id = n.id
                    WHERE n.domain = ?
                    """,
                    (domain,),
                ).fetchone()
                opposition_count = conn.execute(
                    """
                    SELECT COUNT(*) as cnt FROM claimgraph_edges e
                    JOIN claimgraph_nodes n ON e.source_id = n.id
                    WHERE n.domain = ? AND e.edge_type = 'opposition'
                    """,
                    (domain,),
                ).fetchone()
            else:
                node_counts = conn.execute(
                    "SELECT node_type, COUNT(*) as cnt FROM claimgraph_nodes GROUP BY node_type"
                ).fetchall()
                edge_count = conn.execute(
                    "SELECT COUNT(*) as cnt FROM claimgraph_edges"
                ).fetchone()
                opposition_count = conn.execute(
                    "SELECT COUNT(*) as cnt FROM claimgraph_edges WHERE edge_type = 'opposition'"
                ).fetchone()

        counts = {row["node_type"]: row["cnt"] for row in node_counts}
        total_nodes = sum(counts.values())
        total_edges = edge_count["cnt"] if edge_count else 0
        oppositions = opposition_count["cnt"] if opposition_count else 0

        # Calculate density
        if total_nodes <= 1:
            density = 0.0
        else:
            max_edges = total_nodes * (total_nodes - 1)
            density = total_edges / max_edges if max_edges > 0 else 0.0

        # Calculate contradiction rate
        contradiction_rate = oppositions / total_edges if total_edges > 0 else 0.0

        return ClaimGraphMetrics(
            node_count=total_nodes,
            edge_count=total_edges,
            claim_count=counts.get("claim", 0),
            entity_count=counts.get("entity", 0),
            case_count=counts.get("case", 0),
            topic_count=counts.get("topic", 0),
            cluster_density=density,
            contradiction_rate=contradiction_rate,
        )

    # ==================== HELPERS ====================

    def _row_to_node(self, row: sqlite3.Row) -> GraphNode:
        """Convert a database row to a GraphNode."""
        return GraphNode(
            id=row["id"],
            node_type=NodeType(row["node_type"]),
            domain=row["domain"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            properties=json.loads(row["properties"]),
        )

    def _row_to_edge(self, row: sqlite3.Row) -> GraphEdge:
        """Convert a database row to a GraphEdge."""
        return GraphEdge(
            id=row["id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            edge_type=EdgeType(row["edge_type"]),
            weight=row["weight"],
            created_at=datetime.fromisoformat(row["created_at"]),
            properties=json.loads(row["properties"]),
        )
