"""
Tests for cases/loader — S37

Tests for case loading functions.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.cases.loader import (
    _load_yaml,
    _to_case,
    load_cases,
    load_case_by_id,
    load_collections,
    build_debunk_summary,
)
from app.cases.models import CaseDefinition, CaseClaim, CaseCollectionDefinition
from app.debunk.models import DebunkIssue, DebunkIssueStatus, DebunkIssueTarget


class TestLoadYaml:
    """Tests for _load_yaml function."""

    def test_load_yaml_basic(self, tmp_path):
        """Load basic YAML file."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\ncount: 42\n", encoding="utf-8")

        result = _load_yaml(yaml_file)

        assert result["key"] == "value"
        assert result["count"] == 42


class TestToCase:
    """Tests for _to_case function."""

    def test_to_case_minimal(self):
        """Convert minimal raw dict to CaseDefinition."""
        raw = {
            "case_id": "case_1",
            "title": "Test Case",
        }

        result = _to_case(raw)

        assert result.case_id == "case_1"
        assert result.title == "Test Case"
        assert result.summary == ""
        assert result.theme == "general"
        assert result.claims == []

    def test_to_case_with_claims(self):
        """Convert raw dict with claims."""
        raw = {
            "case_id": "case_2",
            "title": "Case with Claims",
            "claims": [
                {"claim_id": "claim_1", "description": "First claim"},
                {"claim_id": "claim_2", "truth_state": "verified"},
            ],
        }

        result = _to_case(raw)

        assert len(result.claims) == 2
        assert result.claims[0].claim_id == "claim_1"
        assert result.claims[0].description == "First claim"
        assert result.claims[1].truth_state == "verified"

    def test_to_case_full(self):
        """Convert full raw dict."""
        raw = {
            "case_id": "case_full",
            "title": "Full Case",
            "summary": "A comprehensive case",
            "theme": "politics",
            "tags": ["important", "verified"],
            "claims": [
                {
                    "claim_id": "claim_1",
                    "description": "Claim desc",
                    "truth_state": "unverified",
                    "debunk_target_id": "target_1",
                    "tags": ["tag1"],
                }
            ],
            "timeline": [{"date": "2024-01-01", "event": "Event 1"}],
            "sources": [{"id": "src_1", "url": "https://example.com"}],
            "metadata": {"author": "tester"},
        }

        result = _to_case(raw)

        assert result.case_id == "case_full"
        assert result.summary == "A comprehensive case"
        assert result.theme == "politics"
        assert result.tags == ["important", "verified"]
        assert result.claims[0].debunk_target_id == "target_1"
        assert len(result.timeline) == 1
        assert len(result.sources) == 1
        assert result.metadata["author"] == "tester"


class TestLoadCases:
    """Tests for load_cases function."""

    def test_load_cases_from_dir(self, tmp_path):
        """Load cases from directory."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)
        (cases_dir / "case_test1.yaml").write_text(
            "case_id: test1\ntitle: Test 1\n", encoding="utf-8"
        )
        (cases_dir / "case_test2.yaml").write_text(
            "case_id: test2\ntitle: Test 2\n", encoding="utf-8"
        )

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_cases()

        assert len(result) == 2


class TestLoadCaseById:
    """Tests for load_case_by_id function."""

    def test_load_case_by_id_direct_match(self, tmp_path):
        """Load case by direct filename match."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)
        (cases_dir / "case_direct.yaml").write_text(
            "case_id: direct\ntitle: Direct Match\n", encoding="utf-8"
        )

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_case_by_id("direct")

        assert result is not None
        assert result.case_id == "direct"
        assert result.title == "Direct Match"

    def test_load_case_by_id_search(self, tmp_path):
        """Load case by searching in files."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)
        (cases_dir / "case_other.yaml").write_text(
            "case_id: search_me\ntitle: Found by Search\n", encoding="utf-8"
        )

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_case_by_id("search_me")

        assert result is not None
        assert result.case_id == "search_me"

    def test_load_case_by_id_not_found(self, tmp_path):
        """Load case returns None when not found."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_case_by_id("nonexistent")

        assert result is None


