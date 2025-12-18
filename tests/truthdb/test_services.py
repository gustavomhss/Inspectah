"""
Tests for TruthDB Services — S37

Tests for PromotionService and ContestationService.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

from app.truthdb.services import (
    PromotionService,
    ContestationService,
    PromotionError,
    _gen_id,
)
from app.truthdb.models import TruthStatus, TruthStateRecord, DecisionBlock


# Test database schema for setup
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS fact_blocks (
    id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    content_hash TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_blocks (
    id TEXT PRIMARY KEY,
    fact_block_id TEXT NOT NULL,
    evidence_type TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (fact_block_id) REFERENCES fact_blocks(id)
);

CREATE TABLE IF NOT EXISTS truth_states (
    id TEXT PRIMARY KEY,
    claim_id TEXT UNIQUE NOT NULL,
    fact_block_id TEXT NOT NULL,
    status TEXT NOT NULL,
    current_decision_block_id TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (fact_block_id) REFERENCES fact_blocks(id)
);

CREATE TABLE IF NOT EXISTS decision_blocks (
    id TEXT PRIMARY KEY,
    fact_block_id TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (fact_block_id) REFERENCES fact_blocks(id)
);

CREATE TABLE IF NOT EXISTS contest_records (
    id TEXT PRIMARY KEY,
    truth_state_id TEXT NOT NULL,
    reason TEXT,
    status TEXT NOT NULL,
    processed_decision_block_id TEXT,
    processed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (truth_state_id) REFERENCES truth_states(id)
);
"""


class TestGenId:
    """Tests for _gen_id function."""

    def test_gen_id_format(self):
        """Generated ID has correct format."""
        result = _gen_id("test")
        assert result.startswith("test_")
        assert len(result) == len("test_") + 10

    def test_gen_id_unique(self):
        """Generated IDs are unique."""
        ids = [_gen_id("prefix") for _ in range(100)]
        assert len(set(ids)) == 100


