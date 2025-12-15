"""
Tests for Policies Schema — S37

Tests for policy schema validation and loading.
"""

import pytest
import json
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory

from app.policies.schema import (
    InvalidPolicyError,
    REQUIRED_FIELDS,
    _validate_payload,
    load_policy_file,
    load_policies_from_dir,
    main,
)
from app.policies.models import PromotionPolicyConfig


class TestValidatePayload:
    """Tests for _validate_payload function."""

    def test_valid_payload(self):
        """Validate valid payload."""
        data = {
            "name": "Test Policy",
            "domain": "politics",
            "min_confidence": 0.8,
            "min_sources": 2,
        }

        result = _validate_payload(data)

        assert isinstance(result, PromotionPolicyConfig)
        assert result.name == "Test Policy"
        assert result.domain == "politics"
        assert result.min_confidence == 0.8
        assert result.min_sources == 2

    def test_valid_payload_with_optional_fields(self):
        """Validate payload with optional fields."""
        data = {
            "name": "Test Policy",
            "domain": "politics",
            "min_confidence": 0.9,
            "min_sources": 3,
            "require_debunk": True,
            "require_human": True,
            "sensitive": True,
            "default_decision": "PROMOTE",
            "metadata": {"key": "value"},
        }

        result = _validate_payload(data)

        assert result.require_debunk is True
        assert result.require_human is True
        assert result.sensitive is True
        assert result.default_decision == "PROMOTE"
        assert result.metadata == {"key": "value"}

    def test_missing_required_field_raises(self):
        """Missing required field raises error."""
        data = {
            "name": "Test Policy",
            "domain": "politics",
            # Missing min_confidence and min_sources
        }

        with pytest.raises(InvalidPolicyError, match="Campos obrigatórios"):
            _validate_payload(data)

    def test_invalid_default_decision_raises(self):
        """Invalid default_decision raises error."""
        data = {
            "name": "Test Policy",
            "domain": "politics",
            "min_confidence": 0.8,
            "min_sources": 2,
            "default_decision": "INVALID",
        }

        with pytest.raises(InvalidPolicyError, match="default_decision inválido"):
            _validate_payload(data)

    def test_default_decision_promote(self):
        """Default decision PROMOTE is valid."""
        data = {
            "name": "Test",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
            "default_decision": "promote",  # lowercase
        }

        result = _validate_payload(data)

        assert result.default_decision == "PROMOTE"

    def test_default_decision_hold(self):
        """Default decision HOLD is valid."""
        data = {
            "name": "Test",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
            "default_decision": "HOLD",
        }

        result = _validate_payload(data)

        assert result.default_decision == "HOLD"

    def test_default_decision_block(self):
        """Default decision BLOCK is valid."""
        data = {
            "name": "Test",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
            "default_decision": "block",
        }

        result = _validate_payload(data)

        assert result.default_decision == "BLOCK"

    def test_default_defaults(self):
        """Defaults are applied when fields missing."""
        data = {
            "name": "Test",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
        }

        result = _validate_payload(data)

        assert result.require_debunk is False
        assert result.require_human is False
        assert result.sensitive is False
        assert result.default_decision == "HOLD"
        assert result.metadata == {}


class TestLoadPolicyFile:
    """Tests for load_policy_file function."""

    def test_load_json_file(self, tmp_path):
        """Load JSON policy file."""
        policy_file = tmp_path / "policy.json"
        data = {
            "name": "JSON Policy",
            "domain": "test",
            "min_confidence": 0.7,
            "min_sources": 2,
        }
        policy_file.write_text(json.dumps(data), encoding="utf-8")

        result = load_policy_file(policy_file)

        assert result.name == "JSON Policy"
        assert result.domain == "test"

    def test_load_yaml_file(self, tmp_path):
        """Load YAML policy file."""
        policy_file = tmp_path / "policy.yaml"
        data = {
            "name": "YAML Policy",
            "domain": "test",
            "min_confidence": 0.8,
            "min_sources": 3,
        }
        policy_file.write_text(yaml.dump(data), encoding="utf-8")

        result = load_policy_file(policy_file)

        assert result.name == "YAML Policy"

    def test_load_yml_file(self, tmp_path):
        """Load .yml policy file."""
        policy_file = tmp_path / "policy.yml"
        data = {
            "name": "YML Policy",
            "domain": "test",
            "min_confidence": 0.6,
            "min_sources": 1,
        }
        policy_file.write_text(yaml.dump(data), encoding="utf-8")

        result = load_policy_file(policy_file)

        assert result.name == "YML Policy"

    def test_file_not_found_raises(self, tmp_path):
        """Non-existent file raises error."""
        policy_file = tmp_path / "nonexistent.json"

        with pytest.raises(InvalidPolicyError, match="não encontrado"):
            load_policy_file(policy_file)

    def test_invalid_content_raises(self, tmp_path):
        """Non-dict content raises error."""
        policy_file = tmp_path / "policy.json"
        policy_file.write_text("[1, 2, 3]", encoding="utf-8")  # Array instead of dict

        with pytest.raises(InvalidPolicyError, match="deve ser um objeto"):
            load_policy_file(policy_file)


