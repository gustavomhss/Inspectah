"""
Tests for Provider Runner — S37

Tests for profile runner and ingestion execution.
"""

import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, MagicMock, patch

from app.providers.runner import ProfileRunner, run_all
from app.providers.models import ProfileKind


class TestProfileRunner:
    """Tests for ProfileRunner class."""

    @pytest.fixture
    def mock_service(self):
        """Create mock provider service."""
        return MagicMock()

    @pytest.fixture
    def mock_run_store(self):
        """Create mock run store."""
        return MagicMock()

    @pytest.fixture
    def temp_evidence_dir(self):
        """Create temp evidence directory."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def runner(self, mock_service, mock_run_store, temp_evidence_dir):
        """Create runner with mocks."""
        return ProfileRunner(
            service=mock_service,
            run_store=mock_run_store,
            evidence_dir=temp_evidence_dir,
        )

    def test_init_default(self):
        """Initialize with defaults."""
        with patch("app.providers.runner.ProviderService"):
            with patch("app.providers.runner.RunStore"):
                with patch("app.providers.runner.ContentRepository"):
                    runner = ProfileRunner()

        assert runner.evidence_dir.exists()

    def test_init_with_dependencies(self, mock_service, mock_run_store, temp_evidence_dir):
        """Initialize with custom dependencies."""
        runner = ProfileRunner(
            service=mock_service,
            run_store=mock_run_store,
            evidence_dir=temp_evidence_dir,
        )

        assert runner.service == mock_service
        assert runner.run_store == mock_run_store
        assert runner.evidence_dir == temp_evidence_dir

    @pytest.mark.asyncio
    async def test_run_profile_not_found(self, runner, mock_service):
        """Run profile raises when not found."""
        mock_service.get_profile.return_value = None

        with pytest.raises(ValueError, match="Profile not found"):
            await runner.run_profile("unknown_profile")

    @pytest.mark.asyncio
    async def test_run_profile_news(self, runner, mock_service, mock_run_store):
        """Run profile for news type."""
        mock_profile = MagicMock()
        mock_profile.id = "profile_1"
        mock_profile.provider_id = "newsdata"
        mock_profile.kind = ProfileKind.NEWS
        mock_profile.slug = "news_br"

        mock_service.get_profile.return_value = mock_profile

        mock_items = [MagicMock() for _ in range(3)]
        for i, item in enumerate(mock_items):
            item.external_id = f"ext_{i}"
            item.title = f"Title {i}"
            item.url = f"https://example.com/{i}"
            item.published_at = "2024-01-01T00:00:00Z"
            item.language = "pt"
            item.country = "BR"
            item.categories = []
            item.source_name = "Source"
            item.summary = ""
            item.payload = {}

        with patch("app.providers.runner.NewsProviderClient") as MockClient:
            client_instance = MockClient.return_value
            client_instance.fetch = AsyncMock(return_value=mock_items)

            with patch("app.providers.runner.normalize_news") as mock_normalize:
                mock_normalize.return_value = [
                    {"content_id": f"c{i}", "provider_id": None, "profile_id": None}
                    for i in range(3)
                ]

                runner.content_repo = MagicMock()
                runner.content_repo.save_items.return_value = 3

                result = await runner.run_profile("profile_1")

        assert result.status == "success"
        assert result.items == 3
        mock_run_store.record.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_profile_social(self, runner, mock_service, mock_run_store):
        """Run profile for social type."""
        mock_profile = MagicMock()
        mock_profile.id = "profile_2"
        mock_profile.provider_id = "social"
        mock_profile.kind = ProfileKind.SOCIAL
        mock_profile.slug = "social_br"

        mock_service.get_profile.return_value = mock_profile

        mock_items = [MagicMock() for _ in range(2)]
        for i, item in enumerate(mock_items):
            item.external_id = f"social_{i}"
            item.text = f"Tweet {i}"
            item.url = f"https://twitter.com/{i}"
            item.published_at = "2024-01-01T00:00:00Z"
            item.author = "user"
            item.language = "pt"
            item.country = "BR"
            item.tags = []
            item.payload = {}

        with patch("app.providers.runner.SocialProviderClient") as MockClient:
            client_instance = MockClient.return_value
            client_instance.fetch = AsyncMock(return_value=mock_items)

            with patch("app.providers.runner.normalize_social") as mock_normalize:
                mock_normalize.return_value = [
                    {"content_id": f"s{i}", "provider_id": None, "profile_id": None}
                    for i in range(2)
                ]

                runner.content_repo = MagicMock()
                runner.content_repo.save_items.return_value = 2

                result = await runner.run_profile("profile_2")

        assert result.status == "success"
        assert result.items == 2

    @pytest.mark.asyncio
    async def test_run_profile_writes_evidence(self, runner, mock_service, mock_run_store, temp_evidence_dir):
        """Run profile writes evidence file."""
        mock_profile = MagicMock()
        mock_profile.id = "profile_1"
        mock_profile.provider_id = "newsdata"
        mock_profile.kind = ProfileKind.NEWS
        mock_profile.slug = "test_profile"

        mock_service.get_profile.return_value = mock_profile

        with patch("app.providers.runner.NewsProviderClient") as MockClient:
            client_instance = MockClient.return_value
            client_instance.fetch = AsyncMock(return_value=[])

            with patch("app.providers.runner.normalize_news") as mock_normalize:
                mock_normalize.return_value = [
                    {"content_id": "c1", "data": "test"}
                ]

                runner.content_repo = MagicMock()
                runner.content_repo.save_items.return_value = 1

                result = await runner.run_profile("profile_1")

        # Check evidence file was written
        assert result.evidence_path is not None
        evidence_path = Path(result.evidence_path)
        assert evidence_path.exists()

        # Read and verify content
        with evidence_path.open() as f:
            content = f.read()
            assert "content_id" in content

    @pytest.mark.asyncio
    async def test_enqueue_calls_run_profile(self, runner, mock_service, mock_run_store):
        """Enqueue calls run_profile asynchronously."""
        mock_profile = MagicMock()
        mock_profile.id = "profile_1"
        mock_profile.provider_id = "newsdata"
        mock_profile.kind = ProfileKind.NEWS
        mock_profile.slug = "test"

        mock_service.get_profile.return_value = mock_profile

        with patch("app.providers.runner.NewsProviderClient") as MockClient:
            client_instance = MockClient.return_value
            client_instance.fetch = AsyncMock(return_value=[])

            with patch("app.providers.runner.normalize_news") as mock_normalize:
                mock_normalize.return_value = []

                runner.content_repo = MagicMock()
                runner.content_repo.save_items.return_value = 0

                result = await runner.enqueue("profile_1", limit=5)

        assert result is not None
        assert result.profile_id == "profile_1"

    def test_as_dict(self, runner):
        """Convert run to dict."""
        from app.providers.run_store import ProfileRun

        run = ProfileRun(
            run_id="run_1",
            provider_id="provider_1",
            profile_id="profile_1",
            started_at="2024-01-01T00:00:00Z",
            finished_at="2024-01-01T00:01:00Z",
            status="success",
            items=10,
            persisted=10,
            calls=10,
            evidence_path="/path/to/evidence.jsonl",
            message=None,
        )

        result = runner.as_dict(run)

        assert isinstance(result, dict)
        assert result["run_id"] == "run_1"
        assert result["status"] == "success"
        assert result["items"] == 10


class TestRunAll:
    """Tests for run_all function."""

    @pytest.mark.asyncio
    async def test_run_all(self):
        """Run all profiles."""
        mock_profiles = [
            MagicMock(id="profile_1", provider_id="p1", kind=ProfileKind.NEWS, slug="p1"),
            MagicMock(id="profile_2", provider_id="p2", kind=ProfileKind.NEWS, slug="p2"),
        ]

        mock_run = MagicMock()
        mock_run.run_id = "run_1"
        mock_run.status = "success"

        with patch("app.providers.runner.ProfileRunner") as MockRunner:
            runner_instance = MockRunner.return_value
            runner_instance.service.list_profiles.return_value = mock_profiles
            runner_instance.enqueue = AsyncMock(return_value=mock_run)
            runner_instance.as_dict.return_value = {"run_id": "run_1"}

            results = await run_all(limit=5)

        assert len(results) == 2
        assert all(r["run_id"] == "run_1" for r in results)

    @pytest.mark.asyncio
    async def test_run_all_empty(self):
        """Run all with no profiles."""
        with patch("app.providers.runner.ProfileRunner") as MockRunner:
            runner_instance = MockRunner.return_value
            runner_instance.service.list_profiles.return_value = []

            results = await run_all()

        assert results == []
