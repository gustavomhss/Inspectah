"""
S38-BE-001: Integrador de Fontes Oficiais

Coordena a ingestao de fontes oficiais do governo brasileiro:
- Portal da Transparencia (gov_br.py)
- Dados Abertos (dados_gov.py)
- TSE (tse.py)

Responsabilidades:
- Orquestrar chamadas aos providers
- Normalizar documentos para formato comum
- Gerenciar health status das fontes
- Integrar com sistema de cache e rate limiting
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union

from app.ingestion.providers.gov_br import GovBrClient, GovBrDocument
from app.ingestion.providers.dados_gov import DadosGovClient, DadosGovDocument
from app.ingestion.providers.tse import TSEClient, TSEDocument

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    """Tipos de fontes oficiais."""
    GOV_BR = "gov_br"
    DADOS_GOV = "dados_gov"
    TSE = "tse"


class SourceStatus(str, Enum):
    """Status de saude da fonte."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class NormalizedDocument:
    """Documento normalizado de qualquer fonte oficial."""
    id: str
    source_type: SourceType
    external_id: str
    title: str
    url: str
    content: str
    published_at: Optional[datetime]
    content_hash: str
    document_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_gov_br(cls, doc: GovBrDocument) -> "NormalizedDocument":
        return cls(
            id=f"gov_br_{doc.content_hash()}",
            source_type=SourceType.GOV_BR,
            external_id=doc.external_id,
            title=doc.title,
            url=doc.url,
            content=doc.content,
            published_at=_parse_date(doc.published_at),
            content_hash=doc.content_hash(),
            document_type=doc.document_type,
            metadata={
                "source_api": doc.source_api,
                **doc.metadata,
            },
        )

    @classmethod
    def from_dados_gov(cls, doc: DadosGovDocument) -> "NormalizedDocument":
        return cls(
            id=f"dados_gov_{doc.content_hash()}",
            source_type=SourceType.DADOS_GOV,
            external_id=doc.external_id,
            title=doc.title,
            url=doc.url,
            content=doc.content,
            published_at=_parse_date(doc.published_at),
            content_hash=doc.content_hash(),
            document_type="dataset",
            metadata={
                "organization": doc.organization,
                "category": doc.category,
                **doc.metadata,
            },
        )

    @classmethod
    def from_tse(cls, doc: TSEDocument) -> "NormalizedDocument":
        return cls(
            id=f"tse_{doc.content_hash()}",
            source_type=SourceType.TSE,
            external_id=doc.external_id,
            title=doc.title,
            url=doc.url,
            content=doc.content,
            published_at=_parse_date(doc.published_at),
            content_hash=doc.content_hash(),
            document_type=doc.document_type,
            metadata={
                "ano_eleicao": doc.ano_eleicao,
                **doc.metadata,
            },
        )


