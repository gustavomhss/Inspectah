"""
S38-BE-003: Framework Base de Scrapers

Define a interface e comportamentos comuns para todos os scrapers.
"""
from __future__ import annotations

import hashlib
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class VerdictType(str, Enum):
    """Tipos de veredito de checagem."""
    TRUE = "true"
    FALSE = "false"
    MISLEADING = "misleading"
    UNVERIFIABLE = "unverifiable"
    OUTDATED = "outdated"
    EXAGGERATED = "exaggerated"
    PARTIALLY_TRUE = "partially_true"
    UNKNOWN = "unknown"


@dataclass
class ScraperConfig:
    """Configuracao de um scraper."""
    name: str
    base_url: str
    rate_limit_rpm: int = 2  # 2 req/min por padrao (conservador)
    timeout_seconds: int = 30
    max_retries: int = 3
    user_agent_pool: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    ])
    enabled: bool = True


@dataclass
class ScrapedArticle:
    """Artigo de checagem extraido."""
    external_id: str
    source_name: str
    url: str
    title: str
    claim: str  # A afirmacao sendo verificada
    verdict: VerdictType
    verdict_label: str  # Label original do site (ex: "FALSO", "Engana")
    content: str
    published_at: Optional[datetime]
    author: Optional[str]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def content_hash(self) -> str:
        raw = f"{self.url}|{self.title}|{self.claim}|{self.verdict}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class ScraperResult:
    """Resultado de uma execucao de scraper."""
    source_name: str
    articles: List[ScrapedArticle]
    total_found: int
    success: bool
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseScraper(ABC):
    """
    Classe base para todos os scrapers.

    Implementa:
    - Rate limiting com sliding window
    - Retry com backoff exponencial
    - Rotacao de User-Agent
    - Parsing HTML com BeautifulSoup
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self._min_interval = 60.0 / config.rate_limit_rpm
        self._last_request_time = 0.0

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers com User-Agent rotacionado."""
        ua = random.choice(self.config.user_agent_pool)
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _wait_rate_limit(self) -> None:
        """Aguarda intervalo minimo entre requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            logger.debug(f"[{self.config.name}] Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _request_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
    ) -> Optional[str]:
        """Faz request HTTP com retry e backoff."""
        backoff = 1.0

        for attempt in range(1, self.config.max_retries + 1):
            self._wait_rate_limit()

            try:
                response = httpx.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.config.timeout_seconds,
                    follow_redirects=True,
                )

                if response.status_code == 200:
                    return response.text

                if response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"[{self.config.name}] Retry {attempt}/{self.config.max_retries} "
                        f"- status {response.status_code}"
                    )
                    if attempt < self.config.max_retries:
                        self._sleep_with_jitter(backoff)
                        backoff *= 2
                        continue

                if response.status_code == 403:
                    logger.error(f"[{self.config.name}] Blocked (403) - {url}")
                    return None

                logger.error(
                    f"[{self.config.name}] Request failed: {response.status_code} - {url}"
                )
                return None

            except httpx.HTTPError as e:
                logger.warning(f"[{self.config.name}] HTTP error attempt {attempt}: {e}")
                if attempt < self.config.max_retries:
                    self._sleep_with_jitter(backoff)
                    backoff *= 2
                    continue

        return None

    @staticmethod
    def _sleep_with_jitter(base: float) -> None:
        jitter = random.uniform(0, 0.5)
        time.sleep(base + jitter)

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML para BeautifulSoup."""
        return BeautifulSoup(html, "html.parser")

    @abstractmethod
    def get_article_urls(self, page: int = 1) -> List[str]:
        """
        Retorna lista de URLs de artigos de checagem.

        Deve ser implementado por cada scraper especifico.
        """
        pass

    @abstractmethod
    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """
        Parse de um artigo de checagem.

        Deve ser implementado por cada scraper especifico.
        """
        pass

    def scrape_article(self, url: str) -> Optional[ScrapedArticle]:
        """Faz scrape de um unico artigo."""
        html = self._request_with_retry(url)
        if not html:
            return None

        try:
            return self.parse_article(url, html)
        except Exception as e:
            logger.error(f"[{self.config.name}] Error parsing {url}: {e}")
            return None

    def scrape(
        self,
        pages: int = 1,
        max_articles: int = 50,
    ) -> ScraperResult:
        """
        Executa scraping completo.

        Args:
            pages: Numero de paginas a processar
            max_articles: Numero maximo de artigos
        """
        start_time = time.time()
        articles: List[ScrapedArticle] = []
        total_found = 0

        try:
            for page in range(1, pages + 1):
                if len(articles) >= max_articles:
                    break

                urls = self.get_article_urls(page=page)
                total_found += len(urls)

                for url in urls:
                    if len(articles) >= max_articles:
                        break

                    article = self.scrape_article(url)
                    if article:
                        articles.append(article)
                        logger.info(
                            f"[{self.config.name}] Scraped: {article.title[:50]}..."
                        )

            duration = time.time() - start_time
            logger.info(
                f"[{self.config.name}] Completed: {len(articles)} articles in {duration:.1f}s"
            )

            return ScraperResult(
                source_name=self.config.name,
                articles=articles,
                total_found=total_found,
                success=True,
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"[{self.config.name}] Scrape failed: {e}")
            return ScraperResult(
                source_name=self.config.name,
                articles=articles,
                total_found=total_found,
                success=False,
                error_message=str(e),
                duration_seconds=time.time() - start_time,
            )

    @staticmethod
    def normalize_verdict(label: str) -> VerdictType:
        """Normaliza label de veredito para enum padrao."""
        label_lower = label.lower().strip()

        # Mapeamentos comuns
        false_labels = ["falso", "fake", "mentira", "falsa", "incorreto", "errado"]
        true_labels = ["verdadeiro", "verdade", "correto", "certo", "true"]
        misleading_labels = ["engana", "enganoso", "distorce", "misleading", "distorcido"]
        partially_labels = ["parcialmente", "partially", "em parte", "incompleto"]
        exaggerated_labels = ["exagerado", "exaggerated", "inflado"]
        outdated_labels = ["desatualizado", "outdated", "antigo"]
        unverifiable_labels = ["inverificavel", "unverifiable", "impossivel verificar"]

        for label_check in false_labels:
            if label_check in label_lower:
                return VerdictType.FALSE

        for label_check in true_labels:
            if label_check in label_lower:
                return VerdictType.TRUE

        for label_check in misleading_labels:
            if label_check in label_lower:
                return VerdictType.MISLEADING

        for label_check in partially_labels:
            if label_check in label_lower:
                return VerdictType.PARTIALLY_TRUE

        for label_check in exaggerated_labels:
            if label_check in label_lower:
                return VerdictType.EXAGGERATED

        for label_check in outdated_labels:
            if label_check in label_lower:
                return VerdictType.OUTDATED

        for label_check in unverifiable_labels:
            if label_check in label_lower:
                return VerdictType.UNVERIFIABLE

        return VerdictType.UNKNOWN
