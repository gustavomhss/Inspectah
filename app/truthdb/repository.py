from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from app.truthdb.models import TruthChangeEvent, TruthRecord, TruthState, utcnow

def _serialize_dt(dt) -> str:
    return dt.isoformat()


def _deserialize_dt(raw: str):
    from datetime import datetime

    return datetime.fromisoformat(raw)


class TruthRepository:
    def __init__(self, db_path: Path | None = None):
        resolved = db_path or Path(os.environ.get("INSPECTAH_S24_TRUTH_DB_PATH", "out/databases/s24_truth.sqlite"))
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

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS truth_records (
                    claim_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    metadata TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS truth_change_events (
                    id TEXT PRIMARY KEY,
                    claim_id TEXT NOT NULL,
                    previous_state TEXT,
                    new_state TEXT NOT NULL,
                    rationale TEXT,
                    source TEXT,
                    debunk_issue_id TEXT,
                    decision_id TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def upsert_truth_record(self, record: TruthRecord) -> TruthRecord:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO truth_records (claim_id, state, version, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(claim_id) DO UPDATE SET
                    state=excluded.state,
                    version=truth_records.version + 1,
                    metadata=excluded.metadata,
                    updated_at=excluded.updated_at
                """,
                (record.claim_id, record.state.value, record.version, json.dumps(record.metadata, ensure_ascii=False), _serialize_dt(record.updated_at)),
            )
            conn.commit()
        return record

    def append_event(self, event: TruthChangeEvent) -> TruthChangeEvent:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO truth_change_events (id, claim_id, previous_state, new_state, rationale, source, debunk_issue_id, decision_id, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.claim_id,
                    event.previous_state.value if event.previous_state else None,
                    event.new_state.value,
                    event.rationale,
                    event.source,
                    event.debunk_issue_id,
                    event.decision_id,
                    json.dumps(event.metadata, ensure_ascii=False),
                    _serialize_dt(event.created_at),
                ),
            )
            conn.commit()
        return event

    def latest_record(self, claim_id: str) -> Optional[TruthRecord]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM truth_records WHERE claim_id=?", (claim_id,)).fetchone()
        if not row:
            return None
        return TruthRecord(
            claim_id=row["claim_id"],
            state=TruthState(row["state"]),
            version=int(row["version"]),
            metadata=json.loads(row["metadata"] or "{}"),
            updated_at=_deserialize_dt(row["updated_at"]),
        )

    def list_events(self, claim_id: str) -> List[TruthChangeEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM truth_change_events WHERE claim_id=? ORDER BY datetime(created_at)",
                (claim_id,),
            ).fetchall()
        return [
            TruthChangeEvent(
                id=row["id"],
                claim_id=row["claim_id"],
                previous_state=TruthState(row["previous_state"]) if row["previous_state"] else None,
                new_state=TruthState(row["new_state"]),
                rationale=row["rationale"],
                source=row["source"],
                debunk_issue_id=row["debunk_issue_id"],
                decision_id=row["decision_id"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=_deserialize_dt(row["created_at"]),
            )
            for row in rows
        ]


def gen_event_id() -> str:
    return f"tce_{uuid.uuid4().hex[:10]}"
