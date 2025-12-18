"""
Tests for app/ingestion/scrapers/efarsas.py

Comprehensive tests for the E-farsas scraper.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.ingestion.scrapers.base import ScraperConfig, VerdictType
from app.ingestion.scrapers.efarsas import EFarsasScraper


class TestEFarsasScraper:
    """Test E-farsas scraper."""

    def test_default_config(self):
        """Test default configuration."""
        scraper = EFarsasScraper()

        assert scraper.config.name == "efarsas"
        assert scraper.config.base_url == "https://www.e-farsas.com"
        assert scraper.config.rate_limit_rpm == 2

    def test_custom_config(self):
        """Test custom configuration."""
        custom_config = ScraperConfig(
            name="custom_efarsas",
            base_url="https://custom.e-farsas.com",
        )
        scraper = EFarsasScraper(config=custom_config)

        assert scraper.config.name == "custom_efarsas"

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_page_1(self, mock_request):
        """Test getting article URLs from page 1."""
        html = """
        <html>
            <article>
                <a href="https://www.e-farsas.com/artigo-1/">Artigo 1</a>
                <h2><a href="https://www.e-farsas.com/artigo-2/">Artigo 2</a></h2>
            </article>
            <div class="post">
                <h3><a href="https://www.e-farsas.com/artigo-3/">Artigo 3</a></h3>
            </div>
        </html>
        """
        mock_request.return_value = html

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 3
        assert "https://www.e-farsas.com/artigo-1/" in urls
        assert "https://www.e-farsas.com/artigo-2/" in urls
        assert "https://www.e-farsas.com/artigo-3/" in urls
        mock_request.assert_called_once_with("https://www.e-farsas.com")

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_page_2(self, mock_request):
        """Test getting article URLs from page 2."""
        html = """
        <html>
            <article>
                <a href="https://www.e-farsas.com/artigo-4/">Artigo 4</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=2)

        mock_request.assert_called_once_with("https://www.e-farsas.com/page/2/")

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_excludes_special_pages(self, mock_request):
        """Test that category/tag/author/page URLs are excluded."""
        html = """
        <html>
            <article>
                <a href="https://www.e-farsas.com/artigo-valido/">Artigo</a>
                <a href="https://www.e-farsas.com/category/politica/">Categoria</a>
                <a href="https://www.e-farsas.com/tag/covid/">Tag</a>
                <a href="https://www.e-farsas.com/page/2/">Page</a>
                <a href="https://www.e-farsas.com/author/joao/">Autor</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 1
        assert "https://www.e-farsas.com/artigo-valido/" in urls

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_no_duplicates(self, mock_request):
        """Test duplicate URLs are removed."""
        html = """
        <html>
            <article>
                <a href="https://www.e-farsas.com/artigo-1/">Artigo 1</a>
                <a href="https://www.e-farsas.com/artigo-1/">Artigo 1 (dup)</a>
                <a href="https://www.e-farsas.com/artigo-2/">Artigo 2</a>
            </article>
        </html>
        """
        mock_request.return_value = html

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 2

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_limits_to_20(self, mock_request):
        """Test URLs are limited to 20."""
        links = "".join([
            f'<a href="https://www.e-farsas.com/artigo-{i}/">Artigo {i}</a>'
            for i in range(50)
        ])
        html = f"<html><article>{links}</article></html>"
        mock_request.return_value = html

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=1)

        assert len(urls) == 20

    @patch.object(EFarsasScraper, "_request_with_retry")
    def test_get_article_urls_request_failed(self, mock_request):
        """Test handling when request fails."""
        mock_request.return_value = None

        scraper = EFarsasScraper()
        urls = scraper.get_article_urls(page=1)

        assert urls == []

    def test_parse_article_standard(self):
        """Test parsing standard article."""
        html = """
        <html>
            <h1>Boato sobre vacina é falso</h1>
            <div class="verdict">FALSO</div>
            <blockquote class="claim">Vacina contém chip</blockquote>
            <article class="entry-content">
                <p>Este boato é falso.</p>
                <p>Não há chips em vacinas.</p>
            </article>
            <time datetime="2024-12-10T10:30:00">10/12/2024</time>
            <div class="author">João Verificador</div>
            <a class="tag">Saúde</a>
            <a class="tag">COVID-19</a>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/vacina-chip/", html)

        assert article is not None
        assert article.title == "Boato sobre vacina é falso"
        assert article.verdict_label == "FALSO"
        assert article.verdict == VerdictType.FALSE
        assert article.claim == "Vacina contém chip"
        assert "Não há chips em vacinas" in article.content
        assert article.author == "João Verificador"
        assert len(article.tags) == 2

    def test_extract_verdict_from_url_category_falso(self):
        """Test extracting verdict from URL with /category/falso/."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/category/falso/artigo/")

        assert verdict == "FALSO"

    def test_extract_verdict_from_url_category_verdadeiro(self):
        """Test extracting verdict from URL with /category/verdadeiro/."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/category/verdadeiro/artigo/")

        assert verdict == "VERDADEIRO"

    def test_extract_verdict_from_url_falso(self):
        """Test extracting verdict from URL with /falso/."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/falso/artigo/")

        assert verdict == "FALSO"

    def test_extract_verdict_from_image_alt(self):
        """Test extracting verdict from image alt attribute."""
        html = """
        <html>
            <h1>Título</h1>
            <img alt="Falso" class="verdict-image"/>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/artigo/")

        assert verdict == "FALSO"

    def test_extract_verdict_from_element(self):
        """Test extracting verdict from verdict element."""
        html = """
        <html>
            <h1>Título</h1>
            <div class="rating">VERDADEIRO</div>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/artigo/")

        assert verdict == "VERDADEIRO"

    def test_extract_verdict_from_categories(self):
        """Test extracting verdict from category links."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="post-categories">
                <a>Notícias</a>
                <a>Falso</a>
            </div>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/artigo/")

        assert verdict == "FALSO"

    def test_extract_verdict_verdade_from_categories(self):
        """Test extracting VERDADEIRO from category with 'verdade'."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="category">
                <a>Verdade</a>
            </div>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/artigo/")

        assert verdict == "VERDADEIRO"

    def test_extract_verdict_unknown(self):
        """Test verdict returns DESCONHECIDO when not found."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        soup = scraper._parse_html(html)
        verdict = scraper._extract_verdict(soup, "https://www.e-farsas.com/artigo/")

        assert verdict == "DESCONHECIDO"

    def test_parse_article_claim_from_subtitle(self):
        """Test extracting claim from subtitle."""
        html = """
        <html>
            <h1>Título</h1>
            <h2 class="excerpt">Subtítulo com afirmação</h2>
            <article><p>Conteúdo</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is not None
        assert article.claim == "Subtítulo com afirmação"

    def test_parse_article_no_title(self):
        """Test parsing article without title returns None."""
        html = """
        <html>
            <body><p>Sem título</p></body>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is None

    def test_parse_article_content_from_content_class(self):
        """Test extracting content from content class."""
        html = """
        <html>
            <h1>Título</h1>
            <div class="content">
                <p>Parágrafo 1.</p>
                <p>Parágrafo 2.</p>
            </div>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is not None
        assert "Parágrafo 1" in article.content
        assert "Parágrafo 2" in article.content

    def test_parse_article_date_from_post_date(self):
        """Test extracting date from post-date class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="post-date">2024-12-10T14:00:00</div>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is not None
        assert article.published_at == datetime(2024, 12, 10, 14, 0, 0, tzinfo=timezone.utc)

    def test_parse_article_author_from_byline(self):
        """Test extracting author from byline class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <div class="byline">Ana Escritora</div>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is not None
        assert article.author == "Ana Escritora"

    def test_parse_article_author_from_author_name(self):
        """Test extracting author from author-name class."""
        html = """
        <html>
            <h1>Título</h1>
            <article><p>Conteúdo</p></article>
            <span class="author-name">Pedro Silva</span>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/test/", html)

        assert article is not None
        assert article.author == "Pedro Silva"

    def test_extract_id_from_url(self):
        """Test extracting ID from URL."""
        scraper = EFarsasScraper()

        # Standard URL
        url1 = "https://www.e-farsas.com/politica/artigo-teste/"
        id1 = scraper._extract_id_from_url(url1)
        assert id1 == "efarsas_artigo-teste"

        # Without trailing slash
        url2 = "https://www.e-farsas.com/outro-artigo"
        id2 = scraper._extract_id_from_url(url2)
        assert id2 == "efarsas_outro-artigo"

        # Empty slug (fallback to hash)
        url3 = "https://www.e-farsas.com/"
        id3 = scraper._extract_id_from_url(url3)
        assert id3.startswith("efarsas_")

    def test_parse_date_iso_format(self):
        """Test parsing ISO datetime."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00")
        assert dt == datetime(2024, 12, 10, 15, 30, 0, tzinfo=timezone.utc)

    def test_parse_date_with_timezone(self):
        """Test parsing datetime with timezone."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("2024-12-10T15:30:00+00:00")
        assert dt is not None
        assert dt.year == 2024

    def test_parse_date_simple_date(self):
        """Test parsing simple date."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("2024-12-10")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_br_format(self):
        """Test parsing Brazilian date format."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("10/12/2024")
        assert dt == datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)

    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("invalid date")
        assert dt is None

    def test_parse_date_empty(self):
        """Test parsing empty date."""
        scraper = EFarsasScraper()

        dt = scraper._parse_date("")
        assert dt is None

    def test_parse_article_full_example(self):
        """Test parsing complete article with all fields."""
        html = """
        <html>
            <h1>Fake news sobre eleições é desmentida</h1>
            <div class="selo">FALSO</div>
            <blockquote>Urnas eletrônicas foram fraudadas</blockquote>
            <article class="post-content">
                <p>A afirmação de fraude em urnas é falsa.</p>
                <p>Todas as auditorias confirmaram a segurança.</p>
                <p>O boato foi amplamente compartilhado nas redes.</p>
            </article>
            <time datetime="2024-10-15T18:20:00">15/10/2024</time>
            <a rel="author">Laura Checadora</a>
            <a class="tag">Política</a>
            <a class="tag">Eleições</a>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article(
            "https://www.e-farsas.com/categoria/falso/urnas-fraude/",
            html
        )

        assert article is not None
        assert article.external_id == "efarsas_urnas-fraude"
        assert article.source_name == "efarsas"
        assert article.title == "Fake news sobre eleições é desmentida"
        assert article.claim == "Urnas eletrônicas foram fraudadas"
        assert article.verdict == VerdictType.FALSE
        assert article.verdict_label == "FALSO"
        assert "afirmação de fraude em urnas é falsa" in article.content
        assert article.published_at == datetime(2024, 10, 15, 18, 20, 0, tzinfo=timezone.utc)
        assert article.author == "Laura Checadora"
        assert "Política" in article.tags
        assert "Eleições" in article.tags

    def test_parse_article_minimal(self):
        """Test parsing minimal article with only required fields."""
        html = """
        <html>
            <h1>Título Simples</h1>
            <article><p>Conteúdo básico.</p></article>
        </html>
        """

        scraper = EFarsasScraper()
        article = scraper.parse_article("https://www.e-farsas.com/simples/", html)

        assert article is not None
        assert article.title == "Título Simples"
        assert article.claim == "Título Simples"  # Falls back to title
        assert article.verdict_label == "DESCONHECIDO"
        assert article.published_at is None
        assert article.author is None
        assert article.tags == []
