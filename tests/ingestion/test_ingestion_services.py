"""
Tests for Ingestion Services — S37

Tests for ingestion service functions.
"""

import os
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, AsyncMock

from app.ingestion.services import (
    _gen_id,
    _assert_source_available,
    _build_newsdata_profile,
    _newsdata_hash,
    _dedup_newsdata_items,
    _ensure_config_allows_trigger,
    _create_default_config,
    _get_or_create_config,
    _log_run_event,
    _run_ingestion_inline,
    _mark_run_success,
    _mark_run_fail,
    start_ingestion_run,
    complete_ingestion_run,
    fail_ingestion_run,
    reprocess_run,
    toggle_ingestion_mode,
    run_newsdata_ingestion,
)
from app.ingestion.errors import (
    ConfigDisabledError,
    ConfigNotFoundError,
    InvalidTransitionError,
    ModeIncompatibleError,
    RunInProgressError,
    RunNotFoundError,
    SourceNotEligibleError,
    SourceNotFoundError,
)
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
)
from app.ingestion.providers.news_provider_client import RawNewsItem
from app.sources.models import Source, SourceState
from app.providers.models import ProfileKind


class TestGenId:
    """Tests for _gen_id function."""

    def test_gen_id_with_prefix(self):
        """Generate ID with prefix."""
        result = _gen_id("test")

        assert result.startswith("test_")
        assert len(result) > 5

    def test_gen_id_unique(self):
        """Generated IDs are unique."""
        id1 = _gen_id("prefix")
        id2 = _gen_id("prefix")

        assert id1 != id2


