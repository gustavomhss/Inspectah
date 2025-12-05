import sqlite3

import pytest

from app.flows.models import FlowExecutionStatus
from app.flows.service import FlowService


def _service(tmp_path):
    return FlowService(db_path=tmp_path / "flows_limits.sqlite")


def test_rollback_respects_hourly_limit(tmp_path):
    service = _service(tmp_path)
    flow = service.create_flow_from_template("news_v2", "Fluxo News v2", "flow_news_v2")
    # cria uma nova versão e aplica rollback até estourar limite
    service.create_version(flow.id, "news_v2", "3")
    service.rollback_flow(flow.id, "2")
    service.create_version(flow.id, "news_v2", "4")
    service.rollback_flow(flow.id, "2")

    with pytest.raises(ValueError):
        service.rollback_flow(flow.id, "2")


def test_record_execution_requires_version(tmp_path):
    service = _service(tmp_path)
    flow = service.create_flow_from_template("contestacao_v0", "Contestacao Piloto", "flow_contestacao")
    # zera flow_version_id para validar invariante
    conn = sqlite3.connect(service.db_path)
    try:
        conn.execute("UPDATE flow_flows SET flow_version_id=NULL WHERE id=?", (flow.id,))
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError):
        service.record_execution(flow.id, "item-1", flow.tipo_entrada, FlowExecutionStatus.EM_ANDAMENTO)
