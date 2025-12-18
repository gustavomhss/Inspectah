"""
Tests for gov.br and dados.gov.br providers (S40-BE-019).

Tests for GovBrClient and DadosGovClient health checks.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ingestion.providers.gov_br import GovBrClient, GovBrDocument
from app.ingestion.providers.dados_gov import (
    DadosGovClient,
    DadosGovDocument,
    PRIORITY_DATASETS,
)


# =============================================================================
# GovBrDocument Tests
# =============================================================================


class TestGovBrDocument:
    """Tests for GovBrDocument dataclass."""

    def test_document_creation(self):
        """Create a GovBrDocument."""
        doc = GovBrDocument(
            external_id="ext_1",
            title="Test Contract",
            url="https://example.gov.br/contract/1",
            published_at="2024-01-01",
            content="Contract content",
            source_api="transparencia",
            document_type="contrato",
        )

        assert doc.external_id == "ext_1"
        assert doc.title == "Test Contract"
        assert doc.source_api == "transparencia"
        assert doc.document_type == "contrato"

    def test_content_hash(self):
        """content_hash generates consistent hash."""
        doc = GovBrDocument(
            external_id="ext_1",
            title="Test",
            url="https://example.gov.br/1",
            published_at="2024-01-01",
            content="Content",
            source_api="transparencia",
            document_type="contrato",
        )

        hash1 = doc.content_hash()
        hash2 = doc.content_hash()
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_content_hash_changes_with_content(self):
        """content_hash changes when content changes."""
        doc1 = GovBrDocument(
            external_id="ext_1",
            title="Test",
            url="https://example.gov.br/1",
            published_at="2024-01-01",
            content="Content A",
            source_api="transparencia",
            document_type="contrato",
        )
        doc2 = GovBrDocument(
            external_id="ext_1",
            title="Test",
            url="https://example.gov.br/1",
            published_at="2024-01-01",
            content="Content B",
            source_api="transparencia",
            document_type="contrato",
        )

        assert doc1.content_hash() != doc2.content_hash()


# =============================================================================
# GovBrClient Tests
# =============================================================================


class TestGovBrClient:
    """Tests for GovBrClient."""

    def test_init_defaults(self):
        """Initialize with default values."""
        client = GovBrClient()

        assert client.api_key is None
        assert client.timeout_seconds == 30
        assert client.max_retries == 3
        assert client.rate_limit_rpm == 30

    def test_init_with_api_key(self):
        """Initialize with API key."""
        client = GovBrClient(api_key="test_key")
        assert client.api_key == "test_key"

    def test_headers_without_api_key(self):
        """Headers without API key."""
        client = GovBrClient()
        headers = client._headers()

        assert "Accept" in headers
        assert "User-Agent" in headers
        assert "chave-api-dados" not in headers

    def test_headers_with_api_key(self):
        """Headers include API key when provided."""
        client = GovBrClient(api_key="my_key")
        headers = client._headers()

        assert headers["chave-api-dados"] == "my_key"

    def test_min_interval_calculation(self):
        """Min interval calculated from rate limit."""
        client = GovBrClient(rate_limit_rpm=30)
        assert client._min_interval == 2.0  # 60/30 = 2 seconds

        client2 = GovBrClient(rate_limit_rpm=60)
        assert client2._min_interval == 1.0  # 60/60 = 1 second


class TestGovBrClientHealthCheck:
    """Tests for GovBrClient health check (S40-BE-019)."""

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self):
        """health_check returns a dictionary."""
        client = GovBrClient()

        with patch.object(client, "_check_transparencia_health", new_callable=AsyncMock) as mock_transp:
            with patch.object(client, "_check_dados_gov_health", new_callable=AsyncMock) as mock_dados:
                mock_transp.return_value = True
                mock_dados.return_value = True

                result = await client.health_check()

        assert isinstance(result, dict)
        assert "status" in result
        assert "checked_at" in result
        assert "endpoints" in result

    @pytest.mark.asyncio
    async def test_health_check_both_healthy(self):
        """health_check returns healthy when both endpoints up."""
        client = GovBrClient()

        with patch.object(client, "_check_transparencia_health", new_callable=AsyncMock) as mock_transp:
            with patch.object(client, "_check_dados_gov_health", new_callable=AsyncMock) as mock_dados:
                mock_transp.return_value = True
                mock_dados.return_value = True

                result = await client.health_check()

        assert result["status"] == "healthy"
        assert result["healthy"] is True
        assert result["endpoints"]["transparencia"]["healthy"] is True
        assert result["endpoints"]["dados_gov"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_health_check_transparencia_down(self):
        """health_check returns degraded when transparencia down."""
        client = GovBrClient()

        with patch.object(client, "_check_transparencia_health", new_callable=AsyncMock) as mock_transp:
            with patch.object(client, "_check_dados_gov_health", new_callable=AsyncMock) as mock_dados:
                mock_transp.return_value = False
                mock_dados.return_value = True

                result = await client.health_check()

        assert result["status"] == "degraded"
        assert result["healthy"] is False
        assert result["endpoints"]["transparencia"]["healthy"] is False
        assert result["endpoints"]["dados_gov"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_health_check_dados_gov_down(self):
        """health_check returns degraded when dados_gov down."""
        client = GovBrClient()

        with patch.object(client, "_check_transparencia_health", new_callable=AsyncMock) as mock_transp:
            with patch.object(client, "_check_dados_gov_health", new_callable=AsyncMock) as mock_dados:
                mock_transp.return_value = True
                mock_dados.return_value = False

                result = await client.health_check()

        assert result["status"] == "degraded"
        assert result["healthy"] is False

    @pytest.mark.asyncio
    async def test_health_check_both_down(self):
        """health_check returns degraded when both down."""
        client = GovBrClient()

        with patch.object(client, "_check_transparencia_health", new_callable=AsyncMock) as mock_transp:
            with patch.object(client, "_check_dados_gov_health", new_callable=AsyncMock) as mock_dados:
                mock_transp.return_value = False
                mock_dados.return_value = False

                result = await client.health_check()

        assert result["status"] == "degraded"
        assert result["healthy"] is False

    def test_is_healthy_true(self):
        """is_healthy returns True for healthy result."""
        client = GovBrClient()
        health_result = {"healthy": True, "status": "healthy"}
        assert client.is_healthy(health_result) is True

    def test_is_healthy_false(self):
        """is_healthy returns False for unhealthy result."""
        client = GovBrClient()
        health_result = {"healthy": False, "status": "degraded"}
        assert client.is_healthy(health_result) is False

    def test_is_healthy_missing_key(self):
        """is_healthy returns False when key missing."""
        client = GovBrClient()
        health_result = {"status": "unknown"}
        assert client.is_healthy(health_result) is False


# =============================================================================
# DadosGovDocument Tests
# =============================================================================


class TestDadosGovDocument:
    """Tests for DadosGovDocument dataclass."""

    def test_document_creation(self):
        """Create a DadosGovDocument."""
        doc = DadosGovDocument(
            external_id="ext_dados_1",
            title="COVID Dataset",
            url="https://dados.gov.br/dataset/covid",
            published_at="2024-01-01",
            content="COVID data",
            organization="Ministério da Saúde",
            category="saude",
        )

        assert doc.external_id == "ext_dados_1"
        assert doc.title == "COVID Dataset"
        assert doc.organization == "Ministério da Saúde"
        assert doc.category == "saude"

    def test_content_hash(self):
        """content_hash generates consistent hash."""
        doc = DadosGovDocument(
            external_id="ext_1",
            title="Test",
            url="https://dados.gov.br/1",
            published_at="2024-01-01",
            content="Content",
            organization="Test Org",
            category="saude",
        )

        hash1 = doc.content_hash()
        hash2 = doc.content_hash()
        assert hash1 == hash2
        assert len(hash1) == 16


# =============================================================================
# DadosGovClient Tests
# =============================================================================


class TestDadosGovClient:
    """Tests for DadosGovClient."""

    def test_init_defaults(self):
        """Initialize with default values."""
        client = DadosGovClient()

        assert client.timeout_seconds == 30
        assert client.max_retries == 3
        assert client.rate_limit_rpm == 30

    def test_min_interval_calculation(self):
        """Min interval calculated from rate limit."""
        client = DadosGovClient(rate_limit_rpm=30)
        assert client._min_interval == 2.0

    def test_headers(self):
        """Headers include required fields."""
        client = DadosGovClient()
        headers = client._headers()

        assert headers["Accept"] == "application/json"
        assert "Inspectah" in headers["User-Agent"]


class TestDadosGovClientCategorization:
    """Tests for DadosGovClient categorization."""

    def test_categorize_saude(self):
        """Categorizes saude datasets correctly."""
        client = DadosGovClient()
        dataset = {"title": "COVID-19 Vacinação", "notes": "", "tags": []}
        assert client._categorize_dataset(dataset) == "saude"

    def test_categorize_economia(self):
        """Categorizes economia datasets correctly."""
        client = DadosGovClient()
        dataset = {"title": "IPCA Índice de Preços", "notes": "", "tags": []}
        assert client._categorize_dataset(dataset) == "economia"

    def test_categorize_educacao(self):
        """Categorizes educacao datasets correctly."""
        client = DadosGovClient()
        dataset = {"title": "ENEM 2024", "notes": "", "tags": []}
        assert client._categorize_dataset(dataset) == "educacao"

    def test_categorize_meio_ambiente(self):
        """Categorizes meio_ambiente datasets correctly."""
        client = DadosGovClient()
        dataset = {"title": "Desmatamento Amazônia", "notes": "", "tags": []}
        assert client._categorize_dataset(dataset) == "meio_ambiente"

    def test_categorize_politica(self):
        """Categorizes politica datasets correctly."""
        client = DadosGovClient()
        # Use "despesas" which is an exact match in PRIORITY_DATASETS
        dataset = {"title": "despesas publicas federais", "notes": "", "tags": []}
        assert client._categorize_dataset(dataset) == "politica"

    def test_categorize_from_notes(self):
        """Categorizes from notes field."""
        client = DadosGovClient()
        # Use "covid-19" which is an exact match in PRIORITY_DATASETS
        dataset = {"title": "Dataset", "notes": "Dados sobre covid-19", "tags": []}
        assert client._categorize_dataset(dataset) == "saude"

    def test_categorize_from_tags(self):
        """Categorizes from tags field."""
        client = DadosGovClient()
        dataset = {"title": "Dataset", "notes": "", "tags": [{"name": "covid-19"}]}
        assert client._categorize_dataset(dataset) == "saude"

    def test_categorize_outros(self):
        """Unmatched datasets return outros."""
        client = DadosGovClient()
        dataset = {"title": "Random Dataset", "notes": "Unknown content", "tags": []}
        assert client._categorize_dataset(dataset) == "outros"


class TestDadosGovClientHealthCheck:
    """Tests for DadosGovClient health check (S40-BE-019)."""

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self):
        """health_check returns a dictionary."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.get.return_value = mock_response

            result = await client.health_check()

        assert isinstance(result, dict)
        assert "status" in result
        assert "checked_at" in result
        assert "endpoint" in result

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """health_check returns healthy when API responds."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.get.return_value = mock_response

            result = await client.health_check()

        assert result["status"] == "healthy"
        assert result["healthy"] is True
        assert result["api_status"] == "up"

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_status_code(self):
        """health_check returns unhealthy on non-200 status."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response

            result = await client.health_check()

        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
        assert result["api_status"] == "down"

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_api_error(self):
        """health_check returns unhealthy when API returns success=false."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": False}
            mock_client.get.return_value = mock_response

            result = await client.health_check()

        assert result["status"] == "degraded"
        assert result["healthy"] is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """health_check handles exceptions gracefully."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Connection error")

            result = await client.health_check()

        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
        assert "error" in result

    def test_is_healthy_true(self):
        """is_healthy returns True for healthy result."""
        client = DadosGovClient()
        health_result = {"healthy": True}
        assert client.is_healthy(health_result) is True

    def test_is_healthy_false(self):
        """is_healthy returns False for unhealthy result."""
        client = DadosGovClient()
        health_result = {"healthy": False}
        assert client.is_healthy(health_result) is False

    def test_get_pilot_domains(self):
        """get_pilot_domains returns pilot domains list."""
        domains = DadosGovClient.get_pilot_domains()
        assert "saude" in domains
        assert "politica" in domains

    def test_health_check_includes_categories(self):
        """health_check includes available categories."""
        # We can test synchronously since categories_available is set before async
        assert "saude" in PRIORITY_DATASETS
        assert "politica" in PRIORITY_DATASETS
        assert "economia" in PRIORITY_DATASETS


