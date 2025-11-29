from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Optional

from .enums import TruthEventType, TruthState
from .models import DecisionRecord, TruthChangeEvent, TruthRecord, utcnow


def _serialize_dt(dt) -> str:
    return dt.isoformat()


def _deserialize_dt(raw: str):
    from datetime import datetime

    return datetime.fromisoformat(raw)


class TruthRepository:
    """
    SQLite-backed storage for Truth-DB v1.5.
    Kept intentionally simple and auditable.
    """

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

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
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
                CREATE INDEX IF NOT EXISTS idx_truth_records_domain ON truth_records(domain);
                CREATE INDEX IF NOT EXISTS idx_truth_records_state ON truth_records(current_state);

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
                CREATE INDEX IF NOT EXISTS idx_decision_truth_record ON decision_records(truth_record_id);

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
                CREATE INDEX IF NOT EXISTS idx_events_truth_record ON truth_change_events(truth_record_id);
                """
            )
            conn.commit()

    def upsert_truth_record(self, record: TruthRecord) -> TruthRecord:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO truth_records (id, slug, claim_id, domain, current_state, last_decision_id, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    current_state=excluded.current_state,
                    last_decision_id=excluded.last_decision_id,
                    metadata=excluded.metadata,
                    updated_at=excluded.updated_at
                """,
                (
                    record.id,
                    record.slug,
                    record.claim_id,
                    record.domain,
                    record.current_state.value,
                    record.last_decision_id,
                    json.dumps(record.metadata, ensure_ascii=False),
                    _serialize_dt(record.created_at),
                    _serialize_dt(record.updated_at),
                ),
            )
            conn.commit()
        return record

    def get_record_by_slug(self, slug: str) -> Optional[TruthRecord]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM truth_records WHERE slug=?", (slug,)).fetchone()
        return self._row_to_record(row)

    def get_record(self, record_id: str) -> Optional[TruthRecord]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM truth_records WHERE id=?", (record_id,)).fetchone()
        return self._row_to_record(row)

    def list_records(self, domain: str | None = None, state: TruthState | None = None, limit: int = 50) -> List[TruthRecord]:
        clauses: list[str] = []
        params: list[str] = []
        if domain:
            clauses.append("domain=?")
            params.append(domain)
        if state:
            clauses.append("current_state=?")
            params.append(state.value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM truth_records {where} ORDER BY datetime(updated_at) DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_record(row) for row in rows if row]

    def insert_decision(self, decision: DecisionRecord) -> DecisionRecord:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO decision_records (id, truth_record_id, rationale, decided_by, policy_version, threat_snapshot, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.id,
                    decision.truth_record_id,
                    decision.rationale,
                    decision.decided_by,
                    decision.policy_version,
                    decision.threat_snapshot,
                    json.dumps(decision.metadata, ensure_ascii=False),
                    _serialize_dt(decision.created_at),
                ),
            )
            conn.commit()
        return decision

    def insert_event(self, event: TruthChangeEvent) -> TruthChangeEvent:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO truth_change_events (id, truth_record_id, previous_state, new_state, event_type, reason, source, decision_id, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.truth_record_id,
                    event.previous_state.value if event.previous_state else None,
                    event.new_state.value,
                    event.event_type.value if event.event_type else None,
                    event.reason,
                    event.source,
                    event.decision_id,
                    json.dumps(event.metadata, ensure_ascii=False),
                    _serialize_dt(event.created_at),
                ),
            )
            conn.commit()
        return event

    def list_events(self, truth_record_id: str) -> List[TruthChangeEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM truth_change_events WHERE truth_record_id=? ORDER BY datetime(created_at)",
                (truth_record_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def list_decisions(self, truth_record_id: str) -> Iterable[DecisionRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM decision_records WHERE truth_record_id=? ORDER BY datetime(created_at)",
                (truth_record_id,),
            ).fetchall()
        return [self._row_to_decision(row) for row in rows]

    def _row_to_record(self, row) -> Optional[TruthRecord]:
        if row is None:
            return None
        return TruthRecord(
            id=row["id"],
            slug=row["slug"],
            claim_id=row["claim_id"],
            domain=row["domain"],
            current_state=TruthState(row["current_state"]),
            last_decision_id=row["last_decision_id"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=_deserialize_dt(row["created_at"]),
            updated_at=_deserialize_dt(row["updated_at"]),
        )

    def _row_to_event(self, row) -> TruthChangeEvent:
        return TruthChangeEvent(
            id=row["id"],
            truth_record_id=row["truth_record_id"],
            previous_state=TruthState(row["previous_state"]) if row["previous_state"] else None,
            new_state=TruthState(row["new_state"]),
            event_type=TruthEventType(row["event_type"]) if row["event_type"] else None,
            reason=row["reason"] or "",
            source=row["source"] or "",
            decision_id=row["decision_id"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=_deserialize_dt(row["created_at"]),
        )

    def _row_to_decision(self, row) -> DecisionRecord:
        return DecisionRecord(
            id=row["id"],
            truth_record_id=row["truth_record_id"],
            rationale=row["rationale"],
            decided_by=row["decided_by"],
            policy_version=row["policy_version"],
            threat_snapshot=row["threat_snapshot"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=_deserialize_dt(row["created_at"]),
        )

    def list_decisions(self, truth_record_id: str) -> Iterable[DecisionRecord]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM decision_records WHERE truth_record_id=? ORDER BY datetime(created_at)",
                (truth_record_id,),
            ).fetchall()
        return [self._row_to_decision(row) for row in rows]
