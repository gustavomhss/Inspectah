"""
S38-BE-002: Integrador Dados.gov.br (Portal de Dados Abertos)

Especializado em datasets de interesse para fact-checking:
- Saude (COVID, vacinacao, epidemias)
- Economia (inflacao, PIB, emprego)
- Educacao (ENEM, Censo Escolar)
- Meio Ambiente (desmatamento, queimadas)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


# Datasets de interesse para fact-checking
PRIORITY_DATASETS = {
    "saude": [
        "covid-19",
        "vacinacao",
        "sus",
        "anvisa",
        "vigilancia-sanitaria",
    ],
    "economia": [
        "ipca",
        "pib",
        "caged",
        "desemprego",
        "inflacao",
        "salario-minimo",
    ],
    "educacao": [
        "enem",
        "censo-escolar",
        "ideb",
        "alfabetizacao",
    ],
    "meio_ambiente": [
        "desmatamento",
        "queimadas",
        "ibama",
        "icmbio",
    ],
    "politica": [
        "orcamento",
        "despesas",
        "receitas",
        "servidores",
    ],
}


@dataclass
class DadosGovDocument:
    """Documento extraido do portal dados.gov.br."""
    external_id: str
    title: str
    url: str
    published_at: str
    content: str
    organization: str
    category: str  # saude, economia, educacao, etc
    metadata: Dict[str, Any] = field(default_factory=dict)

    def content_hash(self) -> str:
        raw = f"{self.external_id}|{self.title}|{self.content}|{self.published_at}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class DadosGovClient:
    """
    Cliente especializado para dados.gov.br.

    Diferente do cliente generico em gov_br.py, este cliente:
    - Foca em datasets de interesse para fact-checking
    - Categoriza automaticamente por tema
    - Monitora atualizacoes de datasets prioritarios

    Rate limiting: 30 req/min
    """

    BASE_URL = "https://dados.gov.br/api/3"

    def __init__(
        self,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        rate_limit_rpm: int = 30,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.rate_limit_rpm = rate_limit_rpm
        self._min_interval = 60.0 / rate_limit_rpm

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": "Inspectah/1.0 (fact-checking platform)",
        }

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
                        await asyncio.sleep(self._min_interval)
                        return response.json()

                    if response.status_code in (429, 500, 502, 503, 504):
                        logger.warning(
                            f"[dados_gov] Retry {attempt}/{self.max_retries} - status {response.status_code}"
                        )
                        if attempt < self.max_retries:
                            await self._sleep_with_jitter(backoff)
                            backoff *= 2
                            continue

                    logger.error(f"[dados_gov] Request failed: {response.status_code} - {url}")
                    return None

                except httpx.HTTPError as e:
                    last_error = e
                    logger.warning(f"[dados_gov] HTTP error attempt {attempt}: {e}")
                    if attempt < self.max_retries:
                        await self._sleep_with_jitter(backoff)
                        backoff *= 2
                        continue

        logger.error(f"[dados_gov] All retries exhausted: {last_error}")
        return None

    @staticmethod
    async def _sleep_with_jitter(base: float) -> None:
        jitter = random.uniform(0, 0.25)
        await asyncio.sleep(base + jitter)

    def _categorize_dataset(self, dataset: Dict) -> str:
        """Categoriza dataset por tema."""
        title = (dataset.get("title") or "").lower()
        notes = (dataset.get("notes") or "").lower()
        tags = [t.get("name", "").lower() for t in dataset.get("tags", [])]

        combined = f"{title} {notes} {' '.join(tags)}"

        for category, keywords in PRIORITY_DATASETS.items():
            for keyword in keywords:
                if keyword in combined:
                    return category

        return "outros"

    # =========================================================================
    # Busca por Categoria
    # =========================================================================

    async def fetch_by_category(
        self,
        category: str,
        rows: int = 20,
        start: int = 0,
    ) -> List[DadosGovDocument]:
        """
        Busca datasets de uma categoria especifica.

        Args:
            category: saude, economia, educacao, meio_ambiente, politica
            rows: numero de resultados (1-100)
            start: offset para paginacao (>= 0)

        Raises:
            ValueError: If rows or start invalid
        """
        if rows < 1 or rows > 100:
            raise ValueError(f"rows must be 1-100, got {rows}")
        if start < 0:
            raise ValueError(f"start must be >= 0, got {start}")

        keywords = PRIORITY_DATASETS.get(category, [])
        if not keywords:
            logger.warning(f"[dados_gov] Unknown category: {category}")
            return []

        query = " OR ".join(keywords)
        return await self.search_datasets(query=query, rows=rows, start=start)

    async def fetch_all_priority_datasets(
        self,
        rows_per_category: int = 10,
    ) -> Dict[str, List[DadosGovDocument]]:
        """Busca datasets de todas as categorias prioritarias."""
        results = {}
        for category in PRIORITY_DATASETS:
            docs = await self.fetch_by_category(category, rows=rows_per_category)
            results[category] = docs
            logger.info(f"[dados_gov] Category '{category}': {len(docs)} datasets")

        return results

    # =========================================================================
    # Busca Geral
    # =========================================================================

    async def search_datasets(
        self,
        query: str,
        rows: int = 10,
        start: int = 0,
    ) -> List[DadosGovDocument]:
        """
        Busca datasets no portal dados.gov.br.

        Args:
            query: Search query string
            rows: Number of results (1-100)
            start: Offset for pagination (>= 0)

        Raises:
            ValueError: If query empty, rows or start invalid
        """
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        if rows < 1 or rows > 100:
            raise ValueError(f"rows must be 1-100, got {rows}")
        if start < 0:
            raise ValueError(f"start must be >= 0, got {start}")

        url = f"{self.BASE_URL}/action/package_search"
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
            category = self._categorize_dataset(item)
            org = item.get("organization") or {}

            doc = DadosGovDocument(
                external_id=item.get("id", ""),
                title=item.get("title", "Dataset sem titulo"),
                url=f"https://dados.gov.br/dados/conjuntos-dados/{item.get('name', '')}",
                published_at=item.get("metadata_created", ""),
                content=item.get("notes", ""),
                organization=org.get("title", ""),
                category=category,
                metadata={
                    "tags": [t.get("name") for t in item.get("tags", [])],
                    "resources_count": len(item.get("resources", [])),
                    "license": item.get("license_title"),
                    "last_modified": item.get("metadata_modified"),
                },
            )
            documents.append(doc)

        logger.info(f"[dados_gov] Found {len(documents)} datasets for query '{query}'")
        return documents

    async def get_dataset_detail(self, dataset_id: str) -> Optional[DadosGovDocument]:
        """Retorna detalhes completos de um dataset."""
        url = f"{self.BASE_URL}/action/package_show"
        params = {"id": dataset_id}

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return None

        item = data.get("result", {})
        category = self._categorize_dataset(item)
        org = item.get("organization") or {}

        return DadosGovDocument(
            external_id=item.get("id", ""),
            title=item.get("title", ""),
            url=f"https://dados.gov.br/dados/conjuntos-dados/{item.get('name', '')}",
            published_at=item.get("metadata_created", ""),
            content=item.get("notes", ""),
            organization=org.get("title", ""),
            category=category,
            metadata={
                "tags": [t.get("name") for t in item.get("tags", [])],
                "resources": item.get("resources", []),
                "license": item.get("license_title"),
                "last_modified": item.get("metadata_modified"),
                "author": item.get("author"),
                "maintainer": item.get("maintainer"),
            },
        )

    async def get_recent_updates(
        self,
        days: int = 7,
        rows: int = 50,
    ) -> List[DadosGovDocument]:
        """Busca datasets atualizados recentemente."""
        # Busca por data de modificacao (sort by metadata_modified)
        url = f"{self.BASE_URL}/action/package_search"
        params = {
            "q": "*:*",
            "rows": rows,
            "sort": "metadata_modified desc",
        }

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return []

        documents = []
        results = data.get("result", {}).get("results", [])
        for item in results:
            category = self._categorize_dataset(item)
            # Filtrar apenas categorias de interesse
            if category == "outros":
                continue

            org = item.get("organization") or {}
            doc = DadosGovDocument(
                external_id=item.get("id", ""),
                title=item.get("title", ""),
                url=f"https://dados.gov.br/dados/conjuntos-dados/{item.get('name', '')}",
                published_at=item.get("metadata_modified", ""),
                content=item.get("notes", ""),
                organization=org.get("title", ""),
                category=category,
                metadata={
                    "tags": [t.get("name") for t in item.get("tags", [])],
                    "resources_count": len(item.get("resources", [])),
                },
            )
            documents.append(doc)

        logger.info(f"[dados_gov] Found {len(documents)} recently updated priority datasets")
        return documents

    # =========================================================================
    # Health Check (S40-BE-019)
    # =========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on dados.gov.br API (S40-BE-019).

        Returns:
            Dict with health status
        """
        from datetime import datetime

        results: Dict[str, Any] = {
            "status": "healthy",
            "checked_at": datetime.now().isoformat(),
            "endpoint": self.BASE_URL,
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.BASE_URL}/action/status_show",
                    headers=self._headers(),
                )

                if response.status_code == 200:
                    data = response.json()
                    api_healthy = data.get("success", False)
                    results["api_status"] = "up" if api_healthy else "degraded"
                    results["healthy"] = api_healthy
                    results["status"] = "healthy" if api_healthy else "degraded"
                else:
                    results["api_status"] = "down"
                    results["healthy"] = False
                    results["status"] = "unhealthy"
                    results["error"] = f"HTTP {response.status_code}"

        except Exception as e:
            logger.warning(f"[dados_gov] Health check failed: {e}")
            results["api_status"] = "error"
            results["healthy"] = False
            results["status"] = "unhealthy"
            results["error"] = str(e)

        # Check category availability
        results["categories_available"] = list(PRIORITY_DATASETS.keys())

        return results

    def is_healthy(self, health_result: Dict[str, Any]) -> bool:
        """Check if health result indicates healthy status."""
        return health_result.get("healthy", False)

    @staticmethod
    def get_pilot_domains() -> List[str]:
        """Get list of pilot domains supported (S40-BE-019)."""
        return ["saude", "politica"]
