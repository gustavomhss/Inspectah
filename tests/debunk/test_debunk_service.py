from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.debunk.routes import router as debunk_router, get_repo
from app.debunk.models import (
    DebunkDecisionType,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTaskStatus,
    DebunkTaskType,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository
from app.debunk import service


def _make_repo(tmp_path: Path) -> DebunkRepository:
    db_path = tmp_path / "debunk.sqlite"
    return DebunkRepository(db_path=db_path)


def test_open_issue_prevents_duplicates(tmp_path: Path):
    repo = _make_repo(tmp_path)
    issue = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.CLAIM,
        target_id="claim-1",
        question="A obra X foi entregue em 2022?",
        reason="Divergência entre fontes oficiais",
        risk_level=DebunkRiskLevel.HIGH,
        priority=10,
        origin="S23_AUTO",
        opened_by="system",
    )
    assert issue.id
    try:
        service.open_issue(
            repo,
            target_type=DebunkIssueTarget.CLAIM,
            target_id="claim-1",
            question="Pergunta duplicada",
            reason="Duplicada",
            risk_level=DebunkRiskLevel.MEDIUM,
            priority=5,
            origin="S23_AUTO",
            opened_by="system",
        )
    except service.DebunkDomainError:
        pass
    else:
        raise AssertionError("Duplicate issue was not blocked")


def test_queue_orders_by_risk_and_age(tmp_path: Path):
    repo = _make_repo(tmp_path)
    old = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.COMMITTEE_DECISION,
        target_id="dec-1",
        question="Decisão crítica?",
        reason="Alto impacto",
        risk_level=DebunkRiskLevel.CRITICAL,
        priority=5,
        origin="S23_AUTO",
        opened_by="system",
    )
    newer = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.CLAIM,
        target_id="claim-2",
        question="Questão de menor risco",
        reason="Checar divergência leve",
        risk_level=DebunkRiskLevel.LOW,
        priority=9,
        origin="S23_AUTO",
        opened_by="system",
    )
    queue = repo.queue_snapshot()
    assert queue[0][1].id == old.id
    assert queue[-1][1].id == newer.id


def test_tasks_drive_issue_to_ready_for_decision(tmp_path: Path):
    repo = _make_repo(tmp_path)
    issue = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.TRUTH_RECORD,
        target_id="truth-1",
        question="Deve ser rebaixado?",
        reason="Sinais de inconsistência",
        risk_level=DebunkRiskLevel.HIGH,
        priority=7,
        origin="human",
        opened_by="analyst",
    )
    task = service.add_task(
        repo,
        issue_id=issue.id,
        task_type=DebunkTaskType.FACT_CHECK,
        instructions="Validar números com fonte oficial",
        assigned_to="analyst",
        due_at=datetime.utcnow() + timedelta(days=1),
    )
    assert task.status == DebunkTaskStatus.PENDING
    updated_task = service.update_task_status(
        repo, task_id=task.id, new_status=DebunkTaskStatus.DONE, result="Confirmado por dados do portal", actor="analyst"
    )
    assert updated_task.status == DebunkTaskStatus.DONE
    refreshed_issue = repo.get_issue(issue.id)
    assert refreshed_issue.status in {DebunkIssueStatus.TRIAGED, DebunkIssueStatus.READY_FOR_DECISION}


def test_decision_requires_valid_state_and_updates_issue(tmp_path: Path):
    repo = _make_repo(tmp_path)
    issue = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.CLAIM,
        target_id="claim-300",
        question="É verdadeiro?",
        reason="Fonte A vs Fonte B",
        risk_level=DebunkRiskLevel.MEDIUM,
        priority=4,
        origin="human",
        opened_by="analyst",
    )
    service.add_task(
        repo,
        issue_id=issue.id,
        task_type=DebunkTaskType.SOURCE_COMPARE,
        instructions="Comparar fontes A e B",
        assigned_to="analyst",
    )
    service.update_task_status(
        repo, task_id=repo.list_tasks(issue.id)[0].id, new_status=DebunkTaskStatus.DONE, result="Fonte A mais atual", actor="analyst"
    )
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.READY_FOR_DECISION, actor="analyst")
    decision = service.record_decision(
        repo,
        issue_id=issue.id,
        decision_type=DebunkDecisionType.CLAIM_POUCO_SUPORTADO,
        rationale="Evidência insuficiente",
        recommended_truth_action=RecommendedTruthAction.MARCAR_EM_DISPUTA,
        created_by="lead",
        confidence=0.35,
        evidence_refs=["evidence://item1"],
    )
    assert decision.id
    refreshed = repo.get_issue(issue.id)
    assert refreshed.status == DebunkIssueStatus.RESOLVED


def test_api_router_exposes_core_flows(tmp_path: Path):
    repo = _make_repo(tmp_path)
    app = FastAPI()

    def override_repo():
        return repo

    app.dependency_overrides[get_repo] = override_repo
    app.include_router(debunk_router, prefix="/api")
    client = TestClient(app)

    create_resp = client.post(
        "/api/debunk/issues",
        json={
            "target_type": "CLAIM",
            "target_id": "claim-api",
            "question": "A afirmação está correta?",
            "reason": "Divergência dos comitês",
            "risk_level": "HIGH",
            "priority": 9,
            "origin": "S23_AUTO",
            "opened_by": "api-tester",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    issue_id = create_resp.json()["id"]

    task_resp = client.post(
        f"/api/debunk/issues/{issue_id}/tasks",
        json={"task_type": "FACT_CHECK", "instructions": "Revisar dados oficiais", "assigned_to": "api-analyst"},
    )
    assert task_resp.status_code == 201
    decision_resp = client.post(
        f"/api/debunk/issues/{issue_id}/decisions",
        json={
            "decision_type": "CLAIM_BEM_SUPORTADO",
            "rationale": "Fontes consistentes",
            "recommended_truth_action": "SUGERE_PROMOVER",
            "created_by": "api-analyst",
            "confidence": 0.9,
            "evidence_refs": ["evidence://item1"],
        },
    )
    assert decision_resp.status_code == 201, decision_resp.text
    overview = client.get(f"/api/debunk/issues/{issue_id}")
    assert overview.status_code == 200
    body = overview.json()
    assert body["decisions"], "decision should be recorded"
