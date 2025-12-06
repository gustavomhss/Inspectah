import pytest

from app.flows.service import FlowService


def _service(tmp_path):
    return FlowService(db_path=tmp_path / "flows_rollout.sqlite")


def test_start_rollout_enforces_limits_and_catalog(tmp_path):
    service = _service(tmp_path)
    service._limits_cache = {"max_test_percentual": 5, "max_rollbacks_per_hour": 2, "max_canary_duration_minutes": 60}
    service._flags_cache = {
        "s34_flow_multidomain_enabled": True,
        "s35_flow_rollout_enabled": True,
        "s35_flow_catalog_enforced": True,
        "s35_flow_logic_contract_enabled": True,
    }
    flow = service.create_flow_from_template("news_v2", "Fluxo News v2", "flow_news_v2")

    with pytest.raises(ValueError):
        service.start_rollout(flow.id, mode="canary", test_percentual=10, criteria={"slo_id": "slo_news"}, actor="ops_user")

    service._limits_cache["max_test_percentual"] = 20
    rollout = service.start_rollout(
        flow.id, mode="canary", test_percentual=10, criteria={"slo_id": "slo_news"}, actor="ops_user"
    )
    assert rollout.rollout_mode == "canary"
    ops = service.list_operations(flow.id, limit=1)[0]
    assert ops.mode == "canary"
    assert ops.catalog_hash


def test_rollback_rollout_respects_limit_and_logs(tmp_path):
    service = _service(tmp_path)
    service._limits_cache = {"max_test_percentual": 20, "max_rollbacks_per_hour": 2, "max_canary_duration_minutes": 60}
    service._flags_cache = {
        "s34_flow_multidomain_enabled": True,
        "s35_flow_rollout_enabled": True,
        "s35_flow_catalog_enforced": True,
        "s35_flow_logic_contract_enabled": True,
    }
    flow = service.create_flow_from_template("contestacao_v0", "Contestacao v0", "flow_contestacao_v0")
    service.start_rollout(flow.id, mode="test", test_percentual=10, criteria={"slo_id": "slo_contest"}, actor="ops_admin")

    base_version = flow.flow_version_id
    service.create_version(flow.id, "contestacao_v0", "v0.1.1")
    service.rollback_rollout(flow.id, target_version_id=base_version, actor="ops_admin")
    service.create_version(flow.id, "contestacao_v0", "v0.1.2")
    service.rollback_rollout(flow.id, target_version_id=base_version, actor="ops_admin")

    with pytest.raises(ValueError):
        service.rollback_rollout(flow.id, target_version_id=base_version, actor="ops_admin")
