"""
S38-BE-004: Scraper Boatos.org

Site especializado em desmentir boatos e fake news.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin

from app.ingestion.scrapers.base import (
    BaseScraper,
    ScrapedArticle,
    ScraperConfig,
    VerdictType,
)

logger = logging.getLogger(__name__)


class BoatosScraper(BaseScraper):
    """
    Scraper para boatos.org.

    Estrutura do site:
    - Lista de checagens: /
    - Artigos: /titulo-do-artigo/
    - Categorias: /category/boato/, /category/verdade/
    - Todos os artigos sao geralmente desmentindo boatos (FALSO)
    """

    DEFAULT_CONFIG = ScraperConfig(
        name="boatos",
        base_url="https://www.boatos.org",
        rate_limit_rpm=2,
        timeout_seconds=30,
        max_retries=3,
    )

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    def get_article_urls(self, page: int = 1) -> List[str]:
        """Retorna URLs de artigos."""
        list_url = self.config.base_url
        if page > 1:
            list_url = f"{self.config.base_url}/page/{page}/"

        html = self._request_with_retry(list_url)
        if not html:
            return []

        soup = self._parse_html(html)
        urls = []

        # Buscar artigos
        article_links = soup.select("article a[href], .post a[href], h2 a[href]")
        for link in article_links:
            href = link.get("href")
            if href and "boatos.org" in href:
                # Excluir paginas de categoria, tag, pagina
                if not any(x in href for x in ["/category/", "/tag/", "/page/", "/author/"]):
                    if href not in urls:
                        urls.append(href)

        # Fallback
        if not urls:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "boatos.org" in href and href.endswith("/"):
                    if not any(x in href for x in ["/category/", "/tag/", "/page/", "/author/"]):
                        if href not in urls:
                            urls.append(href)

        logger.debug(f"[boatos] Found {len(urls)} article URLs on page {page}")
        return urls[:20]  # Limitar para evitar muitos requests

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Parse de um artigo do Boatos.org."""
        soup = self._parse_html(html)

        # Titulo
        title_tag = soup.find("h1")
        if not title_tag:
            logger.warning(f"[boatos] No title found: {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Boatos.org geralmente tem formato "#Boato: [texto do boato]"
        claim = ""
        verdict_label = "FALSO"  # Default para boatos desmentidos

        # Buscar boato
        boato_elem = soup.select_one(".boato, .claim, blockquote")
        if boato_elem:
            claim = boato_elem.get_text(strip=True)
        else:
            # Tentar extrair do titulo
            if "#boato:" in title.lower():
                claim = title.split(":", 1)[-1].strip()
            else:
                claim = title

        # Verificar se e "verdade" (raro no site)
        if "#verdade" in title.lower() or "verdade" in soup.get_text().lower()[:500]:
            # Pode ser uma confirmacao rara
            content_lower = soup.get_text().lower()[:1000]
            if "e verdade" in content_lower or "isso e verdade" in content_lower:
                verdict_label = "VERDADEIRO"

        # Conteudo
        content = ""
        content_elem = soup.select_one("article, .entry-content, .post-content")
        if content_elem:
            paragraphs = content_elem.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Data
        published_at = None
        date_elem = soup.select_one("time[datetime], .date, .published, .entry-date")
        if date_elem:
            datetime_str = date_elem.get("datetime") or date_elem.get_text(strip=True)
            published_at = self._parse_date(datetime_str)

        # Autor
        author = None
        author_elem = soup.select_one(".author, [rel='author'], .byline")
        if author_elem:
            author = author_elem.get_text(strip=True)

        # Tags
        tags = []
        tag_elems = soup.select(".tag, .category, [rel='tag'], .post-categories a")
        for tag_elem in tag_elems:
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)

        external_id = self._extract_id_from_url(url)

        return ScrapedArticle(
            external_id=external_id,
            source_name=self.config.name,
            url=url,
            title=title,
            claim=claim or title,
            verdict=self.normalize_verdict(verdict_label),
            verdict_label=verdict_label,
            content=content,
            published_at=published_at,
            author=author,
            tags=tags,
        )

    def _extract_id_from_url(self, url: str) -> str:
        """Extrai ID unico da URL."""
        parts = url.rstrip("/").split("/")
        slug = parts[-1] if parts[-1] else parts[-2] if len(parts) > 1 else ""
        return f"boatos_{slug}" if slug else f"boatos_{hash(url)}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse de data."""
        if not date_str:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d de %B de %Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

        return None
