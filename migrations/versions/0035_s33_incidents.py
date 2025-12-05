"""
Sprint 33 — Modelo de Incident (OracleOps).
Cria tabela ops_incidents com ciclo de vida básico.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB_PATH = Path("out/databases/s33_ops.sqlite")

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS ops_incidents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    state TEXT NOT NULL,
    component_id TEXT,
    slo_ids TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_s33_incidents_state ON ops_incidents(state);
CREATE INDEX IF NOT EXISTS idx_s33_incidents_component ON ops_incidents(component_id);
"""


def apply_migration(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def verify(db_path: Path = DEFAULT_DB_PATH) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ops_incidents'"
        ).fetchall()
        return {"tables": len(tables)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else DEFAULT_DB_PATH
    apply_migration(target)
    info = verify(target)
    print(f"[s33] incidents migration applied to {target} (tables={info['tables']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
