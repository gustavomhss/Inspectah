"""
Tests for app/ingestion/scrapers/aosfatos.py

Comprehensive tests for the AosFatos scraper.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.ingestion.scrapers.aosfatos import AosFatosScraper
from app.ingestion.scrapers.base import ScraperConfig, VerdictType


class TestAosFatosScraper:
    """Test AosFatos scraper."""

    def test_default_config(self):
        """Test default configuration."""
        scraper = AosFatosScraper()

        assert scraper.config.name == "aos_fatos"
        assert scraper.config.base_url == "https://www.aosfatos.org"
        assert scraper.config.rate_limit_rpm == 2

    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = ScraperConfig(
            name="custom_aos_fatos",
            base_url="https://custom.aosfatos.org",
        )
        scraper = AosFatosScraper(config=custom_config)

        assert scraper.config.name == "custom_aos_fatos"

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_page_1(self, mock_request):
        """Test getting article URLs from page 1."""
        html = """
        <html>
            <article>
                <a href="/noticias/2024/12/10/artigo-teste/">Artigo 1</a>
                <a href="/noticias/2024/12/11/outro-artigo/">Artigo 2</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 2
        assert "https://www.aosfatos.org/noticias/2024/12/10/artigo-teste/" in urls
        assert "https://www.aosfatos.org/noticias/2024/12/11/outro-artigo/" in urls
        mock_request.assert_called_once_with("https://www.aosfatos.org/noticias/checamos/")

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_page_2(self, mock_request):
        """Test getting article URLs from page 2."""
        html = """
        <html>
            <article>
                <a href="/noticias/2024/12/09/artigo/">Artigo</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=2)

        mock_request.assert_called_once_with("https://www.aosfatos.org/noticias/checamos/page/2/")

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_excludes_checamos(self, mock_request):
        """Test that checamos page itself is excluded."""
        html = """
        <html>
            <article>
                <a href="/noticias/2024/12/10/artigo/">Artigo</a>
                <a href="/noticias/checamos/">Checamos</a>
                <a href="/noticias/checamos/page/2/">Page 2</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 1
        assert "/artigo/" in urls[0]

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_fallback_regex(self, mock_request):
        """Test fallback regex matching."""
        html = """
        <html>
            <div>
                <a href="https://www.aosfatos.org/noticias/2024/06/15/artigo-especial/">Link 1</a>
                <a href="/noticias/2024/01/20/outro/">Link 2</a>
            </div>
        </html>
        """
        mock_request.return_value = html

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) >= 2

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_no_duplicates(self, mock_request):
        """Test duplicate URLs are removed."""
        html = """
        <html>
            <article>
                <a href="/noticias/2024/12/10/artigo/">Artigo</a>
                <a href="/noticias/2024/12/10/artigo/">Artigo (dup)</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 1

    @patch.object(AosFatosScraper, "_request_with_retry")
    def test_get_article_urls_request_failed(self, mock_request):
        """Test handling when request fails."""
        mock_request.return_value = None

        scraper = AosFatosScraper()
        urls = scraper.get_article_urls(page=1)

        assert urls == []

    def test_parse_article_with_verdict_element(self):
        """Test parsing article with verdict element."""
        html = """
        <html>
            <h1>Título do Artigo</h1>
            <div class="verdict">FALSO</div>
            <div class="claim">Afirmação sendo verificada</div>
            <article class="post-content">
                <p>Primeiro parágrafo do artigo.</p>
                <p>Segundo parágrafo.</p>
            </article>
            <time datetime="2024-12-10T15:30:00">10/12/2024</time>
            <div class="author">João Repórter</div>
            <a class="tag">Política</a>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.title == "Título do Artigo"
        assert article.verdict_label == "FALSO"
        assert article.verdict == VerdictType.FALSE
        assert article.claim == "Afirmação sendo verificada"
        assert "Primeiro parágrafo" in article.content
        assert article.author == "João Repórter"
        assert "Política" in article.tags

    def test_parse_article_verdict_in_title(self):
        """Test extracting verdict from title."""
        html = """
        <html>
            <h1>É FALSO que vacina causa autismo</h1>
            <article><p>Conteúdo do artigo.</p></article>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.verdict_label == "FALSO"
        assert article.verdict == VerdictType.FALSE

    def test_parse_article_claim_from_subtitle(self):
        """Test extracting claim from subtitle."""
        html = """
        <html>
            <h1>Checagem de Fatos</h1>
            <h2 class="subtitle">Esta é a afirmação verificada</h2>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.claim == "Esta é a afirmação verificada"

    def test_parse_article_claim_from_blockquote(self):
        """Test extracting claim from blockquote."""
        html = """
        <html>
            <h1>Título</h1>
            <blockquote>Afirmação em blockquote</blockquote>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.claim == "Afirmação em blockquote"

    def test_parse_article_no_title(self):
        """Test parsing article without title returns None."""
        html = """
        <html>
            <body>
                <p>Sem título</p>
            </body>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is None

    def test_parse_article_content_from_main(self):
        """Test extracting content from main element."""
        html = """
        <html>
            <h1>Título</h1>
            <main>
                <p>Parágrafo 1.</p>
                <p>Parágrafo 2.</p>
            </main>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert "Parágrafo 1" in article.content
        assert "Parágrafo 2" in article.content

    def test_parse_article_all_verdict_types(self):
        """Test recognizing all verdict types."""
        verdicts = [
            ("VERDADEIRO", VerdictType.TRUE),
            ("ENGANOSO", VerdictType.MISLEADING),
            ("EXAGERADO", VerdictType.EXAGGERATED),
        ]

        for verdict_text, expected_type in verdicts:
            html = f"""
            <html>
                <h1>{verdict_text}: Título</h1>
                <article><p>Conteúdo</p></article>
            </html>
            """

            scraper = AosFatosScraper()
            article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

            assert article is not None
            assert article.verdict_label == verdict_text
            assert article.verdict == expected_type

    def test_extract_id_from_url(self):
        """Test extracting ID from URL."""
        scraper = AosFatosScraper()

        # Standard URL
        url1 = "https://www.aosfatos.org/noticias/2024/12/10/artigo-teste/"
        id1 = scraper._extract_id_from_url(url1)
        assert id1 == "aosfatos_artigo-teste"

        # Without trailing slash
        url2 = "https://www.aosfatos.org/noticias/2024/12/10/outro-artigo"
        id2 = scraper._extract_id_from_url(url2)
        assert id2 == "aosfatos_outro-artigo"

        # Short URL (fallback to hash)
        url3 = "https://www.aosfatos.org/"
        id3 = scraper._extract_id_from_url(url3)
        assert id3.startswith("aosfatos_")

    def test_parse_date_iso_format(self):
        """Test parsing ISO datetime."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00")
        assert dt == datetime(2024, 12, 10, 15, 30, 0, tzinfo=timezone.utc)

    def test_parse_date_with_timezone(self):
        """Test parsing datetime with timezone."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00+00:00")
        assert dt is not None
        assert dt.year == 2024

    def test_parse_date_simple_date(self):
        """Test parsing simple date."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("2024-12-10")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_br_format(self):
        """Test parsing Brazilian format."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("10/12/2024")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_url_pattern(self):
        """Test parsing date from URL pattern."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("2024/06/15")
        assert dt == datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("invalid")
        assert dt is None

    def test_parse_date_empty(self):
        """Test parsing empty date."""
        scraper = AosFatosScraper()

        dt = scraper._parse_date("")
        assert dt is None

    def test_parse_article_full_example(self):
        """Test parsing complete article."""
        html = """
        <html>
            <h1>ENGANOSO: Governo aumenta impostos em 50%</h1>
            <h2 class="lead">Governo anuncia aumento de 50% em impostos</h2>
            <div class="rating">ENGANOSO</div>
            <article class="entry-content">
                <p>A afirmação é enganosa.</p>
                <p>O aumento real é de 5%, não 50%.</p>
                <p>Verificamos todas as fontes oficiais.</p>
            </article>
            <time datetime="2024-08-20T10:00:00">20/08/2024</time>
            <a rel="author">Ana Jornalista</a>
            <a class="category">Economia</a>
            <a class="category">Impostos</a>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article(
            "https://www.aosfatos.org/noticias/2024/08/20/impostos/",
            html
        )

        assert article is not None
        assert article.external_id == "aosfatos_impostos"
        assert article.source_name == "aos_fatos"
        assert article.title == "ENGANOSO: Governo aumenta impostos em 50%"
        assert article.claim == "Governo anuncia aumento de 50% em impostos"
        assert article.verdict == VerdictType.MISLEADING
        assert article.verdict_label == "ENGANOSO"
        assert "aumento real é de 5%" in article.content
        assert article.published_at == datetime(2024, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
        assert article.author == "Ana Jornalista"
        assert "Economia" in article.tags
        assert "Impostos" in article.tags

    def test_parse_article_minimal(self):
        """Test parsing minimal article."""
        html = """
        <html>
            <h1>Título Mínimo</h1>
            <article><p>Conteúdo básico.</p></article>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.title == "Título Mínimo"
        assert article.claim == "Título Mínimo"  # Falls back to title
        assert article.verdict_label == "DESCONHECIDO"
        assert article.published_at is None
        assert article.author is None
        assert article.tags == []

    def test_parse_article_verdict_from_rating_class(self):
        """Test extracting verdict from rating class."""
        html = """
        <html>
            <h1>Título</h1>
            <span class="rating">VERDADEIRO</span>
            <article><p>Conteúdo.</p></article>
        </html>
        """

        scraper = AosFatosScraper()
        article = scraper.parse_article("https://www.aosfatos.org/noticias/2024/12/10/test/", html)

        assert article is not None
        assert article.verdict_label == "VERDADEIRO"
        assert article.verdict == VerdictType.TRUE
