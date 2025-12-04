from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.claims.adapters_truthdb import AdaptedClaim, extract_fact_from_claim, SUPPORTED_CLAIM_TYPE
from app.truthdb import metrics
from app.truthdb.models import (
    DecisionBlock,
    EvidenceBlock,
    FactBlock,
    FINAL_STATUSES,
    TruthStateRecord,
    TruthStatus,
    ContestRecord,
)

DEFAULT_DB_PATH = Path("out/databases/s32_truth.sqlite")


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class PromotionService:
    """Implements claim -> blocks -> truth state for S32."""

    def __init__(self, db_path: Path | str | None = None, env: str = "test"):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.env = env

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def promote_claim(self, claim: Dict[str, Any]) -> TruthStateRecord:
        adapted = extract_fact_from_claim(claim)
        metrics.inc_promotion_attempt(adapted.claim_type, env=self.env)

        with metrics.LatencyTimer(flow_type="promotion", env=self.env):
            try:
                return self._promote(adapted)
            except Exception:
                metrics.inc_flow_error(stage="promotion", env=self.env, error_type="exception")
                raise

    def _promote(self, claim: AdaptedClaim) -> TruthStateRecord:
        fact_block = self._ensure_fact_block(claim)
        self._ensure_evidences(fact_block, claim.evidences)
        truth_state = self._upsert_truth_state(claim, fact_block)
        metrics.inc_promotion_success(claim.claim_type, env=self.env)
        return truth_state

    def _ensure_fact_block(self, claim: AdaptedClaim) -> FactBlock:
        with self._conn() as conn:
            row = conn.execute("SELECT id, claim_id, content_hash, metadata, created_at FROM fact_blocks WHERE claim_id=?", (claim.claim_id,)).fetchone()
            if row:
                return FactBlock(id=row[0], claim_id=row[1], content_hash=row[2], metadata={}, created_at=row[4])
            fact_id = _gen_id("fact")
            conn.execute(
                "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?,?,?,?,datetime('now'))",
                (fact_id, claim.claim_id, claim.content_hash, "{}",),
            )
            conn.commit()
            return FactBlock(id=fact_id, claim_id=claim.claim_id, content_hash=claim.content_hash)

    def _ensure_evidences(self, fact_block: FactBlock, evidences: List[Dict[str, Any]]) -> None:
        if not evidences:
            return
        with self._conn() as conn:
            existing = {row[0] for row in conn.execute("SELECT id FROM evidence_blocks WHERE fact_block_id=?", (fact_block.id,)).fetchall()}
            for ev in evidences:
                ev_id = ev.get("id") or _gen_id("ev")
                if ev_id in existing:
                    continue
                ev_type = ev.get("type", "generic")
                metadata = ev.get("metadata", "{}")
                conn.execute(
                    "INSERT INTO evidence_blocks (id, fact_block_id, evidence_type, metadata, created_at) VALUES (?,?,?,?,datetime('now'))",
                    (ev_id, fact_block.id, ev_type, str(metadata)),
                )
            conn.commit()

    def _upsert_truth_state(self, claim: AdaptedClaim, fact_block: FactBlock) -> TruthStateRecord:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT id, status, current_decision_block_id, created_at, updated_at FROM truth_states WHERE claim_id=?",
                (claim.claim_id,),
            ).fetchone()
            # v1 rule: if claim has field `decision` truthy -> TRUE else PENDING
            target_status = TruthStatus.TRUE if claim.claim_type == SUPPORTED_CLAIM_TYPE and claim.evidences else TruthStatus.PENDING

            decision_id: Optional[str] = None
            if target_status.value in FINAL_STATUSES:
                decision_id = self._create_decision(conn, fact_block.id, decision_type="promote_true")

            if row:
                ts_id = row[0]
                conn.execute(
                    "UPDATE truth_states SET status=?, current_decision_block_id=?, fact_block_id=?, updated_at=datetime('now') WHERE id=?",
                    (target_status.value, decision_id or row[2], fact_block.id, ts_id),
                )
                conn.commit()
                return TruthStateRecord(
                    id=ts_id,
                    claim_id=claim.claim_id,
                    fact_block_id=fact_block.id,
                    status=target_status,
                    current_decision_block_id=decision_id or row[2],
                )

            ts_id = _gen_id("ts")
            conn.execute(
                "INSERT INTO truth_states (id, claim_id, fact_block_id, status, current_decision_block_id, metadata, created_at, updated_at) VALUES (?,?,?,?,?, ?, datetime('now'), datetime('now'))",
                (ts_id, claim.claim_id, fact_block.id, target_status.value, decision_id, "{}",),
            )
            conn.commit()
            return TruthStateRecord(
                id=ts_id,
                claim_id=claim.claim_id,
                fact_block_id=fact_block.id,
                status=target_status,
                current_decision_block_id=decision_id,
            )

    def _create_decision(self, conn: sqlite3.Connection, fact_block_id: str, decision_type: str) -> str:
        dec_id = _gen_id("dec")
        conn.execute(
            "INSERT INTO decision_blocks (id, fact_block_id, decision_type, created_at) VALUES (?,?,?,datetime('now'))",
            (dec_id, fact_block_id, decision_type),
        )
        conn.commit()
        return dec_id


