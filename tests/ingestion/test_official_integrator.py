"""
Tests for app/ingestion/official_integrator.py

Covers:
- OfficialSourceIntegrator initialization
- Fetching from gov.br (contratos, despesas)
- Fetching from dados.gov.br (categories, recent updates)
- Fetching from TSE (eleicoes, partidos, prestacao_contas)
- Document normalization (from_gov_br, from_dados_gov, from_tse)
- Fetch all priority sources
- Health tracking and updates
- Error handling for each source
- Date parsing
- Deduplication logic
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.official_integrator import (
    OfficialSourceIntegrator,
    NormalizedDocument,
    SourceHealth,
    SourceStatus,
    SourceType,
    _parse_date,
)
from app.ingestion.providers.gov_br import GovBrDocument
from app.ingestion.providers.dados_gov import DadosGovDocument
from app.ingestion.providers.tse import TSEDocument


class TestNormalizedDocument:
    """Test suite for NormalizedDocument."""

    def test_from_gov_br(self):
        """Test creating normalized document from GovBrDocument."""
        gov_doc = GovBrDocument(
            external_id="GOV123",
            title="Contrato de Teste",
            url="https://gov.br/contrato/123",
            published_at="2024-12-01",
            content="Conteúdo do contrato",
            source_api="transparencia",
            document_type="contrato",
            metadata={"valor": 100000},
        )

        normalized = NormalizedDocument.from_gov_br(gov_doc)

        assert normalized.source_type == SourceType.GOV_BR
        assert normalized.external_id == "GOV123"
        assert normalized.title == "Contrato de Teste"
        assert normalized.url == "https://gov.br/contrato/123"
        assert normalized.content == "Conteúdo do contrato"
        assert normalized.document_type == "contrato"
        assert normalized.metadata["source_api"] == "transparencia"
        assert normalized.metadata["valor"] == 100000
        assert normalized.id.startswith("gov_br_")

    def test_from_dados_gov(self):
        """Test creating normalized document from DadosGovDocument."""
        dados_doc = DadosGovDocument(
            external_id="DADOS456",
            title="Dataset de Saúde",
            url="https://dados.gov.br/dataset/456",
            published_at="2024-11-15",
            content="Dados sobre COVID-19",
            organization="Ministério da Saúde",
            category="saude",
            metadata={"formato": "CSV"},
        )

        normalized = NormalizedDocument.from_dados_gov(dados_doc)

        assert normalized.source_type == SourceType.DADOS_GOV
        assert normalized.external_id == "DADOS456"
        assert normalized.title == "Dataset de Saúde"
        assert normalized.document_type == "dataset"
        assert normalized.metadata["organization"] == "Ministério da Saúde"
        assert normalized.metadata["category"] == "saude"
        assert normalized.id.startswith("dados_gov_")

    def test_from_tse(self):
        """Test creating normalized document from TSEDocument."""
        tse_doc = TSEDocument(
            external_id="TSE789",
            title="Eleições 2024",
            url="https://tse.jus.br/eleicoes/2024",
            published_at="2024-10-01",
            content="Dados eleitorais",
            document_type="eleicao",
            ano_eleicao=2024,
            metadata={"turno": 1},
        )

        normalized = NormalizedDocument.from_tse(tse_doc)

        assert normalized.source_type == SourceType.TSE
        assert normalized.external_id == "TSE789"
        assert normalized.title == "Eleições 2024"
        assert normalized.document_type == "eleicao"
        assert normalized.metadata["ano_eleicao"] == 2024
        assert normalized.metadata["turno"] == 1
        assert normalized.id.startswith("tse_")


class TestParseDates:
    """Test suite for _parse_date utility."""

    def test_parse_iso_with_microseconds(self):
        """Test parsing ISO format with microseconds."""
        date = _parse_date("2024-12-14T10:30:45.123456Z")
        assert date is not None
        assert date.year == 2024
        assert date.month == 12
        assert date.day == 14
        assert date.tzinfo == timezone.utc

    def test_parse_iso_without_microseconds(self):
        """Test parsing ISO format without microseconds."""
        date = _parse_date("2024-12-14T10:30:45Z")
        assert date is not None
        assert date.year == 2024

    def test_parse_iso_without_timezone(self):
        """Test parsing ISO format without timezone."""
        date = _parse_date("2024-12-14T10:30:45")
        assert date is not None
        assert date.tzinfo == timezone.utc

    def test_parse_date_only(self):
        """Test parsing date-only format."""
        date = _parse_date("2024-12-14")
        assert date is not None
        assert date.year == 2024
        assert date.month == 12
        assert date.day == 14

    def test_parse_brazilian_format(self):
        """Test parsing Brazilian date format."""
        date = _parse_date("14/12/2024")
        assert date is not None
        assert date.year == 2024
        assert date.month == 12
        assert date.day == 14

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        date = _parse_date("")
        assert date is None

    def test_parse_invalid_format(self):
        """Test parsing invalid format."""
        date = _parse_date("invalid-date-format")
        assert date is None


class TestOfficialSourceIntegrator:
    """Test suite for OfficialSourceIntegrator."""

    def test_initialization(self):
        """Test integrator initialization."""
        integrator = OfficialSourceIntegrator(
            gov_br_api_key="test-key",
            timeout_seconds=20,
            max_retries=5,
        )

        assert integrator.gov_br is not None
        assert integrator.dados_gov is not None
        assert integrator.tse is not None
        assert len(integrator._health) == 0

    @pytest.mark.asyncio
    async def test_fetch_from_gov_br_contratos_success(self):
        """Test fetching contratos from gov.br successfully."""
        integrator = OfficialSourceIntegrator()

        mock_doc = GovBrDocument(
            external_id="C123",
            title="Contrato Teste",
            url="https://gov.br/c123",
            published_at="2024-12-01",
            content="Contrato content",
            source_api="transparencia",
            document_type="contrato",
            metadata={},
        )

        with patch.object(
            integrator.gov_br, 'fetch_contratos', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [mock_doc]

            docs = await integrator.fetch_from_gov_br(
                data_inicial="01/12/2024",
                data_final="14/12/2024",
                include_contratos=True,
                include_despesas=False,
            )

            assert len(docs) == 1
            assert docs[0].source_type == SourceType.GOV_BR
            assert docs[0].external_id == "C123"

            # Check health was updated
            health = integrator._health.get(SourceType.GOV_BR)
            assert health is not None
            assert health.status == SourceStatus.HEALTHY
            assert health.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_fetch_from_gov_br_despesas_success(self):
        """Test fetching despesas from gov.br successfully."""
        integrator = OfficialSourceIntegrator()

        mock_doc = GovBrDocument(
            external_id="D456",
            title="Despesa Teste",
            url="https://gov.br/d456",
            published_at="2024-11-15",
            content="Despesa content",
            source_api="transparencia",
            document_type="despesa",
            metadata={},
        )

        with patch.object(
            integrator.gov_br, 'fetch_despesas', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [mock_doc]

            docs = await integrator.fetch_from_gov_br(
                data_inicial="01/11/2024",
                data_final="30/11/2024",
                include_contratos=False,
                include_despesas=True,
            )

            assert len(docs) == 1
            assert docs[0].external_id == "D456"
            assert docs[0].document_type == "despesa"

    @pytest.mark.asyncio
    async def test_fetch_from_gov_br_both_types(self):
        """Test fetching both contratos and despesas."""
        integrator = OfficialSourceIntegrator()

        contrato_doc = GovBrDocument(
            external_id="C1",
            title="Contrato",
            url="https://gov.br/c1",
            published_at="2024-12-01",
            content="C",
            source_api="transparencia",
            document_type="contrato",
        )

        despesa_doc = GovBrDocument(
            external_id="D1",
            title="Despesa",
            url="https://gov.br/d1",
            published_at="2024-12-15",
            content="D",
            source_api="transparencia",
            document_type="despesa",
        )

        with patch.object(
            integrator.gov_br, 'fetch_contratos', new_callable=AsyncMock
        ) as mock_contratos, patch.object(
            integrator.gov_br, 'fetch_despesas', new_callable=AsyncMock
        ) as mock_despesas:
            mock_contratos.return_value = [contrato_doc]
            mock_despesas.return_value = [despesa_doc]

            docs = await integrator.fetch_from_gov_br(
                data_inicial="01/12/2024",
                data_final="31/12/2024",
                include_contratos=True,
                include_despesas=True,
            )

            assert len(docs) == 2
            assert any(d.external_id == "C1" for d in docs)
            assert any(d.external_id == "D1" for d in docs)

    @pytest.mark.asyncio
    async def test_fetch_from_gov_br_error_handling(self):
        """Test error handling when fetching from gov.br."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator.gov_br, 'fetch_contratos', new_callable=AsyncMock
        ) as mock_contratos, patch.object(
            integrator.gov_br, 'fetch_despesas', new_callable=AsyncMock
        ) as mock_despesas:
            # Both should fail
            mock_contratos.side_effect = Exception("API Error")
            mock_despesas.side_effect = Exception("API Error")

            docs = await integrator.fetch_from_gov_br(
                data_inicial="01/12/2024",
                data_final="14/12/2024",
            )

            # Should return empty list on error
            assert len(docs) == 0

            # Health should be updated with failure
            health = integrator._health.get(SourceType.GOV_BR)
            assert health is not None
            assert health.consecutive_failures >= 1
            assert "API Error" in health.error_message

    @pytest.mark.asyncio
    async def test_fetch_from_dados_gov_categories(self):
        """Test fetching from dados.gov.br with categories."""
        integrator = OfficialSourceIntegrator()

        mock_doc = DadosGovDocument(
            external_id="DG1",
            title="Dataset Saúde",
            url="https://dados.gov.br/dg1",
            published_at="2024-12-01",
            content="Health data",
            organization="MS",
            category="saude",
        )

        with patch.object(
            integrator.dados_gov, 'fetch_by_category', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [mock_doc]

            docs = await integrator.fetch_from_dados_gov(
                categories=["saude"],
                include_recent=False,
                rows_per_category=10,
            )

            assert len(docs) == 1
            assert docs[0].external_id == "DG1"

            mock_fetch.assert_called_once_with("saude", rows=10)

    @pytest.mark.asyncio
    async def test_fetch_from_dados_gov_all_priority(self):
        """Test fetching all priority datasets from dados.gov.br."""
        integrator = OfficialSourceIntegrator()

        mock_doc1 = DadosGovDocument(
            external_id="DG1",
            title="Dataset 1",
            url="https://dados.gov.br/dg1",
            published_at="2024-12-01",
            content="Data 1",
            organization="Org1",
            category="saude",
        )

        mock_doc2 = DadosGovDocument(
            external_id="DG2",
            title="Dataset 2",
            url="https://dados.gov.br/dg2",
            published_at="2024-12-02",
            content="Data 2",
            organization="Org2",
            category="economia",
        )

        with patch.object(
            integrator.dados_gov, 'fetch_all_priority_datasets', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = {
                "saude": [mock_doc1],
                "economia": [mock_doc2],
            }

            docs = await integrator.fetch_from_dados_gov(
                categories=None,
                include_recent=False,
            )

            assert len(docs) == 2
            assert any(d.external_id == "DG1" for d in docs)
            assert any(d.external_id == "DG2" for d in docs)

    @pytest.mark.asyncio
    async def test_fetch_from_dados_gov_with_recent(self):
        """Test fetching from dados.gov.br including recent updates."""
        integrator = OfficialSourceIntegrator()

        priority_doc = DadosGovDocument(
            external_id="DG1",
            title="Priority",
            url="https://dados.gov.br/dg1",
            published_at="2024-12-01",
            content="Priority data",
            organization="Org1",
            category="saude",
        )

        recent_doc = DadosGovDocument(
            external_id="DG2",
            title="Recent",
            url="https://dados.gov.br/dg2",
            published_at="2024-12-14",
            content="Recent data",
            organization="Org2",
            category="economia",
        )

        with patch.object(
            integrator.dados_gov, 'fetch_all_priority_datasets', new_callable=AsyncMock
        ) as mock_priority, patch.object(
            integrator.dados_gov, 'get_recent_updates', new_callable=AsyncMock
        ) as mock_recent:
            mock_priority.return_value = {"saude": [priority_doc]}
            mock_recent.return_value = [recent_doc]

            docs = await integrator.fetch_from_dados_gov(include_recent=True)

            assert len(docs) == 2
            mock_recent.assert_called_once_with(days=7, rows=30)

    @pytest.mark.asyncio
    async def test_fetch_from_dados_gov_deduplication(self):
        """Test deduplication of documents from dados.gov.br."""
        integrator = OfficialSourceIntegrator()

        # Same external_id
        doc1 = DadosGovDocument(
            external_id="DG_SAME",
            title="Doc 1",
            url="https://dados.gov.br/dg1",
            published_at="2024-12-01",
            content="Data",
            organization="Org",
            category="saude",
        )

        doc2 = DadosGovDocument(
            external_id="DG_SAME",  # Duplicate
            title="Doc 2",
            url="https://dados.gov.br/dg2",
            published_at="2024-12-02",
            content="Data",
            organization="Org",
            category="saude",
        )

        with patch.object(
            integrator.dados_gov, 'fetch_all_priority_datasets', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = {"saude": [doc1, doc2]}

            docs = await integrator.fetch_from_dados_gov(include_recent=False)

            # Should only return one document (deduplicated)
            assert len(docs) == 1
            assert docs[0].external_id == "DG_SAME"

    @pytest.mark.asyncio
    async def test_fetch_from_dados_gov_error(self):
        """Test error handling for dados.gov.br."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator.dados_gov, 'fetch_all_priority_datasets', new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            docs = await integrator.fetch_from_dados_gov()

            assert len(docs) == 0
            health = integrator._health.get(SourceType.DADOS_GOV)
            assert health.consecutive_failures >= 1
            assert "Network error" in health.error_message

    @pytest.mark.asyncio
    async def test_fetch_from_tse_eleicoes(self):
        """Test fetching eleicoes from TSE."""
        integrator = OfficialSourceIntegrator()

        mock_doc = TSEDocument(
            external_id="TSE1",
            title="Eleições 2024",
            url="https://tse.jus.br/e1",
            published_at="2024-10-01",
            content="Electoral data",
            document_type="eleicao",
            ano_eleicao=2024,
        )

        with patch.object(
            integrator.tse, 'search_datasets', new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [mock_doc]

            docs = await integrator.fetch_from_tse(
                include_eleicoes=True,
                include_partidos=False,
                include_prestacao_contas=False,
                ano_eleicao=2024,
            )

            assert len(docs) == 1
            assert docs[0].external_id == "TSE1"
            mock_search.assert_called_once_with(query="eleicoes 2024", rows=20)

    @pytest.mark.asyncio
    async def test_fetch_from_tse_partidos(self):
        """Test fetching partidos from TSE."""
        integrator = OfficialSourceIntegrator()

        mock_doc = TSEDocument(
            external_id="TSE_P1",
            title="Partido Teste",
            url="https://tse.jus.br/p1",
            published_at="2024-01-01",
            content="Party data",
            document_type="partido",
        )

        with patch.object(
            integrator.tse, 'search_partidos_datasets', new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [mock_doc]

            docs = await integrator.fetch_from_tse(
                include_eleicoes=False,
                include_partidos=True,
                include_prestacao_contas=False,
            )

            assert len(docs) == 1
            assert docs[0].document_type == "partido"

    @pytest.mark.asyncio
    async def test_fetch_from_tse_prestacao_contas(self):
        """Test fetching prestacao de contas from TSE."""
        integrator = OfficialSourceIntegrator()

        mock_doc = TSEDocument(
            external_id="TSE_PC1",
            title="Prestação de Contas",
            url="https://tse.jus.br/pc1",
            published_at="2024-12-01",
            content="Financial report",
            document_type="prestacao_contas",
            ano_eleicao=2024,
        )

        with patch.object(
            integrator.tse, 'search_prestacao_contas', new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [mock_doc]

            docs = await integrator.fetch_from_tse(
                include_eleicoes=False,
                include_partidos=False,
                include_prestacao_contas=True,
                ano_eleicao=2024,
            )

            assert len(docs) == 1
            mock_search.assert_called_once_with(ano=2024)

    @pytest.mark.asyncio
    async def test_fetch_from_tse_all_types(self):
        """Test fetching all document types from TSE."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator.tse, 'search_datasets', new_callable=AsyncMock
        ) as mock_eleicoes, patch.object(
            integrator.tse, 'search_partidos_datasets', new_callable=AsyncMock
        ) as mock_partidos, patch.object(
            integrator.tse, 'search_prestacao_contas', new_callable=AsyncMock
        ) as mock_prestacao:
            mock_eleicoes.return_value = [
                TSEDocument("E1", "El", "url", "2024", "c", "eleicao", 2024)
            ]
            mock_partidos.return_value = [
                TSEDocument("P1", "Pa", "url", "2024", "c", "partido")
            ]
            mock_prestacao.return_value = [
                TSEDocument("PC1", "Pr", "url", "2024", "c", "prestacao", 2024)
            ]

            docs = await integrator.fetch_from_tse(
                include_eleicoes=True,
                include_partidos=True,
                include_prestacao_contas=True,
            )

            assert len(docs) == 3

    @pytest.mark.asyncio
    async def test_fetch_from_tse_deduplication(self):
        """Test deduplication for TSE documents."""
        integrator = OfficialSourceIntegrator()

        # Same external_id
        doc1 = TSEDocument(
            external_id="TSE_SAME",
            title="Doc 1",
            url="url1",
            published_at="2024",
            content="c",
            document_type="eleicao",
        )

        doc2 = TSEDocument(
            external_id="TSE_SAME",  # Duplicate
            title="Doc 2",
            url="url2",
            published_at="2024",
            content="c",
            document_type="eleicao",
        )

        with patch.object(
            integrator.tse, 'search_datasets', new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [doc1, doc2]

            docs = await integrator.fetch_from_tse()

            # Should only return one (deduplicated)
            assert len(docs) == 1

    @pytest.mark.asyncio
    async def test_fetch_from_tse_error(self):
        """Test error handling for TSE."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator.tse, 'search_datasets', new_callable=AsyncMock
        ) as mock_search:
            mock_search.side_effect = Exception("TSE API down")

            docs = await integrator.fetch_from_tse()

            assert len(docs) == 0
            health = integrator._health.get(SourceType.TSE)
            assert health.consecutive_failures >= 1

    @pytest.mark.asyncio
    async def test_fetch_all_priority(self):
        """Test fetching from all priority sources."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator, 'fetch_from_gov_br', new_callable=AsyncMock
        ) as mock_gov, patch.object(
            integrator, 'fetch_from_dados_gov', new_callable=AsyncMock
        ) as mock_dados, patch.object(
            integrator, 'fetch_from_tse', new_callable=AsyncMock
        ) as mock_tse:
            mock_gov.return_value = [MagicMock(external_id="G1")]
            mock_dados.return_value = [MagicMock(external_id="D1")]
            mock_tse.return_value = [MagicMock(external_id="T1")]

            results = await integrator.fetch_all_priority(
                gov_br_data_inicial="01/12/2024",
                gov_br_data_final="14/12/2024",
            )

            assert len(results) == 3
            assert SourceType.GOV_BR in results
            assert SourceType.DADOS_GOV in results
            assert SourceType.TSE in results

    @pytest.mark.asyncio
    async def test_fetch_all_priority_no_gov_br_dates(self):
        """Test fetch_all_priority without gov.br dates."""
        integrator = OfficialSourceIntegrator()

        with patch.object(
            integrator, 'fetch_from_dados_gov', new_callable=AsyncMock
        ) as mock_dados, patch.object(
            integrator, 'fetch_from_tse', new_callable=AsyncMock
        ) as mock_tse:
            mock_dados.return_value = []
            mock_tse.return_value = []

            results = await integrator.fetch_all_priority()

            # Gov.br should return empty list
            assert len(results[SourceType.GOV_BR]) == 0

    def test_update_health_success(self):
        """Test health update on success."""
        integrator = OfficialSourceIntegrator()

        integrator._update_health(
            SourceType.GOV_BR,
            success=True,
            latency_ms=150.0,
        )

        health = integrator._health[SourceType.GOV_BR]
        assert health.status == SourceStatus.HEALTHY
        assert health.consecutive_failures == 0
        assert health.last_success is not None
        assert health.error_message is None

    def test_update_health_failure(self):
        """Test health update on failure."""
        integrator = OfficialSourceIntegrator()

        integrator._update_health(
            SourceType.GOV_BR,
            success=False,
            error="Connection timeout",
        )

        health = integrator._health[SourceType.GOV_BR]
        assert health.consecutive_failures == 1
        assert health.error_message == "Connection timeout"

    def test_update_health_degraded(self):
        """Test health transitions to DEGRADED after 2 failures."""
        integrator = OfficialSourceIntegrator()

        integrator._update_health(SourceType.GOV_BR, success=False)
        integrator._update_health(SourceType.GOV_BR, success=False)

        health = integrator._health[SourceType.GOV_BR]
        assert health.status == SourceStatus.DEGRADED
        assert health.consecutive_failures == 2

    def test_update_health_unhealthy(self):
        """Test health transitions to UNHEALTHY after 5 failures."""
        integrator = OfficialSourceIntegrator()

        for _ in range(5):
            integrator._update_health(SourceType.GOV_BR, success=False)

        health = integrator._health[SourceType.GOV_BR]
        assert health.status == SourceStatus.UNHEALTHY
        assert health.consecutive_failures == 5

    def test_update_health_recovery(self):
        """Test health recovery after failures."""
        integrator = OfficialSourceIntegrator()

        # Fail several times
        for _ in range(3):
            integrator._update_health(SourceType.GOV_BR, success=False)

        # Recover
        integrator._update_health(SourceType.GOV_BR, success=True)

        health = integrator._health[SourceType.GOV_BR]
        assert health.status == SourceStatus.HEALTHY
        assert health.consecutive_failures == 0

    def test_check_health(self):
        """Test check_health returns all source statuses."""
        integrator = OfficialSourceIntegrator()

        health_map = integrator.check_health()

        # Should have all source types
        assert SourceType.GOV_BR in health_map
        assert SourceType.DADOS_GOV in health_map
        assert SourceType.TSE in health_map

        # Initially all UNKNOWN
        for health in health_map.values():
            assert health.status == SourceStatus.UNKNOWN

    def test_get_source_health(self):
        """Test getting health for specific source."""
        integrator = OfficialSourceIntegrator()

        # Initially None
        health = integrator.get_source_health(SourceType.GOV_BR)
        assert health is None

        # After update
        integrator._update_health(SourceType.GOV_BR, success=True)
        health = integrator.get_source_health(SourceType.GOV_BR)
        assert health is not None
        assert health.status == SourceStatus.HEALTHY


def test_source_type_enum():
    """Test SourceType enum values."""
    assert SourceType.GOV_BR.value == "gov_br"
    assert SourceType.DADOS_GOV.value == "dados_gov"
    assert SourceType.TSE.value == "tse"


def test_source_status_enum():
    """Test SourceStatus enum values."""
    assert SourceStatus.HEALTHY.value == "healthy"
    assert SourceStatus.DEGRADED.value == "degraded"
    assert SourceStatus.UNHEALTHY.value == "unhealthy"
    assert SourceStatus.UNKNOWN.value == "unknown"
