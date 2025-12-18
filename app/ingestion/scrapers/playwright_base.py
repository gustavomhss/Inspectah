"""
S39 - Playwright Scraper Base

Framework base para scrapers que utilizam Playwright para renderizacao
JavaScript e automacao de browser.

Features:
- Browser pool com reutilizacao de contextos
- Stealth mode para evitar deteccao
- Screenshot para debug
- Suporte a proxy rotation
- Retry com backoff exponencial
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

from app.ingestion.scrapers.base import ScrapedArticle, ScraperResult, VerdictType

logger = logging.getLogger(__name__)

# Type for Playwright page (to avoid import when not installed)
PageType = TypeVar("PageType")


class BrowserType(str, Enum):
    """Tipos de browser suportados."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class StealthLevel(str, Enum):
    """Niveis de stealth mode."""
    NONE = "none"
    BASIC = "basic"  # User-agent rotation, viewport randomization
    STANDARD = "standard"  # + Webdriver detection bypass
    AGGRESSIVE = "aggressive"  # + All anti-fingerprinting measures


@dataclass
class PlaywrightConfig:
    """Configuracao para scraper Playwright."""
    name: str
    base_url: str
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = True
    stealth_level: StealthLevel = StealthLevel.STANDARD
    rate_limit_rpm: int = 10  # Higher than httpx scrapers
    timeout_ms: int = 30000
    navigation_timeout_ms: int = 60000
    max_retries: int = 3
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "pt-BR"
    timezone_id: str = "America/Sao_Paulo"
    screenshot_on_error: bool = True
    screenshot_dir: str = "data/screenshots"
    proxy: Optional[str] = None  # Format: "http://user:pass@host:port"
    user_agent_pool: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ])
    enabled: bool = True


