from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.agents.models import AgentRole
from app.agents.flows.models import AgentFlowConfig, AgentFlowStep
from app.agents.flows.schemas import AgentFlowConfigIn
from app.agents.flows.validator import AgentFlowValidationError, validate_agent_flow

MIGRATION_MODULE = "migrations.versions.0004_s29_agent_flows"
DEFAULT_DB_PATH = Path(os.environ.get("INSPECTAH_S29_AGENT_FLOWS_DB_PATH", "out/databases/s29_agent_flows.sqlite"))


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _serialize(payload) -> str:
    return json.dumps(payload or {}, ensure_ascii=False)


def _deserialize(payload: Optional[str]):
    if payload is None:
        return {}
    try:
        return json.loads(payload)
    except Exception:
        return {}


class AgentFlowService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            self._ensure_schema(conn)
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        import importlib

        migration = importlib.import_module(MIGRATION_MODULE)
        migration.apply_migration(self.db_path)

    def create_flow(self, payload: AgentFlowConfigIn) -> AgentFlowConfig:
        errors = validate_agent_flow(payload)
        if errors:
            raise AgentFlowValidationError(errors)
        flow_id = _generate_id("afc")
        now = datetime.utcnow().isoformat()
        flow_dict = payload.model_dump()
        steps_payload = flow_dict.pop("steps", [])
        try:
            with self._conn() as conn:
                conn.execute(
                    """
                    INSERT INTO agent_flow_configs (
                        id, domain_key, name, description, is_active, change_reason,
                        created_at, updated_at, created_by, updated_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        flow_id,
                        flow_dict.get("domain_key"),
                        flow_dict.get("name"),
                        flow_dict.get("description"),
                        1 if flow_dict.get("is_active", True) else 0,
                        flow_dict.get("change_reason"),
                        now,
                        now,
                        flow_dict.get("created_by"),
                        flow_dict.get("updated_by") or flow_dict.get("created_by"),
                    ),
                )
                self._insert_steps(conn, flow_id, steps_payload, now)
                conn.commit()
        except sqlite3.IntegrityError as exc:  # pragma: no cover - exercised in API tests
            raise ValueError(f"Could not create agent flow: {exc}") from exc
        return self.get_flow(flow_id)  # type: ignore[return-value]

    def update_flow(self, flow_id: str, payload: AgentFlowConfigIn) -> AgentFlowConfig:
        errors = validate_agent_flow(payload)
        if errors:
            raise AgentFlowValidationError(errors)
        now = datetime.utcnow().isoformat()
        flow_dict = payload.model_dump()
        steps_payload = flow_dict.pop("steps", [])
        try:
            with self._conn() as conn:
                existing = conn.execute("SELECT * FROM agent_flow_configs WHERE id=?", (flow_id,)).fetchone()
                if not existing:
                    raise ValueError("Flow not found")
                conn.execute(
                    """
                    UPDATE agent_flow_configs
                       SET domain_key=?, name=?, description=?, is_active=?, change_reason=?,
                           updated_at=?, updated_by=?
                     WHERE id=?
                    """,
                    (
                        flow_dict.get("domain_key"),
                        flow_dict.get("name"),
                        flow_dict.get("description"),
                        1 if flow_dict.get("is_active", True) else 0,
                        flow_dict.get("change_reason"),
                        now,
                        flow_dict.get("updated_by") or flow_dict.get("created_by"),
                        flow_id,
                    ),
                )
                conn.execute("DELETE FROM agent_flow_steps WHERE flow_id=?", (flow_id,))
                self._insert_steps(conn, flow_id, steps_payload, now)
                conn.commit()
        except sqlite3.IntegrityError as exc:  # pragma: no cover - exercised in API tests
            raise ValueError(f"Could not update agent flow: {exc}") from exc
        return self.get_flow(flow_id)  # type: ignore[return-value]

    def get_flow(self, flow_id: str) -> Optional[AgentFlowConfig]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM agent_flow_configs WHERE id=?", (flow_id,)).fetchone()
            if not row:
                return None
            steps = conn.execute(
                "SELECT * FROM agent_flow_steps WHERE flow_id=? ORDER BY position ASC", (flow_id,)
            ).fetchall()
        return self._row_to_flow(row, steps)

    def get_flow_by_domain(self, domain_key: str) -> Optional[AgentFlowConfig]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM agent_flow_configs WHERE domain_key=?", (domain_key,)).fetchone()
            if not row:
                return None
            steps = conn.execute(
                "SELECT * FROM agent_flow_steps WHERE flow_id=? ORDER BY position ASC", (row["id"],)
            ).fetchall()
        return self._row_to_flow(row, steps)

    def list_flows(self) -> List[AgentFlowConfig]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM agent_flow_configs ORDER BY datetime(updated_at) DESC").fetchall()
            steps_by_flow = self._steps_by_flow(conn)
        return [self._row_to_flow(row, steps_by_flow.get(row["id"], [])) for row in rows]

    def delete_flow(self, flow_id: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM agent_flow_configs WHERE id=?", (flow_id,))
            conn.commit()

    def _insert_steps(self, conn: sqlite3.Connection, flow_id: str, steps: List[Dict], now: str) -> None:
        for step in steps:
            step_id = step.get("id") or _generate_id("afs")
            role = step.get("agent_role")
            if isinstance(role, AgentRole):
                role = role.value
            conn.execute(
                """
                INSERT INTO agent_flow_steps (
                    id, flow_id, position, agent_role, params, required, can_fail_soft, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    step_id,
                    flow_id,
                    step.get("position"),
                    role,
                    _serialize(step.get("params")),
                    1 if step.get("required", True) else 0,
                    1 if step.get("can_fail_soft", False) else 0,
                    now,
                    now,
                ),
            )

    def _steps_by_flow(self, conn: sqlite3.Connection):
        result: Dict[str, List[sqlite3.Row]] = {}
        rows = conn.execute("SELECT * FROM agent_flow_steps ORDER BY position ASC").fetchall()
        for row in rows:
            result.setdefault(row["flow_id"], []).append(row)
        return result

    def _row_to_flow(self, row: sqlite3.Row, steps_rows: List[sqlite3.Row]) -> AgentFlowConfig:
        steps = [
            AgentFlowStep(
                id=step_row["id"],
                flow_id=step_row["flow_id"],
                position=step_row["position"],
                agent_role=step_row["agent_role"],
                params=_deserialize(step_row["params"]),
                required=bool(step_row["required"]),
                can_fail_soft=bool(step_row["can_fail_soft"]),
                created_at=datetime.fromisoformat(step_row["created_at"]),
                updated_at=datetime.fromisoformat(step_row["updated_at"]),
            )
            for step_row in steps_rows
        ]
        return AgentFlowConfig(
            id=row["id"],
            domain_key=row["domain_key"],
            name=row["name"],
            description=row["description"],
            is_active=bool(row["is_active"]),
            change_reason=row["change_reason"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            updated_by=row["updated_by"],
            steps=steps,
        )
