"""
Tests for incidents/service — S37

Tests for IncidentRepository and incident creation functions.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock
import json

from app.incidents.service import (
    IncidentRepository,
    create_incident_from_signal,
    gen_incident_id,
    utcnow,
)
from app.incidents.models import Incident


class TestUtcNow:
    """Tests for utcnow function."""

    def test_utcnow_returns_iso_format(self):
        """utcnow returns ISO format string."""
        result = utcnow()

        assert isinstance(result, str)
        assert "T" in result
        assert "+" in result or "Z" in result or result.endswith("+00:00")


class TestGenIncidentId:
    """Tests for gen_incident_id function."""

    def test_gen_incident_id_format(self):
        """Generated ID has correct format."""
        result = gen_incident_id()

        assert result.startswith("inc_")
        assert len(result) == 14  # "inc_" + 10 hex chars

    def test_gen_incident_id_unique(self):
        """Generated IDs are unique."""
        ids = [gen_incident_id() for _ in range(100)]

        assert len(set(ids)) == 100


class TestIncidentRepository:
    """Tests for IncidentRepository class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database path."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_incidents.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return IncidentRepository(db_path=temp_db)

    def test_init_creates_schema(self, temp_db):
        """Init creates database schema."""
        repo = IncidentRepository(db_path=temp_db)

        assert temp_db.exists()

    def test_init_default_path(self, tmp_path, monkeypatch):
        """Init with default path from env."""
        db_path = tmp_path / "default_incidents.sqlite"
        monkeypatch.setenv("INSPECTAH_S25_TRUTH_DB_PATH", str(db_path))

        repo = IncidentRepository()

        assert repo.db_path == db_path

    def test_upsert_new_incident(self, repo):
        """Upsert a new incident."""
        incident = Incident(
            id="inc_test_001",
            title="Test Incident",
            summary="A test incident",
            domain="test",
            severity="high",
            status="OPEN",
            related_claims=[],
            threat_signals=[{"type": "test", "severity": "high"}],
            created_at=utcnow(),
        )

        result = repo.upsert(incident)

        assert result.id == "inc_test_001"
        assert result.summary == "A test incident"

    def test_upsert_replaces_existing(self, repo):
        """Upsert replaces existing incident."""
        incident1 = Incident(
            id="inc_test_002",
            title="Original",
            summary="Original summary",
            domain="test",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        )
        incident2 = Incident(
            id="inc_test_002",
            title="Updated",
            summary="Updated summary",
            domain="test",
            severity="high",
            status="RESOLVED",
            related_claims=[],
            threat_signals=[{"new": "signal"}],
            created_at=utcnow(),
        )

        repo.upsert(incident1)
        repo.upsert(incident2)
        result = repo.get("inc_test_002")

        assert result.summary == "Updated summary"
        assert result.severity == "high"
        assert result.status == "RESOLVED"

    def test_get_existing_incident(self, repo):
        """Get an existing incident."""
        incident = Incident(
            id="inc_get_test",
            title="Get Test",
            summary="Test for get",
            domain="test",
            severity="medium",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        )
        repo.upsert(incident)

        result = repo.get("inc_get_test")

        assert result is not None
        assert result.id == "inc_get_test"
        assert result.summary == "Test for get"

    def test_get_nonexistent_incident(self, repo):
        """Get returns None for nonexistent incident."""
        result = repo.get("nonexistent")

        assert result is None

    def test_list_all_incidents(self, repo):
        """List all incidents."""
        for i in range(3):
            incident = Incident(
                id=f"inc_list_{i}",
                title=f"Incident {i}",
                summary=f"Summary {i}",
                domain="test",
                severity="medium",
                status="OPEN",
                related_claims=[],
                threat_signals=[],
                created_at=utcnow(),
            )
            repo.upsert(incident)

        result = repo.list()

        assert len(result) == 3

    def test_list_filter_by_status(self, repo):
        """List incidents filtered by status."""
        repo.upsert(Incident(
            id="inc_open_1",
            title="Open 1",
            summary="",
            domain="test",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))
        repo.upsert(Incident(
            id="inc_resolved_1",
            title="Resolved 1",
            summary="",
            domain="test",
            severity="low",
            status="RESOLVED",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))

        result = repo.list(status="OPEN")

        assert len(result) == 1
        assert result[0].status == "OPEN"

    def test_list_filter_by_domain(self, repo):
        """List incidents filtered by domain."""
        repo.upsert(Incident(
            id="inc_domain_a",
            title="Domain A",
            summary="",
            domain="domain_a",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))
        repo.upsert(Incident(
            id="inc_domain_b",
            title="Domain B",
            summary="",
            domain="domain_b",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))

        result = repo.list(domain="domain_a")

        assert len(result) == 1
        assert result[0].domain == "domain_a"

    def test_list_filter_by_severity(self, repo):
        """List incidents filtered by severity."""
        repo.upsert(Incident(
            id="inc_high",
            title="High",
            summary="",
            domain="test",
            severity="high",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))
        repo.upsert(Incident(
            id="inc_low",
            title="Low",
            summary="",
            domain="test",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))

        result = repo.list(severity="high")

        assert len(result) == 1
        assert result[0].severity == "high"

    def test_list_filter_multiple(self, repo):
        """List incidents with multiple filters."""
        repo.upsert(Incident(
            id="inc_multi_1",
            title="Multi 1",
            summary="",
            domain="prod",
            severity="high",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))
        repo.upsert(Incident(
            id="inc_multi_2",
            title="Multi 2",
            summary="",
            domain="prod",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        ))

        result = repo.list(domain="prod", severity="high", status="OPEN")

        assert len(result) == 1
        assert result[0].id == "inc_multi_1"

    def test_update_status_existing(self, repo):
        """Update status of existing incident."""
        incident = Incident(
            id="inc_update_status",
            title="Update Status",
            summary="",
            domain="test",
            severity="medium",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        )
        repo.upsert(incident)

        result = repo.update_status("inc_update_status", "RESOLVED")

        assert result is not None
        assert result.status == "RESOLVED"
        assert result.updated_at is not None

    def test_update_status_nonexistent(self, repo):
        """Update status of nonexistent incident returns None."""
        result = repo.update_status("nonexistent", "RESOLVED")

        assert result is None

    def test_row_to_incident(self, repo):
        """Row to incident converts correctly."""
        incident = Incident(
            id="inc_row_test",
            title="Row Test",
            summary="Test row conversion",
            domain="test",
            severity="medium",
            status="OPEN",
            related_claims=[],
            threat_signals=[{"type": "test"}],
            created_at=utcnow(),
        )
        repo.upsert(incident)

        result = repo.get("inc_row_test")

        assert result.title == "Test row conversion"
        assert result.summary == "Test row conversion"
        assert len(result.threat_signals) == 1

    def test_row_to_incident_null_summary(self, repo):
        """Row to incident handles null summary."""
        incident = Incident(
            id="inc_null_summary",
            title="",
            summary=None,
            domain="test",
            severity="low",
            status="OPEN",
            related_claims=[],
            threat_signals=[],
            created_at=utcnow(),
        )

        repo.upsert(incident)
        result = repo.get("inc_null_summary")

        assert result.title == "inc_null_summary"
        assert result.summary == ""


