"""
S38/S39: Framework de Scrapers para Sites de Checagem

Sites suportados:
- Aos Fatos (aosfatos.org)
- Agencia Lupa (lupa.uol.com.br)
- Boatos.org
- E-farsas (e-farsas.com)
- Fato ou Fake (g1.globo.com/fato-ou-fake)

S39 Additions:
- PlaywrightScraper: Base class for JS-rendered sites
- BrowserPool: Pool manager for parallel scraping
"""
from app.ingestion.scrapers.base import (
    BaseScraper,
    ScrapedArticle,
    ScraperConfig,
    ScraperResult,
)
from app.ingestion.scrapers.aosfatos import AosFatosScraper
from app.ingestion.scrapers.lupa import LupaScraper
from app.ingestion.scrapers.boatos import BoatosScraper
from app.ingestion.scrapers.efarsas import EFarsasScraper
from app.ingestion.scrapers.fatooufake import FatoOuFakeScraper
from app.ingestion.scrapers.playwright_base import (
    BrowserType,
    PlaywrightConfig,
    PlaywrightScraper,
    StealthLevel,
)
from app.ingestion.scrapers.browser_pool import (
    BrowserInstance,
    BrowserPool,
    BrowserState,
    PoolConfig,
    PoolStats,
    get_browser_pool,
)
from app.ingestion.scrapers.proxy_manager import (
    ProxyConfig,
    ProxyEntry,
    ProxyManager,
    ProxyManagerConfig,
    ProxyProtocol,
    ProxyStats,
    RotationStrategy,
    get_proxy_manager,
)

__all__ = [
    # Base classes
    "BaseScraper",
    "ScrapedArticle",
    "ScraperConfig",
    "ScraperResult",
    # Site-specific scrapers
    "AosFatosScraper",
    "LupaScraper",
    "BoatosScraper",
    "EFarsasScraper",
    "FatoOuFakeScraper",
    # Playwright (S39)
    "BrowserType",
    "PlaywrightConfig",
    "PlaywrightScraper",
    "StealthLevel",
    # Browser Pool (S39)
    "BrowserInstance",
    "BrowserPool",
    "BrowserState",
    "PoolConfig",
    "PoolStats",
    "get_browser_pool",
    # Proxy Manager (S39)
    "ProxyConfig",
    "ProxyEntry",
    "ProxyManager",
    "ProxyManagerConfig",
    "ProxyProtocol",
    "ProxyStats",
    "RotationStrategy",
    "get_proxy_manager",
]
