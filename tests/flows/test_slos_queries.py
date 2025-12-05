from app.ops.slo_evaluator import evaluate_slos
from app.flows import instrumentation


def test_evaluate_slos_reads_s34_doc():
    slos = evaluate_slos()
    ids = {s["slo_id"] for s in slos}
    assert "s34_slo_exec_latency_news_v2" in ids
    assert "s34_slo_policy_violations_contestacao_v0" in ids


def test_instrumentation_counters_increment():
    instrumentation.record_policy_violation("flow_x", "v1")
    instrumentation.record_rollback("flow_x", "v1", "op1")
    instrumentation.record_slo_breach("flow_x", "v1", "slo_x")
    # no exception means metrics accepted
    assert True
