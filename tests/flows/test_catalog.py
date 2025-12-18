"""
Tests for flows/catalog — S37

Tests for flow catalog loading and indexing.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import textwrap

from app.flows.catalog import (
    _load_yaml,
    _hash_text,
    load_catalog_entries,
    catalog_index_by_template,
    entry_for_template,
)


class TestLoadYaml:
    """Tests for _load_yaml function."""

    def test_load_yaml_with_yaml_module(self, tmp_path):
        """Load YAML file when yaml module is available."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("name: test\nversion: 1.0\n")

        result = _load_yaml(yaml_file)

        assert result["name"] == "test"
        assert result["version"] == 1.0

    def test_load_yaml_empty_file(self, tmp_path):
        """Load empty YAML file returns empty dict."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        result = _load_yaml(yaml_file)

        assert result == {}

    def test_load_yaml_with_comments(self, tmp_path):
        """Load YAML with comments."""
        yaml_file = tmp_path / "commented.yaml"
        yaml_file.write_text("# Comment\nkey: value\n")

        result = _load_yaml(yaml_file)

        assert result["key"] == "value"


class TestHashText:
    """Tests for _hash_text function."""

    def test_hash_text_returns_sha256(self):
        """Hash returns SHA256 hex digest."""
        result = _hash_text("test")

        assert len(result) == 64
        assert result == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    def test_hash_text_deterministic(self):
        """Same input produces same hash."""
        result1 = _hash_text("hello world")
        result2 = _hash_text("hello world")

        assert result1 == result2

    def test_hash_text_different_inputs(self):
        """Different inputs produce different hashes."""
        result1 = _hash_text("hello")
        result2 = _hash_text("world")

        assert result1 != result2


class TestLoadCatalogEntries:
    """Tests for load_catalog_entries function."""

    def test_load_catalog_entries_nonexistent_dir(self):
        """Load from nonexistent directory returns empty list."""
        result = load_catalog_entries("/nonexistent/path")

        assert result == []

    def test_load_catalog_entries_empty_dir(self, tmp_path):
        """Load from empty directory returns empty list."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()

        result = load_catalog_entries(catalog_dir)

        assert result == []

    def test_load_catalog_entries_single_file(self, tmp_path):
        """Load single catalog entry."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "flow1.yaml"
        entry_file.write_text("flow_id: flow_1\nversion: 1.0\n")

        result = load_catalog_entries(catalog_dir)

        assert len(result) == 1
        assert result[0]["flow_id"] == "flow_1"
        assert "hash" in result[0]
        assert "signature" in result[0]
        assert "template_ref" in result[0]

    def test_load_catalog_entries_multiple_files(self, tmp_path):
        """Load multiple catalog entries in sorted order."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        (catalog_dir / "a_flow.yaml").write_text("flow_id: a\n")
        (catalog_dir / "b_flow.yaml").write_text("flow_id: b\n")
        (catalog_dir / "c_flow.yaml").write_text("flow_id: c\n")

        result = load_catalog_entries(catalog_dir)

        assert len(result) == 3
        assert result[0]["flow_id"] == "a"
        assert result[1]["flow_id"] == "b"
        assert result[2]["flow_id"] == "c"

    def test_load_catalog_entries_with_existing_hash(self, tmp_path):
        """Entry with existing hash uses that value."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "flow.yaml"
        entry_file.write_text("flow_id: flow_1\nhash: existing_hash\n")

        result = load_catalog_entries(catalog_dir)

        assert result[0]["hash"] == "existing_hash"

    def test_load_catalog_entries_with_existing_signature(self, tmp_path):
        """Entry with existing signature uses that value."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "flow.yaml"
        entry_file.write_text("flow_id: flow_1\nsignature: test_sig\n")

        result = load_catalog_entries(catalog_dir)

        assert result[0]["signature"] == "test_sig"

    def test_load_catalog_entries_template_ref_default(self, tmp_path):
        """Default template_ref based on filename."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "my_flow.yaml"
        entry_file.write_text("flow_id: flow_1\n")

        result = load_catalog_entries(catalog_dir)

        assert result[0]["template_ref"] == "config/flow_templates/my_flow.yaml"


class TestCatalogIndexByTemplate:
    """Tests for catalog_index_by_template function."""

    def test_catalog_index_empty(self, tmp_path):
        """Empty catalog returns empty index."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()

        result = catalog_index_by_template(catalog_dir)

        assert result == {}

    def test_catalog_index_single_entry(self, tmp_path):
        """Single entry indexed by template_ref."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "flow.yaml"
        entry_file.write_text("flow_id: flow_1\ntemplate_ref: templates/flow.yaml\n")

        result = catalog_index_by_template(catalog_dir)

        assert "templates/flow.yaml" in result
        assert result["templates/flow.yaml"]["flow_id"] == "flow_1"

    def test_catalog_index_version_comparison(self, tmp_path):
        """Higher version replaces lower version."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        (catalog_dir / "flow_v1.yaml").write_text(
            "flow_id: flow_1\ntemplate_ref: templates/flow.yaml\nversion: 1.0\n"
        )
        (catalog_dir / "flow_v2.yaml").write_text(
            "flow_id: flow_1\ntemplate_ref: templates/flow.yaml\nversion: 2.0\n"
        )

        result = catalog_index_by_template(catalog_dir)

        assert result["templates/flow.yaml"]["version"] == 2.0

    def test_catalog_index_flow_version_id(self, tmp_path):
        """Uses flow_version_id for comparison."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        (catalog_dir / "flow_v1.yaml").write_text(
            "flow_id: flow_1\ntemplate_ref: templates/flow.yaml\nflow_version_id: v1\n"
        )
        (catalog_dir / "flow_v2.yaml").write_text(
            "flow_id: flow_1\ntemplate_ref: templates/flow.yaml\nflow_version_id: v2\n"
        )

        result = catalog_index_by_template(catalog_dir)

        assert result["templates/flow.yaml"]["flow_version_id"] == "v2"

    def test_catalog_index_skips_empty_template_ref(self, tmp_path):
        """Entries without template_ref are skipped."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "no_template.yaml"
        entry_file.write_text("flow_id: flow_1\ntemplate_ref: \n")

        result = catalog_index_by_template(catalog_dir)

        assert result == {}


class TestEntryForTemplate:
    """Tests for entry_for_template function."""

    def test_entry_for_template_found(self, tmp_path):
        """Find entry for existing template."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()
        entry_file = catalog_dir / "my_flow.yaml"
        entry_file.write_text("flow_id: flow_1\n")

        result = entry_for_template("my_flow", catalog_dir)

        assert result is not None
        assert result["flow_id"] == "flow_1"

    def test_entry_for_template_not_found(self, tmp_path):
        """Return None for nonexistent template."""
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()

        result = entry_for_template("nonexistent", catalog_dir)

        assert result is None
