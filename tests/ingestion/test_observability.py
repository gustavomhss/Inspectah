from datetime import datetime, timedelta, timezone

from app.ingestion import observability
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
)
from app.ingestion.repository import IngestionRepository
from app.ingestion.services import fail_ingestion_run, start_ingestion_run
from app.sources.models import SourceState
from metrics import ingestion_s22 as metrics


def _cfg(repo: IngestionRepository, source_id: str = "src_obs") -> IngestionConfig:
    cfg = IngestionConfig.create(
        id=f"ingcfg_{source_id}",
        source_id=source_id,
        source_state=SourceState.ACTIVE,
        enabled=True,
        mode=IngestionMode.AUTOMATIC,
        interval_minutes=60,
        max_attempts=3,
        timeout_seconds=60,
        created_by="tester",
    )
    repo.save_config(cfg)
    return cfg


def _source_fetcher(source_id: str):
    from app.sources.models import Source

    src = Source.create(
        id=source_id,
        slug=source_id,
        name="Fonte Obs",
        description="",
        type="news_rss",
        category="official",
        themes=[],
        info_types=["news"],
        refresh_interval=60,
        protocol="https",
        format="rss",
        endpoint="https://example.com/rss",
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
        created_by="tester",
    )
    src.state = SourceState.ACTIVE
    return src


def test_success_updates_metrics(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo)
    run = start_ingestion_run(cfg.source_id, repo=repo, source_fetcher=_source_fetcher)
    run.finished_at = datetime.now(timezone.utc)
    run.status = IngestionStatus.SUCCESS
    run.items_processed = 5
    observability.log_run_end(run)
    assert metrics.runs_total[(cfg.source_id, "RUNNING")] >= 1
    assert metrics.runs_total[(cfg.source_id, "SUCCESS")] >= 1
    assert cfg.source_id in metrics.last_success_ts


def test_failure_updates_error_metrics(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo)
    run = start_ingestion_run(cfg.source_id, repo=repo, source_fetcher=_source_fetcher)
    fail_ingestion_run(run.id, error_code="network_error", error_message="fail", repo=repo)
    assert metrics.runs_fail_total[cfg.source_id] >= 1
    assert cfg.source_id in metrics.last_failure_ts


