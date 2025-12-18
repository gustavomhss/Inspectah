"""
S38-BE-004: Scraper Aos Fatos (aosfatos.org)

Site de checagem de fatos brasileiro.
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


class AosFatosScraper(BaseScraper):
    """
    Scraper para aosfatos.org.

    Estrutura do site:
    - Lista de checagens: /noticias/checamos/
    - Artigos: /noticias/YYYY/MM/DD/titulo-do-artigo/
    - Vereditos: FALSO, VERDADEIRO, ENGANOSO, IMPRECISO, EXAGERADO, etc.
    """

    DEFAULT_CONFIG = ScraperConfig(
        name="aos_fatos",
        base_url="https://www.aosfatos.org",
        rate_limit_rpm=2,
        timeout_seconds=30,
        max_retries=3,
    )

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    def get_article_urls(self, page: int = 1) -> List[str]:
        """Retorna URLs de artigos da pagina de checagens."""
        list_url = f"{self.config.base_url}/noticias/checamos/"
        if page > 1:
            list_url = f"{list_url}page/{page}/"

        html = self._request_with_retry(list_url)
        if not html:
            return []

        soup = self._parse_html(html)
        urls = []

        # Buscar links de artigos
        article_links = soup.select("article a[href*='/noticias/']")
        for link in article_links:
            href = link.get("href")
            if href and "/checamos/" not in href:
                full_url = urljoin(self.config.base_url, href)
                if full_url not in urls:
                    urls.append(full_url)

        # Fallback: buscar em outros seletores
        if not urls:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                # Match pattern /noticias/YYYY/MM/DD/
                if re.match(r".*/noticias/\d{4}/\d{2}/\d{2}/", href):
                    full_url = urljoin(self.config.base_url, href)
                    if full_url not in urls:
                        urls.append(full_url)

        logger.debug(f"[aos_fatos] Found {len(urls)} article URLs on page {page}")
        return urls

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Parse de um artigo do Aos Fatos."""
        soup = self._parse_html(html)

        # Titulo
        title_tag = soup.find("h1")
        if not title_tag:
            logger.warning(f"[aos_fatos] No title found: {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Veredito - geralmente em um elemento com classe especifica
        verdict_label = "DESCONHECIDO"
        verdict_elem = soup.select_one(".verdict, .rating, [class*='verdict'], [class*='rating']")
        if verdict_elem:
            verdict_label = verdict_elem.get_text(strip=True)
        else:
            # Tentar extrair do titulo ou conteudo
            for label in ["FALSO", "VERDADEIRO", "ENGANOSO", "IMPRECISO", "EXAGERADO"]:
                if label in title.upper():
                    verdict_label = label
                    break

        # Claim (afirmacao verificada)
        claim = ""
        claim_elem = soup.select_one(".claim, .statement, blockquote")
        if claim_elem:
            claim = claim_elem.get_text(strip=True)
        else:
            # Usar subtitulo ou primeiro paragrafo
            subtitle = soup.select_one("h2, .subtitle, .lead")
            if subtitle:
                claim = subtitle.get_text(strip=True)

        # Conteudo
        content_elem = soup.select_one("article, .post-content, .entry-content, main")
        content = ""
        if content_elem:
            paragraphs = content_elem.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Data de publicacao
        published_at = None
        date_elem = soup.select_one("time[datetime], .date, .published")
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
        tag_elems = soup.select(".tag, .category, [rel='tag']")
        for tag_elem in tag_elems:
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)

        # Gerar ID unico
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
        # URL: https://www.aosfatos.org/noticias/2024/12/10/titulo-artigo/
        parts = url.rstrip("/").split("/")
        if len(parts) >= 4:
            return f"aosfatos_{parts[-1]}"
        return f"aosfatos_{hash(url)}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse de data em varios formatos."""
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

        # Tentar extrair ano/mes/dia com regex
        match = re.search(r"(\d{4})/(\d{2})/(\d{2})", date_str)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day), tzinfo=timezone.utc)

        return None