class TestLoadPoliciesFromDir:
    """Tests for load_policies_from_dir function."""

    def test_load_multiple_policies(self, tmp_path):
        """Load multiple policies from directory."""
        policy1 = tmp_path / "politics.json"
        policy1.write_text(json.dumps({
            "name": "Politics Policy",
            "domain": "politics",
            "min_confidence": 0.8,
            "min_sources": 2,
        }), encoding="utf-8")

        policy2 = tmp_path / "health.yaml"
        policy2.write_text(yaml.dump({
            "name": "Health Policy",
            "domain": "health",
            "min_confidence": 0.9,
            "min_sources": 3,
        }), encoding="utf-8")

        result = load_policies_from_dir(tmp_path)

        assert len(result) == 2
        assert "politics" in result
        assert "health" in result

    def test_directory_not_found_raises(self, tmp_path):
        """Non-existent directory raises error."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(InvalidPolicyError, match="não encontrado"):
            load_policies_from_dir(nonexistent)

    def test_no_policies_raises(self, tmp_path):
        """Empty directory raises error."""
        with pytest.raises(InvalidPolicyError, match="Nenhuma policy"):
            load_policies_from_dir(tmp_path)

    def test_ignores_non_policy_files(self, tmp_path):
        """Ignores files with wrong extension."""
        policy = tmp_path / "valid.json"
        policy.write_text(json.dumps({
            "name": "Valid",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
        }), encoding="utf-8")

        # Create non-policy files
        (tmp_path / "readme.txt").write_text("readme", encoding="utf-8")
        (tmp_path / "script.py").write_text("print('hello')", encoding="utf-8")

        result = load_policies_from_dir(tmp_path)

        assert len(result) == 1

    def test_ignores_subdirectories(self, tmp_path):
        """Ignores subdirectories."""
        policy = tmp_path / "valid.json"
        policy.write_text(json.dumps({
            "name": "Valid",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
        }), encoding="utf-8")

        # Create subdirectory with policy file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "policy.json").write_text("{}", encoding="utf-8")

        result = load_policies_from_dir(tmp_path)

        assert len(result) == 1


class TestMain:
    """Tests for main CLI function."""

    def test_main_success(self, tmp_path):
        """Main succeeds with valid policies."""
        from unittest.mock import patch

        # Create valid policy
        policy_dir = tmp_path / "configs/promotion_policies"
        policy_dir.mkdir(parents=True)
        policy = policy_dir / "test.json"
        policy.write_text(json.dumps({
            "name": "Test",
            "domain": "test",
            "min_confidence": 0.5,
            "min_sources": 1,
        }), encoding="utf-8")

        with patch("app.policies.schema.Path", return_value=policy_dir):
            with patch("app.policies.schema.load_policies_from_dir") as mock_load:
                mock_load.return_value = {"test": None}
                result = main()

        assert result == 0

    def test_main_failure(self, tmp_path):
        """Main fails with invalid policies."""
        from unittest.mock import patch

        with patch("app.policies.schema.load_policies_from_dir") as mock_load:
            mock_load.side_effect = InvalidPolicyError("Test error")
            result = main()

        assert result == 1


class TestConstants:
    """Tests for module constants."""

    def test_required_fields(self):
        """REQUIRED_FIELDS has expected values."""
        assert "name" in REQUIRED_FIELDS
        assert "domain" in REQUIRED_FIELDS
        assert "min_confidence" in REQUIRED_FIELDS
        assert "min_sources" in REQUIRED_FIELDS
