"""
Sprint 29 — Fluxos de agentes configuráveis por domínio.
Cria tabelas agent_flow_configs e agent_flow_steps.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict


SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS agent_flow_configs (
        id TEXT PRIMARY KEY,
        domain_key TEXT NOT NULL UNIQUE,
        name TEXT,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        change_reason TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        created_by TEXT,
        updated_by TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_flow_steps (
        id TEXT PRIMARY KEY,
        flow_id TEXT NOT NULL,
        position INTEGER NOT NULL,
        agent_role TEXT NOT NULL,
        params TEXT,
        required INTEGER DEFAULT 1,
        can_fail_soft INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (flow_id, position),
        FOREIGN KEY(flow_id) REFERENCES agent_flow_configs(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_agent_flow_steps_flow_position ON agent_flow_steps(flow_id, position);",
]


def apply_migration(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            for stmt in SCHEMA_STMTS:
                conn.executescript(stmt)
    finally:
        conn.close()


def verify_schema(db_path: Path) -> Dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('agent_flow_configs','agent_flow_steps')"
        ).fetchall()
        step_index = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_agent_flow_steps_flow_position'"
        ).fetchone()
        return {"tables": len(tables), "step_index": 1 if step_index else 0}
    finally:
        conn.close()


def _main() -> None:
    db_path = Path("out/databases/s29_agent_flows.sqlite")
    apply_migration(db_path)
    info = verify_schema(db_path)
    print(f"[s29] migration applied at {db_path} (tables={info['tables']}, index={info['step_index']})")


if __name__ == "__main__":
    _main()