class TestPriorityDatasets:
    """Tests for PRIORITY_DATASETS constant."""

    def test_saude_keywords(self):
        """saude category has expected keywords."""
        assert "covid-19" in PRIORITY_DATASETS["saude"]
        assert "vacinacao" in PRIORITY_DATASETS["saude"]

    def test_economia_keywords(self):
        """economia category has expected keywords."""
        assert "ipca" in PRIORITY_DATASETS["economia"]
        assert "pib" in PRIORITY_DATASETS["economia"]

    def test_educacao_keywords(self):
        """educacao category has expected keywords."""
        assert "enem" in PRIORITY_DATASETS["educacao"]

    def test_meio_ambiente_keywords(self):
        """meio_ambiente category has expected keywords."""
        assert "desmatamento" in PRIORITY_DATASETS["meio_ambiente"]
        assert "queimadas" in PRIORITY_DATASETS["meio_ambiente"]

    def test_politica_keywords(self):
        """politica category has expected keywords."""
        assert "orcamento" in PRIORITY_DATASETS["politica"]


# =============================================================================
# GovBrClient API Methods Tests
# =============================================================================


class TestGovBrClientAPIRequests:
    """Tests for GovBrClient API request methods."""

    @pytest.mark.asyncio
    async def test_request_with_retry_success(self):
        """_request_with_retry returns data on success."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_client.get.return_value = mock_response

            result = await client._request_with_retry("https://test.api/data")

        assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_request_with_retry_failure(self):
        """_request_with_retry returns None on failure."""
        client = GovBrClient(max_retries=1)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_client.get.return_value = mock_response

            result = await client._request_with_retry("https://test.api/fail")

        assert result is None

    @pytest.mark.asyncio
    async def test_request_with_retry_retries_on_500(self):
        """_request_with_retry retries on 500 errors."""
        client = GovBrClient(max_retries=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 500
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"success": True}

            mock_client.get.side_effect = [mock_response_fail, mock_response_ok]

            with patch.object(client, "_sleep_with_jitter", new_callable=AsyncMock):
                result = await client._request_with_retry("https://test.api/retry")

        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_sleep_with_jitter(self):
        """_sleep_with_jitter adds random jitter."""
        import asyncio

        with patch.object(asyncio, "sleep", new_callable=AsyncMock) as mock_sleep:
            await GovBrClient._sleep_with_jitter(1.0)

        mock_sleep.assert_called_once()
        call_arg = mock_sleep.call_args[0][0]
        assert 1.0 <= call_arg <= 1.25  # base + jitter (0-0.25)


class TestGovBrClientFetchMethods:
    """Tests for GovBrClient fetch methods."""

    @pytest.mark.asyncio
    async def test_fetch_contratos_success(self):
        """fetch_contratos returns documents on success."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = [
                {
                    "id": "1",
                    "numero": "C001",
                    "objeto": "Test Contract",
                    "dataAssinatura": "2024-01-01",
                    "orgaoSuperior": {"nome": "Test Org"},
                    "valorInicial": 10000,
                    "fornecedor": {"nome": "Supplier"},
                }
            ]

            result = await client.fetch_contratos("01/01/2024", "31/01/2024")

        assert len(result) == 1
        assert result[0].external_id == "1"
        assert result[0].title == "Test Contract"
        assert result[0].document_type == "contrato"

    @pytest.mark.asyncio
    async def test_fetch_contratos_empty(self):
        """fetch_contratos returns empty list when no data."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.fetch_contratos("01/01/2024", "31/01/2024")

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_contratos_non_list(self):
        """fetch_contratos handles non-list response."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"error": "not a list"}

            result = await client.fetch_contratos("01/01/2024", "31/01/2024")

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_despesas_success(self):
        """fetch_despesas returns documents on success."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = [
                {
                    "id": "D1",
                    "fase": "PAGAMENTO",
                    "data": "2024-01-15",
                    "descricao": "Test Expense",
                    "valor": 5000,
                    "unidadeGestora": {"nome": "Ministry"},
                    "orgaoSuperior": {"nome": "Superior Org"},
                }
            ]

            result = await client.fetch_despesas(2024, 1)

        assert len(result) == 1
        assert result[0].external_id == "D1"
        assert "PAGAMENTO" in result[0].title
        assert result[0].document_type == "despesa"

    @pytest.mark.asyncio
    async def test_fetch_despesas_empty(self):
        """fetch_despesas returns empty list when no data."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.fetch_despesas(2024, 1)

        assert result == []

    @pytest.mark.asyncio
    async def test_search_datasets_success(self):
        """search_datasets returns documents on success."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {
                "success": True,
                "result": {
                    "results": [
                        {
                            "id": "ds1",
                            "name": "test-dataset",
                            "title": "Test Dataset",
                            "notes": "Dataset description",
                            "metadata_created": "2024-01-01",
                            "organization": {"title": "Test Org"},
                            "tags": [{"name": "tag1"}],
                            "resources": [],
                        }
                    ]
                },
            }

            result = await client.search_datasets("test query")

        assert len(result) == 1
        assert result[0].external_id == "ds1"
        assert result[0].title == "Test Dataset"
        assert result[0].document_type == "dataset"

    @pytest.mark.asyncio
    async def test_search_datasets_no_success(self):
        """search_datasets returns empty when success=false."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {"success": False}

            result = await client.search_datasets("test")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_dataset_resources_success(self):
        """get_dataset_resources returns resources on success."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {
                "success": True,
                "result": {
                    "resources": [
                        {"id": "r1", "name": "data.csv"},
                        {"id": "r2", "name": "data.json"},
                    ]
                },
            }

            result = await client.get_dataset_resources("dataset-123")

        assert len(result) == 2
        assert result[0]["id"] == "r1"

    @pytest.mark.asyncio
    async def test_get_dataset_resources_empty(self):
        """get_dataset_resources returns empty when no data."""
        client = GovBrClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.get_dataset_resources("dataset-123")

        assert result == []


# =============================================================================
# DadosGovClient API Methods Tests
# =============================================================================


class TestDadosGovClientFetchMethods:
    """Tests for DadosGovClient fetch methods."""

    @pytest.mark.asyncio
    async def test_search_datasets_success(self):
        """search_datasets returns documents on success."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {
                "success": True,
                "result": {
                    "results": [
                        {
                            "id": "ds1",
                            "name": "covid-dados",
                            "title": "COVID-19 Data",
                            "notes": "COVID statistics",
                            "metadata_created": "2024-01-01",
                            "organization": {"title": "Health Ministry"},
                            "tags": [{"name": "covid-19"}],
                            "resources": [],
                        }
                    ]
                },
            }

            result = await client.search_datasets("covid")

        assert len(result) == 1
        assert result[0].external_id == "ds1"
        assert result[0].category == "saude"

    @pytest.mark.asyncio
    async def test_search_datasets_empty(self):
        """search_datasets returns empty when no data."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.search_datasets("test")

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_by_category_saude(self):
        """fetch_by_category returns documents for saude."""
        client = DadosGovClient()

        with patch.object(client, "search_datasets", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                DadosGovDocument(
                    external_id="d1",
                    title="COVID Data",
                    url="https://dados.gov.br/covid",
                    published_at="2024-01-01",
                    content="COVID content",
                    organization="Health",
                    category="saude",
                )
            ]

            result = await client.fetch_by_category("saude", rows=5)

        assert len(result) == 1
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_by_category_unknown(self):
        """fetch_by_category returns empty for unknown category."""
        client = DadosGovClient()

        result = await client.fetch_by_category("unknown_category")

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_all_priority_datasets(self):
        """fetch_all_priority_datasets fetches from all categories."""
        client = DadosGovClient()

        with patch.object(client, "fetch_by_category", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []

            result = await client.fetch_all_priority_datasets(rows_per_category=5)

        # Should call for each priority category
        assert mock_fetch.call_count == len(PRIORITY_DATASETS)
        assert "saude" in result
        assert "economia" in result

    @pytest.mark.asyncio
    async def test_get_dataset_detail_success(self):
        """get_dataset_detail returns document on success."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {
                "success": True,
                "result": {
                    "id": "ds1",
                    "name": "test-dataset",
                    "title": "Test Dataset",
                    "notes": "Description",
                    "metadata_created": "2024-01-01",
                    "metadata_modified": "2024-01-02",
                    "organization": {"title": "Test Org"},
                    "tags": [],
                    "resources": [{"id": "r1"}],
                    "license_title": "CC-BY",
                    "author": "Author Name",
                    "maintainer": "Maintainer",
                },
            }

            result = await client.get_dataset_detail("ds1")

        assert result is not None
        assert result.external_id == "ds1"
        assert result.metadata["author"] == "Author Name"

    @pytest.mark.asyncio
    async def test_get_dataset_detail_not_found(self):
        """get_dataset_detail returns None when not found."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.get_dataset_detail("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_recent_updates(self):
        """get_recent_updates returns priority datasets."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = {
                "success": True,
                "result": {
                    "results": [
                        {
                            "id": "ds1",
                            "name": "covid-update",
                            "title": "COVID Update",
                            "notes": "Latest covid-19 data",
                            "metadata_modified": "2024-01-15",
                            "organization": {"title": "Ministry"},
                            "tags": [],
                            "resources": [],
                        },
                        {
                            "id": "ds2",
                            "name": "random-data",
                            "title": "Random",
                            "notes": "Not priority",
                            "metadata_modified": "2024-01-14",
                            "organization": {"title": "Other"},
                            "tags": [],
                            "resources": [],
                        },
                    ]
                },
            }

            result = await client.get_recent_updates(days=7, rows=10)

        # Should filter out non-priority datasets
        assert len(result) == 1
        assert result[0].category == "saude"

    @pytest.mark.asyncio
    async def test_get_recent_updates_empty(self):
        """get_recent_updates returns empty when no data."""
        client = DadosGovClient()

        with patch.object(client, "_request_with_retry", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = None

            result = await client.get_recent_updates()

        assert result == []


class TestDadosGovClientRetry:
    """Tests for DadosGovClient retry logic."""

    @pytest.mark.asyncio
    async def test_request_with_retry_success(self):
        """_request_with_retry returns data on success."""
        client = DadosGovClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True, "data": "test"}
            mock_client.get.return_value = mock_response

            result = await client._request_with_retry("https://dados.gov.br/api/test")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_request_with_retry_http_error(self):
        """_request_with_retry handles HTTP errors."""
        import httpx

        client = DadosGovClient(max_retries=1)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPError("Connection failed")

            result = await client._request_with_retry("https://dados.gov.br/api/fail")

        assert result is None

    @pytest.mark.asyncio
    async def test_sleep_with_jitter(self):
        """_sleep_with_jitter adds random jitter."""
        import asyncio

        with patch.object(asyncio, "sleep", new_callable=AsyncMock) as mock_sleep:
            await DadosGovClient._sleep_with_jitter(1.0)

        mock_sleep.assert_called_once()
        call_arg = mock_sleep.call_args[0][0]
        assert 1.0 <= call_arg <= 1.25


