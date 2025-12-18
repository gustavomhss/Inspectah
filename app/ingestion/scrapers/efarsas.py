"""
S38-BE-004: Scraper E-farsas (e-farsas.com)

Site de checagem de fatos e desmentidos de boatos.
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


class EFarsasScraper(BaseScraper):
    """
    Scraper para e-farsas.com.

    Estrutura do site:
    - Lista de checagens: /
    - Artigos: /titulo-do-artigo/
    - Categorias: /category/falso/, /category/verdadeiro/
    - Vereditos indicados por categoria ou icones
    """

    DEFAULT_CONFIG = ScraperConfig(
        name="efarsas",
        base_url="https://www.e-farsas.com",
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
        article_links = soup.select("article a[href], .post a[href], h2 a[href], h3 a[href]")
        for link in article_links:
            href = link.get("href")
            if href and "e-farsas.com" in href:
                # Excluir paginas de categoria, tag, pagina
                if not any(x in href for x in ["/category/", "/tag/", "/page/", "/author/"]):
                    full_url = urljoin(self.config.base_url, href)
                    if full_url not in urls:
                        urls.append(full_url)

        logger.debug(f"[efarsas] Found {len(urls)} article URLs on page {page}")
        return urls[:20]

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Parse de um artigo do E-farsas."""
        soup = self._parse_html(html)

        # Titulo
        title_tag = soup.find("h1")
        if not title_tag:
            logger.warning(f"[efarsas] No title found: {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Veredito - buscar em varios lugares
        verdict_label = self._extract_verdict(soup, url)

        # Claim
        claim = ""
        claim_elem = soup.select_one(".claim, blockquote, .afirmacao")
        if claim_elem:
            claim = claim_elem.get_text(strip=True)
        else:
            # Usar subtitulo ou primeiro paragrafo
            subtitle = soup.select_one("h2, .subtitle, .excerpt")
            if subtitle:
                claim = subtitle.get_text(strip=True)

        # Conteudo
        content = ""
        content_elem = soup.select_one("article, .entry-content, .post-content, .content")
        if content_elem:
            paragraphs = content_elem.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Data
        published_at = None
        date_elem = soup.select_one("time[datetime], .date, .published, .entry-date, .post-date")
        if date_elem:
            datetime_str = date_elem.get("datetime") or date_elem.get_text(strip=True)
            published_at = self._parse_date(datetime_str)

        # Autor
        author = None
        author_elem = soup.select_one(".author, [rel='author'], .byline, .author-name")
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

    def _extract_verdict(self, soup, url: str) -> str:
        """Extrai veredito do artigo."""
        # Verificar categoria na URL
        if "/category/falso/" in url or "/falso/" in url:
            return "FALSO"
        if "/category/verdadeiro/" in url or "/verdadeiro/" in url:
            return "VERDADEIRO"

        # Buscar icone ou selo
        verdict_elem = soup.select_one(
            ".verdict, .rating, .selo, "
            "img[alt*='Falso'], img[alt*='Verdadeiro'], "
            "[class*='verdict'], [class*='rating']"
        )
        if verdict_elem:
            if verdict_elem.name == "img":
                alt = verdict_elem.get("alt", "")
                if alt:
                    return alt.upper()
            text = verdict_elem.get_text(strip=True)
            if text:
                return text.upper()

        # Verificar categorias no conteudo
        categories = soup.select(".category a, .post-categories a")
        for cat in categories:
            cat_text = cat.get_text(strip=True).lower()
            if "falso" in cat_text:
                return "FALSO"
            if "verdadeiro" in cat_text or "verdade" in cat_text:
                return "VERDADEIRO"

        return "DESCONHECIDO"

    def _extract_id_from_url(self, url: str) -> str:
        """Extrai ID unico da URL."""
        parts = url.rstrip("/").split("/")
        slug = parts[-1] if parts[-1] else parts[-2] if len(parts) > 1 else ""
        return f"efarsas_{slug}" if slug else f"efarsas_{hash(url)}"

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