class PromotionError(Exception):
    """Raised for promotion-specific errors."""


class ContestationService:
    """Registers and processes contestations for TruthStates."""

    def __init__(self, db_path: Path | str | None = None, env: str = "test"):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.env = env

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def register_contestation(self, truth_state_id: str, payload: Dict[str, Any]) -> ContestRecord:
        with metrics.LatencyTimer(flow_type="contestation_register", env=self.env):
            with self._conn() as conn:
                ts = conn.execute("SELECT id, fact_block_id FROM truth_states WHERE id=?", (truth_state_id,)).fetchone()
                if not ts:
                    metrics.inc_flow_error(stage="contestation_register", env=self.env, error_type="missing_truth_state")
                    raise ValueError("TruthState not found")
                contest_id = _gen_id("contest")
                reason = payload.get("reason") if payload else None
                conn.execute(
                    "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?,?,?,?,datetime('now'))",
                    (contest_id, truth_state_id, reason, "PENDING"),
                )
                conn.commit()
                metrics.inc_contestation(SUPPORTED_CLAIM_TYPE, env=self.env, outcome="pending")
                return ContestRecord(id=contest_id, truth_state_id=truth_state_id, reason=reason)

    def process_contestation(self, contest_id: str) -> DecisionBlock:
        with metrics.LatencyTimer(flow_type="contestation_process", env=self.env):
            with self._conn() as conn:
                rec = conn.execute(
                    "SELECT id, truth_state_id, status FROM contest_records WHERE id=?", (contest_id,)
                ).fetchone()
                if not rec:
                    metrics.inc_flow_error(stage="contestation_process", env=self.env, error_type="missing_contest")
                    raise ValueError("ContestRecord not found")
                if rec[2] != "PENDING":
                    metrics.inc_flow_error(stage="contestation_process", env=self.env, error_type="already_processed")
                    raise ValueError("ContestRecord already processed")

                ts = conn.execute(
                    "SELECT id, fact_block_id, status FROM truth_states WHERE id=?", (rec[1],)
                ).fetchone()
                if not ts:
                    metrics.inc_flow_error(stage="contestation_process", env=self.env, error_type="missing_truth_state")
                    raise ValueError("TruthState missing for contest")

                dec_id = _gen_id("dec")
                conn.execute(
                    "INSERT INTO decision_blocks (id, fact_block_id, decision_type, created_at) VALUES (?,?,?,datetime('now'))",
                    (dec_id, ts[1], "update_after_contest"),
                )
                conn.execute(
                    "UPDATE truth_states SET status=?, current_decision_block_id=?, updated_at=datetime('now') WHERE id=?",
                    ("CONTESTED", dec_id, ts[0]),
                )
                conn.execute(
                    "UPDATE contest_records SET status=?, processed_decision_block_id=?, processed_at=? WHERE id=?",
                    ("PROCESSED", dec_id, "datetime('now')", rec[0]),
                )
                conn.commit()
                metrics.inc_contestation(SUPPORTED_CLAIM_TYPE, env=self.env, outcome="processed")
                return DecisionBlock(id=dec_id, fact_block_id=ts[1], decision_type="update_after_contest")