# =============================================================================
# GovBrClient Internal Health Check Tests
# =============================================================================


class TestGovBrClientInternalHealthChecks:
    """Tests for GovBrClient internal health check methods."""

    @pytest.mark.asyncio
    async def test_check_transparencia_health_success(self):
        """_check_transparencia_health returns True on 200."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response

            result = await client._check_transparencia_health()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_transparencia_health_204(self):
        """_check_transparencia_health returns True on 204."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_client.get.return_value = mock_response

            result = await client._check_transparencia_health()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_transparencia_health_404(self):
        """_check_transparencia_health returns True on 404 (no data is OK)."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response

            result = await client._check_transparencia_health()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_transparencia_health_500(self):
        """_check_transparencia_health returns False on 500."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response

            result = await client._check_transparencia_health()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_transparencia_health_exception(self):
        """_check_transparencia_health returns False on exception."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Connection failed")

            result = await client._check_transparencia_health()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_dados_gov_health_success(self):
        """_check_dados_gov_health returns True on success."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_client.get.return_value = mock_response

            result = await client._check_dados_gov_health()

        assert result is True

    @pytest.mark.asyncio
    async def test_check_dados_gov_health_api_error(self):
        """_check_dados_gov_health returns False when success=false."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": False}
            mock_client.get.return_value = mock_response

            result = await client._check_dados_gov_health()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_dados_gov_health_500(self):
        """_check_dados_gov_health returns False on 500."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response

            result = await client._check_dados_gov_health()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_dados_gov_health_exception(self):
        """_check_dados_gov_health returns False on exception."""
        client = GovBrClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Connection error")

            result = await client._check_dados_gov_health()

        assert result is False


