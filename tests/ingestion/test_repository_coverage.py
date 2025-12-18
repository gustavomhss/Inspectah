"""
Extended tests for Ingestion Repository

Additional tests to reach 97%+ coverage.
"""

import json
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from app.ingestion.errors import ConfigNotFoundError
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
)
from app.ingestion.repository import (
    IngestionRepository,
    _row_to_config,
    _row_to_run,
)


class TestIngestionRepositoryEdgeCases:
    """Test edge cases and additional code paths."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_ingestion.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return IngestionRepository(db_path=temp_db)

    def test_update_config_mode_nonexistent_raises(self, repo):
        """Test update_config_mode raises for nonexistent config."""
        with pytest.raises(ConfigNotFoundError):
            repo.update_config_mode(
                source_id="nonexistent",
                mode=IngestionMode.SCHEDULED,
                enabled=True,
                updated_by="test"
            )

    def test_update_config_mode_updates_fields(self, repo):
        """Test update_config_mode updates all fields correctly."""
        # Create initial config
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=False,
            mode=IngestionMode.MANUAL,
            created_by="creator",
            updated_by="creator",
        )
        repo.save_config(config)

        # Update
        updated = repo.update_config_mode(
            source_id="src1",
            mode=IngestionMode.SCHEDULED,
            enabled=True,
            updated_by="updater"
        )

        assert updated.mode == IngestionMode.SCHEDULED
        assert updated.enabled is True
        assert updated.updated_by == "updater"
        assert updated.updated_at > config.updated_at

    def test_set_last_run(self, repo):
        """Test setting last_run_id."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        repo.set_last_run("cfg1", "run_123")

        loaded = repo.get_config("src1")
        assert loaded.last_run_id == "run_123"

    def test_list_runs_by_source_heals_stale_running(self, repo):
        """Test list_runs_by_source heals stale RUNNING runs."""
        # Create config
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        # Create old running run (more than 10 minutes ago)
        old_time = datetime.now(timezone.utc) - timedelta(minutes=15)
        run = IngestionRun(
            id="run1",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.RUNNING,
            started_at=old_time,
        )
        repo.insert_run(run)

        # List runs should heal it
        runs = repo.list_runs_by_source("src1")

        assert len(runs) == 1
        assert runs[0].status == IngestionStatus.FAIL
        assert runs[0].error_code == "timeout"
        assert "tempo máximo" in runs[0].error_message

    def test_list_runs_by_source_offset(self, repo):
        """Test list_runs_by_source with offset."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        # Create multiple runs
        for i in range(5):
            run = IngestionRun(
                id=f"run{i}",
                config_id="cfg1",
                source_id="src1",
                trigger=IngestionTrigger.MANUAL,
                status=IngestionStatus.SUCCESS,
            )
            repo.insert_run(run)

        # Get with offset
        runs = repo.list_runs_by_source("src1", limit=2, offset=2)

        assert len(runs) <= 2

    def test_list_runs_by_source_between(self, repo):
        """Test list_runs_by_source_between."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        # Create runs at different times
        old_run = IngestionRun(
            id="old",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.SUCCESS,
            started_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        new_run = IngestionRun(
            id="new",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.SUCCESS,
            started_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        repo.insert_run(old_run)
        repo.insert_run(new_run)

        # Query between
        start = datetime(2024, 5, 1, tzinfo=timezone.utc)
        end = datetime(2024, 7, 1, tzinfo=timezone.utc)
        runs = repo.list_runs_by_source_between("src1", start, end)

        assert len(runs) == 1
        assert runs[0].id == "new"

    def test_count_running_for_source(self, repo):
        """Test count_running_for_source."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        # Create some runs
        run1 = IngestionRun(
            id="run1",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.RUNNING,
        )
        run2 = IngestionRun(
            id="run2",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.SUCCESS,
        )
        repo.insert_run(run1)
        repo.insert_run(run2)

        count = repo.count_running_for_source("src1")

        assert count == 1

    def test_count_running_for_source_none(self, repo):
        """Test count_running_for_source with no running."""
        count = repo.count_running_for_source("nonexistent")

        assert count == 0

    def test_save_raw_payload_custom_base(self, temp_db, tmp_path):
        """Test save_raw_payload with custom base directory."""
        repo = IngestionRepository(db_path=temp_db)

        items = [{"id": 1, "data": "test1"}, {"id": 2, "data": "test2"}]
        custom_base = tmp_path / "custom_raw"

        path = repo.save_raw_payload("run_id", "src_id", items, base_dir=custom_base)

        assert Path(path).exists()
        assert "custom_raw" in path

    def test_load_raw_payload_empty(self, temp_db, tmp_path):
        """Test load_raw_payload with no file."""
        repo = IngestionRepository(db_path=temp_db)

        items = repo.load_raw_payload("nonexistent", "src", base_dir=tmp_path)

        assert items == []

    def test_load_raw_payload_with_empty_lines(self, temp_db, tmp_path):
        """Test load_raw_payload skips empty lines."""
        repo = IngestionRepository(db_path=temp_db)

        # Create file with empty lines
        base = tmp_path / "src" / "2024" / "01" / "01"
        base.mkdir(parents=True)
        path = base / "run_id.ndjson"

        with open(path, "w") as f:
            f.write('{"id": 1}\n')
            f.write('\n')  # Empty line
            f.write('   \n')  # Whitespace line
            f.write('{"id": 2}\n')

        items = repo.load_raw_payload("run_id", "src", base_dir=tmp_path)

        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[1]["id"] == 2

    def test_load_raw_payload_with_invalid_json(self, temp_db, tmp_path):
        """Test load_raw_payload skips invalid JSON."""
        repo = IngestionRepository(db_path=temp_db)

        # Create file with invalid JSON
        base = tmp_path / "src" / "2024" / "01" / "01"
        base.mkdir(parents=True)
        path = base / "run_id.ndjson"

        with open(path, "w") as f:
            f.write('{"id": 1}\n')
            f.write('invalid json\n')  # Invalid
            f.write('{"id": 2}\n')

        items = repo.load_raw_payload("run_id", "src", base_dir=tmp_path)

        # Should skip invalid line
        assert len(items) == 2

    def test_get_run_none(self, repo):
        """Test get_run returns None for nonexistent."""
        result = repo.get_run("nonexistent")

        assert result is None

    def test_get_config_none(self, repo):
        """Test get_config returns None for nonexistent."""
        result = repo.get_config("nonexistent")

        assert result is None

    def test_list_configs_empty(self, repo):
        """Test list_configs with no configs."""
        result = repo.list_configs()

        assert result == []

    def test_list_configs_ordered(self, repo):
        """Test list_configs orders by updated_at DESC."""
        import time

        config1 = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config1)

        time.sleep(0.01)

        config2 = IngestionConfig(
            id="cfg2",
            source_id="src2",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config2)

        configs = repo.list_configs()

        # Newest first
        assert configs[0].id == "cfg2"

    def test_update_run_updates_updated_at(self, repo):
        """Test update_run updates the updated_at timestamp."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        run = IngestionRun(
            id="run1",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.RUNNING,
        )
        repo.insert_run(run)

        original_updated = run.updated_at

        import time
        time.sleep(0.01)

        run.status = IngestionStatus.SUCCESS
        updated_run = repo.update_run(run)

        assert updated_run.updated_at > original_updated

    def test_insert_run_with_all_fields(self, repo):
        """Test inserting run with all optional fields."""
        config = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config)

        run = IngestionRun(
            id="run1",
            config_id="cfg1",
            source_id="src1",
            trigger=IngestionTrigger.SCHEDULED,
            status=IngestionStatus.SUCCESS,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            items_processed=100,
            error_code="ERR001",
            error_message="Test error",
            payload_ref="/path/to/payload",
            meta={"key": "value"},
        )

        inserted = repo.insert_run(run)

        assert inserted.id == "run1"
        assert inserted.items_processed == 100
        assert inserted.error_code == "ERR001"
        assert inserted.meta["key"] == "value"

    def test_save_config_replaces_existing(self, repo):
        """Test save_config replaces existing config."""
        config1 = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=True,
            mode=IngestionMode.MANUAL,
            interval_minutes=60,
            created_by="test",
            updated_by="test",
        )
        repo.save_config(config1)

        config2 = IngestionConfig(
            id="cfg1",
            source_id="src1",
            enabled=False,
            mode=IngestionMode.SCHEDULED,
            interval_minutes=30,
            created_by="test",
            updated_by="test2",
        )
        repo.save_config(config2)

        loaded = repo.get_config("src1")

        assert loaded.enabled is False
        assert loaded.mode == IngestionMode.SCHEDULED
        assert loaded.interval_minutes == 30
        assert loaded.updated_by == "test2"
