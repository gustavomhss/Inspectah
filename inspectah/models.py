from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .config import DB_PATH
from .evidence_vault.metadata import EvidenceRecord, record_from_row, serialize_lgpd_tags

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        source_type TEXT NOT NULL,
        config TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source_runs (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        status TEXT NOT NULL,
        error_message TEXT,
        UNIQUE(source_id, started_at),
        FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS observations (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        run_id TEXT,
        canonical_key TEXT NOT NULL,
        observed_at TEXT NOT NULL,
        payload_hash TEXT NOT NULL,
        payload_path TEXT NOT NULL,
        payload_mime TEXT,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
        UNIQUE(source_id, canonical_key, observed_at),
        FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
        FOREIGN KEY (run_id) REFERENCES source_runs(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT NOT NULL,
        canonical_url TEXT NOT NULL,
        canonical_key TEXT,
        content_hash TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        manifest_path TEXT NOT NULL,
        latest_observation_id TEXT,
        confidence_score REAL NOT NULL DEFAULT 0,
        confidence_profile_id TEXT,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
        updated_at TEXT NOT NULL DEFAULT (DATETIME('now')),
        UNIQUE(source_id, content_hash),
        FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
        FOREIGN KEY (latest_observation_id) REFERENCES observations(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS item_versions (
        id TEXT PRIMARY KEY,
        item_id INTEGER NOT NULL,
        observation_id TEXT NOT NULL,
        source_run_id TEXT,
        collected_at TEXT NOT NULL,
        manifest_path TEXT NOT NULL,
        snapshot_path TEXT,
        version INTEGER NOT NULL,
        diff_summary TEXT,
        created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
        UNIQUE(item_id, version),
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
        FOREIGN KEY (observation_id) REFERENCES observations(id) ON DELETE CASCADE,
        FOREIGN KEY (source_run_id) REFERENCES source_runs(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS item_kv (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        field_type TEXT NOT NULL,
        value_string TEXT,
        value_numeric REAL,
        value_timestamp TEXT,
        value_boolean INTEGER,
        FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence_records (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        item_id INTEGER,
        item_version_id TEXT,
        evidence_type TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        ingested_at TEXT NOT NULL,
        storage_key TEXT NOT NULL,
        hash_alg TEXT NOT NULL,
        hash_value TEXT NOT NULL,
        lgpd_tags TEXT NOT NULL,
        size_bytes INTEGER NOT NULL,
        checksum_status TEXT NOT NULL,
        FOREIGN KEY (source_id) REFERENCES sources(id),
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (item_version_id) REFERENCES item_versions(id)
    )
    """,
]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        for statement in SCHEMA_STATEMENTS:
            conn.execute(statement)
        conn.commit()


def reset_db() -> None:
    db_path = Path(DB_PATH)
    if db_path.exists():
        db_path.unlink()


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def item_exists(conn: sqlite3.Connection, source_id: str, content_hash: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM items WHERE source_id = ? AND content_hash = ? LIMIT 1",
        (source_id, content_hash),
    )
    return cur.fetchone() is not None


def insert_item(
    conn: sqlite3.Connection,
    source_id: str,
    canonical_url: str,
    content_hash: str,
    collected_at: datetime,
    manifest_path: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO items (source_id, canonical_url, content_hash, collected_at, manifest_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source_id, canonical_url, content_hash, collected_at.isoformat(), manifest_path),
    )
    conn.commit()
    return cur.lastrowid


def insert_item_kv(
    conn: sqlite3.Connection,
    item_id: int,
    field_name: str,
    field_type: str,
    value_string: Optional[str] = None,
    value_numeric: Optional[float] = None,
    value_timestamp: Optional[datetime] = None,
) -> None:
    conn.execute(
        """
        INSERT INTO item_kv (item_id, field_name, field_type, value_string, value_numeric, value_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            item_id,
            field_name,
            field_type,
            value_string,
            value_numeric,
            value_timestamp.isoformat() if value_timestamp else None,
        ),
    )
    conn.commit()


def fetch_items_by_source(conn: sqlite3.Connection, source_id: str) -> List[Dict[str, str]]:
    cur = conn.execute(
        "SELECT id, manifest_path FROM items WHERE source_id = ? ORDER BY id",
        (source_id,),
    )
    rows: List[Dict[str, str]] = []
    for row in cur.fetchall():
        rows.append({"id": row["id"], "manifest_path": row["manifest_path"]})
    return rows


def insert_evidence_record(conn: sqlite3.Connection, record: EvidenceRecord) -> None:
    conn.execute(
        """
        INSERT INTO evidence_records (
            id,
            source_id,
            item_id,
            item_version_id,
            evidence_type,
            collected_at,
            ingested_at,
            storage_key,
            hash_alg,
            hash_value,
            lgpd_tags,
            size_bytes,
            checksum_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.evidence_id,
            record.source_id,
            record.item_id,
            record.item_version_id,
            record.evidence_type,
            record.collected_at.isoformat(),
            record.ingested_at.isoformat(),
            record.storage_key,
            record.hash_alg,
            record.hash_value,
            serialize_lgpd_tags(record.lgpd_tags),
            record.size_bytes,
            record.checksum_status,
        ),
    )
    conn.commit()


def fetch_evidence_record(conn: sqlite3.Connection, evidence_id: str) -> Optional[EvidenceRecord]:
    cur = conn.execute(
        """
        SELECT
            id,
            source_id,
            evidence_type,
            collected_at,
            ingested_at,
            storage_key,
            hash_alg,
            hash_value,
            lgpd_tags,
            size_bytes,
            checksum_status
        FROM evidence_records
        WHERE id = ?
        LIMIT 1
        """,
        (evidence_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return record_from_row(row)