class TestAssertSourceAvailable:
    """Tests for _assert_source_available function."""

    def test_source_available(self):
        """Valid source is returned."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        result = _assert_source_available(source, "src_1")

        assert result == source

    def test_source_none_raises(self):
        """None source raises error."""
        with pytest.raises(SourceNotFoundError):
            _assert_source_available(None, "src_1")

    def test_source_id_mismatch_raises(self):
        """ID mismatch raises error."""
        source = MagicMock(spec=Source)
        source.id = "src_2"

        with pytest.raises(SourceNotFoundError):
            _assert_source_available(source, "src_1")

    def test_disabled_perm_raises(self):
        """Disabled permanent raises error."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.DISABLED_PERM

        with pytest.raises(SourceNotEligibleError):
            _assert_source_available(source, "src_1")

    def test_disabled_temp_raises(self):
        """Disabled temp raises error."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.DISABLED_TEMP

        with pytest.raises(SourceNotEligibleError):
            _assert_source_available(source, "src_1")


class TestBuildNewsdataProfile:
    """Tests for _build_newsdata_profile function."""

    def test_build_profile(self):
        """Build newsdata profile."""
        result = _build_newsdata_profile()

        assert result.id == "profile_newsdata_br"
        assert result.provider_id == "newsdata"
        assert result.kind == ProfileKind.NEWS
        assert result.country == "br"
        assert result.language == "pt"
        assert result.enabled is True


class TestNewsdataHash:
    """Tests for _newsdata_hash function."""

    def test_hash_entry(self):
        """Hash entry produces consistent hash."""
        entry = {
            "id": "123",
            "title": "Test Title",
            "link": "https://example.com",
            "pubDate": "2024-01-01",
            "source_id": "source",
            "category": ["news"],
            "description": "Description",
        }

        result = _newsdata_hash(entry)

        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_consistent(self):
        """Same entry produces same hash."""
        entry = {"id": "1", "title": "Test"}

        hash1 = _newsdata_hash(entry)
        hash2 = _newsdata_hash(entry)

        assert hash1 == hash2

    def test_hash_handles_missing_fields(self):
        """Handles missing fields."""
        entry = {}

        result = _newsdata_hash(entry)

        assert isinstance(result, str)


class TestDedupNewsdataItems:
    """Tests for _dedup_newsdata_items function."""

    def test_dedup_empty(self):
        """Dedup empty list."""
        result, duplicates = _dedup_newsdata_items([])

        assert result == []
        assert duplicates == 0

    def test_dedup_single_item(self):
        """Dedup single item."""
        item = RawNewsItem(
            external_id="1",
            title="Title",
            url="https://example.com",
            published_at="2024-01-01",
            language="pt",
            country="BR",
            categories=["news"],
            source_name="Source",
            summary="Summary",
            payload={},
        )

        result, duplicates = _dedup_newsdata_items([item])

        assert len(result) == 1
        assert duplicates == 0
        assert "hash" in result[0]

    def test_dedup_removes_duplicates(self):
        """Removes duplicate items."""
        item = RawNewsItem(
            external_id="1",
            title="Title",
            url="https://example.com",
            published_at="2024-01-01",
            language="pt",
            country="BR",
            categories=[],
            source_name="Source",
            summary="",
            payload={},
        )

        result, duplicates = _dedup_newsdata_items([item, item])

        assert len(result) == 1
        assert duplicates == 1


class TestEnsureConfigAllowsTrigger:
    """Tests for _ensure_config_allows_trigger function."""

    def test_disabled_config_raises(self):
        """Disabled config raises."""
        config = MagicMock(spec=IngestionConfig)
        config.enabled = False

        with pytest.raises(ConfigDisabledError):
            _ensure_config_allows_trigger(config, IngestionTrigger.MANUAL)

    def test_manual_mode_with_auto_trigger_raises(self):
        """Manual mode with auto trigger raises."""
        config = MagicMock(spec=IngestionConfig)
        config.enabled = True
        config.mode = IngestionMode.MANUAL_ONLY

        with pytest.raises(ModeIncompatibleError):
            _ensure_config_allows_trigger(config, IngestionTrigger.AUTOMATIC)

    def test_auto_mode_with_auto_trigger_ok(self):
        """Auto mode with auto trigger is ok."""
        config = MagicMock(spec=IngestionConfig)
        config.enabled = True
        config.mode = IngestionMode.AUTOMATIC

        # Should not raise
        _ensure_config_allows_trigger(config, IngestionTrigger.AUTOMATIC)

    def test_manual_trigger_always_ok(self):
        """Manual trigger is always ok."""
        config = MagicMock(spec=IngestionConfig)
        config.enabled = True
        config.mode = IngestionMode.MANUAL_ONLY

        # Should not raise
        _ensure_config_allows_trigger(config, IngestionTrigger.MANUAL)


class TestCreateDefaultConfig:
    """Tests for _create_default_config function."""

    def test_create_config(self):
        """Create default config."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.refresh_interval = 30

        result = _create_default_config(source, IngestionMode.AUTOMATIC, True, "admin")

        assert result.source_id == "src_1"
        assert result.enabled is True
        assert result.mode == IngestionMode.AUTOMATIC
        assert result.max_attempts == 3

    def test_create_config_no_refresh_interval(self):
        """Create config without refresh interval."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.refresh_interval = None

        result = _create_default_config(source, IngestionMode.MANUAL_ONLY, False, "system")

        assert result.source_id == "src_1"
        assert result.enabled is False


class TestGetOrCreateConfig:
    """Tests for _get_or_create_config function."""

    def test_returns_existing(self):
        """Returns existing config."""
        source = MagicMock(spec=Source)
        source.id = "src_1"

        repo = MagicMock()
        existing_config = MagicMock(spec=IngestionConfig)
        repo.get_config.return_value = existing_config

        result = _get_or_create_config(repo, source)

        assert result == existing_config

    def test_creates_new_when_not_exists(self):
        """Creates new config when none exists."""
        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.refresh_interval = 60

        repo = MagicMock()
        repo.get_config.return_value = None
        repo.save_config.return_value = MagicMock(spec=IngestionConfig)

        result = _get_or_create_config(repo, source)

        repo.save_config.assert_called_once()


class TestLogRunEvent:
    """Tests for _log_run_event function."""

    def test_log_event(self):
        """Log run event."""
        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"
        run.status = IngestionStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        run.finished_at = None

        # Should not raise
        _log_run_event(run, "test_event", {"key": "value"})

    def test_log_event_with_finished_at(self):
        """Log event with finished_at."""
        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"
        run.status = IngestionStatus.SUCCESS
        run.started_at = datetime.now(timezone.utc)
        run.finished_at = datetime.now(timezone.utc)

        _log_run_event(run, "completed")


class TestRunIngestionInline:
    """Tests for _run_ingestion_inline function."""

    def test_unsupported_format_returns_zero(self):
        """Unsupported format returns 0."""
        repo = MagicMock()
        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"

        source = MagicMock(spec=Source)
        source.format = "json"  # Not RSS
        source.endpoint = "https://example.com"

        items, ref = _run_ingestion_inline(repo, run, source)

        assert items == 0
        assert ref is None

    def test_rss_format_fetches(self):
        """RSS format fetches and parses."""
        repo = MagicMock()
        repo.save_raw_payload.return_value = "payload_ref_123"

        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"

        source = MagicMock(spec=Source)
        source.format = "rss"
        source.endpoint = "https://example.com/feed"

        with patch("app.ingestion.services._fetch_rss_feed") as mock_fetch:
            with patch("app.ingestion.services._parse_rss_feed") as mock_parse:
                mock_fetch.return_value = b"<rss></rss>"
                mock_parse.return_value = [{"item": 1}, {"item": 2}]

                items, ref = _run_ingestion_inline(repo, run, source)

        assert items == 2
        assert ref == "payload_ref_123"


class TestMarkRunSuccess:
    """Tests for _mark_run_success function."""

    def test_mark_success(self):
        """Mark run as success."""
        repo = MagicMock()

        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"
        run.config_id = "cfg_1"
        run.status = IngestionStatus.RUNNING

        with patch("app.ingestion.services.state_machine") as mock_sm:
            with patch("app.ingestion.services.observability") as mock_obs:
                result = _mark_run_success(repo, run, items_processed=10, payload_ref="ref")

        mock_sm.apply_event.assert_called_once()
        repo.update_run.assert_called_once()
        repo.set_last_run.assert_called_once()
        mock_obs.log_run_end.assert_called_once()


class TestMarkRunFail:
    """Tests for _mark_run_fail function."""

    def test_mark_fail(self):
        """Mark run as failed."""
        repo = MagicMock()

        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"
        run.config_id = "cfg_1"
        run.status = IngestionStatus.RUNNING

        with patch("app.ingestion.services.state_machine") as mock_sm:
            with patch("app.ingestion.services.observability") as mock_obs:
                result = _mark_run_fail(
                    repo,
                    run,
                    error_code="test_error",
                    error_message="Error message",
                )

        mock_sm.apply_event.assert_called_once()
        repo.update_run.assert_called_once()


class TestStartIngestionRun:
    """Tests for start_ingestion_run function."""

    def test_start_run(self):
        """Start ingestion run."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 0

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.refresh_interval = 60

        config = MagicMock()
        config.id = "cfg_1"
        config.source_id = "src_1"
        config.source_state = SourceState.ACTIVE
        config.enabled = True
        config.mode = IngestionMode.AUTOMATIC
        config.interval_minutes = 60
        config.max_attempts = 3
        config.timeout_seconds = 60
        config.created_by = "test"

        repo.get_config.return_value = config

        with patch("app.ingestion.services.observability") as mock_obs:
            result = start_ingestion_run(
                "src_1",
                trigger=IngestionTrigger.MANUAL,
                repo=repo,
                source_fetcher=lambda x: source,
            )

        assert isinstance(result, IngestionRun)
        repo.insert_run.assert_called_once()

    def test_start_run_in_progress_raises(self):
        """Start run when another is in progress raises."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 1

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        config = MagicMock()
        config.enabled = True
        config.mode = IngestionMode.AUTOMATIC

        repo.get_config.return_value = config

        with pytest.raises(RunInProgressError):
            start_ingestion_run(
                "src_1",
                repo=repo,
                source_fetcher=lambda x: source,
            )


class TestCompleteIngestionRun:
    """Tests for complete_ingestion_run function."""

    def test_complete_run(self):
        """Complete ingestion run."""
        repo = MagicMock()

        run = MagicMock(spec=IngestionRun)
        run.id = "run_1"
        run.source_id = "src_1"
        run.status = IngestionStatus.RUNNING

        config = MagicMock(spec=IngestionConfig)
        config.id = "cfg_1"

        repo.get_run.return_value = run
        repo.get_config.return_value = config

        with patch("app.ingestion.services.state_machine") as mock_sm:
            with patch("app.ingestion.services.observability") as mock_obs:
                with patch("app.ingestion.services.validate_run_invariants"):
                    result = complete_ingestion_run(
                        "run_1",
                        items_processed=10,
                        payload_ref="ref",
                        repo=repo,
                    )

        assert result == run
        repo.update_run.assert_called_once()

    def test_complete_run_not_found_raises(self):
        """Complete non-existent run raises."""
        repo = MagicMock()
        repo.get_run.return_value = None

        with pytest.raises(RunNotFoundError):
            complete_ingestion_run("run_1", items_processed=0, payload_ref="", repo=repo)

    def test_complete_run_no_config_raises(self):
        """Complete run with no config raises."""
        repo = MagicMock()

        run = MagicMock(spec=IngestionRun)
        run.source_id = "src_1"
        run.status = IngestionStatus.RUNNING

        repo.get_run.return_value = run
        repo.get_config.return_value = None

        with pytest.raises(ConfigNotFoundError):
            complete_ingestion_run("run_1", items_processed=0, payload_ref="", repo=repo)

    def test_complete_run_not_running_raises(self):
        """Complete run not in RUNNING raises."""
        repo = MagicMock()

        run = MagicMock(spec=IngestionRun)
        run.source_id = "src_1"
        run.status = IngestionStatus.SUCCESS

        config = MagicMock(spec=IngestionConfig)

        repo.get_run.return_value = run
        repo.get_config.return_value = config

        with pytest.raises(InvalidTransitionError):
            complete_ingestion_run("run_1", items_processed=0, payload_ref="", repo=repo)


class TestFailIngestionRun:
    """Tests for fail_ingestion_run function."""

    def test_fail_run(self):
        """Fail ingestion run."""
        repo = MagicMock()

        run = MagicMock()
        run.id = "run_1"
        run.source_id = "src_1"
        run.status = IngestionStatus.RUNNING

        config = MagicMock()
        config.id = "cfg_1"

        repo.get_run.return_value = run
        repo.get_config.return_value = config

        with patch("app.ingestion.services.state_machine") as mock_sm:
            with patch("app.ingestion.services.observability") as mock_obs:
                with patch("app.ingestion.services.validate_run_invariants"):
                    result = fail_ingestion_run(
                        "run_1",
                        error_code="error",
                        error_message="Failed",
                        repo=repo,
                    )

        assert result == run

    def test_fail_run_partial(self):
        """Fail run with partial flag."""
        repo = MagicMock()

        run = MagicMock()
        run.id = "run_1"
        run.source_id = "src_1"
        run.status = IngestionStatus.RUNNING

        config = MagicMock()
        config.id = "cfg_1"

        repo.get_run.return_value = run
        repo.get_config.return_value = config

        with patch("app.ingestion.services.state_machine") as mock_sm:
            with patch("app.ingestion.services.observability") as mock_obs:
                with patch("app.ingestion.services.validate_run_invariants"):
                    result = fail_ingestion_run(
                        "run_1",
                        error_code="partial_error",
                        error_message="Partial fail",
                        partial=True,
                        repo=repo,
                    )

        assert result == run


class TestReprocessRun:
    """Tests for reprocess_run function."""

    def test_reprocess_run(self):
        """Reprocess existing run."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 0

        previous_run = MagicMock()
        previous_run.id = "run_1"
        previous_run.source_id = "src_1"

        config = MagicMock()
        config.id = "cfg_1"
        config.source_id = "src_1"
        config.source_state = SourceState.ACTIVE
        config.enabled = True
        config.mode = IngestionMode.MANUAL_ONLY
        config.interval_minutes = 60
        config.max_attempts = 3
        config.timeout_seconds = 60
        config.created_by = "test"

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        repo.get_run.return_value = previous_run
        repo.get_config.return_value = config

        with patch("app.ingestion.services.observability") as mock_obs:
            result = reprocess_run(
                "run_1",
                repo=repo,
                source_fetcher=lambda x: source,
            )

        assert isinstance(result, IngestionRun)
        assert result.trigger == IngestionTrigger.REPROCESS

    def test_reprocess_run_not_found_raises(self):
        """Reprocess non-existent run raises."""
        repo = MagicMock()
        repo.get_run.return_value = None

        with pytest.raises(RunNotFoundError):
            reprocess_run("run_1", repo=repo)