class TestPromotionService:
    """Tests for PromotionService class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database with schema."""
        import sqlite3
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_truth.sqlite"
            conn = sqlite3.connect(db_path)
            conn.executescript(SCHEMA_SQL)
            conn.close()
            yield db_path

    @pytest.fixture
    def service(self, temp_db):
        """Create service with temp db."""
        return PromotionService(db_path=temp_db, env="test")

    def test_init_default_path(self):
        """Initialize with default path."""
        service = PromotionService()
        assert service.db_path is not None
        assert service.env == "test"

    def test_init_custom_path(self, temp_db):
        """Initialize with custom path."""
        service = PromotionService(db_path=temp_db, env="production")
        assert service.db_path == temp_db
        assert service.env == "production"

    def test_promote_claim_basic(self, service):
        """Promote a basic claim."""
        claim = {
            "id": "claim_1",
            "claim_type": "price",
            "content_hash": "hash_123",
            "evidences": [],
        }

        with patch("app.truthdb.services.extract_fact_from_claim") as mock_extract:
            mock_adapted = MagicMock()
            mock_adapted.claim_id = "claim_1"
            mock_adapted.claim_type = "price"
            mock_adapted.content_hash = "hash_123"
            mock_adapted.evidences = []
            mock_extract.return_value = mock_adapted

            with patch("app.truthdb.metrics.inc_promotion_attempt"):
                with patch("app.truthdb.metrics.inc_promotion_success"):
                    result = service.promote_claim(claim)

        assert isinstance(result, TruthStateRecord)
        assert result.claim_id == "claim_1"

    def test_promote_claim_with_evidences(self, service):
        """Promote claim with evidences."""
        from app.claims.adapters_truthdb import SUPPORTED_CLAIM_TYPE

        claim = {
            "id": "claim_2",
            "claim_type": SUPPORTED_CLAIM_TYPE,
            "content_hash": "hash_456",
            "evidences": [
                {"id": "ev_1", "type": "source_doc", "metadata": {}},
                {"id": "ev_2", "type": "api_response", "metadata": {}},
            ],
        }

        with patch("app.truthdb.services.extract_fact_from_claim") as mock_extract:
            mock_adapted = MagicMock()
            mock_adapted.claim_id = "claim_2"
            mock_adapted.claim_type = SUPPORTED_CLAIM_TYPE
            mock_adapted.content_hash = "hash_456"
            mock_adapted.evidences = claim["evidences"]
            mock_extract.return_value = mock_adapted

            with patch("app.truthdb.metrics.inc_promotion_attempt"):
                with patch("app.truthdb.metrics.inc_promotion_success"):
                    result = service.promote_claim(claim)

        assert result.status == TruthStatus.TRUE

    def test_promote_claim_exception(self, service):
        """Promote claim records error on exception."""
        claim = {"id": "claim_3"}

        with patch("app.truthdb.services.extract_fact_from_claim") as mock_extract:
            mock_adapted = MagicMock()
            mock_adapted.claim_id = "claim_3"
            mock_adapted.claim_type = "price"
            mock_adapted.content_hash = "hash"
            mock_adapted.evidences = []
            mock_extract.return_value = mock_adapted

            # Make _promote raise an exception
            with patch.object(service, "_promote", side_effect=Exception("Test error")):
                with patch("app.truthdb.metrics.inc_promotion_attempt"):
                    with patch("app.truthdb.metrics.inc_flow_error") as mock_error:
                        with pytest.raises(Exception, match="Test error"):
                            service.promote_claim(claim)
                        mock_error.assert_called_once()

    def test_ensure_fact_block_existing(self, service, temp_db):
        """_ensure_fact_block returns existing block."""
        import sqlite3

        # Pre-insert a fact block
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("existing_fact", "claim_existing", "hash", "{}", ),
        )
        conn.commit()
        conn.close()

        mock_adapted = MagicMock()
        mock_adapted.claim_id = "claim_existing"
        mock_adapted.content_hash = "hash"

        result = service._ensure_fact_block(mock_adapted)

        assert result.id == "existing_fact"
        assert result.claim_id == "claim_existing"

    def test_ensure_evidences_empty(self, service, temp_db):
        """_ensure_evidences handles empty list."""
        from app.truthdb.models import FactBlock

        fact_block = FactBlock(id="fact_1", claim_id="claim_1", content_hash="hash")

        # Should not raise
        service._ensure_evidences(fact_block, [])

    def test_ensure_evidences_skips_existing(self, service, temp_db):
        """_ensure_evidences skips existing evidence."""
        import sqlite3
        from app.truthdb.models import FactBlock

        # Pre-insert fact block and evidence
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_1", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO evidence_blocks (id, fact_block_id, evidence_type, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("ev_existing", "fact_1", "source", "{}"),
        )
        conn.commit()
        conn.close()

        fact_block = FactBlock(id="fact_1", claim_id="claim_1", content_hash="hash")
        evidences = [
            {"id": "ev_existing", "type": "source"},  # Should be skipped
            {"id": "ev_new", "type": "api"},  # Should be added
        ]

        service._ensure_evidences(fact_block, evidences)

        # Verify only ev_new was added
        conn = sqlite3.connect(temp_db)
        rows = conn.execute("SELECT id FROM evidence_blocks WHERE fact_block_id = ?", ("fact_1",)).fetchall()
        conn.close()

        assert len(rows) == 2
        ids = {r[0] for r in rows}
        assert "ev_existing" in ids
        assert "ev_new" in ids

    def test_upsert_truth_state_update_existing(self, service, temp_db):
        """_upsert_truth_state updates existing state."""
        import sqlite3
        from app.truthdb.models import FactBlock
        from app.claims.adapters_truthdb import SUPPORTED_CLAIM_TYPE

        # Pre-insert fact block and truth state
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_update", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO truth_states (id, claim_id, fact_block_id, status, current_decision_block_id, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("ts_existing", "claim_update", "fact_1", "PENDING", None, "{}"),
        )
        conn.commit()
        conn.close()

        fact_block = FactBlock(id="fact_1", claim_id="claim_update", content_hash="hash")
        mock_adapted = MagicMock()
        mock_adapted.claim_id = "claim_update"
        mock_adapted.claim_type = SUPPORTED_CLAIM_TYPE  # Use correct claim type
        mock_adapted.evidences = [{"id": "ev1", "type": "source"}]

        result = service._upsert_truth_state(mock_adapted, fact_block)

        assert result.id == "ts_existing"
        assert result.status == TruthStatus.TRUE


