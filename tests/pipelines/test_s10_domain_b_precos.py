from inspectah.pipelines import s10_domain_b_precos as domain_b


def test_domain_b_demo_summary_is_full_pass():
    report = domain_b.run_demo_report()
    summary = report["summary"]
    assert summary["ratio_valid_actions_accepted"] == 1.0
    assert summary["ratio_invalid_actions_rejected"] == 1.0
    assert summary["audit_trace_completeness"] == 1.0
    assert summary["e2e_scenario_success_rate"] == 1.0
    assert report["results"]


def test_domain_b_truthdb_builder_contains_fact():
    truthdb = domain_b.build_domain_b_truthdb()
    snapshot = truthdb.snapshot()
    assert "preco_media_sp_julho" in snapshot["fatos"]