class TestToggleIngestionMode:
    """Tests for toggle_ingestion_mode function."""

    def test_toggle_mode_existing_config(self):
        """Toggle mode on existing config."""
        repo = MagicMock()

        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        config = MagicMock(spec=IngestionConfig)
        config.mode = IngestionMode.MANUAL_ONLY
        config.enabled = True

        repo.get_config.return_value = config
        repo.save_config.return_value = config

        result = toggle_ingestion_mode(
            "src_1",
            new_mode=IngestionMode.AUTOMATIC,
            enabled=True,
            updated_by="admin",
            repo=repo,
            source_fetcher=lambda x: source,
        )

        assert config.mode == IngestionMode.AUTOMATIC
        repo.save_config.assert_called_once()

    def test_toggle_mode_creates_config(self):
        """Toggle mode creates config when not exists."""
        repo = MagicMock()

        source = MagicMock(spec=Source)
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.refresh_interval = 60

        repo.get_config.return_value = None

        result = toggle_ingestion_mode(
            "src_1",
            new_mode=IngestionMode.AUTOMATIC,
            enabled=True,
            updated_by="admin",
            repo=repo,
            source_fetcher=lambda x: source,
        )

        repo.save_config.assert_called_once()


class TestRunNewsdataIngestion:
    """Tests for run_newsdata_ingestion function."""

    def test_rate_limit_exceeded_raises(self):
        """Rate limit exceeded raises."""
        repo = MagicMock()
        now = datetime.now(timezone.utc)

        # 3 recent runs
        repo.list_runs_by_source_between.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        with pytest.raises(RunInProgressError, match="Limite de 3 runs/min"):
            run_newsdata_ingestion(repo=repo)

    def test_daily_quota_exceeded_raises(self):
        """Daily quota exceeded raises."""
        repo = MagicMock()

        # No recent runs
        repo.list_runs_by_source_between.side_effect = [
            [],  # Recent runs
            [MagicMock(meta={"attempts": list(range(1001))})]  # Daily runs
        ]

        with pytest.raises(RunInProgressError, match="Quota diária"):
            run_newsdata_ingestion(repo=repo)

    def test_newsdata_run_success(self):
        """Run newsdata ingestion successfully."""
        repo = MagicMock()

        # No rate limit issues
        repo.list_runs_by_source_between.side_effect = [
            [],  # Recent runs
            [MagicMock(meta={"attempts": []})]  # Daily runs with no attempts
        ]
        repo.get_config.return_value = None  # Will create new config
        repo.save_raw_payload.return_value = "payload_ref_123"

        with patch.dict(os.environ, {"NEWSDATA_API_KEY": "test-api-key"}):
            with patch("app.ingestion.services.NewsProviderClient") as mock_client_cls:
                with patch("app.ingestion.services.observability"):
                    with patch("app.ingestion.services.newsdata_ingest"):
                        mock_client = MagicMock()
                        mock_client.fetch.return_value = [
                            RawNewsItem(
                                external_id="1",
                                title="Test",
                                url="https://example.com",
                                published_at="2024-01-01",
                                language="pt",
                                country="BR",
                                categories=["news"],
                                source_name="Source",
                                summary="",
                                payload={},
                            )
                        ]
                        mock_client_cls.return_value = mock_client

                        result = run_newsdata_ingestion(
                            repo=repo,
                            size=5,
                            throttle_seconds=0,
                            max_attempts=1,
                            domains_override=["example.com"],
                        )

        assert isinstance(result, IngestionRun)
        assert result.status == IngestionStatus.SUCCESS
        repo.insert_run.assert_called_once()

    def test_newsdata_run_fetch_exception(self):
        """Run newsdata ingestion with fetch exception."""
        repo = MagicMock()

        # No rate limit issues
        repo.list_runs_by_source_between.side_effect = [
            [],  # Recent runs
            []  # Daily runs
        ]
        repo.get_config.return_value = None  # Will create new config

        with patch.dict(os.environ, {"NEWSDATA_API_KEY": "test-api-key"}):
            with patch("app.ingestion.services.NewsProviderClient") as mock_client_cls:
                with patch("app.ingestion.services.observability"):
                    with patch("app.ingestion.services.newsdata_ingest"):
                        mock_client = MagicMock()
                        mock_client.fetch.side_effect = Exception("Network error")
                        mock_client_cls.return_value = mock_client

                        with pytest.raises(Exception, match="Network error"):
                            run_newsdata_ingestion(
                                repo=repo,
                                domains_override=["example.com"],
                            )

            # Run should have been marked as failed
            repo.update_run.assert_called()


