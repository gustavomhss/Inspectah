#!/usr/bin/env python
from __future__ import annotations

import sys
from datetime import datetime

from app.ingestion.repository import IngestionRepository


def main(source_id: str) -> None:
    repo = IngestionRepository()
    runs = repo.list_runs_by_source(source_id, limit=10, offset=0)
    print(f"Last runs for {source_id} at {datetime.utcnow().isoformat()} UTC:")
    for run in runs:
        print(
            run.id,
            run.status.value,
            run.started_at.isoformat(),
            run.finished_at.isoformat() if run.finished_at else None,
            getattr(run, "error_message", None),
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: print_ingestion_runs.py <source_id>")
        sys.exit(1)
    main(sys.argv[1])
