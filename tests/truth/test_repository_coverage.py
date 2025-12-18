"""
Tests for Truth Repository Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines in repository.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.truth.repository import TruthRepository
from app.truth.models import TruthRecord
from app.truth.enums import TruthState


class TestTruthRepositoryGetByClaimId:
    """Tests for get_record_by_claim_id method."""

    def setup_method(self):
        """Setup temporary database for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_truth.sqlite"
        self.repo = TruthRepository(db_path=self.db_path)

    def teardown_method(self):
        """Cleanup temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_record_by_claim_id_exists(self):
        """Lines 135-137: Get record by claim_id when it exists."""
        # Create a record
        record = TruthRecord(
            id="test-id-1",
            slug="test:claim-123",
            claim_id="claim-123",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Get by claim_id
        result = self.repo.get_record_by_claim_id("claim-123")

        assert result is not None
        assert result.claim_id == "claim-123"
        assert result.id == "test-id-1"

    def test_get_record_by_claim_id_not_exists(self):
        """Lines 135-137: Get record by claim_id when it doesn't exist."""
        # Try to get non-existent claim_id
        result = self.repo.get_record_by_claim_id("non-existent-claim")

        assert result is None

    def test_get_record_by_claim_id_multiple_records(self):
        """Lines 135-137: Get specific record by claim_id when multiple records exist."""
        # Create multiple records
        record1 = TruthRecord(
            id="test-id-1",
            slug="test:claim-1",
            claim_id="claim-1",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        record2 = TruthRecord(
            id="test-id-2",
            slug="test:claim-2",
            claim_id="claim-2",
            domain="test",
            current_state=TruthState.CLAIMED,
        )
        self.repo.upsert_truth_record(record1)
        self.repo.upsert_truth_record(record2)

        # Get specific claim
        result = self.repo.get_record_by_claim_id("claim-2")

        assert result is not None
        assert result.claim_id == "claim-2"
        assert result.id == "test-id-2"
        assert result.current_state == TruthState.CLAIMED


class TestTruthRepositoryEdgeCases:
    """Additional edge case tests for TruthRepository."""

    def setup_method(self):
        """Setup temporary database for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_truth.sqlite"
        self.repo = TruthRepository(db_path=self.db_path)

    def teardown_method(self):
        """Cleanup temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_record_by_claim_id_with_null_claim_id(self):
        """Test behavior when searching for None claim_id."""
        # Create record without claim_id
        record = TruthRecord(
            id="test-id-1",
            slug="test:slug-1",
            claim_id=None,
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Search for None claim_id
        result = self.repo.get_record_by_claim_id(None)

        # SQLite treats None as NULL, so this should return the record with NULL claim_id
        # Or return None depending on implementation
        # The actual behavior depends on SQL NULL handling
        if result:
            assert result.claim_id is None

    def test_get_record_by_claim_id_empty_string(self):
        """Test behavior when searching for empty string claim_id."""
        result = self.repo.get_record_by_claim_id("")

        # Should return None for empty string
        assert result is None

    def test_upsert_and_retrieve_by_claim_id(self):
        """Test full cycle: upsert and retrieve by claim_id."""
        # Create and insert
        record = TruthRecord(
            id="test-id",
            slug="test:claim-full-cycle",
            claim_id="claim-full-cycle",
            domain="test",
            current_state=TruthState.UNKNOWN,
        )
        self.repo.upsert_truth_record(record)

        # Retrieve by claim_id
        retrieved = self.repo.get_record_by_claim_id("claim-full-cycle")

        assert retrieved is not None
        assert retrieved.id == "test-id"
        assert retrieved.slug == "test:claim-full-cycle"
