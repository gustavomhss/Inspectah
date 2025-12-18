"""
S38-BE-004: Scraper Fato ou Fake (G1/Globo)

Site de checagem de fatos do portal G1/Globo.
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


class FatoOuFakeScraper(BaseScraper):
    """
    Scraper para g1.globo.com/fato-ou-fake.

    Estrutura do site:
    - Lista de checagens: /fato-ou-fake/
    - Artigos: /fato-ou-fake/noticia/YYYY/MM/DD/titulo.ghtml
    - Vereditos: FATO, FAKE, NAO E BEM ASSIM, etc.
    - Usa formato padrao do G1
    """

    DEFAULT_CONFIG = ScraperConfig(
        name="fato_ou_fake",
        base_url="https://g1.globo.com/fato-ou-fake",
        rate_limit_rpm=2,
        timeout_seconds=30,
        max_retries=3,
    )

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    def get_article_urls(self, page: int = 1) -> List[str]:
        """Retorna URLs de artigos."""
        # G1 usa paginacao diferente
        list_url = f"{self.config.base_url}/"

        html = self._request_with_retry(list_url)
        if not html:
            return []

        soup = self._parse_html(html)
        urls = []

        # Buscar links de artigos (formato G1)
        article_links = soup.select(
            "a[href*='/fato-ou-fake/noticia/'], "
            "a[href*='/fato-ou-fake/'][href$='.ghtml']"
        )
        for link in article_links:
            href = link.get("href")
            if href and ".ghtml" in href:
                full_url = urljoin("https://g1.globo.com", href)
                if full_url not in urls:
                    urls.append(full_url)

        # Fallback: buscar qualquer link para noticias
        if not urls:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "/fato-ou-fake/" in href and ".ghtml" in href:
                    full_url = urljoin("https://g1.globo.com", href)
                    if full_url not in urls:
                        urls.append(full_url)

        logger.debug(f"[fato_ou_fake] Found {len(urls)} article URLs")
        return urls[:20]

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Parse de um artigo do Fato ou Fake."""
        soup = self._parse_html(html)

        # Titulo - G1 usa itemprop="headline"
        title_tag = soup.select_one(
            "h1[itemprop='headline'], h1.content-head__title, h1"
        )
        if not title_tag:
            logger.warning(f"[fato_ou_fake] No title found: {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Veredito - G1 usa etiquetas visuais
        verdict_label = self._extract_verdict(soup, title)

        # Claim - geralmente no titulo ou subtitulo
        claim = ""
        subtitle = soup.select_one(
            ".content-head__subtitle, h2[itemprop='description'], .materia-titulo"
        )
        if subtitle:
            claim = subtitle.get_text(strip=True)
        else:
            # Extrair do titulo (formato: "AFIRMACAO e FATO/FAKE")
            claim = title

        # Conteudo
        content = ""
        content_elem = soup.select_one(
            "article, .content-text, [itemprop='articleBody'], .materia-conteudo"
        )
        if content_elem:
            paragraphs = content_elem.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Data
        published_at = None
        date_elem = soup.select_one(
            "time[datetime], [itemprop='datePublished'], .content-publication-data__updated"
        )
        if date_elem:
            datetime_str = (
                date_elem.get("datetime") or
                date_elem.get("content") or
                date_elem.get_text(strip=True)
            )
            published_at = self._parse_date(datetime_str)

        # Autor
        author = None
        author_elem = soup.select_one(
            "[itemprop='author'], .content-publication-data__from, .author"
        )
        if author_elem:
            author = author_elem.get_text(strip=True)
            # Limpar "Por" do inicio
            if author.lower().startswith("por "):
                author = author[4:]

        # Tags
        tags = []
        tag_elems = soup.select(".entities__list-item a, .content-tags a, [rel='tag']")
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

    def _extract_verdict(self, soup, title: str) -> str:
        """Extrai veredito do artigo."""
        # G1 Fato ou Fake usa etiquetas visuais
        # Tentar extrair do titulo primeiro
        title_upper = title.upper()

        # Padrao comum: "AFIRMACAO e FATO" ou "AFIRMACAO e FAKE"
        if " E FATO" in title_upper or " É FATO" in title_upper:
            return "FATO"
        if " E FAKE" in title_upper or " É FAKE" in title_upper:
            return "FAKE"
        if "NAO E BEM ASSIM" in title_upper or "NÃO É BEM ASSIM" in title_upper:
            return "NAO E BEM ASSIM"

        # Buscar selo/etiqueta
        selo_elem = soup.select_one(
            ".fact-check-label, .selo-checagem, "
            "img[alt*='Fato'], img[alt*='Fake'], "
            "[class*='fato-ou-fake']"
        )
        if selo_elem:
            if selo_elem.name == "img":
                alt = selo_elem.get("alt", "")
                if alt:
                    return alt.upper()
            text = selo_elem.get_text(strip=True)
            if text:
                return text.upper()

        # Buscar no conteudo inicial
        content_elem = soup.select_one(".content-text, article")
        if content_elem:
            first_text = content_elem.get_text()[:500].upper()
            if "FAKE" in first_text:
                return "FAKE"
            if "FATO" in first_text:
                return "FATO"

        return "DESCONHECIDO"

    def _extract_id_from_url(self, url: str) -> str:
        """Extrai ID unico da URL."""
        # URL: https://g1.globo.com/fato-ou-fake/noticia/2024/12/10/titulo.ghtml
        parts = url.rstrip("/").split("/")
        slug = parts[-1].replace(".ghtml", "") if parts else ""
        return f"fatooufake_{slug}" if slug else f"fatooufake_{hash(url)}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse de data."""
        if not date_str:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
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