class TestStartIngestionRunInline:
    """Tests for start_ingestion_run with execute_inline."""

    def test_start_run_inline_success(self):
        """Start run with inline execution success."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 0

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.format = "rss"
        source.endpoint = "https://example.com/feed"
        source.refresh_interval = 60

        config = MagicMock()
        config.id = "cfg_1"
        config.source_id = "src_1"
        config.source_state = SourceState.ACTIVE
        config.enabled = True
        config.mode = IngestionMode.AUTOMATIC
        config.interval_minutes = 60
        config.max_attempts = 3
        config.timeout_seconds = 60
        config.created_by = "test"

        repo.get_config.return_value = config
        repo.save_raw_payload.return_value = "payload_ref"

        with patch("app.ingestion.services.observability"):
            with patch("app.ingestion.services._fetch_rss_feed", return_value=b"<rss></rss>"):
                with patch("app.ingestion.services._parse_rss_feed", return_value=[{"item": 1}]):
                    with patch("app.ingestion.services.state_machine"):
                        result = start_ingestion_run(
                            "src_1",
                            trigger=IngestionTrigger.MANUAL,
                            repo=repo,
                            source_fetcher=lambda x: source,
                            execute_inline=True,
                        )

        assert isinstance(result, IngestionRun)
        repo.insert_run.assert_called_once()

    def test_start_run_inline_failure(self):
        """Start run with inline execution failure."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 0

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE
        source.format = "rss"
        source.endpoint = "https://example.com/feed"
        source.refresh_interval = 60

        config = MagicMock()
        config.id = "cfg_1"
        config.source_id = "src_1"
        config.source_state = SourceState.ACTIVE
        config.enabled = True
        config.mode = IngestionMode.AUTOMATIC
        config.interval_minutes = 60
        config.max_attempts = 3
        config.timeout_seconds = 60
        config.created_by = "test"

        repo.get_config.return_value = config

        with patch("app.ingestion.services.observability"):
            with patch("app.ingestion.services._fetch_rss_feed", side_effect=Exception("Fetch failed")):
                with patch("app.ingestion.services.state_machine"):
                    with pytest.raises(Exception, match="Fetch failed"):
                        start_ingestion_run(
                            "src_1",
                            trigger=IngestionTrigger.MANUAL,
                            repo=repo,
                            source_fetcher=lambda x: source,
                            execute_inline=True,
                        )


