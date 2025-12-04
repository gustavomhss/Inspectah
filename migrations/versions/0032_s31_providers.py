"""
Sprint 31 — Providers e Perfis de Ingestão (provider-first).
Cria tabelas providers e ingestion_profiles.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict

DEFAULT_DB_PATH = Path("out/databases/s31_providers.sqlite")


def _exec_script(conn: sqlite3.Connection, stmt: str) -> None:
    conn.executescript(stmt)


SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS providers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        kind TEXT NOT NULL,
        description TEXT,
        auth TEXT,
        config TEXT,
        limits TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        created_by TEXT,
        updated_by TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ingestion_profiles (
        id TEXT PRIMARY KEY,
        provider_id TEXT NOT NULL,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        kind TEXT NOT NULL,
        country TEXT,
        language TEXT,
        categories TEXT,
        keywords TEXT,
        filters TEXT,
        frequency_minutes INTEGER NOT NULL,
        budget_daily_calls INTEGER,
        budget_monthly_calls INTEGER,
        enabled INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        created_by TEXT,
        updated_by TEXT,
        FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_profiles_provider ON ingestion_profiles(provider_id);",
    "CREATE INDEX IF NOT EXISTS idx_profiles_slug ON ingestion_profiles(slug);",
]


def apply_migration(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            for stmt in SCHEMA_STMTS:
                _exec_script(conn, stmt)
    finally:
        conn.close()


def verify_schema(db_path: Path = DEFAULT_DB_PATH) -> Dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('providers','ingestion_profiles')"
        ).fetchall()
        return {"tables": len(tables)}
    finally:
        conn.close()


def _main() -> None:
    apply_migration()
    info = verify_schema()
    print(f"[s31] migration applied at {DEFAULT_DB_PATH} (tables={info['tables']})")


if __name__ == "__main__":
    _main()
