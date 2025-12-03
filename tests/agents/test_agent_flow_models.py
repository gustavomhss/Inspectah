from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import importlib
import pytest

from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowStepIn
from app.agents.flows.service import AgentFlowService
from app.agents.flows.validator import AgentFlowValidationError
from app.agents.models import AgentRole


def _service(tmp_path: Path) -> AgentFlowService:
    return AgentFlowService(db_path=tmp_path / "s29_flows.sqlite")


def _sample_flow() -> AgentFlowConfigIn:
    steps = [
        AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER, params={"strict_mode": True}),
        AgentFlowStepIn(position=2, agent_role=AgentRole.CLASSIFIER, params={"committee_id": "c-main"}),
        AgentFlowStepIn(position=3, agent_role=AgentRole.DECISION_MAKER, params={"threshold": 0.7}),
    ]
    return AgentFlowConfigIn(
        domain_key="politics_news",
        name="Politics — default",
        description="Fluxo base para notícias de política",
        is_active=True,
        change_reason="seed flow for tests",
        created_by="tester",
        updated_by="tester",
        steps=steps,
    )


def test_create_flow_with_steps(tmp_path: Path):
    service = _service(tmp_path)
    flow = _sample_flow()
    created = service.create_flow(flow)
    assert created.id
    assert created.domain_key == "politics_news"
    assert len(created.steps) == 3
    assert [s.position for s in created.steps] == [1, 2, 3]
    assert created.steps[-1].agent_role == AgentRole.DECISION_MAKER.value


def test_position_uniqueness_enforced(tmp_path: Path):
    service = _service(tmp_path)
    flow = _sample_flow()
    # duplicar a posição 2 apenas para violar unicidade, sem misturar outros erros
    flow.steps.append(
        AgentFlowStepIn(
            position=2,
            agent_role=AgentRole.ANALYST,
            params={},
        )
    )
    with pytest.raises(AgentFlowValidationError) as exc:
        service.create_flow(flow)
    msg = str(exc.value).lower()
    assert "duplicate" in msg and "position" in msg


def test_foreign_keys_and_cascade(tmp_path: Path):
    db_path = tmp_path / "cascade.sqlite"
    mig = importlib.import_module("migrations.versions.0004_s29_agent_flows")
    mig.apply_migration(db_path)
    # manually insert config to verify FK behavior
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    now = datetime.utcnow().isoformat()
    flow_id = "afc_fk"
    conn.execute(
        """
        INSERT INTO agent_flow_configs (
            id, domain_key, name, description, is_active, change_reason, created_at, updated_at, created_by, updated_by
        ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
        """,
        (flow_id, "economy_news", "Flow FK", "", "fk test", now, now, "tester", "tester"),
    )
    conn.execute(
        """
        INSERT INTO agent_flow_steps (
            id, flow_id, position, agent_role, params, required, can_fail_soft, created_at, updated_at
        ) VALUES (?, ?, 1, ?, '{}', 1, 0, ?, ?)
        """,
        ("afs_fk", flow_id, AgentRole.INTERPRETER.value, now, now),
    )
    conn.commit()
    conn.execute("DELETE FROM agent_flow_configs WHERE id=?", (flow_id,))
    conn.commit()
    remaining = conn.execute("SELECT COUNT(*) FROM agent_flow_steps WHERE flow_id=?", (flow_id,)).fetchone()[0]
    conn.close()
    assert remaining == 0
