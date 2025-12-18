"""
S38-BE-004: Scraper Agencia Lupa (lupa.uol.com.br)

Site de checagem de fatos afiliado ao UOL/Folha.
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


class LupaScraper(BaseScraper):
    """
    Scraper para lupa.uol.com.br (Agencia Lupa).

    Estrutura do site:
    - Lista de checagens: /jornalismo/
    - Artigos: /jornalismo/YYYY/MM/DD/titulo/
    - Vereditos: FALSO, VERDADEIRO, EXAGERADO, CONTRADITORIO, INSUSTENTAVEL
    - Etiquetas coloridas (selos) indicam o veredito
    """

    DEFAULT_CONFIG = ScraperConfig(
        name="lupa",
        base_url="https://lupa.uol.com.br",
        rate_limit_rpm=2,
        timeout_seconds=30,
        max_retries=3,
    )

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    def get_article_urls(self, page: int = 1) -> List[str]:
        """Retorna URLs de artigos da pagina de checagens."""
        list_url = f"{self.config.base_url}/jornalismo/"
        if page > 1:
            list_url = f"{list_url}page/{page}/"

        html = self._request_with_retry(list_url)
        if not html:
            return []

        soup = self._parse_html(html)
        urls = []

        # Buscar links de artigos
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Match pattern /jornalismo/YYYY/MM/DD/ ou /YYYY/MM/DD/
            if re.match(r".*/\d{4}/\d{2}/\d{2}/", href):
                full_url = urljoin(self.config.base_url, href)
                if full_url not in urls and "lupa.uol.com.br" in full_url:
                    urls.append(full_url)

        logger.debug(f"[lupa] Found {len(urls)} article URLs on page {page}")
        return urls

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        """Parse de um artigo da Lupa."""
        soup = self._parse_html(html)

        # Titulo
        title_tag = soup.find("h1")
        if not title_tag:
            logger.warning(f"[lupa] No title found: {url}")
            return None
        title = title_tag.get_text(strip=True)

        # Veredito - Lupa usa "selos" coloridos
        verdict_label = self._extract_verdict(soup, title)

        # Claim
        claim = ""
        # Lupa geralmente tem o claim em destaque ou em blockquote
        claim_elem = soup.select_one(".claim, .afirmacao, blockquote, .destaque")
        if claim_elem:
            claim = claim_elem.get_text(strip=True)
        else:
            # Usar subtitulo
            subtitle = soup.select_one("h2, .subtitle, .lead")
            if subtitle:
                claim = subtitle.get_text(strip=True)

        # Conteudo
        content = ""
        content_elem = soup.select_one("article, .post-content, .materia-texto")
        if content_elem:
            paragraphs = content_elem.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Data
        published_at = None
        date_elem = soup.select_one("time[datetime], .data-publicacao, .date")
        if date_elem:
            datetime_str = date_elem.get("datetime") or date_elem.get_text(strip=True)
            published_at = self._parse_date(datetime_str)

        # Autor
        author = None
        author_elem = soup.select_one(".author, .autor, [rel='author']")
        if author_elem:
            author = author_elem.get_text(strip=True)

        # Tags
        tags = []
        tag_elems = soup.select(".tag, .categoria, [rel='tag']")
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
        # Buscar selo/etiqueta de veredito
        selo_selectors = [
            ".selo", ".etiqueta", ".rating", ".verdict",
            "[class*='selo']", "[class*='etiqueta']",
            "img[alt*='FALSO']", "img[alt*='VERDADEIRO']",
        ]

        for selector in selo_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Verificar alt de imagem
                if elem.name == "img":
                    alt = elem.get("alt", "")
                    if alt:
                        return alt.upper()
                # Verificar texto
                text = elem.get_text(strip=True)
                if text:
                    return text.upper()

        # Tentar extrair do titulo
        labels = ["FALSO", "VERDADEIRO", "EXAGERADO", "CONTRADITORIO", "INSUSTENTAVEL"]
        for label in labels:
            if label in title.upper():
                return label

        return "DESCONHECIDO"

    def _extract_id_from_url(self, url: str) -> str:
        """Extrai ID unico da URL."""
        parts = url.rstrip("/").split("/")
        if len(parts) >= 4:
            return f"lupa_{parts[-1]}"
        return f"lupa_{hash(url)}"

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse de data."""
        if not date_str:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d.%m.%Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

        # Regex fallback
        match = re.search(r"(\d{4})/(\d{2})/(\d{2})", date_str)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day), tzinfo=timezone.utc)

        return None
