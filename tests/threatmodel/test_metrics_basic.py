from app.threatmodel.computations import compute_flood_score, compute_reversal_rate, compute_source_diversity, evaluate_signals


def test_compute_metrics_basic():
    assert compute_flood_score(3, 3) == 1
    assert compute_source_diversity(2, 4) == 0.5
    events = [{"new_state": "A"}, {"new_state": "B"}, {"new_state": "B"}]
    assert compute_reversal_rate(events) == 1 / 3


def test_evaluate_signals_detects_single_source():
    metrics = {"flood_score": 0.5, "source_diversity": 0.2, "reversal_rate": 0.1}
    thresholds = {"min_source_diversity": 0.4, "max_reversal_rate": 0.3}
    signals = evaluate_signals(metrics, thresholds, "politics")
    assert any(sig["kind"] == "single_source_dependency" for sig in signals)
