"""
Tests for GPT Client — S37

Tests for GPT client functions and answer generation.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.gpt_client.client import (
    GptAnswer,
    PROMPT_BUILDERS,
    run_query,
    _simulate_model_decision,
    _base_summary,
    _summarize_price,
    _summarize_comparison,
    _summarize_fact,
    _derive_confidence,
    _to_float,
)


class TestGptAnswer:
    """Tests for GptAnswer dataclass."""

    def test_create(self):
        """Create GptAnswer."""
        answer = GptAnswer(
            answer_text="Test answer",
            summary_structured={"key": "value"},
            confidence_flags={"level": "high"},
        )

        assert answer.answer_text == "Test answer"
        assert answer.summary_structured["key"] == "value"
        assert answer.limitations == []
        assert answer.prompt_used == {}

    def test_create_with_all_fields(self):
        """Create GptAnswer with all fields."""
        answer = GptAnswer(
            answer_text="Full answer",
            summary_structured={"resolution": "ok"},
            confidence_flags={"level": "medium"},
            limitations=["Only used bundle data."],
            prompt_used={"system": "test", "user": "query"},
        )

        assert len(answer.limitations) == 1
        assert "system" in answer.prompt_used


class TestPromptBuilders:
    """Tests for PROMPT_BUILDERS mapping."""

    def test_has_expected_keys(self):
        """Has expected info type keys."""
        assert "C1_preco_medio" in PROMPT_BUILDERS
        assert "C2_comparacao_simples" in PROMPT_BUILDERS
        assert "C3_checagem_factual" in PROMPT_BUILDERS


class TestRunQuery:
    """Tests for run_query function."""

    def test_run_query_price(self):
        """Run query for price type."""
        mock_bundle = MagicMock()
        mock_bundle.items_by_source = {"source1": []}
        mock_bundle.query_filters = {}
        mock_bundle.info_type = "C1_preco_medio"

        with patch("app.gpt_client.prompts.build_price_prompt") as mock_builder:
            mock_builder.return_value = {
                "system": "test",
                "user": "query",
                "context": {
                    "meta": {"num_sources": 2, "num_items": 3, "info_type": "C1_preco_medio", "scenario_tag": "test"},
                    "sources": [],
                },
                "settings": {},
            }

            result = run_query(
                info_type="C1_preco_medio",
                bundle=mock_bundle,
                query_spec={"query_type": "preco_medio"},
                scenario_tag="test",
                user_query="What is the price?",
            )

        assert isinstance(result, GptAnswer)
        assert result.answer_text is not None

    def test_run_query_unsupported_type(self):
        """Run query with unsupported type raises."""
        mock_bundle = MagicMock()

        with pytest.raises(ValueError, match="não suportado"):
            run_query(
                info_type="UNKNOWN_TYPE",
                bundle=mock_bundle,
                query_spec={},
                scenario_tag="test",
                user_query="Test",
            )


class TestSimulateModelDecision:
    """Tests for _simulate_model_decision function."""

    def test_out_of_scope(self):
        """Returns out of scope when query_type is fora_de_escopo."""
        context = {
            "meta": {"num_sources": 2, "num_items": 5},
            "sources": [],
        }
        query_spec = {"query_type": "fora_de_escopo"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert result["summary_structured"]["resolution"] == "fora_de_escopo"
        assert result["confidence_flags"]["level"] == "low"

    def test_insufficient_data_few_sources(self):
        """Returns insufficient data when few sources."""
        context = {
            "meta": {"num_sources": 1, "num_items": 5},
            "sources": [],
        }
        query_spec = {"query_type": "preco_medio"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert result["summary_structured"]["resolution"] == "dados_insuficientes"
        assert "dados insuficientes" in result["confidence_flags"]["reasons"]

    def test_insufficient_data_no_items(self):
        """Returns insufficient data when no items."""
        context = {
            "meta": {"num_sources": 3, "num_items": 0},
            "sources": [],
        }
        query_spec = {"query_type": "preco_medio"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert result["summary_structured"]["resolution"] == "dados_insuficientes"

    def test_price_query(self):
        """Processes price query type."""
        context = {
            "meta": {"num_sources": 2, "num_items": 3},
            "sources": [
                {
                    "source_id": "s1",
                    "items": [{"payload": {"valor": 10.0, "produto": "Item A"}}],
                },
            ],
        }
        query_spec = {"query_type": "preco_medio"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert "main_value" in result["summary_structured"]

    def test_comparison_query(self):
        """Processes comparison query type."""
        context = {
            "meta": {"num_sources": 2, "num_items": 2},
            "sources": [
                {
                    "source_id": "s1",
                    "items": [{"payload": {"valor": 10.0, "bairro": "Centro"}}],
                },
            ],
        }
        query_spec = {"query_type": "comparacao_simples"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert "best_location" in result["summary_structured"]

    def test_fact_query(self):
        """Processes fact check query type."""
        context = {
            "meta": {"num_sources": 2, "num_items": 2},
            "sources": [
                {
                    "source_id": "s1",
                    "items": [{"payload": {"status": "confirmado", "pessoa": "John"}}],
                },
            ],
        }
        query_spec = {"query_type": "checagem_factual"}

        result = _simulate_model_decision("C1_preco_medio", context, query_spec)

        assert "verdict" in result["summary_structured"]


class TestBaseSummary:
    """Tests for _base_summary function."""

    def test_base_summary(self):
        """Creates base summary."""
        meta = {
            "info_type": "C1_preco_medio",
            "scenario_tag": "test",
            "num_sources": 3,
            "num_items": 10,
        }

        result = _base_summary(meta, "preco_medio")

        assert result["query_type"] == "preco_medio"
        assert result["info_type"] == "C1_preco_medio"
        assert result["num_sources"] == 3
        assert result["num_items"] == 10


class TestSummarizePrice:
    """Tests for _summarize_price function."""

    def test_summarize_price_with_values(self):
        """Summarize price with multiple values."""
        meta = {"num_sources": 2, "num_items": 3}
        sources = [
            {
                "source_id": "s1",
                "items": [
                    {"payload": {"valor": 10.0, "produto": "Coffee", "cidade": "SP"}},
                    {"payload": {"valor": 12.0}},
                ],
            },
            {
                "source_id": "s2",
                "items": [{"payload": {"valor_medio": 11.0}}],
            },
        ]

        extra, answer = _summarize_price(meta, sources)

        assert extra["main_value"] == 11.0  # (10 + 12 + 11) / 3
        assert extra["range"]["min"] == 10.0
        assert extra["range"]["max"] == 12.0
        assert extra["resolution"] == "ok"
        assert "Coffee" in answer

    def test_summarize_price_no_values(self):
        """Summarize price with no values."""
        meta = {"num_sources": 2, "num_items": 2}
        sources = [
            {"source_id": "s1", "items": [{"payload": {}}]},
        ]

        extra, answer = _summarize_price(meta, sources)

        assert extra["resolution"] == "dados_insuficientes"
        assert extra["main_value"] is None

    def test_summarize_price_with_currency(self):
        """Summarize price preserves currency."""
        meta = {"num_sources": 1, "num_items": 1}
        sources = [
            {
                "source_id": "s1",
                "items": [{"payload": {"valor": 100.0, "moeda": "USD"}}],
            },
        ]

        extra, answer = _summarize_price(meta, sources)

        assert extra["unit"] == "USD"


class TestSummarizeComparison:
    """Tests for _summarize_comparison function."""

    def test_summarize_comparison_finds_best(self):
        """Finds best location."""
        meta = {"num_sources": 2, "num_items": 3}
        sources = [
            {
                "source_id": "s1",
                "items": [
                    {"payload": {"valor": 15.0, "bairro": "Centro"}},
                    {"payload": {"valor": 10.0, "bairro": "Zona Sul"}},
                ],
            },
            {
                "source_id": "s2",
                "items": [{"payload": {"valor": 12.0, "cidade": "Rio"}}],
            },
        ]

        extra, answer = _summarize_comparison(meta, sources)

        assert extra["best_location"] == "Zona Sul"
        assert extra["best_value"] == 10.0
        assert extra["runner_up"] == 12.0
        assert extra["resolution"] == "ok"

    def test_summarize_comparison_no_location(self):
        """Handles missing location."""
        meta = {"num_sources": 1, "num_items": 1}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"valor": 10.0}}]},
        ]

        extra, answer = _summarize_comparison(meta, sources)

        assert extra["resolution"] == "dados_insuficientes"

    def test_summarize_comparison_calculates_delta(self):
        """Calculates price delta percentage."""
        meta = {"num_sources": 2, "num_items": 2}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"valor": 80.0, "bairro": "A"}}]},
            {"source_id": "s2", "items": [{"payload": {"valor": 100.0, "bairro": "B"}}]},
        ]

        extra, answer = _summarize_comparison(meta, sources)

        assert extra["price_delta_pct"] == 20.0  # (100-80)/100 * 100


class TestSummarizeFact:
    """Tests for _summarize_fact function."""

    def test_summarize_fact_confirmed(self):
        """Fact is confirmed."""
        meta = {"num_sources": 2, "num_items": 2}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"status": "confirmado", "pessoa": "John"}}]},
            {"source_id": "s2", "items": [{"payload": {"status": "sim"}}]},
        ]

        extra, answer = _summarize_fact(meta, sources)

        assert extra["verdict"] == "confirmado"
        assert extra["confirmations"] == 2
        assert extra["negatives"] == 0

    def test_summarize_fact_denied(self):
        """Fact is denied."""
        meta = {"num_sources": 1, "num_items": 1}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"status": "negado", "pessoa": "Jane"}}]},
        ]

        extra, answer = _summarize_fact(meta, sources)

        assert extra["verdict"] == "negado"

    def test_summarize_fact_divergent(self):
        """Fact has divergent sources."""
        meta = {"num_sources": 2, "num_items": 2}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"status": "confirmado"}}]},
            {"source_id": "s2", "items": [{"payload": {"status": "nao"}}]},
        ]

        extra, answer = _summarize_fact(meta, sources)

        assert extra["verdict"] == "divergente"

    def test_summarize_fact_undefined(self):
        """Fact is undefined."""
        meta = {"num_sources": 1, "num_items": 1}
        sources = [
            {"source_id": "s1", "items": [{"payload": {"status": "talvez"}}]},
        ]

        extra, answer = _summarize_fact(meta, sources)

        assert extra["verdict"] == "indefinido"


class TestDeriveConfidence:
    """Tests for _derive_confidence function."""

    def test_high_confidence(self):
        """High confidence when all is well."""
        summary = {
            "num_sources": 3,
            "resolution": "ok",
        }

        result = _derive_confidence(summary)

        assert result["level"] == "high"
        assert result["reasons"] == []

    def test_medium_few_sources(self):
        """Medium confidence with few sources."""
        summary = {
            "num_sources": 1,
            "resolution": "ok",
        }

        result = _derive_confidence(summary)

        assert result["level"] == "medium"
        assert "apenas uma fonte" in result["reasons"][0]

    def test_medium_high_variation(self):
        """Medium confidence with high price variation."""
        summary = {
            "num_sources": 3,
            "resolution": "ok",
            "range": {"min": 10.0, "max": 20.0},
        }

        result = _derive_confidence(summary)

        assert result["level"] == "medium"
        assert "variação" in result["reasons"][0]

    def test_low_divergent(self):
        """Low confidence when divergent."""
        summary = {
            "num_sources": 3,
            "verdict": "divergente",
            "resolution": "ok",
        }

        result = _derive_confidence(summary)

        assert result["level"] == "low"
        assert "contradizem" in result["reasons"][0]

    def test_low_not_ok(self):
        """Low confidence when not ok."""
        summary = {
            "num_sources": 3,
            "resolution": "dados_insuficientes",
        }

        result = _derive_confidence(summary)

        assert result["level"] == "low"


class TestToFloat:
    """Tests for _to_float function."""

    def test_to_float_number(self):
        """Converts number."""
        assert _to_float(10) == 10.0
        assert _to_float(3.14) == 3.14

    def test_to_float_string(self):
        """Converts string."""
        assert _to_float("42.5") == 42.5

    def test_to_float_none(self):
        """Returns None for None."""
        assert _to_float(None) is None

    def test_to_float_invalid(self):
        """Returns None for invalid."""
        assert _to_float("abc") is None
        assert _to_float([1, 2]) is None