class TestCreateIncidentFromSignal:
    """Tests for create_incident_from_signal function."""

    @pytest.fixture
    def temp_repo(self):
        """Create temp repository."""
        with TemporaryDirectory() as tmpdir:
            yield IncidentRepository(db_path=Path(tmpdir) / "test.sqlite")

    def test_create_incident_basic(self, temp_repo):
        """Create incident from basic signal."""
        signal = {"type": "test", "severity": "high"}

        result = create_incident_from_signal(
            signal=signal,
            domain="test_domain",
            summary="Test incident",
            repo=temp_repo,
        )

        assert result.id.startswith("inc_")
        assert result.title == "Test incident"
        assert result.summary == "Test incident"
        assert result.domain == "test_domain"
        assert result.severity == "high"
        assert result.status == "OPEN"
        assert len(result.threat_signals) == 1

    def test_create_incident_with_refs(self, temp_repo):
        """Create incident with reference IDs."""
        signal = {"type": "test"}

        result = create_incident_from_signal(
            signal=signal,
            domain="test",
            summary="Test with refs",
            ref_truth_record_id="tr_123",
            ref_case_id="case_456",
            repo=temp_repo,
        )

        assert result.ref_truth_record_id == "tr_123"
        assert result.ref_case_id == "case_456"

    def test_create_incident_default_severity(self, temp_repo):
        """Create incident with default severity."""
        signal = {"type": "test"}

        result = create_incident_from_signal(
            signal=signal,
            domain="test",
            summary="Default severity",
            repo=temp_repo,
        )

        assert result.severity == "medium"

    def test_create_incident_persisted(self, temp_repo):
        """Created incident is persisted."""
        signal = {"type": "test", "severity": "low"}

        result = create_incident_from_signal(
            signal=signal,
            domain="test",
            summary="Persisted",
            repo=temp_repo,
        )

        fetched = temp_repo.get(result.id)
        assert fetched is not None
        assert fetched.summary == "Persisted"
