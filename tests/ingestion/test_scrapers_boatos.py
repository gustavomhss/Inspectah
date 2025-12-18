"""
Tests for app/ingestion/scrapers/boatos.py

Comprehensive tests for the Boatos.org scraper.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from app.ingestion.scrapers.base import ScraperConfig, VerdictType
from app.ingestion.scrapers.boatos import BoatosScraper


class TestBoatosScraper:
    """Test Boatos.org scraper."""

    def test_default_config(self):
        """Test default configuration."""
        scraper = BoatosScraper()

        assert scraper.config.name == "boatos"
        assert scraper.config.base_url == "https://www.boatos.org"
        assert scraper.config.rate_limit_rpm == 2
        assert scraper.config.timeout_seconds == 30
        assert scraper.config.max_retries == 3

    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = ScraperConfig(
            name="custom_boatos",
            base_url="https://custom.boatos.org",
            rate_limit_rpm=5,
        )
        scraper = BoatosScraper(config=custom_config)

        assert scraper.config.name == "custom_boatos"
        assert scraper.config.base_url == "https://custom.boatos.org"

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_page_1(self, mock_request):
        """Test getting article URLs from page 1."""
        html = """
        <html>
            <article>
                <a href="https://www.boatos.org/politica/artigo-1/">Artigo 1</a>
                <a href="https://www.boatos.org/saude/artigo-2/">Artigo 2</a>
            </article>
            <div class="post">
                <h2><a href="https://www.boatos.org/tecnologia/artigo-3/">Artigo 3</a></h2>
            </div>
        </html>
        """
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 3
        assert "https://www.boatos.org/politica/artigo-1/" in urls
        assert "https://www.boatos.org/saude/artigo-2/" in urls
        assert "https://www.boatos.org/tecnologia/artigo-3/" in urls
        mock_request.assert_called_once_with("https://www.boatos.org")

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_page_2(self, mock_request):
        """Test getting article URLs from page 2."""
        html = """
        <html>
            <article>
                <a href="https://www.boatos.org/artigo-4/">Artigo 4</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=2)

        mock_request.assert_called_once_with("https://www.boatos.org/page/2/")

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_excludes_category_pages(self, mock_request):
        """Test that category/tag/author pages are excluded."""
        html = """
        <html>
            <article>
                <a href="https://www.boatos.org/artigo-1/">Artigo</a>
                <a href="https://www.boatos.org/category/politica/">Categoria</a>
                <a href="https://www.boatos.org/tag/covid/">Tag</a>
                <a href="https://www.boatos.org/page/2/">Pagina</a>
                <a href="https://www.boatos.org/author/joao/">Autor</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 1
        assert "https://www.boatos.org/artigo-1/" in urls

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_fallback(self, mock_request):
        """Test fallback URL extraction."""
        html = """
        <html>
            <div>
                <a href="https://www.boatos.org/artigo-especial/">Link 1</a>
                <a href="https://www.boatos.org/outro-artigo/">Link 2</a>
            </div>
        </html>
        """
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) >= 1

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_no_duplicates(self, mock_request):
        """Test that duplicate URLs are removed."""
        html = """
        <html>
            <article>
                <a href="https://www.boatos.org/artigo-1/">Artigo 1</a>
                <a href="https://www.boatos.org/artigo-1/">Artigo 1 (dup)</a>
                <a href="https://www.boatos.org/artigo-2/">Artigo 2</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 2

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_request_failed(self, mock_request):
        """Test handling when request fails."""
        mock_request.return_value = None

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert urls == []

    @patch.object(BoatosScraper, "_request_with_retry")
    def test_get_article_urls_limits_to_20(self, mock_request):
        """Test that URLs are limited to 20."""
        links = "".join([
            f'<a href="https://www.boatos.org/artigo-{i}/">Artigo {i}</a>'
            for i in range(50)
        ])
        html = f"<html><article>{links}</article></html>"
        mock_request.return_value = html

        scraper = BoatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 20

    def test_parse_article_standard(self):
        """Test parsing a standard article."""
        html = """
        <html>
            <h1>#Boato: Vacina causa 5G no corpo</h1>
            <div class="boato">
                Vacina contra COVID-19 instala chip 5G no corpo das pessoas
            </div>
            <article>
                <p>Este boato é completamente falso.</p>
                <p>Não há evidências de chips 5G em vacinas.</p>
            </article>
            <time datetime="2024-01-15T10:30:00">15/01/2024</time>
            <div class="author">João Silva</div>
            <div class="tag">COVID-19</div>
            <div class="tag">Saúde</div>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/vacina-5g/", html)

        assert article is not None
        assert article.title == "#Boato: Vacina causa 5G no corpo"
        assert "Vacina contra COVID-19" in article.claim
        assert article.verdict == VerdictType.FALSE
        assert article.verdict_label == "FALSO"
        assert "completamente falso" in article.content
        assert article.author == "João Silva"
        assert len(article.tags) == 2
        assert "COVID-19" in article.tags

    def test_parse_article_claim_from_blockquote(self):
        """Test extracting claim from blockquote."""
        html = """
        <html>
            <h1>Título do artigo</h1>
            <blockquote>Esta é a afirmação sendo verificada</blockquote>
            <article>
                <p>Conteúdo do artigo.</p>
            </article>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert article.claim == "Esta é a afirmação sendo verificada"

    def test_parse_article_claim_from_title(self):
        """Test extracting claim from title when no boato element."""
        html = """
        <html>
            <h1>#boato: Governo vai fechar internet</h1>
            <article>
                <p>Conteúdo do artigo.</p>
            </article>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert article.claim == "Governo vai fechar internet"

    def test_parse_article_verdict_verdade(self):
        """Test parsing article marked as VERDADE (rare case)."""
        html = """
        <html>
            <h1>#verdade: Isso e verdade</h1>
            <article>
                <p>Isso e verdade mesmo.</p>
            </article>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert article.verdict == VerdictType.TRUE
        assert article.verdict_label == "VERDADEIRO"

    def test_parse_article_verdict_verdade_in_content(self):
        """Test detecting VERDADE in content."""
        html = """
        <html>
            <h1>verdade</h1>
            <article>
                <p>Isso e verdade e foi confirmado.</p>
            </article>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert article.verdict == VerdictType.TRUE

    def test_parse_article_no_title(self):
        """Test parsing article without title."""
        html = """
        <html>
            <body>
                <p>Sem título</p>
            </body>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is None

    def test_parse_article_content_from_entry_content(self):
        """Test extracting content from entry-content class."""
        html = """
        <html>
            <h1>Título</h1>
            <div class="entry-content">
                <p>Primeiro parágrafo.</p>
                <p>Segundo parágrafo.</p>
            </div>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert "Primeiro parágrafo" in article.content
        assert "Segundo parágrafo" in article.content

    def test_parse_article_author_from_rel_author(self):
        """Test extracting author from rel=author."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <a rel="author">Maria Santos</a>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert article.author == "Maria Santos"

    def test_parse_article_tags_from_categories(self):
        """Test extracting tags from post-categories."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="post-categories">
                <a>Política</a>
                <a>Eleições</a>
            </div>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/test/", html)

        assert article is not None
        assert "Política" in article.tags
        assert "Eleições" in article.tags

    def test_extract_id_from_url(self):
        """Test extracting ID from URL."""
        scraper = BoatosScraper()

        # Normal URL with slug
        url1 = "https://www.boatos.org/politica/vacina-5g/"
        id1 = scraper._extract_id_from_url(url1)
        assert id1 == "boatos_vacina-5g"

        # URL ending with /
        url2 = "https://www.boatos.org/artigo-teste/"
        id2 = scraper._extract_id_from_url(url2)
        assert id2 == "boatos_artigo-teste"

        # URL without trailing /
        url3 = "https://www.boatos.org/outro-artigo"
        id3 = scraper._extract_id_from_url(url3)
        assert id3 == "boatos_outro-artigo"

        # Empty slug (fallback to hash)
        url4 = "https://www.boatos.org/"
        id4 = scraper._extract_id_from_url(url4)
        assert id4.startswith("boatos_")

    def test_parse_date_iso_format(self):
        """Test parsing ISO datetime format."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("2024-01-15T10:30:00")
        assert dt == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_parse_date_iso_with_timezone(self):
        """Test parsing ISO datetime with timezone."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("2024-01-15T10:30:00+00:00")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_date_simple_date(self):
        """Test parsing simple date format."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("2024-01-15")
        assert dt == datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_br_format(self):
        """Test parsing Brazilian date format."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("15/01/2024")
        assert dt == datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("invalid date")
        assert dt is None

    def test_parse_date_empty(self):
        """Test parsing empty date."""
        scraper = BoatosScraper()

        dt = scraper._parse_date("")
        assert dt is None

    def test_parse_date_none(self):
        """Test parsing None date."""
        scraper = BoatosScraper()

        dt = scraper._parse_date(None)
        assert dt is None

    def test_parse_article_full_example(self):
        """Test parsing complete article with all fields."""
        html = """
        <html>
            <h1>#Boato: Política vai mudar</h1>
            <div class="claim">Governo vai fazer mudança radical na política</div>
            <article class="entry-content">
                <p>Este boato circula nas redes sociais.</p>
                <p>Verificamos todas as fontes.</p>
                <p>Conclusão: é falso.</p>
            </article>
            <time datetime="2024-06-10T14:20:00">10/06/2024</time>
            <div class="author">Pedro Investigador</div>
            <a rel="tag">Política</a>
            <a rel="tag">Governo</a>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/politica-mudanca/", html)

        assert article is not None
        assert article.external_id == "boatos_politica-mudanca"
        assert article.source_name == "boatos"
        assert article.url == "https://www.boatos.org/politica-mudanca/"
        assert article.title == "#Boato: Política vai mudar"
        assert article.claim == "Governo vai fazer mudança radical na política"
        assert article.verdict == VerdictType.FALSE
        assert article.verdict_label == "FALSO"
        assert "Verificamos todas as fontes" in article.content
        assert article.published_at == datetime(2024, 6, 10, 14, 20, 0, tzinfo=timezone.utc)
        assert article.author == "Pedro Investigador"
        assert len(article.tags) == 2
        assert "Política" in article.tags
        assert "Governo" in article.tags

    def test_parse_article_minimal(self):
        """Test parsing minimal article with only required fields."""
        html = """
        <html>
            <h1>Título Simples</h1>
            <article><p>Conteúdo básico.</p></article>
        </html>
        """

        scraper = BoatosScraper()
        article = scraper.parse_article("https://www.boatos.org/simples/", html)

        assert article is not None
        assert article.title == "Título Simples"
        assert article.claim == "Título Simples"  # Falls back to title
        assert article.verdict == VerdictType.FALSE  # Default for Boatos
        assert article.verdict_label == "FALSO"
        assert article.published_at is None
        assert article.author is None
        assert article.tags == []
