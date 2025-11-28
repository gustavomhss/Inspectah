from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.agents.models import (
    AgentCommittee,
    AgentInstructionVersion,
    AgentKBRef,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentRun,
    AgentRunStatus,
    AgentStatus,
    CommitteePolicy,
    ModelUpgradePolicy,
)
from scripts.db.migrate import apply_sql

DEFAULT_DB_PATH = Path(os.environ.get("INSPECTAH_S23_DB_PATH", "out/databases/s23_agents.sqlite"))
MIGRATION_PATH = Path(__file__).resolve().parents[2] / "db/migrations/023_sprint23_agents.sql"


class AgentsRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self) -> None:
        apply_sql(MIGRATION_PATH, self.db_path)

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # Agents
    def create_agent(self, agent: AgentProfile) -> AgentProfile:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ai_agents (
                    id, name, description, instructions, role, layer, model_name, recommended_model_name,
                    temperature, max_tokens, top_p, status, kb_refs, created_at, updated_at, created_by, last_modified_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent.id,
                    agent.name,
                    agent.description,
                    agent.instructions,
                    agent.role.value,
                    agent.layer.value,
                    agent.model_name,
                    agent.recommended_model_name,
                    agent.temperature,
                    agent.max_tokens,
                    agent.top_p,
                    agent.status.value,
                    json.dumps([kb.__dict__ for kb in agent.kb_refs], ensure_ascii=False),
                    agent.created_at.isoformat(),
                    agent.updated_at.isoformat(),
                    agent.created_by,
                    agent.last_modified_by,
                ),
            )
            conn.commit()
        return agent

    def update_agent(self, agent: AgentProfile) -> AgentProfile:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE ai_agents SET
                    name=?, description=?, instructions=?, role=?, layer=?, model_name=?, recommended_model_name=?,
                    temperature=?, max_tokens=?, top_p=?, status=?, kb_refs=?, updated_at=?, last_modified_by=?
                WHERE id=?
                """,
                (
                    agent.name,
                    agent.description,
                    agent.instructions,
                    agent.role.value,
                    agent.layer.value,
                    agent.model_name,
                    agent.recommended_model_name,
                    agent.temperature,
                    agent.max_tokens,
                    agent.top_p,
                    agent.status.value,
                    json.dumps([kb.__dict__ for kb in agent.kb_refs], ensure_ascii=False),
                    agent.updated_at.isoformat(),
                    agent.last_modified_by,
                    agent.id,
                ),
            )
            conn.commit()
        return agent

    def list_agents(self, layer: Optional[AgentLayer] = None, role: Optional[AgentRole] = None, status: Optional[AgentStatus] = None) -> List[AgentProfile]:
        query = "SELECT * FROM ai_agents WHERE 1=1"
        params: list = []
        if layer:
            query += " AND layer=?"
            params.append(layer.value)
        if role:
            query += " AND role=?"
            params.append(role.value)
        if status:
            query += " AND status=?"
            params.append(status.value)
        query += " ORDER BY datetime(updated_at) DESC"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_agent(r) for r in rows]

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ai_agents WHERE id=?", (agent_id,)).fetchone()
        return self._row_to_agent(row) if row else None

    # Versions
    def create_instruction_version(self, version: AgentInstructionVersion) -> AgentInstructionVersion:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ai_agent_versions (
                    id, agent_id, version_number, instructions, model_name, temperature, max_tokens, top_p,
                    kb_snapshot, changelog, created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version.id,
                    version.agent_id,
                    version.version_number,
                    version.instructions,
                    version.model_name,
                    version.temperature,
                    version.max_tokens,
                    version.top_p,
                    json.dumps([kb.__dict__ for kb in version.kb_snapshot], ensure_ascii=False),
                    version.changelog,
                    version.created_at.isoformat(),
                    version.created_by,
                ),
            )
            conn.commit()
        return version

    def list_instruction_versions(self, agent_id: str) -> List[AgentInstructionVersion]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM ai_agent_versions WHERE agent_id=? ORDER BY version_number DESC", (agent_id,)
            ).fetchall()
        return [self._row_to_version(r) for r in rows]

    # Committees
    def create_committee(self, committee: AgentCommittee) -> AgentCommittee:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ai_committees (
                    id, name, description, layer, primary_agents, mediator_agent, policy, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    committee.id,
                    committee.name,
                    committee.description,
                    committee.layer.value,
                    json.dumps(committee.primary_agents, ensure_ascii=False),
                    committee.mediator_agent,
                    json.dumps(committee.policy.__dict__, ensure_ascii=False),
                    committee.status.value,
                    committee.created_at.isoformat(),
                    committee.updated_at.isoformat(),
                ),
            )
            conn.commit()
        return committee

    def update_committee(self, committee: AgentCommittee) -> AgentCommittee:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE ai_committees
                   SET name=?, description=?, layer=?, primary_agents=?, mediator_agent=?, policy=?, status=?, updated_at=?
                 WHERE id=?
                """,
                (
                    committee.name,
                    committee.description,
                    committee.layer.value,
                    json.dumps(committee.primary_agents, ensure_ascii=False),
                    committee.mediator_agent,
                    json.dumps(committee.policy.__dict__, ensure_ascii=False),
                    committee.status.value,
                    committee.updated_at.isoformat(),
                    committee.id,
                ),
            )
            conn.commit()
        return committee

    def list_committees(self, layer: Optional[AgentLayer] = None) -> List[AgentCommittee]:
        query = "SELECT * FROM ai_committees WHERE 1=1"
        params: list = []
        if layer:
            query += " AND layer=?"
            params.append(layer.value)
        query += " ORDER BY datetime(updated_at) DESC"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_committee(r) for r in rows]

    def get_committee(self, committee_id: str) -> Optional[AgentCommittee]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ai_committees WHERE id=?", (committee_id,)).fetchone()
        return self._row_to_committee(row) if row else None

    # Model policy
    def get_model_policy(self) -> ModelUpgradePolicy:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ai_model_policy WHERE id=1").fetchone()
            if not row:
                policy = ModelUpgradePolicy()
                conn.execute(
                    """
                    INSERT INTO ai_model_policy (id, global_default_model, auto_upgrade_enabled, adoption_delay_days,
                        allowed_models, last_upgrade_at, next_upgrade_at, updated_at)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        policy.global_default_model,
                        1 if policy.auto_upgrade_enabled else 0,
                        policy.adoption_delay_days,
                        json.dumps(policy.allowed_models, ensure_ascii=False),
                        policy.last_upgrade_at.isoformat() if policy.last_upgrade_at else None,
                        policy.next_upgrade_at.isoformat() if policy.next_upgrade_at else None,
                        policy.updated_at.isoformat(),
                    ),
                )
                conn.commit()
                return policy
        return self._row_to_policy(row) if row else ModelUpgradePolicy()

    def save_model_policy(self, policy: ModelUpgradePolicy) -> ModelUpgradePolicy:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ai_model_policy
                (id, global_default_model, auto_upgrade_enabled, adoption_delay_days, allowed_models, last_upgrade_at, next_upgrade_at, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    policy.global_default_model,
                    1 if policy.auto_upgrade_enabled else 0,
                    policy.adoption_delay_days,
                    json.dumps(policy.allowed_models, ensure_ascii=False),
                    policy.last_upgrade_at.isoformat() if policy.last_upgrade_at else None,
                    policy.next_upgrade_at.isoformat() if policy.next_upgrade_at else None,
                    policy.updated_at.isoformat(),
                ),
            )
            conn.commit()
        return policy

    # Runs
    def create_run(self, run: AgentRun) -> AgentRun:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ai_agent_runs (
                    id, committee_id, input_ref, payload_snapshot, result_bundle_ref, status, error, started_at, finished_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.committee_id,
                    run.input_ref,
                    json.dumps(run.payload_snapshot, ensure_ascii=False),
                    run.result_bundle_ref,
                    run.status.value,
                    run.error,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.created_at.isoformat(),
                ),
            )
            conn.commit()
        return run

    def update_run(self, run: AgentRun) -> AgentRun:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE ai_agent_runs
                   SET result_bundle_ref=?, status=?, error=?, finished_at=?
                 WHERE id=?
                """,
                (
                    run.result_bundle_ref,
                    run.status.value,
                    run.error,
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.id,
                ),
            )
            conn.commit()
        return run

    def get_run(self, run_id: str) -> Optional[AgentRun]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ai_agent_runs WHERE id=?", (run_id,)).fetchone()
        return self._row_to_run(row) if row else None

    def list_runs_by_committee(self, committee_id: str, limit: int = 20) -> List[AgentRun]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM ai_agent_runs WHERE committee_id=? ORDER BY datetime(started_at) DESC LIMIT ?",
                (committee_id, limit),
            ).fetchall()
        return [self._row_to_run(r) for r in rows]

    # helpers
    def _row_to_agent(self, row: sqlite3.Row) -> AgentProfile:
        kb_refs = []
        if row["kb_refs"]:
            try:
                kb_refs = [AgentKBRef(**data) for data in json.loads(row["kb_refs"])]
            except Exception:
                kb_refs = []
        return AgentProfile(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            instructions=row["instructions"] or "",
            role=AgentRole(row["role"]),
            layer=AgentLayer(row["layer"]),
            model_name=row["model_name"],
            recommended_model_name=row["recommended_model_name"],
            temperature=float(row["temperature"] or 0.0),
            max_tokens=int(row["max_tokens"] or 0),
            top_p=float(row["top_p"] or 1.0),
            status=AgentStatus(row["status"]),
            kb_refs=kb_refs,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            last_modified_by=row["last_modified_by"],
        )

    def _row_to_version(self, row: sqlite3.Row) -> AgentInstructionVersion:
        kb_snapshot = []
        if row["kb_snapshot"]:
            try:
                kb_snapshot = [AgentKBRef(**data) for data in json.loads(row["kb_snapshot"])]
            except Exception:
                kb_snapshot = []
        return AgentInstructionVersion(
            id=row["id"],
            agent_id=row["agent_id"],
            version_number=int(row["version_number"]),
            instructions=row["instructions"] or "",
            model_name=row["model_name"],
            temperature=float(row["temperature"] or 0.0),
            max_tokens=int(row["max_tokens"] or 0),
            top_p=float(row["top_p"] or 1.0),
            kb_snapshot=kb_snapshot,
            changelog=row["changelog"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            created_by=row["created_by"],
        )

    def _row_to_committee(self, row: sqlite3.Row) -> AgentCommittee:
        primary_agents = []
        policy_dict = {}
        try:
            primary_agents = json.loads(row["primary_agents"]) if row["primary_agents"] else []
            policy_dict = json.loads(row["policy"]) if row["policy"] else {}
        except Exception:
            primary_agents = []
            policy_dict = {}
        return AgentCommittee(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            layer=AgentLayer(row["layer"]),
            primary_agents=primary_agents,
            mediator_agent=row["mediator_agent"],
            policy=CommitteePolicy(**policy_dict) if policy_dict else CommitteePolicy(),
            status=AgentStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_policy(self, row: sqlite3.Row) -> ModelUpgradePolicy:
        allowed = []
        try:
            allowed = json.loads(row["allowed_models"]) if row["allowed_models"] else []
        except Exception:
            allowed = []
        return ModelUpgradePolicy(
            global_default_model=row["global_default_model"],
            auto_upgrade_enabled=bool(row["auto_upgrade_enabled"]),
            adoption_delay_days=int(row["adoption_delay_days"]),
            allowed_models=allowed,
            last_upgrade_at=datetime.fromisoformat(row["last_upgrade_at"]) if row["last_upgrade_at"] else None,
            next_upgrade_at=datetime.fromisoformat(row["next_upgrade_at"]) if row["next_upgrade_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_run(self, row: sqlite3.Row) -> AgentRun:
        payload: dict = {}
        try:
            payload = json.loads(row["payload_snapshot"]) if row["payload_snapshot"] else {}
        except Exception:
            payload = {}
        return AgentRun(
            id=row["id"],
            committee_id=row["committee_id"],
            input_ref=row["input_ref"],
            payload_snapshot=payload,
            result_bundle_ref=row["result_bundle_ref"],
            status=AgentRunStatus(row["status"]),
            error=row["error"],
            started_at=datetime.fromisoformat(row["started_at"]),
            finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
