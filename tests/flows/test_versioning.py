"""
Tests for flows/versioning — S37

Tests for FlowVersioning and count_rollbacks functions.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from app.flows.versioning import FlowVersioning, count_rollbacks_last_hour


class TestFlowVersioning:
    """Tests for FlowVersioning class."""

    @pytest.fixture
    def db_conn(self):
        """Create in-memory SQLite connection with schema."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE flow_flow_versions (
                id TEXT PRIMARY KEY,
                flow_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                template_slug TEXT NOT NULL,
                estado TEXT NOT NULL,
                catalog_hash TEXT,
                catalog_signature TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        return conn

    @pytest.fixture
    def versioning(self, db_conn):
        """Create FlowVersioning instance."""
        return FlowVersioning(conn=db_conn, limits={"max_versions_to_keep": 3})

    def test_create_version_new(self, versioning, db_conn):
        """Create a new version."""
        result = versioning.create_version(
            flow_id="flow_1",
            template_slug="template_1",
            version_id="v1",
            estado="ativo",
            catalog_hash="abc123",
            catalog_signature="sig123",
        )

        assert result.flow_id == "flow_1"
        assert result.version_id == "v1"
        assert result.template_slug == "template_1"
        assert result.estado == "ativo"
        assert result.catalog_hash == "abc123"

    def test_create_version_existing(self, versioning, db_conn):
        """Creating same version returns existing."""
        versioning.create_version(
            flow_id="flow_1",
            template_slug="template_1",
            version_id="v1",
        )
        result = versioning.create_version(
            flow_id="flow_1",
            template_slug="template_1",
            version_id="v1",
        )

        assert result.version_id == "v1"
        rows = db_conn.execute(
            "SELECT COUNT(*) as cnt FROM flow_flow_versions WHERE flow_id='flow_1' AND version_id='v1'"
        ).fetchone()
        assert rows["cnt"] == 1

    def test_set_version_state(self, versioning, db_conn):
        """Update version state."""
        ver = versioning.create_version(
            flow_id="flow_1",
            template_slug="template_1",
            version_id="v1",
            estado="draft",
        )

        versioning.set_version_state(ver.id, "ativo")

        row = db_conn.execute(
            "SELECT estado FROM flow_flow_versions WHERE id=?", (ver.id,)
        ).fetchone()
        assert row["estado"] == "ativo"

    def test_enforce_version_retention(self, versioning, db_conn):
        """Old versions are deleted when limit exceeded."""
        # Create versions one by one and commit after each
        for i in range(5):
            db_conn.execute(
                """
                INSERT INTO flow_flow_versions (id, flow_id, version_id, template_slug, estado, catalog_hash, catalog_signature, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, '{}', datetime('now'), datetime('now'))
                """,
                (f"ver_{i}", "flow_1", f"v{i}", "template_1", "ativo", None, None),
            )

        # Now call enforce retention
        versioning._enforce_version_retention("flow_1")

        rows = db_conn.execute(
            "SELECT COUNT(*) as cnt FROM flow_flow_versions WHERE flow_id='flow_1'"
        ).fetchone()
        assert rows["cnt"] == 3

    def test_create_version_without_catalog_fields(self, versioning):
        """Create version without catalog_hash/signature."""
        result = versioning.create_version(
            flow_id="flow_2",
            template_slug="template_2",
            version_id="v1",
        )

        assert result.catalog_hash is None
        assert result.catalog_signature is None


class TestCountRollbacksLastHour:
    """Tests for count_rollbacks_last_hour function."""

    @pytest.fixture
    def db_conn(self):
        """Create in-memory SQLite connection with schema."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE flow_flow_operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id TEXT NOT NULL,
                operacao TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        return conn

    def test_count_rollbacks_none(self, db_conn):
        """Count zero when no rollbacks exist."""
        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 0

    def test_count_rollbacks_recent(self, db_conn):
        """Count recent rollbacks within the hour."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(minutes=30)
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", recent.isoformat()),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 1

    def test_count_rollbacks_old(self, db_conn):
        """Don't count rollbacks older than an hour."""
        old = datetime.now(timezone.utc) - timedelta(hours=2)
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", old.isoformat()),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 0

    def test_count_rollbacks_mixed(self, db_conn):
        """Count only recent rollbacks in mixed set."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(minutes=15)
        old = now - timedelta(hours=3)

        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", recent.isoformat()),
        )
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", old.isoformat()),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 1

    def test_count_rollbacks_naive_datetime(self, db_conn):
        """Handle naive datetime (no timezone)."""
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(minutes=30)).replace(tzinfo=None)
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", recent.isoformat()),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 1

    def test_count_rollbacks_invalid_date(self, db_conn):
        """Skip entries with invalid dates."""
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", "invalid-date"),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 0

    def test_count_rollbacks_different_flow(self, db_conn):
        """Only count rollbacks for specified flow."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(minutes=15)
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_1", "rollback", recent.isoformat()),
        )
        db_conn.execute(
            "INSERT INTO flow_flow_operation_logs (flow_id, operacao, created_at) VALUES (?, ?, ?)",
            ("flow_2", "rollback", recent.isoformat()),
        )

        result = count_rollbacks_last_hour(db_conn, "flow_1")

        assert result == 1
