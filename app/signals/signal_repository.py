"""
Signal Repository — S37

Persistence layer for signal snapshots.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from uuid import uuid4

DEFAULT_DB_PATH = Path("out/databases/s37_signals.sqlite")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS signal_snapshots (
    id TEXT PRIMARY KEY,
    signal_type TEXT NOT NULL,
    domain TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    values_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ss_type_domain ON signal_snapshots(signal_type, domain);
CREATE INDEX IF NOT EXISTS idx_ss_timestamp ON signal_snapshots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ss_domain ON signal_snapshots(domain);

CREATE TABLE IF NOT EXISTS signal_schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

INSERT OR IGNORE INTO signal_schema_version (version, applied_at)
VALUES ('signals_schema_v1', datetime('now'));
"""


def _generate_id() -> str:
    return f"sig_{uuid4().hex[:12]}"


class SignalRepository:
    """Repository for persisting signal snapshots."""

    def __init__(self, db_path: Optional[Path] = None):
        # Support in-memory database for testing
        if db_path == ":memory:" or str(db_path) == ":memory:":
            self.db_path = ":memory:"
            self._is_memory = True
            self._memory_conn: Optional[sqlite3.Connection] = None
        else:
            self.db_path = db_path or DEFAULT_DB_PATH
            self._is_memory = False
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Ensure database exists and has schema applied."""
        if not self._is_memory:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)

    @property
    def conn(self) -> sqlite3.Connection:
        """Direct connection access (for testing). Use with caution."""
        if self._is_memory and self._memory_conn:
            return self._memory_conn
        raise ValueError("Direct conn access only available for in-memory databases")

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with row factory."""
        # For in-memory databases, reuse the same connection
        if self._is_memory:
            if self._memory_conn is None:
                self._memory_conn = sqlite3.connect(":memory:")
                self._memory_conn.row_factory = sqlite3.Row
            try:
                yield self._memory_conn
                self._memory_conn.commit()
            except Exception:
                self._memory_conn.rollback()
                raise
        else:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def save_snapshot(self, snapshot: Dict[str, Any]) -> str:
        """
        Save a signal snapshot.

        Args:
            snapshot: Dict with signal_type, domain, timestamp, values, metadata

        Returns:
            Snapshot ID
        """
        snapshot_id = _generate_id()
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO signal_snapshots
                (id, signal_type, domain, timestamp, values_json, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    snapshot["signal_type"],
                    snapshot["domain"],
                    snapshot["timestamp"],
                    json.dumps(snapshot.get("values", {})),
                    json.dumps(snapshot.get("metadata", {})),
                    now,
                ),
            )

        return snapshot_id

    def get_latest(
        self,
        signal_type: str,
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        """Get the latest snapshot for a signal type and domain."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM signal_snapshots
                WHERE signal_type = ? AND domain = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (signal_type, domain),
            ).fetchone()

        if not row:
            return None

        return self._row_to_snapshot(row)

    def get_history(
        self,
        signal_type: str,
        domain: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get historical snapshots for a signal type and domain."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM signal_snapshots
                WHERE signal_type = ? AND domain = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (signal_type, domain, limit),
            ).fetchall()

        return [self._row_to_snapshot(row) for row in rows]

    def get_all_latest(self, domain: str) -> List[Dict[str, Any]]:
        """Get latest snapshot for each signal type in a domain.

        Note: Uses 4 separate queries instead of window function because SQLite's
        indexed lookups with LIMIT 1 are 2-4x faster than ROW_NUMBER() OVER().
        Benchmarked with 40-40000 rows: 4 queries consistently outperforms.
        """
        signal_types = [
            "mentiras_em_circulacao",
            "campo_batalha",
            "radar_silencio",
            "fragilidade_narrativa",
        ]

        results = []
        for signal_type in signal_types:
            snapshot = self.get_latest(signal_type, domain)
            if snapshot:
                results.append(snapshot)

        return results

    def count_snapshots(
        self,
        signal_type: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> int:
        """Count snapshots with optional filters."""
        conditions = []
        params: List[Any] = []

        if signal_type:
            conditions.append("signal_type = ?")
            params.append(signal_type)
        if domain:
            conditions.append("domain = ?")
            params.append(domain)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_connection() as conn:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM signal_snapshots WHERE {where_clause}",
                params,
            ).fetchone()

        return row["cnt"] if row else 0

    def _row_to_snapshot(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a snapshot dict."""
        try:
            values = json.loads(row["values_json"]) if row["values_json"] else {}
        except (json.JSONDecodeError, TypeError):
            values = {}

        try:
            metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
        except (json.JSONDecodeError, TypeError):
            metadata = {}

        return {
            "id": row["id"],
            "signal_type": row["signal_type"],
            "domain": row["domain"],
            "timestamp": row["timestamp"],
            "values": values,
            "metadata": metadata,
            "created_at": row["created_at"],
        }
