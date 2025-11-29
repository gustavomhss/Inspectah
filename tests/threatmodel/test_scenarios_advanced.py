from app.demo.golden_sets_loader import load_golden_case
from app.context.service import build_case_dossier
from app.threatmodel.service import compute_snapshot_for_case, load_thresholds


def test_politics_case_triggers_risk_signals():
    thresholds = load_thresholds()
    dossier = build_case_dossier("politics_case_01")
    snapshot = compute_snapshot_for_case(dossier, thresholds)
    assert snapshot.signals, "caso político deve gerar sinais de risco"


def test_gossip_case_low_risk():
    thresholds = load_thresholds()
    dossier = build_case_dossier("gossip_case_01")
    snapshot = compute_snapshot_for_case(dossier, thresholds)
    # gossip tende a ser menos sensível, aceitar zero ou poucos sinais
    assert snapshot.metrics["flood_score"] <= 1
