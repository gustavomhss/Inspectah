from inspectah.pipelines import s10_domain_a_obras as domain_a


def test_domain_a_demo_summary_is_full_pass():
    report = domain_a.run_demo_report()
    summary = report["summary"]
    assert summary["ratio_valid_actions_accepted"] == 1.0
    assert summary["ratio_invalid_actions_rejected"] == 1.0
    assert summary["audit_trace_completeness"] == 1.0
    assert summary["e2e_scenario_success_rate"] == 1.0
    assert summary["scenarios_total"] == summary["scenarios_passed"] == 1
    assert report["results"]


def test_domain_a_truthdb_builder_contains_fact():
    truthdb = domain_a.build_domain_a_truthdb()
    snapshot = truthdb.snapshot()
    assert "obra_123_prazo" in snapshot["fatos"]
