"""
Sprint 25 - Truth-DB v1.5 minimal models (TruthRecord, DecisionRecord, TruthChangeEvent).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS truth_records (
        id TEXT PRIMARY KEY,
        slug TEXT UNIQUE NOT NULL,
        claim_id TEXT,
        domain TEXT NOT NULL,
        current_state TEXT NOT NULL,
        last_decision_id TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s25_truth_records_domain ON truth_records(domain);",
    "CREATE INDEX IF NOT EXISTS idx_s25_truth_records_state ON truth_records(current_state);",
    """
    CREATE TABLE IF NOT EXISTS decision_records (
        id TEXT PRIMARY KEY,
        truth_record_id TEXT NOT NULL,
        rationale TEXT NOT NULL,
        decided_by TEXT NOT NULL,
        policy_version TEXT,
        threat_snapshot TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s25_decisions_truth_record ON decision_records(truth_record_id);",
    """
    CREATE TABLE IF NOT EXISTS truth_change_events (
        id TEXT PRIMARY KEY,
        truth_record_id TEXT NOT NULL,
        previous_state TEXT,
        new_state TEXT NOT NULL,
        event_type TEXT,
        reason TEXT,
        source TEXT,
        decision_id TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s25_events_truth_record ON truth_change_events(truth_record_id);",
]


def apply_migration(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for stmt in SCHEMA_STMTS:
                conn.executescript(stmt)
    finally:
        conn.close()


def verify_schema(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('truth_records','decision_records','truth_change_events')"
        )
        names = {row[0] for row in cursor.fetchall()}
        return {"tables": len(names)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("out/databases/s25_truth.sqlite")
    apply_migration(target)
    info = verify_schema(target)
    print(f"[S25] Truth-DB migration applied to {target} ({info['tables']} tables).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
