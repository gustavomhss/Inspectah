from __future__ import annotations

from pathlib import Path

import importlib
import sqlite3

from app.agents.flows.runtime_adapter import DEFAULT_FALLBACK_STEPS, get_agent_flow_for_domain, get_executable_flow_plan
from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowStepIn
from app.agents.flows.service import AgentFlowService
from app.agents.models import AgentRole


def _service(tmp_path: Path) -> AgentFlowService:
    return AgentFlowService(db_path=tmp_path / "runtime.sqlite")


def _seed_flow(service: AgentFlowService, domain_key: str) -> None:
    payload = AgentFlowConfigIn(
        domain_key=domain_key,
        name="Runtime flow",
        description="Test flow",
        change_reason="seed",
        created_by="tester",
        steps=[
            AgentFlowStepIn(position=1, agent_role=AgentRole.INTERPRETER, params={"strict_mode": True}),
            AgentFlowStepIn(position=2, agent_role=AgentRole.CLASSIFIER, params={"committee_id": "c-test"}),
            AgentFlowStepIn(position=3, agent_role=AgentRole.DECISION_MAKER, params={"threshold": 0.7}),
        ],
    )
    service.create_flow(payload)


def test_get_executable_flow(tmp_path: Path):
    service = _service(tmp_path)
    _seed_flow(service, "politics_news")

    plan = get_executable_flow_plan("politics_news", service=service)
    assert plan["used_fallback"] is False
    assert [step["agent_role"] for step in plan["steps"]] == [
        AgentRole.INTERPRETER.value,
        AgentRole.CLASSIFIER.value,
        AgentRole.DECISION_MAKER.value,
    ]


def test_fallback_when_missing(tmp_path: Path):
    service = _service(tmp_path)
    plan = get_executable_flow_plan("unknown_domain", service=service)
    assert plan["used_fallback"] is True
    assert [s["agent_role"] for s in plan["steps"]] == [s["agent_role"] for s in DEFAULT_FALLBACK_STEPS]


def test_invalid_flow_triggers_fallback(tmp_path: Path):
    service = _service(tmp_path)
    # insert malformed role directly to simulate corruption
    mig = importlib.import_module("migrations.versions.0004_s29_agent_flows")
    db_path = service.db_path
    mig.apply_migration(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    now = "2024-01-01T00:00:00Z"
    conn.execute(
        """
        INSERT INTO agent_flow_configs (id, domain_key, name, is_active, created_at, updated_at)
        VALUES ('flow_bad', 'bad_domain', 'Bad', 1, ?, ?)
        """,
        (now, now),
    )
    conn.execute(
        """
        INSERT INTO agent_flow_steps (id, flow_id, position, agent_role, params, required, can_fail_soft, created_at, updated_at)
        VALUES ('step_bad', 'flow_bad', 1, 'unknown_role', '{}', 1, 0, ?, ?)
        """,
        (now, now),
    )
    conn.commit()
    conn.close()

    flow, fallback = get_agent_flow_for_domain("bad_domain", service=service)
    assert flow is None
    assert fallback is True
    plan = get_executable_flow_plan("bad_domain", service=service)
    assert plan["used_fallback"] is True
