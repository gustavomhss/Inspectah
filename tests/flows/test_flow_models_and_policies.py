import pytest

from app.flows import policy_engine
from app.flows.models import FlowState
from app.flows.policy_engine import PolicyViolation
from app.flows.service import FlowService


def _service(tmp_path):
    return FlowService(db_path=tmp_path / "flows.sqlite")


def test_create_flow_from_template_sets_version_and_domain(tmp_path):
    service = _service(tmp_path)
    flow = service.create_flow_from_template("news_v2", "Fluxo News v2", "flow_news_v2")

    assert flow.flow_version_id == "2"
    assert flow.domain == "noticias"
    assert flow.active_version_id is not None


def test_set_flow_state_enforces_percent_limit(tmp_path):
    service = _service(tmp_path)
    flow = service.create_flow_from_template("contestacao_v0", "Contestacao Piloto", "flow_contestacao")

    with pytest.raises(ValueError):
        service.set_flow_state(flow.id, FlowState.EM_TESTE, percentual_teste=50)

    updated = service.set_flow_state(flow.id, FlowState.EM_TESTE, percentual_teste=10)
    assert updated.estado == FlowState.EM_TESTE
    assert updated.percentual_teste == 10


def test_policy_engine_requires_policies_for_unknown_domain():
    with pytest.raises(PolicyViolation):
        policy_engine.validate_transition("dominio_sem_politica", "em_teste")
