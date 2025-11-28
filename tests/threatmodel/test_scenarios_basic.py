from pathlib import Path
import tempfile

from app.context.models import CaseContextDossier, DossierClaim
from app.threatmodel.service import compute_snapshot_for_case, load_thresholds


def _make_dossier(domain: str, claims):
    return CaseContextDossier(
        case_id="case_x",
        domain=domain,
        title="Case X",
        claims=claims,
        entities=[],
        debunk_issue_ids=[],
        truth_events=[event for claim in claims for event in claim.events],
        summary="",
    )


def test_snapshot_detects_flood_and_diversity():
    thresholds = {
        "default": {"max_flood": 2, "min_source_diversity": 0.5, "max_reversal_rate": 0.3}
    }
    claims = [
        DossierClaim(claim_id="c1", domain="general", sources=["s1"], events=[], description=""),
        DossierClaim(claim_id="c2", domain="general", sources=["s1"], events=[], description=""),
        DossierClaim(claim_id="c3", domain="general", sources=["s1"], events=[], description=""),
    ]
    dossier = _make_dossier("general", claims)
    snapshot = compute_snapshot_for_case(dossier, thresholds)
    assert snapshot.signals, "deve sinalizar flood ou baixa diversidade"
    kinds = [sig.kind for sig in snapshot.signals]
    assert "flood" in kinds or "single_source_dependency" in kinds
