"""
Tests for GPT Client Prompts — S37

Tests for prompt building functions.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.gpt_client.prompts import (
    build_price_prompt,
    build_comparison_prompt,
    build_fact_prompt,
    _format_user_prompt,
    _deterministic_settings,
    _bundle_to_context,
)


class TestBuildPricePrompt:
    """Tests for build_price_prompt function."""

    def test_build_price_prompt(self):
        """Build price prompt."""
        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {"s1": []}
        mock_bundle.query_filters = {"product": "coffee"}
        mock_bundle.info_type = "C1_preco_medio"

        with patch("app.gpt_client.prompts._bundle_to_context") as mock_ctx:
            mock_ctx.return_value = {
                "meta": {"num_sources": 1},
                "sources": [],
            }

            result = build_price_prompt(
                mock_bundle,
                {"query_type": "preco_medio"},
                "test_scenario",
                "What is the price?",
            )

        assert "system" in result
        assert "user" in result
        assert "context" in result
        assert "settings" in result
        assert "preço médio" in result["system"]


class TestBuildComparisonPrompt:
    """Tests for build_comparison_prompt function."""

    def test_build_comparison_prompt(self):
        """Build comparison prompt."""
        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {}
        mock_bundle.query_filters = {}
        mock_bundle.info_type = "C2_comparacao_simples"

        with patch("app.gpt_client.prompts._bundle_to_context") as mock_ctx:
            mock_ctx.return_value = {"meta": {}, "sources": []}

            result = build_comparison_prompt(
                mock_bundle,
                {"query_type": "comparacao_simples"},
                "test",
                "Compare prices",
            )

        assert "compara preços" in result["system"]


class TestBuildFactPrompt:
    """Tests for build_fact_prompt function."""

    def test_build_fact_prompt(self):
        """Build fact check prompt."""
        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {}
        mock_bundle.query_filters = {}
        mock_bundle.info_type = "C3_checagem_factual"

        with patch("app.gpt_client.prompts._bundle_to_context") as mock_ctx:
            mock_ctx.return_value = {"meta": {}, "sources": []}

            result = build_fact_prompt(
                mock_bundle,
                {"query_type": "checagem_factual"},
                "test",
                "Is this true?",
            )

        assert "checa declarações" in result["system"]
        assert "confirmado/negado/divergente/indefinido" in result["system"]


class TestFormatUserPrompt:
    """Tests for _format_user_prompt function."""

    def test_format_user_prompt(self):
        """Format user prompt."""
        context = {"meta": {"num_sources": 2}, "sources": []}
        query_spec = {"query_type": "preco_medio"}

        result = _format_user_prompt(
            user_query="What is the price of coffee?",
            query_spec=query_spec,
            context=context,
            expected_fields="summary_structured must contain: resolution",
        )

        assert "What is the price of coffee?" in result
        assert "preco_medio" in result
        assert "summary_structured must contain" in result
        assert "JSON" in result


class TestDeterministicSettings:
    """Tests for _deterministic_settings function."""

    def test_deterministic_settings(self):
        """Returns deterministic settings."""
        result = _deterministic_settings()

        assert result["temperature"] == 0.0
        assert result["top_p"] == 0.0
        assert result["max_tokens"] == 800


class TestBundleToContext:
    """Tests for _bundle_to_context function."""

    def test_bundle_to_context_empty(self):
        """Convert empty bundle to context."""
        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {}
        mock_bundle.query_filters = {"key": "value"}
        mock_bundle.info_type = "C1_preco_medio"

        result = _bundle_to_context(mock_bundle, "test_scenario")

        assert result["meta"]["num_sources"] == 0
        assert result["meta"]["num_items"] == 0
        assert result["meta"]["scenario_tag"] == "test_scenario"
        assert result["meta"]["info_type"] == "C1_preco_medio"
        assert result["sources"] == []

    def test_bundle_to_context_with_items(self):
        """Convert bundle with items to context."""
        mock_ref = MagicMock()
        mock_ref.item_id = "item_123"
        mock_ref.key_fields = {"field": "value"}

        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {"source1": [mock_ref]}
        mock_bundle.query_filters = {}
        mock_bundle.info_type = "C1_preco_medio"

        mock_item = MagicMock()
        mock_item.payload = {"price": 10.0}
        mock_item.created_at.isoformat.return_value = "2024-01-01T00:00:00"

        with patch("app.gpt_client.prompts.storage.get_item", return_value=mock_item):
            result = _bundle_to_context(mock_bundle, "test")

        assert result["meta"]["num_sources"] == 1
        assert result["meta"]["num_items"] == 1
        assert len(result["sources"]) == 1
        assert result["sources"][0]["source_id"] == "source1"
        assert result["sources"][0]["items"][0]["payload"] == {"price": 10.0}

    def test_bundle_to_context_item_not_found(self):
        """Handle item not found in storage."""
        mock_ref = MagicMock()
        mock_ref.item_id = "missing_item"
        mock_ref.key_fields = {}

        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {"source1": [mock_ref]}
        mock_bundle.query_filters = {}
        mock_bundle.info_type = "test"

        with patch("app.gpt_client.prompts.storage.get_item", return_value=None):
            result = _bundle_to_context(mock_bundle, "test")

        assert result["meta"]["num_items"] == 1
        # Item should still be included but without payload
        assert "payload" not in result["sources"][0]["items"][0]
