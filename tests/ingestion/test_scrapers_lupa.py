"""
Tests for app/ingestion/scrapers/lupa.py

Comprehensive tests for the Lupa (Agência Lupa) scraper.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.ingestion.scrapers.base import ScraperConfig, VerdictType
from app.ingestion.scrapers.lupa import LupaScraper


class TestLupaScraper:
    """Test Lupa scraper."""

    def test_default_config(self):
        """Test default configuration."""
        scraper = LupaScraper()

        assert scraper.config.name == "lupa"
        assert scraper.config.base_url == "https://lupa.uol.com.br"
        assert scraper.config.rate_limit_rpm == 2

    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = ScraperConfig(
            name="custom_lupa",
            base_url="https://custom.lupa.com.br",
        )
        scraper = LupaScraper(config=custom_config)

        assert scraper.config.name == "custom_lupa"

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_page_1(self, mock_request):
        """Test getting article URLs from page 1."""
        html = """
        <html>
            <div>
                <a href="/jornalismo/2024/12/10/artigo-1/">Artigo 1</a>
                <a href="https://lupa.uol.com.br/2024/12/11/artigo-2/">Artigo 2</a>
            </div>
        </html>
        """
        mock_request.return_value = html

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 2
        assert any("2024/12/10/artigo-1" in url for url in urls)
        assert any("2024/12/11/artigo-2" in url for url in urls)
        mock_request.assert_called_once_with("https://lupa.uol.com.br/jornalismo/")

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_page_2(self, mock_request):
        """Test getting article URLs from page 2."""
        html = """
        <html>
            <a href="/2024/06/15/artigo/">Artigo</a>
        </html>
        """
        mock_request.return_value = html

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=2)

        mock_request.assert_called_once_with("https://lupa.uol.com.br/jornalismo/page/2/")

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_regex_matching(self, mock_request):
        """Test regex matching for date pattern."""
        html = """
        <html>
            <a href="/jornalismo/2024/01/20/artigo-especial/">Link 1</a>
            <a href="/2024/06/30/outro-artigo/">Link 2</a>
            <a href="/categoria/geral/">Not an article</a>
        </html>
        """
        mock_request.return_value = html

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) >= 2
        assert all("lupa.uol.com.br" in url for url in urls)

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_no_duplicates(self, mock_request):
        """Test duplicate URLs are removed."""
        html = """
        <html>
            <a href="/2024/12/10/artigo/">Link 1</a>
            <a href="/2024/12/10/artigo/">Link 2 (duplicate)</a>
        </html>
        """
        mock_request.return_value = html

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 1

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_filters_by_domain(self, mock_request):
        """Test that only lupa.uol.com.br URLs are included."""
        html = """
        <html>
            <a href="https://lupa.uol.com.br/2024/12/10/artigo/">Lupa</a>
            <a href="https://example.com/2024/12/10/other/">Other</a>
        </html>
        """
        mock_request.return_value = html

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=1)

        assert all("lupa.uol.com.br" in url for url in urls)

    @patch.object(LupaScraper, "_request_with_retry")
    def test_get_article_urls_request_failed(self, mock_request):
        """Test handling when request fails."""
        mock_request.return_value = None

        scraper = LupaScraper()
        urls = scraper.get_article_urls(page=1)

        assert urls == []

    def test_parse_article_with_selo(self):
        """Test parsing article with selo (verdict label)."""
        html = """
        <html>
            <h1>Título da Checagem</h1>
            <div class="selo">FALSO</div>
            <blockquote class="claim">Afirmação verificada aqui</blockquote>
            <article class="post-content">
                <p>Conteúdo da checagem.</p>
            </article>
            <time datetime="2024-12-10T14:30:00">10/12/2024</time>
            <div class="author">Repórter Lupa</div>
            <a class="tag">Saúde</a>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.title == "Título da Checagem"
        assert article.verdict_label == "FALSO"
        assert article.verdict == VerdictType.FALSE
        assert article.claim == "Afirmação verificada aqui"
        assert "Conteúdo da checagem" in article.content
        assert article.author == "Repórter Lupa"
        assert "Saúde" in article.tags

    def test_parse_article_verdict_from_image_alt(self):
        """Test extracting verdict from image alt text."""
        html = """
        <html>
            <h1>Título</h1>
            <img class="selo" alt="VERDADEIRO"/>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.verdict_label == "VERDADEIRO"
        assert article.verdict == VerdictType.TRUE

    def test_parse_article_verdict_in_title(self):
        """Test extracting verdict from title."""
        html = """
        <html>
            <h1>É FALSO que governo vai acabar com SUS</h1>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.verdict_label == "FALSO"

    def test_extract_verdict_all_types(self):
        """Test extracting all verdict types from Lupa."""
        verdicts = [
            ("VERDADEIRO", VerdictType.TRUE),
            ("FALSO", VerdictType.FALSE),
            ("EXAGERADO", VerdictType.EXAGGERATED),
            ("CONTRADITORIO", VerdictType.MISLEADING),
            ("INSUSTENTAVEL", VerdictType.UNVERIFIABLE),
        ]

        for verdict_text, expected_type in verdicts:
            html = f"""
            <html>
                <h1>Título</h1>
                <div class="etiqueta">{verdict_text}</div>
                <article><p>Conteúdo</p></article>
            </html>
            """

            scraper = LupaScraper()
            soup = scraper._parse_html(html)
            verdict = scraper._extract_verdict(soup, "Título")

            assert verdict == verdict_text

    def test_parse_article_claim_from_destaque(self):
        """Test extracting claim from destaque class."""
        html = """
        <html>
            <h1>Título</h1>
            <div class="destaque">Afirmação em destaque</div>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.claim == "Afirmação em destaque"

    def test_parse_article_claim_from_subtitle(self):
        """Test extracting claim from subtitle."""
        html = """
        <html>
            <h1>Título</h1>
            <h2 class="lead">Subtítulo com a afirmação</h2>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.claim == "Subtítulo com a afirmação"

    def test_parse_article_no_title(self):
        """Test parsing article without title returns None."""
        html = """
        <html>
            <body><p>Sem título</p></body>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is None

    def test_parse_article_content_from_materia_texto(self):
        """Test extracting content from materia-texto class."""
        html = """
        <html>
            <h1>Título</h1>
            <div class="materia-texto">
                <p>Parágrafo 1.</p>
                <p>Parágrafo 2.</p>
            </div>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert "Parágrafo 1" in article.content
        assert "Parágrafo 2" in article.content

    def test_parse_article_date_from_data_publicacao(self):
        """Test extracting date from data-publicacao class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="data-publicacao">2024-12-10T10:00:00</div>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.published_at == datetime(2024, 12, 10, 10, 0, 0, tzinfo=timezone.utc)

    def test_parse_article_author_from_autor_class(self):
        """Test extracting author from autor class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="autor">Maria Silva</div>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.author == "Maria Silva"

    def test_parse_article_tags_from_categoria(self):
        """Test extracting tags from categoria class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <a class="categoria">Política</a>
            <a class="categoria">Eleições</a>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert "Política" in article.tags
        assert "Eleições" in article.tags

    def test_extract_id_from_url(self):
        """Test extracting ID from URL."""
        scraper = LupaScraper()

        # Standard URL
        url1 = "https://lupa.uol.com.br/jornalismo/2024/12/10/artigo-teste/"
        id1 = scraper._extract_id_from_url(url1)
        assert id1 == "lupa_artigo-teste"

        # Without trailing slash
        url2 = "https://lupa.uol.com.br/jornalismo/2024/12/10/outro"
        id2 = scraper._extract_id_from_url(url2)
        assert id2 == "lupa_outro"

        # Short URL (fallback to hash)
        url3 = "https://lupa.uol.com.br/"
        id3 = scraper._extract_id_from_url(url3)
        assert id3.startswith("lupa_")

    def test_parse_date_iso_format(self):
        """Test parsing ISO datetime."""
        scraper = LupaScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00")
        assert dt == datetime(2024, 12, 10, 15, 30, 0, tzinfo=timezone.utc)

    def test_parse_date_with_timezone(self):
        """Test parsing datetime with timezone."""
        scraper = LupaScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00+00:00")
        assert dt is not None
        assert dt.year == 2024

    def test_parse_date_simple_date(self):
        """Test parsing simple date."""
        scraper = LupaScraper()

        dt = scraper._parse_date("2024-12-10")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_br_format(self):
        """Test parsing Brazilian date format."""
        scraper = LupaScraper()

        dt = scraper._parse_date("10/12/2024")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_dot_format(self):
        """Test parsing date with dots."""
        scraper = LupaScraper()

        dt = scraper._parse_date("10.12.2024")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_url_pattern(self):
        """Test parsing date from URL pattern."""
        scraper = LupaScraper()

        dt = scraper._parse_date("2024/06/15")
        assert dt == datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        scraper = LupaScraper()

        dt = scraper._parse_date("invalid date")
        assert dt is None

    def test_parse_date_empty(self):
        """Test parsing empty date."""
        scraper = LupaScraper()

        dt = scraper._parse_date("")
        assert dt is None

    def test_extract_verdict_multiple_selectors(self):
        """Test verdict extraction from multiple selectors."""
        scraper = LupaScraper()

        # Test etiqueta selector
        html1 = '<html><div class="etiqueta">FALSO</div></html>'
        soup1 = scraper._parse_html(html1)
        verdict1 = scraper._extract_verdict(soup1, "Title")
        assert verdict1 == "FALSO"

        # Test rating selector
        html2 = '<html><span class="rating">VERDADEIRO</span></html>'
        soup2 = scraper._parse_html(html2)
        verdict2 = scraper._extract_verdict(soup2, "Title")
        assert verdict2 == "VERDADEIRO"

        # Test verdict selector
        html3 = '<html><div class="verdict">EXAGERADO</div></html>'
        soup3 = scraper._parse_html(html3)
        verdict3 = scraper._extract_verdict(soup3, "Title")
        assert verdict3 == "EXAGERADO"

    def test_extract_verdict_from_title_fallback(self):
        """Test verdict extraction from title as fallback."""
        scraper = LupaScraper()

        html = '<html><h1>Título sem selo</h1></html>'
        soup = scraper._parse_html(html)

        title1 = "É FALSO que X aconteceu"
        verdict1 = scraper._extract_verdict(soup, title1)
        assert verdict1 == "FALSO"

        title2 = "VERDADEIRO: Y foi confirmado"
        verdict2 = scraper._extract_verdict(soup, title2)
        assert verdict2 == "VERDADEIRO"

    def test_extract_verdict_unknown(self):
        """Test verdict extraction returns DESCONHECIDO when not found."""
        scraper = LupaScraper()

        html = '<html><h1>Título neutro</h1></html>'
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "Título neutro")

        assert verdict == "DESCONHECIDO"

    def test_parse_article_full_example(self):
        """Test parsing complete article with all fields."""
        html = """
        <html>
            <h1>EXAGERADO: Político afirma crescimento econômico absurdo</h1>
            <div class="selo-lupa-exagerado">EXAGERADO</div>
            <div class="afirmacao">Político diz que economia cresceu 500%</div>
            <article class="materia-texto">
                <p>A afirmação do político é exagerada.</p>
                <p>O crescimento real foi de 5%, não 500%.</p>
                <p>Os dados foram inflados.</p>
            </article>
            <time datetime="2024-09-05T16:45:00">05/09/2024</time>
            <div class="autor">Carlos Investigador</div>
            <a rel="tag">Economia</a>
            <a class="categoria">Política</a>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article(
            "https://lupa.uol.com.br/jornalismo/2024/09/05/politico-economia/",
            html
        )

        assert article is not None
        assert article.external_id == "lupa_politico-economia"
        assert article.source_name == "lupa"
        assert article.title == "EXAGERADO: Político afirma crescimento econômico absurdo"
        assert article.claim == "Político diz que economia cresceu 500%"
        assert article.verdict == VerdictType.EXAGGERATED
        assert article.verdict_label == "EXAGERADO"
        assert "afirmação do político é exagerada" in article.content
        assert article.published_at == datetime(2024, 9, 5, 16, 45, 0, tzinfo=timezone.utc)
        assert article.author == "Carlos Investigador"
        assert "Economia" in article.tags
        assert "Política" in article.tags

    def test_parse_article_minimal(self):
        """Test parsing minimal article with only required fields."""
        html = """
        <html>
            <h1>Título Básico</h1>
            <article><p>Conteúdo simples.</p></article>
        </html>
        """

        scraper = LupaScraper()
        article = scraper.parse_article("https://lupa.uol.com.br/jornalismo/2024/12/10/test/", html)

        assert article is not None
        assert article.title == "Título Básico"
        assert article.claim == "Título Básico"  # Falls back to title
        assert article.verdict_label == "DESCONHECIDO"
        assert article.published_at is None
        assert article.author is None
        assert article.tags == []
