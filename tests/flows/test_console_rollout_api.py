import sqlite3

from app.flows.service import FlowService


def _service(tmp_path):
    return FlowService(db_path=tmp_path / "flow_console.sqlite")


def test_catalog_entries_present(tmp_path):
    service = _service(tmp_path)
    entries = service.list_catalog()
    assert any(e.get("flow_id") == "flow_news_v2" for e in entries)
    assert any(e.get("flow_id") == "flow_contestacao_v0" for e in entries)


def test_rollout_status_and_ops(tmp_path):
    service = _service(tmp_path)
    service._limits_cache = {"max_test_percentual": 20, "max_rollbacks_per_hour": 2, "max_canary_duration_minutes": 60}
    service._flags_cache = {
        "s34_flow_multidomain_enabled": True,
        "s35_flow_rollout_enabled": True,
        "s35_flow_catalog_enforced": True,
        "s35_flow_logic_contract_enabled": True,
    }
    service._rbac_cache = {"start_rollout": ["ops_user"], "promote": ["ops_user"], "rollback": ["ops_user"]}
    flow = service.create_flow_from_template("news_v2", "Fluxo News v2", "flow_news_v2")
    service.start_rollout(flow.id, mode="canary", test_percentual=10, criteria={"slo_id": "slo_noticias"}, actor="ops_user")
    # força drift de catálogo para alertas
    conn = sqlite3.connect(service.db_path)
    try:
        conn.execute("UPDATE flow_flows SET catalog_hash='drifted' WHERE id=?", (flow.id,))
        conn.commit()
    finally:
        conn.close()
    status = service.rollout_status(flow.id)
    assert status["rollout_mode"] == "canary"
    assert "catalog_hash_drift" in status["alerts"]
    assert status["slo_status"][0]["slo_id"] == "slo_noticias"
    ops = service.list_operations(flow.id, limit=2)
    assert len(ops) >= 1
    assert ops[0].operacao in {"start_rollout", "promote", "rollback"}
