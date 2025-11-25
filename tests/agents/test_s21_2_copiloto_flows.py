import uuid

from inspectah.agents.s21_1_copiloto_fontes import run_copiloto_interaction
from app.sources import service
from app.sources.schemas import SourceCreate


def _sample_payload(slug: str) -> SourceCreate:
    return SourceCreate(
        slug=f"{slug}-{uuid.uuid4().hex[:6]}",
        name="Fonte Teste",
        description="",
        type="news_rss",
        category="official",
        themes=["politica"],
        info_types=["news"],
        protocol="https",
        format="rss",
        endpoint="https://example.com/rss",
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="daily",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        meta={},
        created_by="tester",
        refresh_interval=180,
    )


def test_creation_flow_suggests_type_and_refresh():
    result = run_copiloto_interaction(
        "sess-create",
        "quero cadastrar fonte de notícias em https://portal.com/rss",
        {},
        [],
    )
    actions = result["actions"]
    assert any(a.get("field") == "type" for a in actions)
    assert any(a.get("field") == "refresh_interval" for a in actions)


def test_edit_flow_proposes_diff():
    src = service.create_source(_sample_payload("edit-src"))
    result = run_copiloto_interaction(
        "sess-edit",
        "atualize endpoint para https://novo.com/rss e refresh 120",
        {"source_id": src.id, "type": src.type},
        [],
    )
    actions = result["actions"]
    assert any(a.get("type") == "propose_update" for a in actions)
    change_fields = [c["field"] for a in actions if a.get("type") == "propose_update" for c in a.get("changes", [])]
    assert "endpoint" in change_fields
    assert "refresh_interval" in change_fields


def test_status_flow_builds_plan():
    src = service.create_source(_sample_payload("status-src"))
    result = run_copiloto_interaction(
        "sess-status",
        "preciso aprovar esta fonte",
        {"source_id": src.id, "state": src.state.value},
        [],
    )
    actions = result["actions"]
    assert any(a.get("type") == "plan_status_change" for a in actions)
    plan = next(a["plan"] for a in actions if a.get("type") == "plan_status_change")
    assert plan["to_state"] == "ACTIVE"


def test_official_open_flow_marks_type():
    result = run_copiloto_interaction(
        "sess-official",
        "fonte oficial aberta do IBGE",
        {},
        [],
    )
    actions = result["actions"]
    assert any(a.get("field") == "type" and a.get("value") == "official_open" for a in actions)


def test_data_api_flow_infers_type_and_suggestions():
    result = run_copiloto_interaction(
        "sess-data",
        "Quero cadastrar a API de dados do IBGE: https://servicodados.ibge.gov.br/api/v3/agregados",
        {},
        [],
    )
    actions = result["actions"]
    assert any(a.get("field") == "type" and a.get("value") == "data_api" for a in actions)
    assert any(a.get("field") in {"themes", "info_types"} for a in actions)
    assert "api" in result["assistant_message"].lower()


def test_conceptual_help_on_endpoint():
    result = run_copiloto_interaction(
        "sess-concept",
        "Não sei o que é endpoint, como eu descubro isso neste site?",
        {},
        [],
    )
    assert result["assistant_message"]
    assert "endpoint" in result["assistant_message"].lower()
    assert all(a.get("type") != "propose_update" for a in result["actions"])
