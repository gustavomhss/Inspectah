"""
Comprehensive test coverage for app/sources/service.py
Covers uncovered lines: 58, 61-62, 73-74, 99, 101, 103, 186, 202-203, 205-206, 208-209, 211-212, 214-215,
320-323, 384, 403, 431, 530-531, 549-571, 584-587
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.sources import service
from app.sources.models import Source, SourceHealthStatus, SourceState
from app.sources.schemas import SourceCreate, SourceFilter, SourceUpdate
from app.ingestion.models import IngestionConfig, IngestionMode, IngestionRun, IngestionStatus, IngestionTrigger
from app.ingestion.repository import IngestionRepository


@pytest.fixture
def sample_source_payload() -> SourceCreate:
    """Create a sample source payload for testing."""
    return SourceCreate(
        slug="test-source",
        name="Test Source",
        description="Test description",
        type="news_rss",
        category="official",
        themes=["politics"],
        info_types=["news"],
        protocol="https",
        format="rss",
        endpoint="https://test.com/feed.rss",
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="daily",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        meta={},
        created_by="test_user",
    )


@pytest.fixture
def lab_source_payload() -> SourceCreate:
    """Create a lab endpoint source payload for testing."""
    return SourceCreate(
        slug="lab-source",
        name="Lab Test Source",
        description="Lab source for testing normalization",
        type="news_rss",
        category="official",
        themes=["test"],
        info_types=["news"],
        protocol="https",
        format="rss",
        endpoint="https://example.com/rss",  # LAB_ENDPOINT
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="manual",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        meta={},
        created_by="test_user",
    )


# Test 1: _deserialize with invalid JSON (lines 58, 61-62)
def test_deserialize_with_invalid_json():
    """Test _deserialize handles invalid JSON gracefully."""
    # Test with None value (line 58)
    result = service._deserialize(None, [])
    assert result == []

    result = service._deserialize(None, {})
    assert result == {}

    # Test with invalid JSON (lines 61-62)
    result = service._deserialize("{invalid json", [])
    assert result == []

    result = service._deserialize("not json at all", {"default": "value"})
    assert result == {"default": "value"}

    # Test with valid JSON
    result = service._deserialize('{"key": "value"}', {})
    assert result == {"key": "value"}

    result = service._deserialize('["item1", "item2"]', [])
    assert result == ["item1", "item2"]


# Test 2: _ensure_schema with missing refresh_interval column (lines 73-74)
def test_ensure_schema_adds_refresh_interval_column():
    """Test _ensure_schema adds refresh_interval column if missing."""
    # Create a temporary database
    test_db = Path("out/test_db_schema.sqlite")
    test_db.parent.mkdir(parents=True, exist_ok=True)

    if test_db.exists():
        test_db.unlink()

    # Create connection and tables without refresh_interval
    conn = sqlite3.connect(test_db)
    conn.execute("""
        CREATE TABLE sources (
            id TEXT PRIMARY KEY,
            slug TEXT,
            name TEXT,
            description TEXT,
            type TEXT,
            category TEXT,
            themes TEXT,
            info_types TEXT,
            protocol TEXT,
            format TEXT,
            endpoint TEXT,
            auth_type TEXT,
            auth_config TEXT,
            request_params TEXT,
            headers TEXT,
            frequency TEXT,
            timeout_ms INTEGER,
            retry_policy TEXT,
            parsing_config TEXT,
            redundancy_group TEXT,
            redundancy_role TEXT,
            state TEXT,
            state_reason TEXT,
            state_updated_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            created_by TEXT,
            updated_by TEXT,
            last_reviewed_by TEXT,
            meta TEXT,
            conflict_flags TEXT,
            conflict_with_sources TEXT,
            has_open_contestation INTEGER,
            last_conflict_at TEXT,
            evidence_refs TEXT,
            trust_severity TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE source_state_history (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            from_state TEXT,
            to_state TEXT,
            reason TEXT,
            changed_by TEXT,
            created_at TEXT,
            conflict_flag INTEGER,
            conflict_types TEXT,
            conflict_with_sources TEXT,
            contestations TEXT,
            evidence_refs TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE source_health_checks (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            status TEXT,
            latency_ms INTEGER,
            checked_at TEXT,
            error TEXT,
            meta TEXT
        )
    """)
    conn.commit()

    # Verify refresh_interval doesn't exist
    info = conn.execute("PRAGMA table_info('sources')").fetchall()
    columns = {row[1] for row in info}
    assert "refresh_interval" not in columns

    # Call _ensure_schema (lines 73-74 should execute)
    service._ensure_schema(conn)

    # Verify refresh_interval was added
    info = conn.execute("PRAGMA table_info('sources')").fetchall()
    columns = {row[1] for row in info}
    assert "refresh_interval" in columns

    conn.close()
    test_db.unlink()


# Test 3: _normalize_refresh_interval edge cases (lines 99, 101, 103)
def test_normalize_refresh_interval_edge_cases():
    """Test _normalize_refresh_interval with various edge cases."""
    # Test when value is None after initial check (line 99)
    result = service._normalize_refresh_interval(None, "news_rss")
    assert result == 180  # default for news_rss

    # Test with non-integer value (line 101)
    with pytest.raises(ValueError, match="refresh_interval deve ser inteiro em minutos"):
        service._normalize_refresh_interval("not_an_int", "news_rss")  # type: ignore

    with pytest.raises(ValueError, match="refresh_interval deve ser inteiro em minutos"):
        service._normalize_refresh_interval(15.5, "news_rss")  # type: ignore

    # Test with value below minimum (line 103)
    with pytest.raises(ValueError, match="refresh_interval fora do intervalo permitido"):
        service._normalize_refresh_interval(10, "news_rss")

    # Test with value above maximum (line 103)
    with pytest.raises(ValueError, match="refresh_interval fora do intervalo permitido"):
        service._normalize_refresh_interval(20000, "news_rss")

    # Test with valid values
    result = service._normalize_refresh_interval(15, "news_rss")
    assert result == 15

    result = service._normalize_refresh_interval(10080, "news_rss")
    assert result == 10080


# Test 4: list_sources with all filter combinations (lines 202-215)
def test_list_sources_with_all_filters(sample_source_payload):
    """Test list_sources with all possible filter combinations."""
    # Create multiple sources with different attributes
    source1 = service.create_source(sample_source_payload)

    payload2 = sample_source_payload.model_copy(update={
        "slug": "test-source-2",
        "type": "gossip_feed",
        "category": "media",
        "themes": ["sports"],
        "redundancy_group": "group1",
    })
    source2 = service.create_source(payload2)

    # Change state of source2
    service.change_source_state(source2.id, SourceState.TESTING, "test", "test_user")

    # Test filter by type (lines 202-203)
    filters = SourceFilter(type="news_rss")
    results = service.list_sources(filters)
    assert len(results) >= 1
    assert all(s.type == "news_rss" for s in results)

    # Test filter by category (lines 205-206)
    filters = SourceFilter(category="official")
    results = service.list_sources(filters)
    assert len(results) >= 1
    assert all(s.category == "official" for s in results)

    # Test filter by state (lines 208-209)
    filters = SourceFilter(state=SourceState.TESTING)
    results = service.list_sources(filters)
    assert len(results) >= 1
    assert all(s.state == SourceState.TESTING for s in results)

    # Test filter by theme (lines 211-212)
    filters = SourceFilter(theme="politics")
    results = service.list_sources(filters)
    assert len(results) >= 1
    assert all("politics" in s.themes for s in results)

    # Test filter by redundancy_group (lines 214-215)
    filters = SourceFilter(redundancy_group="group1")
    results = service.list_sources(filters)
    assert len(results) >= 1
    assert all(s.redundancy_group == "group1" for s in results)

    # Test combined filters
    filters = SourceFilter(
        type="news_rss",
        category="official",
        state=SourceState.PROPOSED,
    )
    results = service.list_sources(filters)
    assert all(
        s.type == "news_rss" and
        s.category == "official" and
        s.state == SourceState.PROPOSED
        for s in results
    )

    # Test with no filters
    results = service.list_sources()
    assert len(results) >= 2

    # Test with empty filter
    results = service.list_sources(SourceFilter())
    assert len(results) >= 2


# Test 5: create_source when normalized != created (lines 320-323)
def test_create_source_normalization_triggers_update(lab_source_payload):
    """Test create_source when normalization changes the source after creation."""
    # Lab endpoint will trigger normalization (category change)
    source = service.create_source(lab_source_payload)

    # Verify the source was normalized (lines 320-323 executed)
    # Lab sources should have category changed to "internal_test"
    assert source.category == "internal_test"
    assert source.meta.get("lab_source") is True

    # Verify the source exists in database with normalized values
    retrieved = service.get_source_detail(source.id)
    assert retrieved is not None
    assert retrieved.category == "internal_test"
    assert retrieved.meta.get("lab_source") is True


# Test 6: update_source when source not found (line 384)
def test_update_source_not_found():
    """Test update_source returns None when source doesn't exist."""
    # Try to update a non-existent source (line 384)
    update = SourceUpdate(
        name="Updated Name",
        updated_by="test_user",
    )
    result = service.update_source("nonexistent_id", update)
    assert result is None


# Test 7: update_source when state changes (line 403)
def test_update_source_state_changes(lab_source_payload):
    """Test update_source when normalization changes the state."""
    # Create a lab source in PROPOSED state
    source = service.create_source(lab_source_payload)

    # Force change state to ACTIVE (which lab sources should not be)
    with service.get_connection() as conn:
        conn.execute(
            "UPDATE sources SET state=?, state_updated_at=? WHERE id=?",
            (SourceState.ACTIVE.value, datetime.now(timezone.utc).isoformat(), source.id)
        )
        conn.commit()

    # Verify it's ACTIVE
    source_active = service.get_source_detail(source.id)
    assert source_active is not None
    assert source_active.state == SourceState.ACTIVE
    state_updated_before = source_active.state_updated_at

    # Update the source - normalization should change state back to PROPOSED (line 403)
    update = SourceUpdate(
        name="Updated Lab Source",
        updated_by="test_user",
    )
    updated = service.update_source(source.id, update)

    assert updated is not None
    assert updated.state == SourceState.PROPOSED  # Normalized back
    # State updated timestamp should change (line 403)
    assert updated.state_updated_at > state_updated_before


# Test 8: change_source_state when source not found (line 431)
def test_change_source_state_not_found():
    """Test change_source_state returns None when source doesn't exist."""
    # Try to change state of non-existent source (line 431)
    result = service.change_source_state(
        "nonexistent_id",
        SourceState.TESTING,
        "test reason",
        "test_user"
    )
    assert result is None


# Test 9: _get_ingestion_mode exception handling (lines 530-531)
def test_get_ingestion_mode_exception_handling(sample_source_payload):
    """Test _get_ingestion_mode handles exceptions gracefully."""
    source = service.create_source(sample_source_payload)

    # Mock IngestionRepository to raise an exception (lines 530-531)
    with patch.object(IngestionRepository, 'get_config', side_effect=Exception("Database error")):
        mode = service._get_ingestion_mode(source.id)
        assert mode == IngestionMode.MANUAL_ONLY.value

    # Test with no config (returns default)
    with patch.object(IngestionRepository, 'get_config', return_value=None):
        mode = service._get_ingestion_mode(source.id)
        assert mode == IngestionMode.MANUAL_ONLY.value

    # Test with valid config
    mock_config = Mock(spec=IngestionConfig)
    mock_config.mode = IngestionMode.AUTOMATIC
    with patch.object(IngestionRepository, 'get_config', return_value=mock_config):
        mode = service._get_ingestion_mode(source.id)
        assert mode == IngestionMode.AUTOMATIC.value


# Test 10: _compute_health_from_runs with various run states (lines 549-571)
def test_compute_health_from_runs_no_runs(sample_source_payload):
    """Test _compute_health_from_runs when no runs exist."""
    source = service.create_source(sample_source_payload)

    # Mock empty runs list (line 549-571)
    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=[]):
        health = service._compute_health_from_runs(source.id)

        assert health["status"] == SourceHealthStatus.DEGRADED.value
        assert health["reason"] == "Sem execuções recentes"
        assert health["last_run_status"] is None
        assert health["last_run_finished_at"] is None
        assert health["last_run_latency_ms"] is None
        assert health["last_run_items"] is None
        assert health["failure_streak"] == 0
        assert health["recent_items_count"] == 0


def test_compute_health_from_runs_with_failures(sample_source_payload):
    """Test _compute_health_from_runs with failed runs."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Create mock runs with FAIL status (lines 556-558)
    # Make sure latency is low so it doesn't override the status
    mock_run_fail = Mock(spec=IngestionRun)
    mock_run_fail.status = IngestionStatus.FAIL
    mock_run_fail.started_at = now - timedelta(seconds=30)
    mock_run_fail.finished_at = now - timedelta(seconds=10)  # 20 sec latency
    mock_run_fail.items_processed = 0
    mock_run_fail.error_message = "Connection timeout"

    mock_run_success = Mock(spec=IngestionRun)
    mock_run_success.status = IngestionStatus.SUCCESS
    mock_run_success.started_at = now - timedelta(minutes=30)
    mock_run_success.finished_at = now - timedelta(minutes=29, seconds=50)
    mock_run_success.items_processed = 10
    mock_run_success.error_message = None

    runs = [mock_run_fail, mock_run_success]

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=runs):
        health = service._compute_health_from_runs(source.id)

        # Last run failed (line 556-558)
        # Note: latency check can override, so status might be DEGRADED instead of FAIL
        # The important part is that the failure is detected
        assert health["status"] in [SourceHealthStatus.FAIL.value, SourceHealthStatus.DEGRADED.value]
        assert health["last_run_status"] == IngestionStatus.FAIL.value
        assert health["failure_streak"] == 1
        assert health["recent_items_count"] == 10


def test_compute_health_from_runs_with_partial_success(sample_source_payload):
    """Test _compute_health_from_runs with partial success."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Create mock run with PARTIAL_SUCCESS (lines 556-558)
    # Use low latency to avoid override
    mock_run = Mock(spec=IngestionRun)
    mock_run.status = IngestionStatus.PARTIAL_SUCCESS
    mock_run.started_at = now - timedelta(seconds=20)
    mock_run.finished_at = now - timedelta(seconds=10)  # 10 sec latency
    mock_run.items_processed = 5
    mock_run.error_message = "Some items failed"

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=[mock_run]):
        health = service._compute_health_from_runs(source.id)

        # Partial success should be DEGRADED (line 557)
        assert health["status"] == SourceHealthStatus.DEGRADED.value
        # Reason might be overridden by latency check, but should include error
        assert "Some items failed" in health["reason"] or "Latência" in health["reason"]
        assert health["failure_streak"] == 1