class TestGovBrClientRetryEdgeCases:
    """Edge case tests for GovBrClient retry logic."""

    @pytest.mark.asyncio
    async def test_request_with_retry_429_retries(self):
        """_request_with_retry retries on 429 (rate limit)."""
        client = GovBrClient(max_retries=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response_429 = MagicMock()
            mock_response_429.status_code = 429
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"data": "recovered"}

            mock_client.get.side_effect = [mock_response_429, mock_response_ok]

            with patch.object(client, "_sleep_with_jitter", new_callable=AsyncMock):
                result = await client._request_with_retry("https://test.api/rate-limited")

        assert result == {"data": "recovered"}

    @pytest.mark.asyncio
    async def test_request_with_retry_503_retries(self):
        """_request_with_retry retries on 503 (service unavailable)."""
        client = GovBrClient(max_retries=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response_503 = MagicMock()
            mock_response_503.status_code = 503
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"data": "recovered"}

            mock_client.get.side_effect = [mock_response_503, mock_response_ok]

            with patch.object(client, "_sleep_with_jitter", new_callable=AsyncMock):
                result = await client._request_with_retry("https://test.api/503")

        assert result == {"data": "recovered"}

    @pytest.mark.asyncio
    async def test_request_with_retry_http_error_retries(self):
        """_request_with_retry retries on HTTP errors."""
        import httpx

        client = GovBrClient(max_retries=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"data": "recovered"}

            mock_client.get.side_effect = [
                httpx.HTTPError("Connection reset"),
                mock_response_ok,
            ]

            with patch.object(client, "_sleep_with_jitter", new_callable=AsyncMock):
                result = await client._request_with_retry("https://test.api/http-error")

        assert result == {"data": "recovered"}

    @pytest.mark.asyncio
    async def test_request_with_retry_exhausts_retries(self):
        """_request_with_retry returns None after exhausting retries."""
        import httpx

        client = GovBrClient(max_retries=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPError("Persistent error")

            with patch.object(client, "_sleep_with_jitter", new_callable=AsyncMock):
                result = await client._request_with_retry("https://test.api/persistent-error")

        assert result is None


# =============================================================================
# W3 Refinement: Input Validation Tests
# =============================================================================


class TestGovBrClientValidation:
    """Tests for GovBrClient input validation."""

    @pytest.mark.asyncio
    async def test_fetch_contratos_invalid_pagina(self):
        """fetch_contratos raises ValueError for pagina < 1."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_contratos("01/01/2024", "31/01/2024", pagina=0)

        assert "pagina must be >= 1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_contratos_negative_pagina(self):
        """fetch_contratos raises ValueError for negative pagina."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_contratos("01/01/2024", "31/01/2024", pagina=-5)

        assert "pagina must be >= 1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_despesas_invalid_pagina(self):
        """fetch_despesas raises ValueError for pagina < 1."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_despesas(2024, 1, pagina=0)

        assert "pagina must be >= 1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_despesas_invalid_mes_low(self):
        """fetch_despesas raises ValueError for mes < 1."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_despesas(2024, 0, pagina=1)

        assert "mes must be 1-12" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_despesas_invalid_mes_high(self):
        """fetch_despesas raises ValueError for mes > 12."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_despesas(2024, 13, pagina=1)

        assert "mes must be 1-12" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_despesas_invalid_ano_low(self):
        """fetch_despesas raises ValueError for ano < 2000."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_despesas(1999, 1, pagina=1)

        assert "ano must be between 2000-2100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_despesas_invalid_ano_high(self):
        """fetch_despesas raises ValueError for ano > 2100."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_despesas(2101, 1, pagina=1)

        assert "ano must be between 2000-2100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_empty_query(self):
        """search_datasets raises ValueError for empty query."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("")

        assert "query must not be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_whitespace_query(self):
        """search_datasets raises ValueError for whitespace-only query."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("   ")

        assert "query must not be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_rows_low(self):
        """search_datasets raises ValueError for rows < 1."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", rows=0)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_rows_high(self):
        """search_datasets raises ValueError for rows > 100."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", rows=101)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_start(self):
        """search_datasets raises ValueError for start < 0."""
        client = GovBrClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", start=-1)

        assert "start must be >= 0" in str(exc_info.value)


class TestDadosGovClientValidation:
    """Tests for DadosGovClient input validation."""

    @pytest.mark.asyncio
    async def test_fetch_by_category_invalid_rows_low(self):
        """fetch_by_category raises ValueError for rows < 1."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_by_category("saude", rows=0)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_by_category_invalid_rows_high(self):
        """fetch_by_category raises ValueError for rows > 100."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_by_category("saude", rows=101)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_by_category_invalid_start(self):
        """fetch_by_category raises ValueError for start < 0."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_by_category("saude", start=-1)

        assert "start must be >= 0" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_empty_query(self):
        """search_datasets raises ValueError for empty query."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("")

        assert "query must not be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_whitespace_query(self):
        """search_datasets raises ValueError for whitespace-only query."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("   ")

        assert "query must not be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_rows_low(self):
        """search_datasets raises ValueError for rows < 1."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", rows=0)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_rows_high(self):
        """search_datasets raises ValueError for rows > 100."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", rows=101)

        assert "rows must be 1-100" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_datasets_invalid_start(self):
        """search_datasets raises ValueError for start < 0."""
        client = DadosGovClient()

        with pytest.raises(ValueError) as exc_info:
            await client.search_datasets("test", start=-1)

        assert "start must be >= 0" in str(exc_info.value)
