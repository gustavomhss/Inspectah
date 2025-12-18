"""
S38-BE-002b: Integrador TSE (Tribunal Superior Eleitoral)

APIs suportadas:
- Dados Abertos TSE: https://dadosabertos.tse.jus.br/
- API de Candidatos e Resultados
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


@dataclass
class TSEDocument:
    """Documento extraido da API do TSE."""
    external_id: str
    title: str
    url: str
    published_at: str
    content: str
    document_type: str  # candidato, eleicao, partido, prestacao_contas
    ano_eleicao: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def content_hash(self) -> str:
        raw = f"{self.external_id}|{self.title}|{self.content}|{self.ano_eleicao}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class TSEClient:
    """
    Cliente para APIs do TSE (Tribunal Superior Eleitoral).

    Endpoints suportados:
    - Dados abertos (CSV/JSON)
    - API de candidatos
    - API de resultados eleitorais

    Rate limiting: 20 req/min (conservador)
    """

    BASE_URL = "https://dadosabertos.tse.jus.br/api/3"
    DIVULGACAO_URL = "https://resultados.tse.jus.br/oficial"

    def __init__(
        self,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        rate_limit_rpm: int = 20,
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
                            f"[tse] Retry {attempt}/{self.max_retries} - status {response.status_code}"
                        )
                        if attempt < self.max_retries:
                            await self._sleep_with_jitter(backoff)
                            backoff *= 2
                            continue

                    logger.error(f"[tse] Request failed: {response.status_code} - {url}")
                    return None

                except httpx.HTTPError as e:
                    last_error = e
                    logger.warning(f"[tse] HTTP error attempt {attempt}: {e}")
                    if attempt < self.max_retries:
                        await self._sleep_with_jitter(backoff)
                        backoff *= 2
                        continue

        logger.error(f"[tse] All retries exhausted: {last_error}")
        return None

    @staticmethod
    async def _sleep_with_jitter(base: float) -> None:
        jitter = random.uniform(0, 0.25)
        await asyncio.sleep(base + jitter)

    # =========================================================================
    # Datasets Eleitorais
    # =========================================================================

    async def search_datasets(
        self,
        query: str = "eleicoes",
        rows: int = 10,
        start: int = 0,
    ) -> List[TSEDocument]:
        """Busca datasets no portal de dados abertos do TSE."""
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
            # Extrair ano da eleicao do titulo/tags se possivel
            ano_eleicao = None
            for tag in item.get("tags", []):
                tag_name = tag.get("name", "")
                if tag_name.isdigit() and len(tag_name) == 4:
                    ano_eleicao = int(tag_name)
                    break

            doc = TSEDocument(
                external_id=item.get("id", ""),
                title=item.get("title", "Dataset sem titulo"),
                url=f"https://dadosabertos.tse.jus.br/dataset/{item.get('name', '')}",
                published_at=item.get("metadata_created", ""),
                content=item.get("notes", ""),
                document_type="dataset",
                ano_eleicao=ano_eleicao,
                metadata={
                    "organization": item.get("organization", {}).get("title"),
                    "tags": [t.get("name") for t in item.get("tags", [])],
                    "resources_count": len(item.get("resources", [])),
                    "license": item.get("license_title"),
                },
            )
            documents.append(doc)

        logger.info(f"[tse] Found {len(documents)} datasets for query '{query}'")
        return documents

    async def get_dataset_resources(self, dataset_id: str) -> List[Dict]:
        """Retorna recursos (arquivos CSV/JSON) de um dataset."""
        url = f"{self.BASE_URL}/action/package_show"
        params = {"id": dataset_id}

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return []

        resources = data.get("result", {}).get("resources", [])
        # Filtrar apenas recursos JSON/CSV
        filtered = [
            r for r in resources
            if r.get("format", "").upper() in ("JSON", "CSV", "XLSX")
        ]
        return filtered

    # =========================================================================
    # Candidatos (dados estaticos por eleicao)
    # =========================================================================

    async def list_eleicoes_disponiveis(self) -> List[Dict]:
        """Lista eleicoes com dados disponiveis."""
        url = f"{self.BASE_URL}/action/package_search"
        params = {
            "q": "candidatos",
            "rows": 50,
        }

        data = await self._request_with_retry(url, params)
        if not data or not data.get("success"):
            return []

        eleicoes = []
        for item in data.get("result", {}).get("results", []):
            for tag in item.get("tags", []):
                tag_name = tag.get("name", "")
                if tag_name.isdigit() and len(tag_name) == 4:
                    eleicoes.append({
                        "ano": int(tag_name),
                        "dataset_id": item.get("id"),
                        "title": item.get("title"),
                    })
                    break

        # Remover duplicatas e ordenar
        seen = set()
        unique = []
        for e in sorted(eleicoes, key=lambda x: x["ano"], reverse=True):
            if e["ano"] not in seen:
                seen.add(e["ano"])
                unique.append(e)

        return unique

    # =========================================================================
    # Partidos
    # =========================================================================

    async def search_partidos_datasets(self) -> List[TSEDocument]:
        """Busca datasets relacionados a partidos politicos."""
        return await self.search_datasets(query="partidos", rows=20)

    # =========================================================================
    # Prestacao de Contas
    # =========================================================================

    async def search_prestacao_contas(self, ano: Optional[int] = None) -> List[TSEDocument]:
        """Busca datasets de prestacao de contas eleitorais."""
        query = "prestacao contas"
        if ano:
            query = f"{query} {ano}"
        return await self.search_datasets(query=query, rows=20)
