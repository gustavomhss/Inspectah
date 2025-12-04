"""
Sprint 30 — Modelo de fluxos v1.5.
Cria tabelas canônicas de fluxo/execução/template/log operacional.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

DEFAULT_DB_PATH = Path("out/databases/s30_flows.sqlite")


def _exec_script(conn: sqlite3.Connection, stmt: str) -> None:
    conn.executescript(stmt)


SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS flow_flows (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        tipo_entrada TEXT NOT NULL,
        estado TEXT NOT NULL,
        template_origem_id TEXT,
        percentual_teste INTEGER DEFAULT 0,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS flow_flow_steps (
        id TEXT PRIMARY KEY,
        flow_id TEXT NOT NULL,
        ordem INTEGER NOT NULL,
        tipo_etapa TEXT NOT NULL,
        agent_role TEXT NOT NULL,
        agent_binding TEXT,
        config TEXT,
        flags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(flow_id, ordem),
        FOREIGN KEY(flow_id) REFERENCES flow_flows(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS flow_flow_templates (
        id TEXT PRIMARY KEY,
        slug TEXT NOT NULL UNIQUE,
        versao TEXT NOT NULL,
        tipo_entrada TEXT NOT NULL,
        estrutura TEXT NOT NULL,
        ativo INTEGER DEFAULT 1,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS flow_flow_executions (
        id TEXT PRIMARY KEY,
        flow_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        tipo_entrada TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        erro_resumo TEXT,
        metadata TEXT,
        FOREIGN KEY(flow_id) REFERENCES flow_flows(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS flow_flow_step_executions (
        id TEXT PRIMARY KEY,
        flow_execution_id TEXT NOT NULL,
        step_id TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        output_resumo TEXT,
        erro_resumo TEXT,
        raw_ref TEXT,
        FOREIGN KEY(flow_execution_id) REFERENCES flow_flow_executions(id) ON DELETE CASCADE,
        FOREIGN KEY(step_id) REFERENCES flow_flow_steps(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS flow_flow_operation_logs (
        id TEXT PRIMARY KEY,
        flow_id TEXT NOT NULL,
        operacao TEXT NOT NULL,
        payload TEXT,
        resultado TEXT NOT NULL,
        user_id TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(flow_id) REFERENCES flow_flows(id) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_flow_steps_flow_ordem ON flow_flow_steps(flow_id, ordem);",
    "CREATE INDEX IF NOT EXISTS idx_flow_exec_flow_started ON flow_flow_executions(flow_id, started_at);",
    "CREATE INDEX IF NOT EXISTS idx_flow_step_exec_flow_exec ON flow_flow_step_executions(flow_execution_id, step_id);",
    "CREATE INDEX IF NOT EXISTS idx_flow_state_tipo ON flow_flows(tipo_entrada, estado);",
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
            """
            SELECT name FROM sqlite_master
             WHERE type='table'
               AND name IN (
                   'flow_flows','flow_flow_steps','flow_flow_templates',
                   'flow_flow_executions','flow_flow_step_executions','flow_flow_operation_logs'
               )
            """
        ).fetchall()
        return {"tables": len(tables)}
    finally:
        conn.close()


def _main() -> None:
    apply_migration()
    info = verify_schema()
    print(f"[s30] migration applied at {DEFAULT_DB_PATH} (tables={info['tables']})")


if __name__ == "__main__":
    _main()