def test_sources_without_recent_runs(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo, source_id="src_stale")
    # create stale run
    run = IngestionRun.create(
        id="run_old",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    run.status = IngestionStatus.SUCCESS
    run.finished_at = run.started_at + timedelta(minutes=1)
    repo.insert_run(run)
    repo.update_run(run)
    stale = observability.sources_without_recent_runs(repo, threshold_minutes=60)
    assert "src_stale" in stale


# =============================================================================
# S40-BE-020: P1 Latency Metrics Tests
# =============================================================================


class TestP1PilotDomains:
    """Tests for P1 pilot domain detection."""

    def test_is_pilot_domain_saude(self):
        """saude is a pilot domain."""
        assert observability.is_pilot_domain("saude") is True

    def test_is_pilot_domain_politica(self):
        """politica is a pilot domain."""
        assert observability.is_pilot_domain("politica") is True

    def test_is_pilot_domain_case_insensitive(self):
        """Domain check is case insensitive."""
        assert observability.is_pilot_domain("SAUDE") is True
        assert observability.is_pilot_domain("Politica") is True

    def test_is_not_pilot_domain(self):
        """Non-pilot domains return False."""
        assert observability.is_pilot_domain("economia") is False
        assert observability.is_pilot_domain("esporte") is False
        assert observability.is_pilot_domain("other") is False


class TestP1LatencyTracking:
    """Tests for P1 latency mark_collected and mark_ready."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_mark_collected_pilot_domain(self):
        """mark_collected stores timestamp for pilot domain."""
        observability.mark_collected("doc1", "saude", "source1")
        assert len(observability._collected_timestamps) == 1
        assert "saude:source1:doc1" in observability._collected_timestamps

    def test_mark_collected_non_pilot_domain(self):
        """mark_collected ignores non-pilot domains."""
        observability.mark_collected("doc1", "economia", "source1")
        assert len(observability._collected_timestamps) == 0

    def test_mark_ready_returns_latency(self):
        """mark_ready returns latency for tracked document."""
        import time

        observability.mark_collected("doc2", "politica", "source2")
        time.sleep(0.01)  # 10ms
        latency = observability.mark_ready("doc2", "politica", "source2")
        assert latency is not None
        assert latency > 0.01  # At least 10ms

    def test_mark_ready_removes_timestamp(self):
        """mark_ready removes the collected timestamp."""
        observability.mark_collected("doc3", "saude", "source3")
        observability.mark_ready("doc3", "saude", "source3")
        assert len(observability._collected_timestamps) == 0

    def test_mark_ready_not_tracked(self):
        """mark_ready returns None for untracked document."""
        latency = observability.mark_ready("unknown", "saude", "source1")
        assert latency is None

    def test_mark_ready_non_pilot_domain(self):
        """mark_ready returns None for non-pilot domain."""
        observability.mark_collected("doc4", "saude", "source4")
        # Try to mark ready with wrong domain
        latency = observability.mark_ready("doc4", "economia", "source4")
        assert latency is None

    def test_mark_ready_custom_timestamp(self):
        """mark_ready can use custom ready_at timestamp."""
        import time

        collected_time = time.time()
        observability._collected_timestamps["saude:source5:doc5"] = collected_time
        ready_time = collected_time + 0.5  # 500ms later
        latency = observability.mark_ready("doc5", "saude", "source5", ready_at=ready_time)
        assert latency is not None
        assert abs(latency - 0.5) < 0.01


class TestP1PipelineComplete:
    """Tests for P1 end-to-end latency tracking."""

    def test_mark_pipeline_complete_pilot_domain(self):
        """mark_pipeline_complete records latency for pilot domain."""
        import time

        collected_at = time.time() - 1.0  # 1 second ago
        latency = observability.mark_pipeline_complete(
            "doc1", "saude", "source1", collected_at
        )
        assert latency is not None
        assert latency >= 1.0

    def test_mark_pipeline_complete_non_pilot_domain(self):
        """mark_pipeline_complete returns None for non-pilot domain."""
        import time

        collected_at = time.time() - 1.0
        latency = observability.mark_pipeline_complete(
            "doc1", "economia", "source1", collected_at
        )
        assert latency is None

    def test_mark_pipeline_complete_custom_completed_at(self):
        """mark_pipeline_complete can use custom completed_at timestamp."""
        collected_at = 1000.0
        completed_at = 1002.5  # 2.5 seconds later
        latency = observability.mark_pipeline_complete(
            "doc2", "politica", "source2", collected_at, completed_at
        )
        assert latency is not None
        assert abs(latency - 2.5) < 0.01


class TestP1LatencyStats:
    """Tests for P1 latency statistics."""

    def test_get_p1_latency_stats_pilot_domain(self):
        """get_p1_latency_stats returns stats for pilot domain."""
        stats = observability.get_p1_latency_stats("saude", "test_source")
        assert stats["domain"] == "saude"
        assert stats["source"] == "test_source"
        assert "collected_to_ready" in stats
        assert "end_to_end" in stats
        assert "pending_documents" in stats

    def test_get_p1_latency_stats_non_pilot_domain(self):
        """get_p1_latency_stats returns error for non-pilot domain."""
        stats = observability.get_p1_latency_stats("economia", "source1")
        assert "error" in stats


class TestClearStaleTimestamps:
    """Tests for clearing stale timestamps."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_clear_stale_timestamps(self):
        """clear_stale_timestamps removes old entries."""
        import time

        old_time = time.time() - 7200  # 2 hours ago
        observability._collected_timestamps["saude:src:old_doc"] = old_time
        observability._collected_timestamps["saude:src:new_doc"] = time.time()

        cleared = observability.clear_stale_timestamps(max_age_seconds=3600)
        assert cleared == 1
        assert "saude:src:old_doc" not in observability._collected_timestamps
        assert "saude:src:new_doc" in observability._collected_timestamps

    def test_clear_stale_timestamps_none_stale(self):
        """clear_stale_timestamps returns 0 when nothing stale."""
        import time

        observability._collected_timestamps["saude:src:recent"] = time.time()
        cleared = observability.clear_stale_timestamps(max_age_seconds=3600)
        assert cleared == 0


class TestGetPendingCount:
    """Tests for pending document count."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_get_pending_count_empty(self):
        """get_pending_count returns 0 when empty."""
        assert observability.get_pending_count() == 0

    def test_get_pending_count_with_entries(self):
        """get_pending_count returns correct count."""
        import time

        with observability._timestamps_lock:
            observability._collected_timestamps["saude:src:doc1"] = time.time()
            observability._collected_timestamps["politica:src:doc2"] = time.time()
        assert observability.get_pending_count() == 2


class TestGetPendingDocuments:
    """Tests for get_pending_documents function."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_get_pending_documents_empty(self):
        """get_pending_documents returns empty list when no documents."""
        result = observability.get_pending_documents()
        assert result == []

    def test_get_pending_documents_all(self):
        """get_pending_documents returns all pending documents."""
        import time

        now = time.time()
        with observability._timestamps_lock:
            observability._collected_timestamps["saude:src1:doc1"] = now - 10
            observability._collected_timestamps["politica:src2:doc2"] = now - 5

        result = observability.get_pending_documents()

        assert len(result) == 2
        # Oldest first (saude doc1 is older)
        assert result[0][0] == "saude"
        assert result[0][2] == "doc1"

    def test_get_pending_documents_filtered(self):
        """get_pending_documents can filter by domain."""
        import time

        now = time.time()
        with observability._timestamps_lock:
            observability._collected_timestamps["saude:src1:doc1"] = now
            observability._collected_timestamps["politica:src2:doc2"] = now

        result = observability.get_pending_documents(domain="saude")

        assert len(result) == 1
        assert result[0][0] == "saude"


class TestGetP1Summary:
    """Tests for get_p1_summary function."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_get_p1_summary_empty(self):
        """get_p1_summary returns summary with no pending."""
        result = observability.get_p1_summary()

        assert "pilot_domains" in result
        assert "saude" in result["pilot_domains"]
        assert "politica" in result["pilot_domains"]
        assert result["pending_documents"] == 0
        assert result["oldest_pending_seconds"] is None
        assert "histograms" in result

    def test_get_p1_summary_with_pending(self):
        """get_p1_summary returns summary with pending documents."""
        import time

        now = time.time()
        with observability._timestamps_lock:
            observability._collected_timestamps["saude:src:doc1"] = now - 30

        result = observability.get_p1_summary()

        assert result["pending_documents"] == 1
        assert result["oldest_pending_seconds"] >= 30


class TestThreadSafety:
    """Tests for thread safety of latency tracking."""

    def setup_method(self):
        """Clear timestamps before each test."""
        with observability._timestamps_lock:
            observability._collected_timestamps.clear()

    def test_concurrent_mark_collected(self):
        """mark_collected is thread-safe."""
        import threading

        def mark_docs():
            for i in range(100):
                observability.mark_collected(f"doc{i}", "saude", "src")

        threads = [threading.Thread(target=mark_docs) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 100 unique docs (not 500 - same doc IDs from different threads)
        assert observability.get_pending_count() == 100

    def test_concurrent_mark_collected_ready(self):
        """mark_collected and mark_ready are thread-safe together."""
        import threading
        import time

        # First mark some docs as collected
        for i in range(50):
            observability.mark_collected(f"doc{i}", "saude", "src")

        time.sleep(0.01)  # Small delay

        def mark_ready():
            for i in range(50):
                observability.mark_ready(f"doc{i}", "saude", "src")

        threads = [threading.Thread(target=mark_ready) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All docs should be marked ready now
        assert observability.get_pending_count() == 0
