"""
S39 - Browser Pool Manager

Gerenciador de pool de browsers Playwright para scraping paralelo.

Features:
- Pool de browsers com limite configuravel
- Rotacao automatica de proxies
- Health check e reciclagem de instancias
- Metricas de uso
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.ingestion.scrapers.playwright_base import (
    BrowserType,
    PlaywrightConfig,
    StealthLevel,
)

logger = logging.getLogger(__name__)


class BrowserState(str, Enum):
    """Estado de uma instancia de browser."""
    IDLE = "idle"
    BUSY = "busy"
    RECYCLING = "recycling"
    CLOSED = "closed"


@dataclass
class BrowserInstance:
    """Instancia de browser no pool."""
    id: str
    browser: Any  # playwright Browser object
    context: Any  # playwright BrowserContext object
    state: BrowserState = BrowserState.IDLE
    pages_processed: int = 0
    errors: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None
    proxy: Optional[str] = None

    def mark_busy(self) -> None:
        """Marca como ocupado."""
        self.state = BrowserState.BUSY
        self.last_used_at = datetime.now(timezone.utc)

    def mark_idle(self) -> None:
        """Marca como disponivel."""
        self.state = BrowserState.IDLE
        self.pages_processed += 1

    def mark_error(self) -> None:
        """Registra erro."""
        self.errors += 1
        self.state = BrowserState.IDLE

    def should_recycle(self, max_pages: int, max_errors: int) -> bool:
        """Verifica se deve ser reciclado."""
        return self.pages_processed >= max_pages or self.errors >= max_errors


@dataclass
class PoolConfig:
    """Configuracao do pool de browsers."""
    min_instances: int = 1
    max_instances: int = 5
    max_pages_per_instance: int = 100  # Recicla apos X paginas
    max_errors_per_instance: int = 5   # Recicla apos X erros
    idle_timeout_seconds: int = 300    # Fecha instancia ociosa apos X segundos
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = True
    stealth_level: StealthLevel = StealthLevel.STANDARD
    proxies: List[str] = field(default_factory=list)  # Lista de proxies para rotacao
    proxy_rotation: bool = True


@dataclass
class PoolStats:
    """Estatisticas do pool."""
    total_instances_created: int = 0
    total_instances_recycled: int = 0
    total_pages_processed: int = 0
    total_errors: int = 0
    current_active: int = 0
    current_idle: int = 0
    started_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "total_instances_created": self.total_instances_created,
            "total_instances_recycled": self.total_instances_recycled,
            "total_pages_processed": self.total_pages_processed,
            "total_errors": self.total_errors,
            "current_active": self.current_active,
            "current_idle": self.current_idle,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class BrowserPool:
    """
    Pool de browsers Playwright.

    Gerencia multiplas instancias de browser para scraping paralelo
    com rotacao de proxy e reciclagem automatica.
    """

    def __init__(self, config: Optional[PoolConfig] = None):
        self.config = config or PoolConfig()
        self._instances: Dict[str, BrowserInstance] = {}
        self._playwright = None
        self._lock = asyncio.Lock()
        self._initialized = False
        self._instance_counter = 0
        self.stats = PoolStats()
        self._proxy_index = 0

    async def initialize(self) -> None:
        """Inicializa o pool."""
        if self._initialized:
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._initialized = True
            self.stats.started_at = datetime.now(timezone.utc)

            # Create minimum instances
            for _ in range(self.config.min_instances):
                await self._create_instance()

            logger.info(f"BrowserPool initialized with {len(self._instances)} instances")

        except ImportError:
            logger.warning("Playwright not installed, pool running in mock mode")
            self._initialized = True
            self.stats.started_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"Failed to initialize BrowserPool: {e}")
            raise

    async def close(self) -> None:
        """Fecha o pool e todos os browsers."""
        async with self._lock:
            for instance_id in list(self._instances.keys()):
                await self._close_instance(instance_id)

            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

            self._initialized = False

        logger.info("BrowserPool closed")

    def _get_next_proxy(self) -> Optional[str]:
        """Retorna proximo proxy na rotacao."""
        if not self.config.proxies:
            return None

        if self.config.proxy_rotation:
            proxy = self.config.proxies[self._proxy_index % len(self.config.proxies)]
            self._proxy_index += 1
            return proxy

        return random.choice(self.config.proxies)

    async def _create_instance(self) -> Optional[BrowserInstance]:
        """Cria nova instancia de browser."""
        if not self._playwright:
            return None

        try:
            self._instance_counter += 1
            instance_id = f"browser-{self._instance_counter}"

            browser_launcher = getattr(self._playwright, self.config.browser_type.value)

            launch_options = {"headless": self.config.headless}
            proxy = self._get_next_proxy()
            if proxy:
                launch_options["proxy"] = {"server": proxy}

            browser = await browser_launcher.launch(**launch_options)

            # Create context with stealth
            context_options = {
                "viewport": {"width": 1920, "height": 1080},
                "locale": "pt-BR",
                "timezone_id": "America/Sao_Paulo",
            }
            context = await browser.new_context(**context_options)

            # Apply stealth scripts
            if self.config.stealth_level != StealthLevel.NONE:
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

            instance = BrowserInstance(
                id=instance_id,
                browser=browser,
                context=context,
                proxy=proxy,
            )

            self._instances[instance_id] = instance
            self.stats.total_instances_created += 1
            self.stats.current_idle += 1

            logger.debug(f"Created browser instance: {instance_id}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create browser instance: {e}")
            return None

    async def _close_instance(self, instance_id: str) -> None:
        """Fecha uma instancia de browser."""
        instance = self._instances.pop(instance_id, None)
        if not instance:
            return

        try:
            if instance.context:
                await instance.context.close()
            if instance.browser:
                await instance.browser.close()

            if instance.state == BrowserState.IDLE:
                self.stats.current_idle -= 1
            elif instance.state == BrowserState.BUSY:
                self.stats.current_active -= 1

            logger.debug(f"Closed browser instance: {instance_id}")

        except Exception as e:
            logger.error(f"Error closing instance {instance_id}: {e}")

    async def _recycle_instance(self, instance_id: str) -> Optional[BrowserInstance]:
        """Recicla uma instancia (fecha e cria nova)."""
        self.stats.total_instances_recycled += 1
        await self._close_instance(instance_id)
        return await self._create_instance()

    async def acquire(self) -> Optional[BrowserInstance]:
        """
        Adquire uma instancia do pool.

        Returns:
            BrowserInstance ou None se nao disponivel
        """
        async with self._lock:
            # Find idle instance
            for instance in self._instances.values():
                if instance.state == BrowserState.IDLE:
                    # Check if needs recycling
                    if instance.should_recycle(
                        self.config.max_pages_per_instance,
                        self.config.max_errors_per_instance,
                    ):
                        new_instance = await self._recycle_instance(instance.id)
                        if new_instance:
                            new_instance.mark_busy()
                            self.stats.current_idle -= 1
                            self.stats.current_active += 1
                            return new_instance
                        continue

                    instance.mark_busy()
                    self.stats.current_idle -= 1
                    self.stats.current_active += 1
                    return instance

            # No idle instances, create new if below max
            if len(self._instances) < self.config.max_instances:
                instance = await self._create_instance()
                if instance:
                    instance.mark_busy()
                    self.stats.current_idle -= 1
                    self.stats.current_active += 1
                    return instance

            return None

    async def release(self, instance: BrowserInstance, error: bool = False) -> None:
        """
        Libera uma instancia de volta ao pool.

        Args:
            instance: Instancia a liberar
            error: Se houve erro no uso
        """
        async with self._lock:
            if instance.id not in self._instances:
                return

            if error:
                instance.mark_error()
                self.stats.total_errors += 1
            else:
                instance.mark_idle()
                self.stats.total_pages_processed += 1

            self.stats.current_active -= 1
            self.stats.current_idle += 1

    async def cleanup_idle(self) -> int:
        """
        Fecha instancias ociosas alem do minimo.

        Returns:
            Numero de instancias fechadas
        """
        closed = 0
        now = datetime.now(timezone.utc)

        async with self._lock:
            idle_instances = [
                i for i in self._instances.values()
                if i.state == BrowserState.IDLE
            ]

            # Keep minimum instances
            to_close = len(idle_instances) - self.config.min_instances

            for instance in idle_instances:
                if to_close <= 0:
                    break

                if instance.last_used_at:
                    idle_seconds = (now - instance.last_used_at).total_seconds()
                    if idle_seconds > self.config.idle_timeout_seconds:
                        await self._close_instance(instance.id)
                        to_close -= 1
                        closed += 1

        return closed

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do pool."""
        return self.stats.to_dict()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Global pool instance
_pool: Optional[BrowserPool] = None


async def get_browser_pool(config: Optional[PoolConfig] = None) -> BrowserPool:
    """Retorna instancia global do pool."""
    global _pool
    if _pool is None:
        _pool = BrowserPool(config)
        await _pool.initialize()
    return _pool
