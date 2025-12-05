import pathlib


def test_alert_files_exist():
    base = pathlib.Path("observability/alerts/s34")
    alerts = list(base.glob("*.yaml"))
    assert {"policy_violations.yaml", "rollbacks.yaml", "slo_breach.yaml"}.issubset({p.name for p in alerts})


def test_dashboard_not_empty():
    path = pathlib.Path("observability/dashboards/s34_flow_ops_overview.json")
    assert path.exists()
    assert path.read_text().strip() != ""
