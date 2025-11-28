"""
Sprint 25 - LayersTrace and Incidents persistence.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS layers_traces (
        id TEXT PRIMARY KEY,
        truth_record_id TEXT,
        claim_id TEXT NOT NULL,
        pipeline TEXT NOT NULL,
        trace_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s25_layers_traces_truth ON layers_traces(truth_record_id);",
    """
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        domain TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        ref_truth_record_id TEXT,
        ref_case_id TEXT,
        signals TEXT,
        summary TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_s25_incidents_status ON incidents(status);",
    "CREATE INDEX IF NOT EXISTS idx_s25_incidents_domain ON incidents(domain);",
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
            "AND name IN ('layers_traces','incidents')"
        )
        names = {row[0] for row in cursor.fetchall()}
        return {"tables": len(names)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("out/databases/s25_truth.sqlite")
    apply_migration(target)
    info = verify_schema(target)
    print(f"[S25] LayersTrace/Incidents migration applied to {target} ({info['tables']} tables).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