@dataclass
class SourceHealth:
    """Status de saude de uma fonte."""
    source_type: SourceType
    status: SourceStatus
    last_check: datetime
    last_success: Optional[datetime]
    consecutive_failures: int
    avg_latency_ms: float
    error_message: Optional[str] = None


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse de data em varios formatos."""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    logger.warning(f"Could not parse date: {date_str}")
    return None


class OfficialSourceIntegrator:
    """
    Coordenador de ingestao de fontes oficiais.

    Uso:
        integrator = OfficialSourceIntegrator()

        # Buscar documentos de uma fonte especifica
        docs = integrator.fetch_from_gov_br(data_inicial="01/12/2024", data_final="14/12/2024")

        # Buscar de todas as fontes prioritarias
        all_docs = integrator.fetch_all_priority()

        # Verificar saude das fontes
        health = integrator.check_health()
    """

    def __init__(
        self,
        gov_br_api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 3,
    ):
        self.gov_br = GovBrClient(
            api_key=gov_br_api_key,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self.dados_gov = DadosGovClient(
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self.tse = TSEClient(
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        self._health: Dict[SourceType, SourceHealth] = {}

    # =========================================================================
    # Gov.br - Portal da Transparencia
    # =========================================================================

    async def fetch_from_gov_br(
        self,
        data_inicial: str,
        data_final: str,
        include_contratos: bool = True,
        include_despesas: bool = True,
    ) -> List[NormalizedDocument]:
        """
        Busca documentos do Portal da Transparencia.

        Args:
            data_inicial: Data inicial (DD/MM/AAAA)
            data_final: Data final (DD/MM/AAAA)
            include_contratos: Incluir contratos
            include_despesas: Incluir despesas
        """
        documents = []

        if include_contratos:
            try:
                raw_docs = await self.gov_br.fetch_contratos(data_inicial, data_final)
                for doc in raw_docs:
                    documents.append(NormalizedDocument.from_gov_br(doc))
                self._update_health(SourceType.GOV_BR, success=True)
            except Exception as e:
                logger.error(f"[official_integrator] Error fetching contratos: {e}")
                self._update_health(SourceType.GOV_BR, success=False, error=str(e))

        if include_despesas:
            # Extrair ano/mes das datas
            try:
                parts = data_final.split("/")
                if len(parts) == 3:
                    ano = int(parts[2])
                    mes = int(parts[1])
                    raw_docs = await self.gov_br.fetch_despesas(ano, mes)
                    for doc in raw_docs:
                        documents.append(NormalizedDocument.from_gov_br(doc))
                    self._update_health(SourceType.GOV_BR, success=True)
            except Exception as e:
                logger.error(f"[official_integrator] Error fetching despesas: {e}")
                self._update_health(SourceType.GOV_BR, success=False, error=str(e))

        logger.info(f"[official_integrator] Fetched {len(documents)} documents from gov.br")
        return documents

    # =========================================================================
    # Dados.gov.br - Portal de Dados Abertos
    # =========================================================================

    async def fetch_from_dados_gov(
        self,
        categories: Optional[List[str]] = None,
        include_recent: bool = True,
        rows_per_category: int = 10,
    ) -> List[NormalizedDocument]:
        """
        Busca datasets do portal dados.gov.br.

        Args:
            categories: Lista de categorias (saude, economia, educacao, meio_ambiente, politica)
            include_recent: Incluir datasets atualizados recentemente
            rows_per_category: Numero de resultados por categoria
        """
        documents = []

        try:
            if categories:
                for category in categories:
                    raw_docs = await self.dados_gov.fetch_by_category(category, rows=rows_per_category)
                    for doc in raw_docs:
                        documents.append(NormalizedDocument.from_dados_gov(doc))
            else:
                # Buscar todas as categorias prioritarias
                all_docs = await self.dados_gov.fetch_all_priority_datasets(rows_per_category)
                for category_docs in all_docs.values():
                    for doc in category_docs:
                        documents.append(NormalizedDocument.from_dados_gov(doc))

            if include_recent:
                recent = await self.dados_gov.get_recent_updates(days=7, rows=30)
                for doc in recent:
                    documents.append(NormalizedDocument.from_dados_gov(doc))

            self._update_health(SourceType.DADOS_GOV, success=True)

        except Exception as e:
            logger.error(f"[official_integrator] Error fetching from dados.gov: {e}")
            self._update_health(SourceType.DADOS_GOV, success=False, error=str(e))

        # Dedup por external_id
        seen = set()
        unique = []
        for doc in documents:
            if doc.external_id not in seen:
                seen.add(doc.external_id)
                unique.append(doc)

        logger.info(f"[official_integrator] Fetched {len(unique)} documents from dados.gov.br")
        return unique

    # =========================================================================
    # TSE - Dados Eleitorais
    # =========================================================================

    async def fetch_from_tse(
        self,
        include_eleicoes: bool = True,
        include_partidos: bool = True,
        include_prestacao_contas: bool = False,
        ano_eleicao: Optional[int] = None,
    ) -> List[NormalizedDocument]:
        """
        Busca datasets do TSE.

        Args:
            include_eleicoes: Incluir dados eleitorais
            include_partidos: Incluir dados de partidos
            include_prestacao_contas: Incluir prestacao de contas
            ano_eleicao: Filtrar por ano de eleicao
        """
        documents = []

        try:
            if include_eleicoes:
                query = f"eleicoes {ano_eleicao}" if ano_eleicao else "eleicoes"
                raw_docs = await self.tse.search_datasets(query=query, rows=20)
                for doc in raw_docs:
                    documents.append(NormalizedDocument.from_tse(doc))

            if include_partidos:
                raw_docs = await self.tse.search_partidos_datasets()
                for doc in raw_docs:
                    documents.append(NormalizedDocument.from_tse(doc))

            if include_prestacao_contas:
                raw_docs = await self.tse.search_prestacao_contas(ano=ano_eleicao)
                for doc in raw_docs:
                    documents.append(NormalizedDocument.from_tse(doc))

            self._update_health(SourceType.TSE, success=True)

        except Exception as e:
            logger.error(f"[official_integrator] Error fetching from TSE: {e}")
            self._update_health(SourceType.TSE, success=False, error=str(e))

        # Dedup
        seen = set()
        unique = []
        for doc in documents:
            if doc.external_id not in seen:
                seen.add(doc.external_id)
                unique.append(doc)

        logger.info(f"[official_integrator] Fetched {len(unique)} documents from TSE")
        return unique

    # =========================================================================
    # Agregado
    # =========================================================================

    async def fetch_all_priority(
        self,
        gov_br_data_inicial: Optional[str] = None,
        gov_br_data_final: Optional[str] = None,
    ) -> Dict[SourceType, List[NormalizedDocument]]:
        """
        Busca documentos de todas as fontes prioritarias.

        Retorna um dicionario com documentos por tipo de fonte.
        """
        results: Dict[SourceType, List[NormalizedDocument]] = {}

        # Gov.br - precisa de datas
        if gov_br_data_inicial and gov_br_data_final:
            results[SourceType.GOV_BR] = await self.fetch_from_gov_br(
                data_inicial=gov_br_data_inicial,
                data_final=gov_br_data_final,
            )
        else:
            results[SourceType.GOV_BR] = []

        # Dados.gov.br
        results[SourceType.DADOS_GOV] = await self.fetch_from_dados_gov()

        # TSE
        results[SourceType.TSE] = await self.fetch_from_tse()

        total = sum(len(docs) for docs in results.values())
        logger.info(f"[official_integrator] Total fetched from all sources: {total}")

        return results

    # =========================================================================
    # Health Check
    # =========================================================================

    def _update_health(
        self,
        source_type: SourceType,
        success: bool,
        error: Optional[str] = None,
        latency_ms: float = 0.0,
    ) -> None:
        """Atualiza status de saude de uma fonte."""
        now = datetime.now(timezone.utc)

        if source_type not in self._health:
            self._health[source_type] = SourceHealth(
                source_type=source_type,
                status=SourceStatus.UNKNOWN,
                last_check=now,
                last_success=None,
                consecutive_failures=0,
                avg_latency_ms=0.0,
            )

        health = self._health[source_type]
        health.last_check = now

        if success:
            health.last_success = now
            health.consecutive_failures = 0
            health.status = SourceStatus.HEALTHY
            health.error_message = None
            # Atualizar media de latencia
            if latency_ms > 0:
                health.avg_latency_ms = (health.avg_latency_ms + latency_ms) / 2
        else:
            health.consecutive_failures += 1
            health.error_message = error

            if health.consecutive_failures >= 5:
                health.status = SourceStatus.UNHEALTHY
            elif health.consecutive_failures >= 2:
                health.status = SourceStatus.DEGRADED

    def check_health(self) -> Dict[SourceType, SourceHealth]:
        """Retorna status de saude de todas as fontes."""
        # Fazer probe rapido em cada fonte
        for source_type in SourceType:
            if source_type not in self._health:
                self._health[source_type] = SourceHealth(
                    source_type=source_type,
                    status=SourceStatus.UNKNOWN,
                    last_check=datetime.now(timezone.utc),
                    last_success=None,
                    consecutive_failures=0,
                    avg_latency_ms=0.0,
                )

        return self._health.copy()

    def get_source_health(self, source_type: SourceType) -> Optional[SourceHealth]:
        """Retorna status de saude de uma fonte especifica."""
        return self._health.get(source_type)