class TestFailIngestionRunErrors:
    """Tests for fail_ingestion_run error cases."""

    def test_fail_run_not_found(self):
        """Fail run when not found raises."""
        repo = MagicMock()
        repo.get_run.return_value = None

        with pytest.raises(RunNotFoundError):
            fail_ingestion_run(
                "run_missing",
                error_code="error",
                error_message="Fail",
                repo=repo,
            )

    def test_fail_run_no_config(self):
        """Fail run when no config exists raises."""
        repo = MagicMock()

        run = MagicMock()
        run.source_id = "src_1"

        repo.get_run.return_value = run
        repo.get_config.return_value = None

        with pytest.raises(ConfigNotFoundError):
            fail_ingestion_run(
                "run_1",
                error_code="error",
                error_message="Fail",
                repo=repo,
            )


class TestReprocessRunErrors:
    """Tests for reprocess_run error cases."""

    def test_reprocess_run_no_config(self):
        """Reprocess run when no config exists raises."""
        repo = MagicMock()

        previous_run = MagicMock()
        previous_run.source_id = "src_1"

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        repo.get_run.return_value = previous_run
        repo.get_config.return_value = None

        with pytest.raises(ConfigNotFoundError):
            reprocess_run(
                "run_1",
                repo=repo,
                source_fetcher=lambda x: source,
            )

    def test_reprocess_run_in_progress(self):
        """Reprocess run when another is in progress raises."""
        repo = MagicMock()
        repo.count_running_for_source.return_value = 1

        previous_run = MagicMock()
        previous_run.source_id = "src_1"

        source = MagicMock()
        source.id = "src_1"
        source.state = SourceState.ACTIVE

        config = MagicMock()
        config.enabled = True
        config.mode = IngestionMode.MANUAL_ONLY

        repo.get_run.return_value = previous_run
        repo.get_config.return_value = config

        with pytest.raises(RunInProgressError):
            reprocess_run(
                "run_1",
                repo=repo,
                source_fetcher=lambda x: source,
            )
