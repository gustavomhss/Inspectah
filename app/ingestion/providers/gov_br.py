"""
S38-BE-002: Integrador gov.br (Portal da Transparencia, dados abertos)

APIs suportadas:
- Portal da Transparencia: https://api.portaldatransparencia.gov.br/
- Dados Abertos: https://dados.gov.br/api/3/
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class GovBrDocument:
    """Documento extraido de API gov.br."""
    external_id: str
    title: str
    url: str
    published_at: str
    content: str
    source_api: str  # transparencia, dados_abertos
    document_type: str  # contrato, convenio, despesa, etc
    metadata: Dict[str, Any] = field(default_factory=dict)

    def content_hash(self) -> str:
        raw = f"{self.external_id}|{self.title}|{self.content}|{self.published_at}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class GovBrClient:
    """
    Cliente para APIs oficiais do governo brasileiro.

    Endpoints suportados:
    - Portal da Transparencia (contratos, convenios, despesas)
    - Dados.gov.br (datasets abertos)

    Rate limiting: 30 req/min por padrao (conservador)
    Retry: backoff exponencial 1/2/4s com jitter
    """

    TRANSPARENCIA_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
    DADOS_GOV_BASE = "https://dados.gov.br/api/3"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        rate_limit_rpm: int = 30,
    ):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.rate_limit_rpm = rate_limit_rpm
        self._min_interval = 60.0 / rate_limit_rpm

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Inspectah/1.0 (fact-checking platform)",
        }
        if self.api_key:
            headers["chave-api-dados"] = self.api_key
        return headers

    async def _request_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Faz request com retry e backoff exponencial."""
        backoff = 1.0
        last_error: Optional[Exception] = None

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = await client.get(
                        url,
                        params=params,
                        headers=self._headers(),
                    )

                    if response.status_code == 200:
                        await asyncio.sleep(self._min_interval)  # rate limiting
                        return response.json()

                    if response.status_code in (429, 500, 502, 503, 504):
                        logger.warning(
                            f"[gov_br] Retry {attempt}/{self.max_retries} - status {response.status_code}"
                        )
                        if attempt < self.max_retries:
                            await self._sleep_with_jitter(backoff)
                            backoff *= 2
                            continue

                    # 4xx nao-recuperavel
                    logger.error(f"[gov_br] Request failed: {response.status_code} - {url}")
                    return None

                except httpx.HTTPError as e:
                    last_error = e
                    logger.warning(f"[gov_br] HTTP error attempt {attempt}: {e}")
                    if attempt < self.max_retries:
                        await self._sleep_with_jitter(backoff)
                        backoff *= 2
                        continue

        logger.error(f"[gov_br] All retries exhausted: {last_error}")
        return None

    @staticmethod
    async def _sleep_with_jitter(base: float) -> None:
        jitter = random.uniform(0, 0.25)
        await asyncio.sleep(base + jitter)

    # =========================================================================
    # Portal da Transparencia
    # =========================================================================

    async def fetch_contratos(
        self,
        data_inicial: str,
        data_final: str,
        pagina: int = 1,
    ) -> List[GovBrDocument]:
        """
        Busca contratos no Portal da Transparencia.

        Args:
            data_inicial: Data inicial (DD/MM/AAAA)
            data_final: Data final (DD/MM/AAAA)
            pagina: Numero da pagina (1-indexed, must be >= 1)

        Raises:
            ValueError: If pagina < 1
        """
        if pagina < 1:
            raise ValueError(f"pagina must be >= 1, got {pagina}")

        url = f"{self.TRANSPARENCIA_BASE}/contratos"
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "pagina": pagina,
        }

        data = await self._request_with_retry(url, params)
        if not data:
            return []

        documents = []
        for item in data if isinstance(data, list) else []:
            doc = GovBrDocument(
                external_id=str(item.get("id") or item.get("numero", "")),
                title=item.get("objeto", "Contrato sem titulo"),
                url=f"https://portaldatransparencia.gov.br/contratos/{item.get('id', '')}",
                published_at=item.get("dataAssinatura", ""),
                content=item.get("objeto", ""),
                source_api="transparencia",
                document_type="contrato",
                metadata={
                    "orgao": item.get("orgaoSuperior", {}).get("nome"),
                    "valor": item.get("valorInicial"),
                    "fornecedor": item.get("fornecedor", {}).get("nome"),
                },
            )
            documents.append(doc)

        logger.info(f"[gov_br] Fetched {len(documents)} contratos")
        return documents

    async def fetch_despesas(
        self,
        ano: int,
        mes: int,
        pagina: int = 1,
    ) -> List[GovBrDocument]:
        """
        Busca despesas publicas.

        Args:
            ano: Year (e.g., 2024)
            mes: Month (1-12)
            pagina: Page number (1-indexed, must be >= 1)

        Raises:
            ValueError: If pagina < 1, mes invalid, or ano invalid
        """
        if pagina < 1:
            raise ValueError(f"pagina must be >= 1, got {pagina}")
        if not 1 <= mes <= 12:
            raise ValueError(f"mes must be 1-12, got {mes}")
        if ano < 2000 or ano > 2100:
            raise ValueError(f"ano must be between 2000-2100, got {ano}")

        url = f"{self.TRANSPARENCIA_BASE}/despesas/documentos"
        params = {
            "ano": ano,
            "mes": mes,
            "pagina": pagina,
        }

        data = await self._request_with_retry(url, params)
        if not data:
            return []

        documents = []
        for item in data if isinstance(data, list) else []:
            doc = GovBrDocument(
                external_id=str(item.get("id", "")),
                title=f"Despesa {item.get('fase', '')} - {item.get('unidadeGestora', {}).get('nome', '')}",
                url=f"https://portaldatransparencia.gov.br/despesas/{item.get('id', '')}",
                published_at=item.get("data", ""),
                content=item.get("descricao", ""),
                source_api="transparencia",
                document_type="despesa",
                metadata={
                    "valor": item.get("valor"),
                    "fase": item.get("fase"),
                    "orgao": item.get("orgaoSuperior", {}).get("nome"),
                },
            )
            documents.append(doc)

        logger.info(f"[gov_br] Fetched {len(documents)} despesas")
        return documents

    # =========================================================================
    # Dados.gov.br
    # =========================================================================

    async def search_datasets(
        self,
        query: str,
        rows: int = 10,
        start: int = 0,
    ) -> List[GovBrDocument]:
        """
        Busca datasets no portal dados.gov.br.

        Args:
            query: Search query string
            rows: Number of results (1-100)
            start: Offset for pagination (>= 0)

        Raises:
            ValueError: If rows or start invalid
        """
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        if rows < 1 or rows > 100:
            raise ValueError(f"rows must be 1-100, got {rows}")
        if start < 0:
            raise ValueError(f"start must be >= 0, got {start}")

        url = f"{self.DADOS_GOV_BASE}/action/package_search"
        params = {
            "q": query,
            "rows": rows,
            "start": start,
        }

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return []

        documents = []
        results = data.get("result", {}).get("results", [])
        for item in results:
            doc = GovBrDocument(
                external_id=item.get("id", ""),
                title=item.get("title", "Dataset sem titulo"),
                url=f"https://dados.gov.br/dados/conjuntos-dados/{item.get('name', '')}",
                published_at=item.get("metadata_created", ""),
                content=item.get("notes", ""),
                source_api="dados_abertos",
                document_type="dataset",
                metadata={
                    "organization": item.get("organization", {}).get("title"),
                    "tags": [t.get("name") for t in item.get("tags", [])],
                    "resources_count": len(item.get("resources", [])),
                },
            )
            documents.append(doc)

        logger.info(f"[gov_br] Found {len(documents)} datasets for query '{query}'")
        return documents

    async def get_dataset_resources(self, dataset_id: str) -> List[Dict]:
        """Retorna recursos (arquivos) de um dataset."""
        url = f"{self.DADOS_GOV_BASE}/action/package_show"
        params = {"id": dataset_id}

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return []

        return data.get("result", {}).get("resources", [])

    # =========================================================================
    # Health Check (S40-BE-019)
    # =========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on gov.br APIs (S40-BE-019).

        Returns:
            Dict with health status for each API endpoint
        """
        results: Dict[str, Any] = {
            "status": "healthy",
            "checked_at": datetime.now().isoformat(),
            "endpoints": {},
        }

        # Check Portal da Transparencia
        transparencia_ok = await self._check_transparencia_health()
        results["endpoints"]["transparencia"] = {
            "url": self.TRANSPARENCIA_BASE,
            "status": "up" if transparencia_ok else "down",
            "healthy": transparencia_ok,
        }

        # Check Dados.gov.br
        dados_gov_ok = await self._check_dados_gov_health()
        results["endpoints"]["dados_gov"] = {
            "url": self.DADOS_GOV_BASE,
            "status": "up" if dados_gov_ok else "down",
            "healthy": dados_gov_ok,
        }

        # Overall status
        all_healthy = transparencia_ok and dados_gov_ok
        results["status"] = "healthy" if all_healthy else "degraded"
        results["healthy"] = all_healthy

        return results

    async def _check_transparencia_health(self) -> bool:
        """Check Portal da Transparencia API health."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Simple health check - fetch first page of contratos
                response = await client.get(
                    f"{self.TRANSPARENCIA_BASE}/contratos",
                    params={"dataInicial": "01/01/2024", "dataFinal": "01/01/2024", "pagina": 1},
                    headers=self._headers(),
                )
                return response.status_code in (200, 204, 404)  # 404 = no data is OK
        except Exception as e:
            logger.warning(f"[gov_br] Transparencia health check failed: {e}")
            return False

    async def _check_dados_gov_health(self) -> bool:
        """Check Dados.gov.br API health."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Simple health check - status endpoint
                response = await client.get(
                    f"{self.DADOS_GOV_BASE}/action/status_show",
                    headers={"Accept": "application/json"},
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("success", False)
                return False
        except Exception as e:
            logger.warning(f"[gov_br] Dados.gov health check failed: {e}")
            return False

    def is_healthy(self, health_result: Dict[str, Any]) -> bool:
        """Check if health result indicates healthy status."""
        return health_result.get("healthy", False)
