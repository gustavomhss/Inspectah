"""
Tests for Truth Repository — S37

Tests for truth database repository.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from app.truth.repository import TruthRepository, _serialize_dt, _deserialize_dt
from app.truth.models import TruthRecord, DecisionRecord, TruthChangeEvent, utcnow
from app.truth.enums import TruthState, TruthEventType


class TestSerializeDt:
    """Tests for _serialize_dt function."""

    def test_serialize_datetime(self):
        """Serialize datetime to ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

        result = _serialize_dt(dt)

        assert "2024-01-15" in result
        assert "10:30:00" in result


class TestDeserializeDt:
    """Tests for _deserialize_dt function."""

    def test_deserialize_datetime(self):
        """Deserialize ISO format to datetime."""
        raw = "2024-01-15T10:30:00+00:00"

        result = _deserialize_dt(raw)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15


class TestTruthRepository:
    """Tests for TruthRepository class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_truth.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return TruthRepository(db_path=temp_db)

    def test_init_creates_schema(self, temp_db):
        """Init creates database schema."""
        repo = TruthRepository(db_path=temp_db)

        assert temp_db.exists()

    def test_init_default_path(self):
        """Init with default path."""
        with TemporaryDirectory() as tmpdir:
            import os
            os.environ["INSPECTAH_S25_TRUTH_DB_PATH"] = str(Path(tmpdir) / "test.sqlite")
            try:
                repo = TruthRepository()
                assert repo.db_path is not None
            finally:
                del os.environ["INSPECTAH_S25_TRUTH_DB_PATH"]

    def test_upsert_truth_record(self, repo):
        """Upsert truth record."""
        now = utcnow()
        record = TruthRecord(
            id="tr_1",
            slug="test-record",
            claim_id="claim_1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={"key": "value"},
            created_at=now,
            updated_at=now,
        )

        result = repo.upsert_truth_record(record)

        assert result.id == "tr_1"
        assert result.slug == "test-record"

    def test_upsert_updates_existing(self, repo):
        """Upsert updates existing record."""
        now = utcnow()
        record = TruthRecord(
            id="tr_1",
            slug="test-record",
            claim_id="claim_1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        )
        repo.upsert_truth_record(record)

        # Update state
        record.current_state = TruthState.ESTABLISHED_FACT
        record.last_decision_id = "dec_1"
        repo.upsert_truth_record(record)

        fetched = repo.get_record_by_slug("test-record")
        assert fetched.current_state == TruthState.ESTABLISHED_FACT
        assert fetched.last_decision_id == "dec_1"

    def test_get_record_by_slug(self, repo):
        """Get record by slug."""
        now = utcnow()
        record = TruthRecord(
            id="tr_1",
            slug="unique-slug",
            claim_id="claim_1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        )
        repo.upsert_truth_record(record)

        result = repo.get_record_by_slug("unique-slug")

        assert result is not None
        assert result.id == "tr_1"

    def test_get_record_by_slug_not_found(self, repo):
        """Get record by slug returns None when not found."""
        result = repo.get_record_by_slug("nonexistent")

        assert result is None

    def test_get_record_by_id(self, repo):
        """Get record by ID."""
        now = utcnow()
        record = TruthRecord(
            id="tr_123",
            slug="test-slug",
            claim_id="claim_1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        )
        repo.upsert_truth_record(record)

        result = repo.get_record("tr_123")

        assert result is not None
        assert result.slug == "test-slug"

    def test_get_record_not_found(self, repo):
        """Get record returns None when not found."""
        result = repo.get_record("nonexistent")

        assert result is None

    def test_list_records_all(self, repo):
        """List all records."""
        now = utcnow()
        for i in range(3):
            record = TruthRecord(
                id=f"tr_{i}",
                slug=f"slug-{i}",
                claim_id=f"claim_{i}",
                domain="politics",
                current_state=TruthState.CLAIMED,
                last_decision_id=None,
                metadata={},
                created_at=now,
                updated_at=now,
            )
            repo.upsert_truth_record(record)

        result = repo.list_records()

        assert len(result) == 3

    def test_list_records_by_domain(self, repo):
        """List records filtered by domain."""
        now = utcnow()
        repo.upsert_truth_record(TruthRecord(
            id="tr_1",
            slug="politics-1",
            claim_id="c1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        ))
        repo.upsert_truth_record(TruthRecord(
            id="tr_2",
            slug="health-1",
            claim_id="c2",
            domain="health",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        ))

        result = repo.list_records(domain="politics")

        assert len(result) == 1
        assert result[0].domain == "politics"

    def test_list_records_by_state(self, repo):
        """List records filtered by state."""
        now = utcnow()
        repo.upsert_truth_record(TruthRecord(
            id="tr_1",
            slug="pending-1",
            claim_id="c1",
            domain="politics",
            current_state=TruthState.CLAIMED,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        ))
        repo.upsert_truth_record(TruthRecord(
            id="tr_2",
            slug="verified-1",
            claim_id="c2",
            domain="politics",
            current_state=TruthState.ESTABLISHED_FACT,
            last_decision_id=None,
            metadata={},
            created_at=now,
            updated_at=now,
        ))

        result = repo.list_records(state=TruthState.ESTABLISHED_FACT)

        assert len(result) == 1
        assert result[0].current_state == TruthState.ESTABLISHED_FACT

    def test_list_records_with_limit(self, repo):
        """List records respects limit."""
        now = utcnow()
        for i in range(10):
            repo.upsert_truth_record(TruthRecord(
                id=f"tr_{i}",
                slug=f"slug-{i}",
                claim_id=f"c{i}",
                domain="politics",
                current_state=TruthState.CLAIMED,
                last_decision_id=None,
                metadata={},
                created_at=now,
                updated_at=now,
            ))

        result = repo.list_records(limit=5)

        assert len(result) == 5

    def test_insert_decision(self, repo):
        """Insert decision record."""
        now = utcnow()
        decision = DecisionRecord(
            id="dec_1",
            truth_record_id="tr_1",
            rationale="Evidence supports claim",
            decided_by="human_reviewer",
            policy_version="1.0.0",
            threat_snapshot="low_risk",
            metadata={"confidence": 0.9},
            created_at=now,
        )

        result = repo.insert_decision(decision)

        assert result.id == "dec_1"

    def test_list_decisions(self, repo):
        """List decisions for truth record."""
        now = utcnow()
        for i in range(3):
            decision = DecisionRecord(
                id=f"dec_{i}",
                truth_record_id="tr_1",
                rationale=f"Reason {i}",
                decided_by="reviewer",
                policy_version="1.0.0",
                threat_snapshot=None,
                metadata={},
                created_at=now,
            )
            repo.insert_decision(decision)

        result = list(repo.list_decisions("tr_1"))

        assert len(result) == 3

    def test_insert_event(self, repo):
        """Insert change event."""
        now = utcnow()
        event = TruthChangeEvent(
            id="evt_1",
            truth_record_id="tr_1",
            previous_state=TruthState.CLAIMED,
            new_state=TruthState.ESTABLISHED_FACT,
            event_type=TruthEventType.PROMOTION,
            reason="Evidence verified",
            source="human_review",
            decision_id="dec_1",
            metadata={},
            created_at=now,
        )

        result = repo.insert_event(event)

        assert result.id == "evt_1"

    def test_insert_event_no_previous_state(self, repo):
        """Insert event without previous state."""
        now = utcnow()
        event = TruthChangeEvent(
            id="evt_1",
            truth_record_id="tr_1",
            previous_state=None,
            new_state=TruthState.CLAIMED,
            event_type=None,
            reason="Initial state",
            source="system",
            decision_id=None,
            metadata={},
            created_at=now,
        )

        result = repo.insert_event(event)

        assert result.id == "evt_1"

    def test_list_events(self, repo):
        """List events for truth record."""
        now = utcnow()
        for i in range(2):
            event = TruthChangeEvent(
                id=f"evt_{i}",
                truth_record_id="tr_1",
                previous_state=TruthState.CLAIMED if i > 0 else None,
                new_state=TruthState.CLAIMED if i == 0 else TruthState.ESTABLISHED_FACT,
                event_type=TruthEventType.PROMOTION,
                reason=f"Reason {i}",
                source="system",
                decision_id=None,
                metadata={},
                created_at=now,
            )
            repo.insert_event(event)

        result = repo.list_events("tr_1")

        assert len(result) == 2

    def test_row_to_record_none(self, repo):
        """_row_to_record handles None."""
        result = repo._row_to_record(None)

        assert result is None
