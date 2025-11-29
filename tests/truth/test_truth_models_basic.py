from pathlib import Path
import tempfile

from app.truth.enums import TruthState
from app.truth.models import DecisionRecord, TruthChangeEvent, TruthRecord, gen_decision_id, gen_event_id, gen_truth_record_id
from app.truth.repository import TruthRepository


def test_truth_models_persist_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "truth.sqlite"
        repo = TruthRepository(db_path=db_path)

        record = TruthRecord(
            id=gen_truth_record_id(),
            slug="politics:claim-001",
            claim_id="claim-001",
            domain="politics",
            current_state=TruthState.UNKNOWN,
        )
        repo.upsert_truth_record(record)

        decision = DecisionRecord(
            id=gen_decision_id(),
            truth_record_id=record.id,
            rationale="primeira decisão",
            decided_by="manual",
        )
        repo.insert_decision(decision)

        event = TruthChangeEvent(
            id=gen_event_id(),
            truth_record_id=record.id,
            previous_state=None,
            new_state=TruthState.UNDER_REVIEW,
            reason="registro inicial",
            source="pipeline",
            decision_id=decision.id,
        )
        repo.insert_event(event)

        fetched = repo.get_record(record.id)
        assert fetched is not None
        assert fetched.slug == record.slug
        assert fetched.current_state == TruthState.UNKNOWN

        events = repo.list_events(record.id)
        assert len(events) == 1
        assert events[0].new_state == TruthState.UNDER_REVIEW
