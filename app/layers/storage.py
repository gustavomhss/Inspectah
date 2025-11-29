from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from app.layers.models import LayersTrace


class LayersTraceRepository:
    def __init__(self, db_path: Path | None = None):
        resolved = db_path or Path(os.environ.get("INSPECTAH_S25_TRUTH_DB_PATH", "out/databases/s25_truth.sqlite"))
        self.db_path = Path(resolved)
        self._ensure_schema()

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self):
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS layers_traces (
                    id TEXT PRIMARY KEY,
                    truth_record_id TEXT,
                    claim_id TEXT NOT NULL,
                    pipeline TEXT NOT NULL,
                    trace_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def save_trace(self, trace: LayersTrace, trace_id: str, truth_record_id: str | None = None) -> str:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO layers_traces (id, truth_record_id, claim_id, pipeline, trace_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    truth_record_id,
                    trace.claim_id,
                    trace.pipeline,
                    json.dumps(asdict(trace), ensure_ascii=False, default=str),
                    trace.created_at.isoformat(),
                ),
            )
            conn.commit()
        return trace_id

    def get_by_truth_record(self, truth_record_id: str) -> Optional[LayersTrace]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT trace_json FROM layers_traces WHERE truth_record_id=? ORDER BY datetime(created_at) DESC LIMIT 1",
                (truth_record_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row["trace_json"])
        return LayersTrace(
            claim_id=data["claim_id"],
            pipeline=data["pipeline"],
            executions=data.get("executions", []),
            created_at=data.get("created_at"),
        )
