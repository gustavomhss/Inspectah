"""
Sprint 21 — Console de Fontes: schema de fontes.
Ref.: docs/sprint_21_modelo_dados_fontes.md, docs/sprint_21_ciclo_vida_fontes.md
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        slug TEXT UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        type TEXT NOT NULL,
        category TEXT,
        themes TEXT,
        info_types TEXT,
        refresh_interval INTEGER,
        protocol TEXT,
        format TEXT,
        endpoint TEXT,
        auth_type TEXT,
        auth_config TEXT,
        request_params TEXT,
        headers TEXT,
        frequency TEXT,
        timeout_ms INTEGER,
        retry_policy TEXT,
        parsing_config TEXT,
        redundancy_group TEXT,
        redundancy_role TEXT,
        state TEXT NOT NULL,
        state_reason TEXT,
        state_updated_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        created_by TEXT,
        updated_by TEXT,
        last_reviewed_by TEXT,
        meta TEXT,
        conflict_flags TEXT,
        conflict_with_sources TEXT,
        has_open_contestation INTEGER DEFAULT 0,
        last_conflict_at TEXT,
        evidence_refs TEXT,
        trust_severity TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS source_state_history (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL REFERENCES sources(id),
        from_state TEXT,
        to_state TEXT NOT NULL,
        reason TEXT NOT NULL,
        changed_by TEXT,
        created_at TEXT NOT NULL,
        conflict_flag INTEGER DEFAULT 0,
        conflict_types TEXT,
        conflict_with_sources TEXT,
        contestations TEXT,
        evidence_refs TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS source_health_checks (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL REFERENCES sources(id),
        status TEXT NOT NULL,
        latency_ms INTEGER NOT NULL,
        checked_at TEXT NOT NULL,
        error TEXT,
        meta TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS source_categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS source_category_links (
        source_id TEXT NOT NULL REFERENCES sources(id),
        category_id TEXT NOT NULL REFERENCES source_categories(id),
        PRIMARY KEY (source_id, category_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS source_types (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        defaults TEXT
    );
    """,
]


def apply_migration(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for stmt in SCHEMA_STMTS:
                conn.executescript(stmt)
            _ensure_refresh_interval(conn)
    finally:
        conn.close()


def verify_schema(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('sources','source_state_history','source_health_checks','source_categories','source_category_links','source_types')"
        )
        names = {row[0] for row in cursor.fetchall()}
        return {"tables": len(names)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("out/databases/s21_sources.sqlite")
    apply_migration(target)
    info = verify_schema(target)
    print(f"Sprint 21 sources migration applied to {target} ({info['tables']} tables).")
    return 0


def _ensure_refresh_interval(conn: sqlite3.Connection) -> None:
    info = conn.execute("PRAGMA table_info('sources')").fetchall()
    columns = {row[1] for row in info}
    if "refresh_interval" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN refresh_interval INTEGER")
        conn.commit()


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
