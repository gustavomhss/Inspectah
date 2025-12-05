"""
Sprint 34 — Multi-domínio governável: versionamento, políticas e hooks de operação.
Estende o modelo de fluxos para registrar flow_version_id, domínio e perfil de ops,
e cria tabela de versões por fluxo.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List

base_schema = __import__("migrations.versions.0030_s30_flow_model_v15", fromlist=["apply_migration", "DEFAULT_DB_PATH"])

DEFAULT_DB_PATH = Path("out/databases/s34_flows.sqlite")


def _safe_exec(conn: sqlite3.Connection, stmt: str) -> None:
    try:
        conn.execute(stmt)
    except sqlite3.OperationalError:
        # Ignora erros de coluna já existente/índice já criado.
        return


def _apply_alters(conn: sqlite3.Connection) -> None:
    alter_stmts: List[str] = [
        "ALTER TABLE flow_flows ADD COLUMN domain TEXT DEFAULT 'generic';",
        "ALTER TABLE flow_flows ADD COLUMN flow_version_id TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN active_version_id TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN test_version_id TEXT;",
        "ALTER TABLE flow_flows ADD COLUMN flow_ops_profile_id TEXT;",
        "ALTER TABLE flow_flow_executions ADD COLUMN flow_version_id TEXT;",
        "ALTER TABLE flow_flow_executions ADD COLUMN operation_id TEXT;",
        "ALTER TABLE flow_flow_operation_logs ADD COLUMN flow_version_id TEXT;",
        "ALTER TABLE flow_flow_operation_logs ADD COLUMN updated_at TEXT;",
    ]
    for stmt in alter_stmts:
        _safe_exec(conn, stmt)


def _apply_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS flow_flow_versions (
            id TEXT PRIMARY KEY,
            flow_id TEXT NOT NULL,
            version_id TEXT NOT NULL,
            template_slug TEXT NOT NULL,
            estado TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(flow_id, version_id),
            FOREIGN KEY(flow_id) REFERENCES flow_flows(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_flow_versions_flow_id ON flow_flow_versions(flow_id);
        """
    )


def apply_migration(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        # garante base S30 antes de aplicar alterações
        base_schema.apply_migration(db_path)
        with conn:
            _apply_alters(conn)
            _apply_tables(conn)
    finally:
        conn.close()


def verify_schema(db_path: Path = DEFAULT_DB_PATH) -> Dict[str, Iterable[str]]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cols = conn.execute("PRAGMA table_info(flow_flows)").fetchall()
        flow_cols = [c[1] for c in cols]
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
    print(f"[s34] migration applied at {DEFAULT_DB_PATH} (tables: {len(info)})")