class TestLoadCollections:
    """Tests for load_collections function."""

    def test_load_collections_file_not_exists(self, tmp_path):
        """Load collections returns empty when file doesn't exist."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_collections()

        assert result == []

    def test_load_collections_success(self, tmp_path):
        """Load collections from file."""
        cases_dir = tmp_path / "docs" / "cases"
        cases_dir.mkdir(parents=True)
        (cases_dir / "collections.yaml").write_text(
            """collections:
  - collection_id: col_1
    title: Collection 1
    description: First collection
    case_ids:
      - case_1
      - case_2
    tags:
      - featured
""",
            encoding="utf-8",
        )

        with patch("app.cases.loader.CASE_DIR", cases_dir):
            result = load_collections()

        assert len(result) == 1
        assert result[0].collection_id == "col_1"
        assert result[0].title == "Collection 1"
        assert len(result[0].case_ids) == 2


class TestBuildDebunkSummary:
    """Tests for build_debunk_summary function."""

    def test_build_debunk_summary_no_issues(self):
        """Build summary with no issues found."""
        repo = MagicMock()
        repo.find_open_issue_for_target.return_value = None

        case = CaseDefinition(
            case_id="case_1",
            title="Test",
            summary="",
            theme="general",
            tags=[],
            claims=[CaseClaim(claim_id="claim_1", description="", truth_state=None)],
            timeline=[],
            sources=[],
            metadata={},
        )

        result = build_debunk_summary(repo, case)

        assert result["total"] == 0
        assert result["open"] == 0
        assert result["resolved"] == 0

    def test_build_debunk_summary_with_open_issues(self):
        """Build summary with open issues."""
        repo = MagicMock()

        issue = MagicMock(spec=DebunkIssue)
        issue.id = "issue_1"
        issue.status = DebunkIssueStatus.OPEN

        repo.find_open_issue_for_target.return_value = issue

        case = CaseDefinition(
            case_id="case_1",
            title="Test",
            summary="",
            theme="general",
            tags=[],
            claims=[
                CaseClaim(claim_id="claim_1", description="", truth_state=None),
                CaseClaim(claim_id="claim_2", description="", truth_state=None),
            ],
            timeline=[],
            sources=[],
            metadata={},
        )

        result = build_debunk_summary(repo, case)

        assert result["total"] == 2
        assert result["open"] == 2
        assert result["resolved"] == 0

    def test_build_debunk_summary_with_resolved_issues(self):
        """Build summary with resolved issues."""
        repo = MagicMock()

        resolved_issue = MagicMock(spec=DebunkIssue)
        resolved_issue.id = "issue_resolved"
        resolved_issue.status = DebunkIssueStatus.RESOLVED

        repo.find_open_issue_for_target.return_value = resolved_issue

        case = CaseDefinition(
            case_id="case_1",
            title="Test",
            summary="",
            theme="general",
            tags=[],
            claims=[CaseClaim(claim_id="claim_1", description="", truth_state=None)],
            timeline=[],
            sources=[],
            metadata={},
        )

        result = build_debunk_summary(repo, case)

        assert result["total"] == 1
        assert result["open"] == 0
        assert result["resolved"] == 1

    def test_build_debunk_summary_uses_debunk_target_id(self):
        """Build summary uses debunk_target_id when available."""
        repo = MagicMock()
        repo.find_open_issue_for_target.return_value = None

        case = CaseDefinition(
            case_id="case_1",
            title="Test",
            summary="",
            theme="general",
            tags=[],
            claims=[
                CaseClaim(
                    claim_id="claim_1",
                    description="",
                    truth_state=None,
                    debunk_target_id="custom_target",
                )
            ],
            timeline=[],
            sources=[],
            metadata={},
        )

        build_debunk_summary(repo, case)

        repo.find_open_issue_for_target.assert_called_with(
            DebunkIssueTarget.CLAIM, "custom_target"
        )
