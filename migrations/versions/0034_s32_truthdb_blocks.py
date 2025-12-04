"""
Sprint 32 — Truth-DB & Sistema de Blocos v1.
Cria tabelas de FactBlock, EvidenceBlock, DecisionBlock, TruthState e ContestRecord.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Dict

DEFAULT_DB_PATH = Path("out/databases/s32_truth.sqlite")


SCHEMA_STMTS = [
    """
    PRAGMA foreign_keys = ON;
    """,
    """
    CREATE TABLE IF NOT EXISTS fact_blocks (
        id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence_blocks (
        id TEXT PRIMARY KEY,
        fact_block_id TEXT NOT NULL,
        evidence_type TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(fact_block_id) REFERENCES fact_blocks(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS decision_blocks (
        id TEXT PRIMARY KEY,
        fact_block_id TEXT NOT NULL,
        decision_type TEXT NOT NULL,
        reasoning_summary TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(fact_block_id) REFERENCES fact_blocks(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS truth_states (
        id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        fact_block_id TEXT NOT NULL,
        status TEXT NOT NULL,
        current_decision_block_id TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(fact_block_id) REFERENCES fact_blocks(id) ON DELETE CASCADE,
        FOREIGN KEY(current_decision_block_id) REFERENCES decision_blocks(id) ON DELETE SET NULL,
        CHECK (
            status NOT IN ('TRUE','REJECTED')
            OR current_decision_block_id IS NOT NULL
        )
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS contest_records (
        id TEXT PRIMARY KEY,
        truth_state_id TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        processed_decision_block_id TEXT,
        created_at TEXT NOT NULL,
        processed_at TEXT,
        FOREIGN KEY(truth_state_id) REFERENCES truth_states(id) ON DELETE CASCADE,
        FOREIGN KEY(processed_decision_block_id) REFERENCES decision_blocks(id) ON DELETE SET NULL,
        CHECK (
            status NOT IN ('RESOLVED','REJECTED','UPHELD')
            OR processed_decision_block_id IS NOT NULL
        )
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s32_fact_blocks_claim ON fact_blocks(claim_id);",
    "CREATE INDEX IF NOT EXISTS idx_s32_evidence_fact ON evidence_blocks(fact_block_id);",
    "CREATE INDEX IF NOT EXISTS idx_s32_decisions_fact ON decision_blocks(fact_block_id);",
    "CREATE INDEX IF NOT EXISTS idx_s32_truth_states_claim ON truth_states(claim_id);",
    "CREATE INDEX IF NOT EXISTS idx_s32_truth_states_status ON truth_states(status);",
    "CREATE INDEX IF NOT EXISTS idx_s32_contests_truth_state ON contest_records(truth_state_id);",
]


def apply_migration(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            for stmt in SCHEMA_STMTS:
                conn.executescript(stmt)
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
                   'fact_blocks','evidence_blocks','decision_blocks',
                   'truth_states','contest_records'
               )
            """
        ).fetchall()
        return {"tables": len(tables)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else DEFAULT_DB_PATH
    apply_migration(target)
    info = verify_schema(target)
    print(f"[s32] migration applied at {target} (tables={info['tables']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
