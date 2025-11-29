from __future__ import annotations

from app.observability import metrics_s9


def test_metrics_snapshot_records_counts():
    metrics_s9.reset_metrics()
    metrics_s9.record_user_query("C1_preco_medio", "C1", "ok", 0.5)
    metrics_s9.record_user_query("C1_preco_medio", "C1", "ok", 0.7)
    metrics_s9.record_admin_action("create", info_type="C1_preco_medio", scenario_id="C1")
    metrics_s9.record_error("user", "prepare_failed")

    snapshot = metrics_s9.get_metrics_snapshot()
    queries = snapshot["inspectah_s9_user_queries_total"]
    key = "info_type=C1_preco_medio,scenario_id=C1,outcome=ok"
    assert queries[key] == 2
    latency = snapshot["inspectah_s9_user_latency_seconds"]["info_type=C1_preco_medio,scenario_id=C1"]
    assert latency["count"] == 2.0
    admins = snapshot["inspectah_s9_admin_actions_total"]
    assert admins["action=create,info_type=C1_preco_medio,scenario_id=C1"] == 1
    errors = snapshot["inspectah_s9_errors_total"]
    assert errors["route=user,kind=prepare_failed"] == 1
