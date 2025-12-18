"""
Tests for Feedback Repository — S37

Tests for FeedbackRepository persistence layer.
"""

import pytest
import tempfile
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.feedback.repository import FeedbackRepository


class TestFeedbackRepositoryInit:
    """Tests for repository initialization."""

    def test_init_default_path(self):
        """Initialize with default path."""
        with patch.object(FeedbackRepository, "_ensure_schema"):
            repo = FeedbackRepository()
            assert repo.db_path is not None

    def test_init_custom_path(self):
        """Initialize with custom path."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as f:
            with patch.object(FeedbackRepository, "_ensure_schema"):
                repo = FeedbackRepository(db_path=Path(f.name))
                assert repo.db_path == Path(f.name)


class TestSanitizeComment:
    """Tests for comment sanitization."""

    @pytest.fixture
    def repo(self):
        """Create repository with mocked schema."""
        with patch.object(FeedbackRepository, "_ensure_schema"):
            return FeedbackRepository()

    def test_sanitize_normal_text(self, repo):
        """Normal text passes through."""
        text = "This is a normal comment"
        result = repo._sanitize_comment(text)
        assert result == text

    def test_sanitize_email_detected(self, repo):
        """Text with email gets masked."""
        text = "Contact me at user@example.com"
        result = repo._sanitize_comment(text)
        # Should be masked if email detected
        assert "@" not in result or result != text

    def test_sanitize_long_text(self, repo):
        """Long text gets masked."""
        text = "x" * 600
        result = repo._sanitize_comment(text)
        assert result != text


class TestRecordFeedbackOnTrace:
    """Tests for recording trace feedback."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with test database."""
        db_path = tmp_path / "test_feedback.sqlite"

        # Create schema manually
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback_on_trace (
                feedback_id TEXT PRIMARY KEY,
                target_type TEXT,
                target_id TEXT,
                authored_by_actor TEXT,
                authored_by_role TEXT,
                origin_surface TEXT,
                feedback_kind TEXT,
                severity TEXT,
                comment TEXT,
                suggested_action TEXT,
                pii_tags TEXT,
                redaction_applied INTEGER,
                request_id TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback_on_decision (
                feedback_id TEXT PRIMARY KEY,
                decision_record_id TEXT,
                committee_trace_id TEXT,
                agent_trace_id TEXT,
                authored_by_actor TEXT,
                authored_by_role TEXT,
                origin_surface TEXT,
                feedback_kind TEXT,
                severity TEXT,
                comment TEXT,
                suggested_action TEXT,
                pii_tags TEXT,
                redaction_applied INTEGER,
                request_id TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(FeedbackRepository, "_ensure_schema"):
            repo = FeedbackRepository(db_path=db_path)
            return repo

    def test_record_feedback_on_trace(self, repo):
        """Record trace feedback."""
        # Create mock feedback object
        feedback = MagicMock()
        feedback.feedback_id = "fb_123"
        feedback.target_id = "trace_456"
        feedback.authored_by_actor = "user_1"
        feedback.authored_by_role = "admin"
        feedback.origin_surface = "web"
        feedback.feedback_kind = "correction"
        feedback.severity = "medium"
        feedback.comment = "Test comment"
        feedback.suggested_action = "review"
        feedback.pii_tags = []
        feedback.redaction_applied = False
        feedback.request_id = "req_789"
        feedback.created_at = datetime.now(timezone.utc)

        result = repo.record_feedback_on_trace(feedback)

        assert result == feedback

    def test_list_feedback_for_trace(self, repo):
        """List feedback for a trace."""
        # Insert test data directly
        conn = sqlite3.connect(str(repo.db_path))
        conn.execute(
            """
            INSERT INTO feedback_on_trace (feedback_id, target_type, target_id, authored_by_actor,
            authored_by_role, origin_surface, feedback_kind, severity, comment, suggested_action,
            pii_tags, redaction_applied, request_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("fb_1", "trace", "trace_123", "user_1", "admin", "web", "correction",
             "high", "Test", "review", "[]", 0, "req_1", "2024-01-01T00:00:00Z")
        )
        conn.commit()
        conn.close()

        results = repo.list_feedback_for_trace("trace_123")

        assert len(results) == 1
        assert results[0]["feedback_id"] == "fb_1"


class TestRecordFeedbackOnDecision:
    """Tests for recording decision feedback."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with test database."""
        db_path = tmp_path / "test_feedback.sqlite"

        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback_on_trace (
                feedback_id TEXT PRIMARY KEY,
                target_type TEXT,
                target_id TEXT,
                authored_by_actor TEXT,
                authored_by_role TEXT,
                origin_surface TEXT,
                feedback_kind TEXT,
                severity TEXT,
                comment TEXT,
                suggested_action TEXT,
                pii_tags TEXT,
                redaction_applied INTEGER,
                request_id TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback_on_decision (
                feedback_id TEXT PRIMARY KEY,
                decision_record_id TEXT,
                committee_trace_id TEXT,
                agent_trace_id TEXT,
                authored_by_actor TEXT,
                authored_by_role TEXT,
                origin_surface TEXT,
                feedback_kind TEXT,
                severity TEXT,
                comment TEXT,
                suggested_action TEXT,
                pii_tags TEXT,
                redaction_applied INTEGER,
                request_id TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

        with patch.object(FeedbackRepository, "_ensure_schema"):
            repo = FeedbackRepository(db_path=db_path)
            return repo

    def test_record_feedback_on_decision(self, repo):
        """Record decision feedback."""
        feedback = MagicMock()
        feedback.feedback_id = "fb_dec_123"
        feedback.decision_record_id = "dec_456"
        feedback.committee_trace_id = "comm_789"
        feedback.agent_trace_id = "agent_012"
        feedback.authored_by_actor = "user_1"
        feedback.authored_by_role = "reviewer"
        feedback.origin_surface = "admin"
        feedback.feedback_kind = "disagreement"
        feedback.severity = "high"
        feedback.comment = "Decision feedback"
        feedback.suggested_action = "escalate"
        feedback.pii_tags = []
        feedback.redaction_applied = False
        feedback.request_id = "req_dec_1"
        feedback.created_at = datetime.now(timezone.utc)

        result = repo.record_feedback_on_decision(feedback)

        assert result == feedback

    def test_list_feedback_for_decision(self, repo):
        """List feedback for a decision."""
        conn = sqlite3.connect(str(repo.db_path))
        conn.execute(
            """
            INSERT INTO feedback_on_decision (feedback_id, decision_record_id, committee_trace_id,
            agent_trace_id, authored_by_actor, authored_by_role, origin_surface, feedback_kind,
            severity, comment, suggested_action, pii_tags, redaction_applied, request_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("fb_dec_1", "dec_123", "comm_1", "agent_1", "user_1", "admin", "web",
             "correction", "medium", "Test", "review", "[]", 0, "req_1", "2024-01-01T00:00:00Z")
        )
        conn.commit()
        conn.close()

        results = repo.list_feedback_for_decision("dec_123")

        assert len(results) == 1
        assert results[0]["decision_record_id"] == "dec_123"


class TestConnectionContext:
    """Tests for connection context manager."""

    @pytest.fixture
    def repo(self, tmp_path):
        """Create repository with test database."""
        db_path = tmp_path / "test_feedback.sqlite"

        with patch.object(FeedbackRepository, "_ensure_schema"):
            repo = FeedbackRepository(db_path=db_path)
            return repo

    def test_conn_creates_directory(self, repo, tmp_path):
        """Connection creates parent directory if needed."""
        nested_path = tmp_path / "nested" / "dir" / "test.sqlite"
        repo.db_path = nested_path

        # This should create the directory
        with repo._conn() as conn:
            pass

        assert nested_path.parent.exists()

    def test_conn_row_factory(self, repo, tmp_path):
        """Connection has row factory set."""
        db_path = tmp_path / "test.sqlite"
        repo.db_path = db_path

        with repo._conn() as conn:
            # Should be able to access rows by column name
            assert conn.row_factory == sqlite3.Row