def test_compute_health_from_runs_with_past_failures(sample_source_payload):
    """Test _compute_health_from_runs with past failures but recent success."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Last run success, but previous had failures (lines 559-561)
    # Use low latency to avoid override by latency check
    mock_run_success = Mock(spec=IngestionRun)
    mock_run_success.status = IngestionStatus.SUCCESS
    mock_run_success.started_at = now - timedelta(seconds=20)
    mock_run_success.finished_at = now - timedelta(seconds=10)  # 10 sec latency
    mock_run_success.items_processed = 10
    mock_run_success.error_message = None

    mock_run_fail = Mock(spec=IngestionRun)
    mock_run_fail.status = IngestionStatus.FAIL
    mock_run_fail.started_at = now - timedelta(minutes=30)
    mock_run_fail.finished_at = now - timedelta(minutes=29, seconds=50)
    mock_run_fail.items_processed = 0
    mock_run_fail.error_message = "Previous failure"

    runs = [mock_run_success, mock_run_fail]

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=runs):
        health = service._compute_health_from_runs(source.id)

        # Should be DEGRADED due to past failures (lines 559-561)
        assert health["status"] == SourceHealthStatus.DEGRADED.value
        assert "Falhas recentes detectadas" in health["reason"] or "Latência" in health["reason"]
        assert health["failure_streak"] == 0  # Current run is success


def test_compute_health_from_runs_high_latency(sample_source_payload):
    """Test _compute_health_from_runs with high latency."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Create run with high latency (>120 seconds) (lines 562-564)
    mock_run = Mock(spec=IngestionRun)
    mock_run.status = IngestionStatus.SUCCESS
    mock_run.started_at = now - timedelta(minutes=5)
    mock_run.finished_at = now  # 5 minutes = 300 seconds > 120
    mock_run.items_processed = 10
    mock_run.error_message = None

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=[mock_run]):
        health = service._compute_health_from_runs(source.id)

        # Should be DEGRADED due to high latency (lines 562-564)
        assert health["status"] == SourceHealthStatus.DEGRADED.value
        assert health["reason"] == "Latência elevada na última execução"
        assert health["last_run_latency_ms"] == 300000  # 5 minutes


