from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .enums import TruthEventType, TruthState
from .models import DecisionRecord, TruthChangeEvent, TruthRecord, utcnow

logger = logging.getLogger(__name__)


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

    def get_record_by_claim_id(self, claim_id: str) -> Optional[TruthRecord]:
        """Get truth record by claim_id."""
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM truth_records WHERE claim_id=?", (claim_id,)).fetchone()
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


class DecisionBlockRepository:
    """
    Repository for DecisionBlocks (S40-BE-006).

    DecisionBlocks are immutable records with full provenance.
    Once created, they cannot be modified or deleted.
    """

    def __init__(self, db_path: Path | None = None):
        resolved = db_path or Path(
            os.environ.get("INSPECTAH_DECISION_BLOCK_DB_PATH", "out/databases/decision_blocks.sqlite")
        )
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
        """Create decision_blocks table if not exists."""
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS decision_blocks (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    claim_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    gate TEXT NOT NULL,
                    initial_state TEXT NOT NULL,
                    final_state TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    policy_name TEXT,
                    policy_version TEXT,
                    committee_summary TEXT,
                    invariants_checked TEXT NOT NULL,
                    evidence_refs TEXT NOT NULL,
                    -- S40: New fields
                    references_json TEXT,      -- JSONB: guias[], pilares[], e40_5
                    state_transition TEXT,     -- JSONB: from/to/reason
                    experience_refs TEXT,      -- JSON array of experience IDs
                    created_at TEXT NOT NULL,
                    latency_ms INTEGER
                );
                CREATE INDEX IF NOT EXISTS idx_decision_blocks_claim ON decision_blocks(claim_id);
                CREATE INDEX IF NOT EXISTS idx_decision_blocks_domain ON decision_blocks(domain);
                CREATE INDEX IF NOT EXISTS idx_decision_blocks_decision ON decision_blocks(decision_id);
                CREATE INDEX IF NOT EXISTS idx_decision_blocks_created ON decision_blocks(created_at);
                """
            )
            conn.commit()

    def record(self, block) -> Any:
        """
        Record a DecisionBlock (S40-BE-006).

        This is an append-only operation. DecisionBlocks are immutable.

        Args:
            block: DecisionBlock to record

        Returns:
            The recorded DecisionBlock

        Raises:
            ValueError: If block already exists (immutability check)
        """
        # Check immutability - block should not already exist
        existing = self.get(block.id)
        if existing:
            raise ValueError(f"DecisionBlock {block.id} already exists - blocks are immutable")

        # Serialize references if present
        references_json = None
        if hasattr(block, "references") and block.references:
            references_json = json.dumps(block.references.to_dict(), ensure_ascii=False)

        # Serialize state_transition if present
        state_transition_json = None
        if hasattr(block, "state_transition") and block.state_transition:
            st = block.state_transition
            state_transition_json = json.dumps(
                {
                    "from_state": st.from_state,
                    "to_state": st.to_state,
                    "reason": st.reason,
                    "timestamp": st.timestamp.isoformat() if hasattr(st, "timestamp") and st.timestamp else None,
                },
                ensure_ascii=False,
            )

        # Serialize experience_refs if present
        experience_refs_json = "[]"
        if hasattr(block, "experience_ref") and block.experience_ref:
            experience_refs_json = json.dumps(block.experience_ref, ensure_ascii=False)

        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO decision_blocks (
                    id, decision_id, claim_id, domain, gate,
                    initial_state, final_state, decision_type,
                    policy_name, policy_version, committee_summary,
                    invariants_checked, evidence_refs,
                    references_json, state_transition, experience_refs,
                    created_at, latency_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block.id,
                    block.decision_id,
                    block.claim_id,
                    block.domain,
                    block.gate,
                    block.initial_state,
                    block.final_state,
                    block.decision_type,
                    block.policy_name,
                    block.policy_version,
                    json.dumps(block.committee_summary or {}, ensure_ascii=False),
                    json.dumps(block.invariants_checked, ensure_ascii=False),
                    json.dumps(block.evidence_refs, ensure_ascii=False),
                    references_json,
                    state_transition_json,
                    experience_refs_json,
                    _serialize_dt(block.created_at),
                    block.latency_ms,
                ),
            )
            conn.commit()

        logger.info(f"Recorded DecisionBlock {block.id} for claim {block.claim_id}")
        return block

    def get(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get a DecisionBlock by ID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM decision_blocks WHERE id=?", (block_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def get_by_claim(self, claim_id: str) -> List[Dict[str, Any]]:
        """Get all DecisionBlocks for a claim."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM decision_blocks WHERE claim_id=? ORDER BY datetime(created_at)",
                (claim_id,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_by_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get DecisionBlock by decision ID."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM decision_blocks WHERE decision_id=?", (decision_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def list_recent(self, limit: int = 50, domain: str | None = None) -> List[Dict[str, Any]]:
        """List recent DecisionBlocks."""
        if domain:
            query = "SELECT * FROM decision_blocks WHERE domain=? ORDER BY datetime(created_at) DESC LIMIT ?"
            params = (domain, limit)
        else:
            query = "SELECT * FROM decision_blocks ORDER BY datetime(created_at) DESC LIMIT ?"
            params = (limit,)

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def count(self, domain: str | None = None) -> int:
        """Count DecisionBlocks."""
        if domain:
            query = "SELECT COUNT(*) FROM decision_blocks WHERE domain=?"
            params = (domain,)
        else:
            query = "SELECT COUNT(*) FROM decision_blocks"
            params = ()

        with self._conn() as conn:
            result = conn.execute(query, params).fetchone()
        return result[0] if result else 0

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a row to a dictionary."""
        return {
            "id": row["id"],
            "decision_id": row["decision_id"],
            "claim_id": row["claim_id"],
            "domain": row["domain"],
            "gate": row["gate"],
            "initial_state": row["initial_state"],
            "final_state": row["final_state"],
            "decision_type": row["decision_type"],
            "policy_name": row["policy_name"],
            "policy_version": row["policy_version"],
            "committee_summary": json.loads(row["committee_summary"] or "{}"),
            "invariants_checked": json.loads(row["invariants_checked"] or "{}"),
            "evidence_refs": json.loads(row["evidence_refs"] or "[]"),
            "references": json.loads(row["references_json"]) if row["references_json"] else None,
            "state_transition": json.loads(row["state_transition"]) if row["state_transition"] else None,
            "experience_refs": json.loads(row["experience_refs"] or "[]"),
            "created_at": _deserialize_dt(row["created_at"]),
            "latency_ms": row["latency_ms"],
        }


# Singleton instances
_decision_block_repository: Optional[DecisionBlockRepository] = None


def get_decision_block_repository() -> DecisionBlockRepository:
    """Get the default DecisionBlockRepository."""
    global _decision_block_repository
    if _decision_block_repository is None:
        _decision_block_repository = DecisionBlockRepository()
    return _decision_block_repository


def record_decision_block(block) -> Any:
    """
    Record a DecisionBlock (S40-BE-006).

    Convenience function that uses the default repository.

    Args:
        block: DecisionBlock to record

    Returns:
        The recorded DecisionBlock
    """
    return get_decision_block_repository().record(block)
