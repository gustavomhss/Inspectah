"""Aplicador simples de migrations SQL para a Sprint 22."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path("out/databases/s22_ingestion.sqlite")


def apply_sql(sql_path: Path, db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    script = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(script)
        conn.commit()
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("usage: python -m scripts.db.migrate <sql_file> [db_path]")
    sql_path = Path(argv[1]).expanduser()
    db_path = Path(argv[2]).expanduser() if len(argv) > 2 else DEFAULT_DB
    if not sql_path.exists():
        raise SystemExit(f"SQL file not found: {sql_path}")
    apply_sql(sql_path, db_path)
    print(f"[s22_migrate] Applied {sql_path} to {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
