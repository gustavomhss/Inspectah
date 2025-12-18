"""
Tests for Layers Storage — S37

Tests for LayersTraceRepository persistence.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timezone

from app.layers.storage import LayersTraceRepository
from app.layers.models import LayersTrace


class TestLayersTraceRepository:
    """Tests for LayersTraceRepository class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_layers.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return LayersTraceRepository(db_path=temp_db)

    def test_init_creates_schema(self, temp_db):
        """Init creates database schema."""
        repo = LayersTraceRepository(db_path=temp_db)

        assert temp_db.exists()

    def test_init_default_path(self, tmp_path, monkeypatch):
        """Init with default path."""
        db_path = tmp_path / "default.sqlite"
        monkeypatch.setenv("INSPECTAH_S25_TRUTH_DB_PATH", str(db_path))

        repo = LayersTraceRepository()

        assert repo.db_path == db_path

    def test_save_trace(self, repo):
        """Save a trace."""
        trace = LayersTrace(
            claim_id="claim_1",
            pipeline="promotion",
            executions=[{"layer": "l1", "result": "ok"}],
            created_at=datetime.now(timezone.utc),
        )

        trace_id = repo.save_trace(trace, "trace_1", truth_record_id="tr_1")

        assert trace_id == "trace_1"

    def test_save_trace_without_truth_record(self, repo):
        """Save trace without truth_record_id."""
        trace = LayersTrace(
            claim_id="claim_2",
            pipeline="validation",
            executions=[],
            created_at=datetime.now(timezone.utc),
        )

        trace_id = repo.save_trace(trace, "trace_2", truth_record_id=None)

        assert trace_id == "trace_2"

    def test_save_trace_replaces_existing(self, repo):
        """Save trace replaces existing with same ID."""
        trace1 = LayersTrace(
            claim_id="claim_1",
            pipeline="v1",
            executions=[],
            created_at=datetime.now(timezone.utc),
        )
        trace2 = LayersTrace(
            claim_id="claim_1",
            pipeline="v2",
            executions=[{"new": "data"}],
            created_at=datetime.now(timezone.utc),
        )

        repo.save_trace(trace1, "trace_1", truth_record_id="tr_1")
        repo.save_trace(trace2, "trace_1", truth_record_id="tr_1")

        result = repo.get_by_truth_record("tr_1")
        assert result.pipeline == "v2"

    def test_get_by_truth_record(self, repo):
        """Get trace by truth record ID."""
        trace = LayersTrace(
            claim_id="claim_test",
            pipeline="test_pipeline",
            executions=[
                {"layer": "layer_1", "status": "success"},
                {"layer": "layer_2", "status": "success"},
            ],
            created_at=datetime.now(timezone.utc),
        )
        repo.save_trace(trace, "trace_get", truth_record_id="tr_get")

        result = repo.get_by_truth_record("tr_get")

        assert result is not None
        assert result.claim_id == "claim_test"
        assert result.pipeline == "test_pipeline"
        assert len(result.executions) == 2

    def test_get_by_truth_record_not_found(self, repo):
        """Get trace returns None when not found."""
        result = repo.get_by_truth_record("nonexistent")

        assert result is None

    def test_get_by_truth_record_latest(self, repo):
        """Get trace returns latest for truth record."""
        import time

        trace1 = LayersTrace(
            claim_id="claim_1",
            pipeline="old",
            executions=[],
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        trace2 = LayersTrace(
            claim_id="claim_1",
            pipeline="new",
            executions=[],
            created_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )

        repo.save_trace(trace1, "trace_old", truth_record_id="tr_multi")
        repo.save_trace(trace2, "trace_new", truth_record_id="tr_multi")

        result = repo.get_by_truth_record("tr_multi")

        assert result.pipeline == "new"

    def test_save_trace_complex_executions(self, repo):
        """Save trace with complex execution data."""
        trace = LayersTrace(
            claim_id="claim_complex",
            pipeline="complex",
            executions=[
                {
                    "layer": "extraction",
                    "input": {"text": "some content"},
                    "output": {"entities": ["e1", "e2"]},
                    "duration_ms": 150,
                },
                {
                    "layer": "validation",
                    "input": {"entities": ["e1", "e2"]},
                    "output": {"valid": True, "confidence": 0.95},
                    "duration_ms": 50,
                },
            ],
            created_at=datetime.now(timezone.utc),
        )

        trace_id = repo.save_trace(trace, "trace_complex", truth_record_id="tr_complex")
        result = repo.get_by_truth_record("tr_complex")

        assert result is not None
        assert len(result.executions) == 2
        assert result.executions[0]["layer"] == "extraction"
        assert result.executions[1]["output"]["confidence"] == 0.95
