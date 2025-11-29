from pathlib import Path
import tempfile

from app.context.service import build_case_dossier, build_entity_dossier
from app.truth.enums import TruthState
from app.truth.service import get_or_create_truth_record_for_claim, apply_transition
from app.truth.repository import TruthRepository


def test_build_case_dossier_includes_truth_events_and_sources():
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        record = get_or_create_truth_record_for_claim("pol-claim-1", domain="politics", repo=repo)
        apply_transition(record, TruthState.UNDER_REVIEW, "registro inicial", "test", repo=repo)

        dossier = build_case_dossier("politics_case_01", truth_repo=repo)
        assert dossier.case_id == "politics_case_01"
        assert dossier.domain == "politics"
        assert dossier.claims, "deve ter claims carregadas do golden set"
        claim = dossier.claims[0]
        assert claim.sources, "claim deve carregar fontes do golden set"
        assert claim.events, "timeline de verdade deve ser anexada"


def test_build_entity_dossier_collects_claims():
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        record = get_or_create_truth_record_for_claim("sci-claim-1", domain="science", repo=repo)
        apply_transition(record, TruthState.UNDER_REVIEW, "registro inicial", "test", repo=repo)

        dossier = build_entity_dossier("ent_sci_001", truth_repo=repo)
        assert dossier.entity_id == "ent_sci_001"
        assert dossier.claims, "entidade deve ter claims do golden set"
        assert any(cl.domain == "science" for cl in dossier.claims)