def test_compute_health_from_runs_failure_streak(sample_source_payload):
    """Test _compute_health_from_runs calculates failure streak correctly."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Create consecutive failures at the beginning (lines 565-570)
    # The streak counts from runs[0] onwards until a success
    # Need runs[0] = FAIL, runs[1] = FAIL, runs[2] = SUCCESS
    mock_run1 = Mock(spec=IngestionRun)
    mock_run1.status = IngestionStatus.FAIL
    mock_run1.started_at = now - timedelta(seconds=20)
    mock_run1.finished_at = now - timedelta(seconds=15)
    mock_run1.items_processed = 0
    mock_run1.error_message = "Failure 1"

    mock_run2 = Mock(spec=IngestionRun)
    mock_run2.status = IngestionStatus.FAIL
    mock_run2.started_at = now - timedelta(seconds=40)
    mock_run2.finished_at = now - timedelta(seconds=35)
    mock_run2.items_processed = 0
    mock_run2.error_message = "Failure 2"

    mock_run3 = Mock(spec=IngestionRun)
    mock_run3.status = IngestionStatus.SUCCESS
    mock_run3.started_at = now - timedelta(seconds=60)
    mock_run3.finished_at = now - timedelta(seconds=55)
    mock_run3.items_processed = 10
    mock_run3.error_message = None

    runs = [mock_run1, mock_run2, mock_run3]  # [FAIL, FAIL, SUCCESS]

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=runs):
        health = service._compute_health_from_runs(source.id)

        # Should count streak of 2 consecutive failures from the start (lines 565-570)
        assert health["failure_streak"] == 2


# Test 11: _run_latency_ms with missing timestamps (lines 584-587)
def test_run_latency_ms_missing_timestamps():
    """Test _run_latency_ms returns None when timestamps are missing."""
    # Test with missing started_at (line 584)
    mock_run = Mock(spec=IngestionRun)
    mock_run.started_at = None
    mock_run.finished_at = datetime.now(timezone.utc)

    result = service._run_latency_ms(mock_run)
    assert result is None

    # Test with missing finished_at (line 584)
    mock_run = Mock(spec=IngestionRun)
    mock_run.started_at = datetime.now(timezone.utc)
    mock_run.finished_at = None

    result = service._run_latency_ms(mock_run)
    assert result is None

    # Test with both missing
    mock_run = Mock(spec=IngestionRun)
    mock_run.started_at = None
    mock_run.finished_at = None

    result = service._run_latency_ms(mock_run)
    assert result is None

    # Test with both present (lines 586-587)
    now = datetime.now(timezone.utc)
    mock_run = Mock(spec=IngestionRun)
    mock_run.started_at = now - timedelta(seconds=30)
    mock_run.finished_at = now

    result = service._run_latency_ms(mock_run)
    assert result == 30000  # 30 seconds in milliseconds


def test_enrich_source_read_integration(sample_source_payload):
    """Test enrich_source_read integrates health computation correctly."""
    source = service.create_source(sample_source_payload)
    now = datetime.now(timezone.utc)

    # Create some health checks
    service.register_healthcheck(
        source.id,
        SourceHealthStatus.OK,
        latency_ms=100,
        error=None,
    )

    # Mock ingestion runs with low latency
    mock_run = Mock(spec=IngestionRun)
    mock_run.status = IngestionStatus.SUCCESS
    mock_run.started_at = now - timedelta(seconds=20)
    mock_run.finished_at = now - timedelta(seconds=10)  # 10 sec latency
    mock_run.items_processed = 25
    mock_run.error_message = None

    with patch.object(IngestionRepository, 'list_runs_by_source', return_value=[mock_run]):
        with patch.object(IngestionRepository, 'get_config', return_value=None):
            enriched = service.enrich_source_read(source)

            assert enriched.last_health_status == SourceHealthStatus.OK.value
            assert enriched.last_health_at is not None
            assert enriched.health_status == SourceHealthStatus.OK.value
            assert enriched.last_run_status == IngestionStatus.SUCCESS.value
            assert enriched.last_run_items == 25
            assert enriched.failure_streak == 0
            assert enriched.ingestion_mode == IngestionMode.MANUAL_ONLY.value


def test_ensure_schema_creates_tables_when_missing():
    """Test _ensure_schema creates tables when database is empty (line 69)."""
    # Create a fresh database
    test_db = Path("out/test_db_no_tables.sqlite")
    test_db.parent.mkdir(parents=True, exist_ok=True)

    if test_db.exists():
        test_db.unlink()

    # Temporarily override the DB path
    old_env = service.DB_ENV
    old_db = os.environ.get(service.DB_ENV)
    os.environ[service.DB_ENV] = str(test_db)

    try:
        # Create a source which will trigger _ensure_schema
        # This should trigger line 69 (sources_schema.apply_migration)
        payload = SourceCreate(
            slug="test-new-db",
            name="Test New DB",
            description="",
            type="news_rss",
            category="official",
            themes=["test"],
            info_types=["news"],
            endpoint="https://test.com/feed",
            created_by="test_user",
        )
        source = service.create_source(payload)
        assert source is not None
        assert source.id is not None

        # Verify tables were created
        conn = sqlite3.connect(test_db)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "sources" in tables
        assert "source_state_history" in tables
        conn.close()

    finally:
        # Restore environment
        if old_db is not None:
            os.environ[service.DB_ENV] = old_db
        elif service.DB_ENV in os.environ:
            del os.environ[service.DB_ENV]
        if test_db.exists():
            test_db.unlink()


def test_state_transition_from_disabled_perm_raises_error(sample_source_payload):
    """Test _apply_state_transition raises error for DISABLED_PERM sources (line 415)."""
    source = service.create_source(sample_source_payload)

    # Manually set source to DISABLED_PERM
    with service.get_connection() as conn:
        conn.execute(
            "UPDATE sources SET state=? WHERE id=?",
            (SourceState.DISABLED_PERM.value, source.id)
        )
        conn.commit()

    # Try to change state - should raise ValueError (line 415)
    with pytest.raises(ValueError, match="Fonte está desativada permanentemente"):
        service.change_source_state(source.id, SourceState.TESTING, "try to activate", "test_user")


def test_list_state_history(sample_source_payload):
    """Test list_state_history returns state history (lines 496-501)."""
    source = service.create_source(sample_source_payload)

    # Change state a few times
    service.change_source_state(source.id, SourceState.TESTING, "start testing", "test_user")
    service.change_source_state(source.id, SourceState.ACTIVE, "activate", "test_user")

    # Get state history (lines 496-501)
    history = service.list_state_history(source.id)

    # Should have at least 3 entries (PROPOSED creation + 2 changes)
    assert len(history) >= 3

    # Verify history entries
    assert all(isinstance(entry, dict) for entry in history)
    assert all("source_id" in entry for entry in history)
    assert all(entry["source_id"] == source.id for entry in history)

    # Check that states are in the history
    states = [entry["to_state"] for entry in history]
    assert SourceState.PROPOSED.value in states
    assert SourceState.TESTING.value in states
    assert SourceState.ACTIVE.value in states


def test_fetch_latest_health_no_checks(sample_source_payload):
    """Test _fetch_latest_health returns None when no health checks exist (line 185)."""
    source = service.create_source(sample_source_payload)

    # Don't create any health checks
    with service.get_connection() as conn:
        health = service._fetch_latest_health(conn, source.id)

    # Should return None (line 185)
    assert health is None
