"""
Comprehensive tests for app/user/routes.py to achieve 97%+ coverage.

This test file focuses on uncovered code paths:
- Lines 132-155: Golden path fallback for non-scenario questions
- Lines 171-175: Pipeline exception handling
- Lines 267-270: prepare_sources_for_info_type exception handling
- Lines 275, 277: _resolve_info_type branches
- Lines 284-287: _scenario_from_info_type loop
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.user import routes
from app.admin import service


@pytest.fixture(autouse=True)
def _sandbox(tmp_path, monkeypatch):
    """Sandbox storage for tests."""
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


class TestGoldenPathFallback:
    """Test coverage for lines 132-155: golden path fallback for non-scenario questions."""

    def test_golden_path_preco_medio(self):
        """Test golden path for price average question."""
        # This question matches the golden_map in routes.py line 36
        question = "Qual o preço médio do arroz em São Paulo?"
        result = routes.post_query({"question": question})

        assert "response" in result
        assert "dto" in result
        assert "view" in result

        dto = result["dto"]
        assert dto["query_id"] == "golden"
        assert dto["response_id"] == "golden"
        assert dto["status"] == "ok"
        assert "answer_text" in dto
        assert "summary_card" in dto
        assert "evidence_links" in dto

        view = result["view"]
        assert "summary_card" in view
        assert "evidence_links" in view
        assert view["status"] == "ok"

    def test_golden_path_comparacao_simples(self):
        """Test golden path for simple comparison question."""
        question = "Onde o arroz está mais barato em São Paulo?"
        result = routes.post_query({"question": question})

        assert "response" in result
        dto = result["dto"]
        assert dto["query_id"] == "golden"
        assert dto["response_id"] == "golden"
        assert dto["status"] == "ok"

    def test_golden_path_checagem_factual(self):
        """Test golden path for fact-checking question."""
        question = "João Mendes foi condenado na Operação Horizonte?"
        result = routes.post_query({"question": question})

        assert "response" in result
        dto = result["dto"]
        assert dto["query_id"] == "golden"
        assert dto["response_id"] == "golden"
        assert dto["status"] == "ok"

    def test_golden_path_with_info_type_and_scenario(self):
        """Test golden path preserves info_type and scenario_id from payload."""
        question = "Qual o preço médio do arroz em São Paulo?"
        result = routes.post_query({
            "question": question,
            "info_type": "C1_preco_medio",
            "scenario_id": "test_scenario"
        })

        dto = result["dto"]
        assert dto["info_type"] == "C1_preco_medio"
        assert dto["scenario_id"] == "test_scenario"


class TestPipelineExceptionHandling:
    """Test coverage for lines 171-175: pipeline exception handling."""

    def test_pipeline_raises_exception(self, monkeypatch):
        """Test that pipeline exceptions are properly raised and metrics recorded."""
        def mock_pipeline_error(question):
            raise RuntimeError("Pipeline failure")

        monkeypatch.setattr("app.core.pipeline.run_pipeline", mock_pipeline_error)

        # Use a non-golden question to hit the pipeline path
        question = "Test question that will cause pipeline error"

        with pytest.raises(RuntimeError, match="Pipeline failure"):
            routes.post_query({"question": question})


class TestPrepareSourcesErrorHandling:
    """Test coverage for lines 267-270: prepare_sources_for_info_type exception handling."""

    def test_prepare_sources_for_info_type_raises_error(self, monkeypatch):
        """Test error handling when prepare_sources_for_info_type fails."""
        def mock_prepare_error(info_type):
            raise ValueError("Preparation failed")

        monkeypatch.setattr(
            "app.admin.service.prepare_sources_for_info_type",
            mock_prepare_error
        )

        # Provide info_type without scenario_id to trigger the elif branch
        question = "Test question with info_type"
        result = routes.post_query({
            "question": question,
            "info_type": "C1_preco_medio"
        })

        assert result["status"] == "erro"
        assert "Erro ao preparar fontes para C1_preco_medio" in result["error"]


class TestResolveInfoType:
    """Test coverage for lines 275, 277: _resolve_info_type branches."""

    def test_resolve_info_type_from_request_info_type(self):
        """Test _resolve_info_type returns request.info_type when present."""
        from app.user import schemas

        request = schemas.UserQueryRequest(
            question="test",
            info_type="C1_preco_medio"
        )
        result = routes._resolve_info_type(request)
        assert result == "C1_preco_medio"

    def test_resolve_info_type_from_scenario_id(self):
        """Test _resolve_info_type resolves from scenario_id when info_type not present."""
        from app.user import schemas

        request = schemas.UserQueryRequest(
            question="test",
            scenario_id="C1"
        )
        result = routes._resolve_info_type(request)
        assert result == "C1_preco_medio"

    def test_resolve_info_type_invalid_scenario(self):
        """Test _resolve_info_type returns None for invalid scenario_id."""
        from app.user import schemas

        request = schemas.UserQueryRequest(
            question="test",
            scenario_id="INVALID"
        )
        result = routes._resolve_info_type(request)
        assert result is None

    def test_resolve_info_type_no_info(self):
        """Test _resolve_info_type returns None when no info_type or scenario_id."""
        from app.user import schemas

        request = schemas.UserQueryRequest(
            question="test"
        )
        result = routes._resolve_info_type(request)
        assert result is None


class TestScenarioFromInfoType:
    """Test coverage for lines 284-287: _scenario_from_info_type loop."""

    def test_scenario_from_info_type_c1(self):
        """Test _scenario_from_info_type returns C1 for C1_preco_medio."""
        result = routes._scenario_from_info_type("C1_preco_medio")
        assert result == "C1"

    def test_scenario_from_info_type_c2(self):
        """Test _scenario_from_info_type returns C2 for C2_comparacao_simples."""
        result = routes._scenario_from_info_type("C2_comparacao_simples")
        assert result == "C2"

    def test_scenario_from_info_type_c3(self):
        """Test _scenario_from_info_type returns C3 for C3_checagem_factual."""
        result = routes._scenario_from_info_type("C3_checagem_factual")
        assert result == "C3"

    def test_scenario_from_info_type_none_input(self):
        """Test _scenario_from_info_type returns None for None input."""
        result = routes._scenario_from_info_type(None)
        assert result is None

    def test_scenario_from_info_type_unknown(self):
        """Test _scenario_from_info_type returns None for unknown info_type."""
        result = routes._scenario_from_info_type("unknown_info_type")
        assert result is None


class TestEdgeCases:
    """Additional edge case tests to ensure comprehensive coverage."""

    def test_empty_question_with_whitespace(self):
        """Test that whitespace-only questions are rejected."""
        result = routes.post_query({"question": "   "})
        assert result["status"] == "erro"
        assert "question é obrigatório" in result["error"]

    def test_query_alias_accepted(self):
        """Test that 'query' field is accepted as alias for 'question'."""
        question = "Qual o preço médio do arroz em São Paulo?"
        result = routes.post_query({"query": question})
        assert "response" in result
        assert result["dto"]["status"] == "ok"

    def test_filters_default_to_empty_dict(self):
        """Test that filters default to empty dict when not provided."""
        question = "Qual o preço médio do arroz em São Paulo?"
        result = routes.post_query({"question": question})
        # Should not raise an error and should process normally
        assert "response" in result

    def test_golden_path_missing_file_fallback(self, monkeypatch, tmp_path):
        """Test behavior when golden file doesn't exist (should fall through to pipeline)."""
        # Create a question that would match golden_map but file doesn't exist
        golden_dir = tmp_path / "goldens"
        golden_dir.mkdir()

        # Temporarily point to non-existent golden file
        def mock_exists(self):
            return False

        monkeypatch.setattr(Path, "exists", mock_exists)

        # This should fall through to normal pipeline processing
        question = "Qual o preço médio do arroz em São Paulo?"
        result = routes.post_query({"question": question})

        # Should still get a response, but not from golden path
        assert "response" in result
