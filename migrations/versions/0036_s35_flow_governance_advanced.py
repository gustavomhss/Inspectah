"""
Sprint 35 — Governança avançada de rollout/catalogo.
Adiciona campos para modo/estado de rollout, critérios, hash de catálogo e auditoria.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List

base_schema = __import__(
    "migrations.versions.0034_s34_flow_multidomain_ops", fromlist=["apply_migration", "DEFAULT_DB_PATH"]
)

DEFAULT_DB_PATH = Path("out/databases/s35_flows.sqlite")


def _safe_exec(conn: sqlite3.Connection, stmt: str) -> None:
    try:
        conn.execute(stmt)
    except sqlite3.OperationalError:
        return


def _apply_alters(conn: sqlite3.Connection) -> None:
    alter_stmts: List[str] = [
        "ALTER TABLE flow_flows ADD COLUMN rollout_mode TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN rollout_state TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN rollout_started_at TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN rollout_criteria TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN catalog_hash TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN catalog_signature TEXT;",
        "ALTER TABLE flow_flow_executions ADD COLUMN mode TEXT;",
        "ALTER TABLE flow_flow_operation_logs ADD COLUMN mode TEXT;",
        "ALTER TABLE flow_flow_operation_logs ADD COLUMN actor TEXT;",
        "ALTER TABLE flow_flow_operation_logs ADD COLUMN catalog_hash TEXT;",
        "ALTER TABLE flow_flow_versions ADD COLUMN catalog_hash TEXT;",
        "ALTER TABLE flow_flow_versions ADD COLUMN catalog_signature TEXT;",
    ]
    for stmt in alter_stmts:
        _safe_exec(conn, stmt)


def apply_migration(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        base_schema.apply_migration(db_path)
        with conn:
            _apply_alters(conn)
    finally:
        conn.close()


def verify_schema(db_path: Path = DEFAULT_DB_PATH) -> Dict[str, Iterable[str]]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        flow_cols = [c[1] for c in conn.execute("PRAGMA table_info(flow_flows)").fetchall()]
        exec_cols = [c[1] for c in conn.execute("PRAGMA table_info(flow_flow_executions)").fetchall()]
        ops_cols = [c[1] for c in conn.execute("PRAGMA table_info(flow_flow_operation_logs)").fetchall()]
        versions_cols = [c[1] for c in conn.execute("PRAGMA table_info(flow_flow_versions)").fetchall()]
        return {
            "flow_flows": flow_cols,
            "flow_flow_executions": exec_cols,
            "flow_flow_operation_logs": ops_cols,
            "flow_flow_versions": versions_cols,
        }
    finally:
        conn.close()


if __name__ == "__main__":  # pragma: no cover
    apply_migration()
    info = verify_schema()
    print(f"[s35] migration applied at {DEFAULT_DB_PATH} (tables: {len(info)})")
