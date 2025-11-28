from pathlib import Path
import tempfile

from app.layers.router import route_and_run
from app.truth.repository import TruthRepository
from app.truth.enums import TruthState
from app.truth.service import get_or_create_truth_record_for_claim


def test_standard_pipeline_promotes_non_sensitive():
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        trace = route_and_run(claim_id="gossip-1", domain="gossip", truth_repo=repo)
        assert trace.executions, "trace deve registrar execuções"
        record = repo.get_record_by_slug("gossip:gossip-1")
        assert record is not None
        assert record.current_state in {TruthState.ESTABLISHED_FACT, TruthState.PROVISIONAL, TruthState.UNDER_REVIEW}


def test_hardened_pipeline_holds_sensitive():
    with tempfile.TemporaryDirectory() as tmp:
        repo = TruthRepository(db_path=Path(tmp) / "truth.sqlite")
        get_or_create_truth_record_for_claim("pol-claim-1", domain="politics", repo=repo)
        trace = route_and_run(claim_id="pol-claim-1", domain="politics", case_id="politics_case_01", truth_repo=repo)
        assert trace.pipeline == "hardened"
        record = repo.get_record_by_slug("politics:pol-claim-1")
        assert record is not None
        assert record.current_state in {TruthState.PROVISIONAL, TruthState.UNDER_REVIEW}
