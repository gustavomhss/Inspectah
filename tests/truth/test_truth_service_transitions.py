from pathlib import Path
import tempfile

import pytest

from app.truth.enums import TruthState
from app.truth.service import InvalidTruthTransition, apply_transition, get_or_create_truth_record_for_claim, get_timeline
from app.truth.repository import TruthRepository


def _make_repo(tmp_path: Path) -> TruthRepository:
    return TruthRepository(db_path=tmp_path / "truth.sqlite")


def test_apply_transition_updates_state_and_events():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(Path(tmp))
        record = get_or_create_truth_record_for_claim("claim-xyz", domain="science", repo=repo)

        event = apply_transition(
            truth_record=record,
            new_state=TruthState.UNDER_REVIEW,
            reason="triagem inicial",
            source="pipeline",
            repo=repo,
        )

        updated = repo.get_record(record.id)
        assert updated is not None
        assert updated.current_state == TruthState.UNDER_REVIEW
        assert event.new_state == TruthState.UNDER_REVIEW

        timeline = get_timeline(record.id, repo=repo)
        assert len(timeline) == 1
        assert timeline[0].reason == "triagem inicial"


def test_invalid_transition_same_state():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(Path(tmp))
        record = get_or_create_truth_record_for_claim("claim-xyz", domain="science", repo=repo)
        apply_transition(truth_record=record, new_state=TruthState.UNDER_REVIEW, reason="go", source="pipeline", repo=repo)

        updated = repo.get_record(record.id)
        assert updated is not None

        with pytest.raises(InvalidTruthTransition):
            apply_transition(
                truth_record=updated,
                new_state=TruthState.UNDER_REVIEW,
                reason="redundante",
                source="pipeline",
                repo=repo,
            )