class TestContestationService:
    """Tests for ContestationService class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database with schema."""
        import sqlite3
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_truth.sqlite"
            conn = sqlite3.connect(db_path)
            conn.executescript(SCHEMA_SQL)
            conn.close()
            yield db_path

    @pytest.fixture
    def service(self, temp_db):
        """Create service with temp db."""
        return ContestationService(db_path=temp_db, env="test")

    def test_init_default_path(self):
        """Initialize with default path."""
        service = ContestationService()
        assert service.db_path is not None
        assert service.env == "test"

    def test_init_custom_path(self, temp_db):
        """Initialize with custom path."""
        service = ContestationService(db_path=temp_db, env="production")
        assert service.db_path == temp_db
        assert service.env == "production"

    def test_register_contestation_success(self, service, temp_db):
        """Register a contestation successfully."""
        import sqlite3

        # Pre-insert required records
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_1", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO truth_states (id, claim_id, fact_block_id, status, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("ts_1", "claim_1", "fact_1", "TRUE", "{}"),
        )
        conn.commit()
        conn.close()

        with patch("app.truthdb.metrics.inc_contestation"):
            result = service.register_contestation("ts_1", {"reason": "Incorrect data"})

        assert result.truth_state_id == "ts_1"
        assert result.reason == "Incorrect data"

    def test_register_contestation_missing_truth_state(self, service):
        """Register contestation raises for missing truth state."""
        with patch("app.truthdb.metrics.inc_flow_error") as mock_error:
            with pytest.raises(ValueError, match="TruthState not found"):
                service.register_contestation("nonexistent", {"reason": "test"})
            mock_error.assert_called_once()

    def test_register_contestation_no_reason(self, service, temp_db):
        """Register contestation with no reason."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_1", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO truth_states (id, claim_id, fact_block_id, status, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("ts_1", "claim_1", "fact_1", "TRUE", "{}"),
        )
        conn.commit()
        conn.close()

        with patch("app.truthdb.metrics.inc_contestation"):
            result = service.register_contestation("ts_1", {})

        assert result.reason is None

    def test_process_contestation_success(self, service, temp_db):
        """Process a contestation successfully."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_1", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO truth_states (id, claim_id, fact_block_id, status, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("ts_1", "claim_1", "fact_1", "TRUE", "{}"),
        )
        conn.execute(
            "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("contest_1", "ts_1", "test reason", "PENDING"),
        )
        conn.commit()
        conn.close()

        with patch("app.truthdb.metrics.inc_contestation"):
            result = service.process_contestation("contest_1")

        assert isinstance(result, DecisionBlock)
        assert result.decision_type == "update_after_contest"

    def test_process_contestation_missing_record(self, service):
        """Process contestation raises for missing record."""
        with patch("app.truthdb.metrics.inc_flow_error") as mock_error:
            with pytest.raises(ValueError, match="ContestRecord not found"):
                service.process_contestation("nonexistent")
            mock_error.assert_called_once()

    def test_process_contestation_already_processed(self, service, temp_db):
        """Process contestation raises for already processed record."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO fact_blocks (id, claim_id, content_hash, metadata, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("fact_1", "claim_1", "hash", "{}"),
        )
        conn.execute(
            "INSERT INTO truth_states (id, claim_id, fact_block_id, status, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("ts_1", "claim_1", "fact_1", "TRUE", "{}"),
        )
        conn.execute(
            "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("contest_1", "ts_1", "test", "PROCESSED"),  # Already processed
        )
        conn.commit()
        conn.close()

        with patch("app.truthdb.metrics.inc_flow_error") as mock_error:
            with pytest.raises(ValueError, match="already processed"):
                service.process_contestation("contest_1")
            mock_error.assert_called_once()

    def test_process_contestation_missing_truth_state(self, service, temp_db):
        """Process contestation raises when truth state is missing."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        # Only insert contest_record without truth_state
        conn.execute(
            "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("contest_1", "missing_ts", "test", "PENDING"),
        )
        conn.commit()
        conn.close()

        with patch("app.truthdb.metrics.inc_flow_error") as mock_error:
            with pytest.raises(ValueError, match="TruthState missing"):
                service.process_contestation("contest_1")
            mock_error.assert_called_once()


class TestPromotionError:
    """Tests for PromotionError class."""

    def test_promotion_error(self):
        """PromotionError can be raised."""
        with pytest.raises(PromotionError, match="test error"):
            raise PromotionError("test error")