@dataclass
class PlaywrightScraperStats:
    """Estatisticas do scraper Playwright."""
    pages_loaded: int = 0
    pages_failed: int = 0
    screenshots_taken: int = 0
    retries: int = 0
    total_navigation_time_ms: float = 0.0
    started_at: Optional[datetime] = None

    def record_page_load(self, navigation_time_ms: float) -> None:
        """Registra carregamento de pagina."""
        self.pages_loaded += 1
        self.total_navigation_time_ms += navigation_time_ms

    def record_failure(self) -> None:
        """Registra falha."""
        self.pages_failed += 1

    def avg_navigation_time_ms(self) -> float:
        """Tempo medio de navegacao."""
        if self.pages_loaded == 0:
            return 0.0
        return self.total_navigation_time_ms / self.pages_loaded

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "pages_loaded": self.pages_loaded,
            "pages_failed": self.pages_failed,
            "screenshots_taken": self.screenshots_taken,
            "retries": self.retries,
            "avg_navigation_time_ms": round(self.avg_navigation_time_ms(), 2),
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class PlaywrightScraper(ABC):
    """
    Base class para scrapers usando Playwright.

    Implementa:
    - Navegacao com retry e backoff
    - Stealth mode configuravel
    - Rate limiting
    - Screenshot em caso de erro
    - Suporte a proxy
    """

    def __init__(self, config: PlaywrightConfig):
        self.config = config
        self._browser = None
        self._context = None
        self._playwright = None
        self._initialized = False
        self._min_interval = 60.0 / config.rate_limit_rpm
        self._last_request_time = 0.0
        self.stats = PlaywrightScraperStats()

    async def initialize(self) -> None:
        """Inicializa o browser."""
        if self._initialized:
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()

            browser_launcher = getattr(self._playwright, self.config.browser_type.value)

            launch_options = {
                "headless": self.config.headless,
            }

            if self.config.proxy:
                launch_options["proxy"] = {"server": self.config.proxy}

            self._browser = await browser_launcher.launch(**launch_options)

            # Create context with stealth settings
            context_options = self._get_context_options()
            self._context = await self._browser.new_context(**context_options)

            # Apply stealth scripts if needed
            if self.config.stealth_level != StealthLevel.NONE:
                await self._apply_stealth_scripts()

            self._initialized = True
            self.stats.started_at = datetime.now(timezone.utc)
            logger.info(f"[{self.config.name}] Playwright initialized ({self.config.browser_type.value})")

        except ImportError:
            logger.warning("Playwright not installed, scraper running in mock mode")
            self._initialized = True
            self.stats.started_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"[{self.config.name}] Failed to initialize: {e}")
            raise

    def _get_context_options(self) -> Dict[str, Any]:
        """Retorna opcoes de contexto do browser."""
        user_agent = random.choice(self.config.user_agent_pool)

        options = {
            "user_agent": user_agent,
            "viewport": {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            "locale": self.config.locale,
            "timezone_id": self.config.timezone_id,
        }

        # Add randomization for stealth
        if self.config.stealth_level != StealthLevel.NONE:
            # Randomize viewport slightly
            options["viewport"]["width"] += random.randint(-50, 50)
            options["viewport"]["height"] += random.randint(-30, 30)

        return options

    async def _apply_stealth_scripts(self) -> None:
        """Aplica scripts de stealth no contexto."""
        if not self._context:
            return

        # Basic stealth: hide webdriver
        if self.config.stealth_level in (StealthLevel.BASIC, StealthLevel.STANDARD, StealthLevel.AGGRESSIVE):
            await self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

        # Standard stealth: additional fingerprint masking
        if self.config.stealth_level in (StealthLevel.STANDARD, StealthLevel.AGGRESSIVE):
            await self._context.add_init_script("""
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en']
                });

                // Chrome specific
                window.chrome = {
                    runtime: {}
                };
            """)

        # Aggressive stealth: full fingerprint randomization
        if self.config.stealth_level == StealthLevel.AGGRESSIVE:
            await self._context.add_init_script("""
                // Override screen properties
                const originalScreen = window.screen;
                Object.defineProperty(window, 'screen', {
                    get: () => ({
                        ...originalScreen,
                        availWidth: window.innerWidth,
                        availHeight: window.innerHeight,
                        width: window.innerWidth,
                        height: window.innerHeight,
                        colorDepth: 24,
                        pixelDepth: 24
                    })
                });

                // Override WebGL vendor
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, arguments);
                };
            """)

    async def close(self) -> None:
        """Fecha o browser."""
        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._initialized = False
        logger.info(f"[{self.config.name}] Playwright closed")

    async def _wait_rate_limit(self) -> None:
        """Aguarda intervalo minimo entre requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            logger.debug(f"[{self.config.name}] Rate limiting: sleeping {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        self._last_request_time = time.time()

    async def navigate(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
    ) -> Optional[PageType]:
        """
        Navega para uma URL com retry.

        Args:
            url: URL para navegar
            wait_until: Evento de espera (domcontentloaded, load, networkidle)

        Returns:
            Page object ou None em caso de falha
        """
        if not self._context:
            logger.warning(f"[{self.config.name}] No context - running in mock mode")
            return None

        backoff = 1.0

        for attempt in range(1, self.config.max_retries + 1):
            await self._wait_rate_limit()

            try:
                page = await self._context.new_page()
                page.set_default_timeout(self.config.timeout_ms)
                page.set_default_navigation_timeout(self.config.navigation_timeout_ms)

                start_time = time.time()
                await page.goto(url, wait_until=wait_until)
                navigation_time = (time.time() - start_time) * 1000

                self.stats.record_page_load(navigation_time)
                logger.debug(f"[{self.config.name}] Loaded {url} in {navigation_time:.0f}ms")

                return page

            except Exception as e:
                logger.warning(f"[{self.config.name}] Navigation error (attempt {attempt}): {e}")
                self.stats.record_failure()
                self.stats.retries += 1

                if attempt < self.config.max_retries:
                    jitter = random.uniform(0, 0.5)
                    await asyncio.sleep(backoff + jitter)
                    backoff *= 2

        return None

    async def take_screenshot(
        self,
        page: PageType,
        name: str,
    ) -> Optional[str]:
        """
        Tira screenshot da pagina.

        Args:
            page: Page object
            name: Nome do screenshot

        Returns:
            Caminho do arquivo ou None
        """
        if not page:
            return None

        try:
            import os
            os.makedirs(self.config.screenshot_dir, exist_ok=True)

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.name}_{name}_{timestamp}.png"
            filepath = os.path.join(self.config.screenshot_dir, filename)

            await page.screenshot(path=filepath, full_page=True)
            self.stats.screenshots_taken += 1

            logger.debug(f"[{self.config.name}] Screenshot saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"[{self.config.name}] Screenshot failed: {e}")
            return None

    async def get_page_content(self, page: PageType) -> str:
        """Extrai conteudo HTML da pagina."""
        if not page:
            return ""
        return await page.content()

    async def wait_for_selector(
        self,
        page: PageType,
        selector: str,
        timeout_ms: Optional[int] = None,
    ) -> bool:
        """Aguarda por um seletor na pagina."""
        if not page:
            return False

        try:
            await page.wait_for_selector(
                selector,
                timeout=timeout_ms or self.config.timeout_ms,
            )
            return True
        except Exception:
            logger.debug(f"[{self.config.name}] wait_for_selector timed out for {selector}")
            return False

    async def click(
        self,
        page: PageType,
        selector: str,
    ) -> bool:
        """Clica em um elemento."""
        if not page:
            return False

        try:
            await page.click(selector)
            return True
        except Exception as e:
            logger.debug(f"[{self.config.name}] Click failed on {selector}: {e}")
            return False

    async def scroll_to_bottom(self, page: PageType) -> None:
        """Rola a pagina ate o final."""
        if not page:
            return

        await page.evaluate("""
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        """)
        await asyncio.sleep(0.5)  # Wait for scroll

    async def infinite_scroll(
        self,
        page: PageType,
        max_scrolls: int = 10,
        scroll_delay_ms: int = 1000,
    ) -> None:
        """Faz scroll infinito ate carregar todo conteudo."""
        if not page:
            return

        previous_height = 0

        for _ in range(max_scrolls):
            current_height = await page.evaluate("document.body.scrollHeight")

            if current_height == previous_height:
                break

            await self.scroll_to_bottom(page)
            await asyncio.sleep(scroll_delay_ms / 1000)
            previous_height = current_height

    @abstractmethod
    async def get_article_urls(self, page: int = 1) -> List[str]:
        """
        Retorna lista de URLs de artigos.

        Deve ser implementado por cada scraper especifico.
        """
        pass

    @abstractmethod
    async def parse_article(
        self,
        page: PageType,
        url: str,
    ) -> Optional[ScrapedArticle]:
        """
        Parse de um artigo de checagem.

        Deve ser implementado por cada scraper especifico.
        """
        pass

    async def scrape_article(self, url: str) -> Optional[ScrapedArticle]:
        """Faz scrape de um unico artigo."""
        page = await self.navigate(url)
        if not page:
            return None

        try:
            article = await self.parse_article(page, url)
            return article
        except Exception as e:
            logger.error(f"[{self.config.name}] Error parsing {url}: {e}")

            if self.config.screenshot_on_error:
                await self.take_screenshot(page, "error")

            return None
        finally:
            if page:
                await page.close()

    async def scrape(
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
            await self.initialize()

            for page_num in range(1, pages + 1):
                if len(articles) >= max_articles:
                    break

                urls = await self.get_article_urls(page=page_num)
                total_found += len(urls)

                for url in urls:
                    if len(articles) >= max_articles:
                        break

                    article = await self.scrape_article(url)
                    if article:
                        articles.append(article)
                        logger.info(f"[{self.config.name}] Scraped: {article.title[:50]}...")

            duration = time.time() - start_time
            logger.info(f"[{self.config.name}] Completed: {len(articles)} articles in {duration:.1f}s")

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

        finally:
            await self.close()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do scraper."""
        return self.stats.to_dict()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Convenience function for one-off scrapes
async def scrape_with_playwright(
    url: str,
    extractor: Callable[[PageType], Any],
    config: Optional[PlaywrightConfig] = None,
) -> Any:
    """
    Funcao utilitaria para scrape simples.

    Args:
        url: URL para navegar
        extractor: Funcao que extrai dados da pagina
        config: Configuracao opcional

    Returns:
        Resultado do extractor
    """
    if config is None:
        config = PlaywrightConfig(name="one-off", base_url=url)

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            result = await extractor(page)
            await browser.close()
            return result

    except ImportError:
        logger.warning("Playwright not installed")
        return None
