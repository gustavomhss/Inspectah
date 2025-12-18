"""
S39 - Proxy Manager

Gerenciador de proxies com health checking e rotacao inteligente.

Features:
- Verificacao automatica de saude dos proxies
- Rotacao round-robin ou com peso
- Blacklist temporaria de proxies falhando
- Metricas de uso
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class RotationStrategy(str, Enum):
    """Estrategias de rotacao de proxy."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED = "weighted"  # Mais requisicoes para proxies mais saudaveis
    LEAST_USED = "least_used"


class ProxyProtocol(str, Enum):
    """Protocolos suportados."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


@dataclass
class ProxyConfig:
    """Configuracao de um proxy."""
    host: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None

    def to_url(self) -> str:
        """Converte para URL de proxy."""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"

        return f"{self.protocol.value}://{auth}{self.host}:{self.port}"

    @classmethod
    def from_url(cls, url: str, name: Optional[str] = None) -> "ProxyConfig":
        """Cria configuracao a partir de URL."""
        # Parse URL like "http://user:pass@host:port"
        protocol = ProxyProtocol.HTTP
        if url.startswith("https://"):
            protocol = ProxyProtocol.HTTPS
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]
        elif url.startswith("socks5://"):
            protocol = ProxyProtocol.SOCKS5
            url = url[9:]

        username = None
        password = None
        if "@" in url:
            auth, hostport = url.rsplit("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
        else:
            hostport = url

        if ":" in hostport:
            host, port_str = hostport.rsplit(":", 1)
            port = int(port_str)
        else:
            host = hostport
            port = 80 if protocol == ProxyProtocol.HTTP else 443

        return cls(
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password,
            name=name,
        )


@dataclass
class ProxyStats:
    """Estatisticas de um proxy."""
    requests_success: int = 0
    requests_failed: int = 0
    total_response_time_ms: float = 0.0
    last_used_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    last_error: Optional[str] = None
    is_healthy: bool = True
    blacklisted_until: Optional[datetime] = None
    consecutive_failures: int = 0

    def record_success(self, response_time_ms: float) -> None:
        """Registra requisicao bem sucedida."""
        self.requests_success += 1
        self.total_response_time_ms += response_time_ms
        self.last_used_at = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.is_healthy = True
        self.last_error = None

    def record_failure(self, error: str) -> None:
        """Registra falha."""
        self.requests_failed += 1
        self.last_used_at = datetime.now(timezone.utc)
        self.last_error = error
        self.consecutive_failures += 1

    def avg_response_time_ms(self) -> float:
        """Tempo medio de resposta."""
        if self.requests_success == 0:
            return 0.0
        return self.total_response_time_ms / self.requests_success

    def success_rate(self) -> float:
        """Taxa de sucesso."""
        total = self.requests_success + self.requests_failed
        if total == 0:
            return 1.0
        return self.requests_success / total

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "requests_success": self.requests_success,
            "requests_failed": self.requests_failed,
            "avg_response_time_ms": round(self.avg_response_time_ms(), 2),
            "success_rate": round(self.success_rate(), 4),
            "is_healthy": self.is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_error": self.last_error,
        }


@dataclass
class ProxyManagerConfig:
    """Configuracao do gerenciador de proxies."""
    rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    health_check_interval_seconds: int = 300  # 5 minutos
    health_check_timeout_seconds: int = 10
    health_check_url: str = "https://httpbin.org/ip"
    blacklist_duration_seconds: int = 300  # 5 minutos
    max_consecutive_failures: int = 3  # Blacklist apos X falhas
    auto_health_check: bool = True


@dataclass
class ProxyEntry:
    """Entrada de proxy no gerenciador."""
    config: ProxyConfig
    stats: ProxyStats = field(default_factory=ProxyStats)
    weight: float = 1.0  # Para estrategia weighted


class ProxyManager:
    """
    Gerenciador de proxies.

    Implementa:
    - Rotacao de proxies com diferentes estrategias
    - Health checking automatico
    - Blacklist temporaria para proxies falhando
    - Metricas de uso
    """

    def __init__(self, config: Optional[ProxyManagerConfig] = None):
        self.config = config or ProxyManagerConfig()
        self._proxies: Dict[str, ProxyEntry] = {}
        self._rotation_index = 0
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False

    def add_proxy(
        self,
        proxy: ProxyConfig,
        weight: float = 1.0,
    ) -> None:
        """Adiciona um proxy ao pool."""
        key = proxy.to_url()
        if key not in self._proxies:
            self._proxies[key] = ProxyEntry(
                config=proxy,
                stats=ProxyStats(),
                weight=weight,
            )
            logger.info(f"Added proxy: {proxy.host}:{proxy.port}")

    def add_proxies_from_urls(self, urls: List[str]) -> None:
        """Adiciona proxies a partir de lista de URLs."""
        for i, url in enumerate(urls):
            try:
                config = ProxyConfig.from_url(url, name=f"proxy-{i}")
                self.add_proxy(config)
            except Exception as e:
                logger.warning(f"Failed to parse proxy URL {url}: {e}")

    def remove_proxy(self, proxy_url: str) -> None:
        """Remove um proxy do pool."""
        if proxy_url in self._proxies:
            del self._proxies[proxy_url]
            logger.info(f"Removed proxy: {proxy_url}")

    async def start(self) -> None:
        """Inicia o gerenciador."""
        if self._running:
            return

        self._running = True

        if self.config.auto_health_check and len(self._proxies) > 0:
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info(f"ProxyManager started with {len(self._proxies)} proxies")

    async def stop(self) -> None:
        """Para o gerenciador."""
        self._running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

        logger.info("ProxyManager stopped")

    async def _health_check_loop(self) -> None:
        """Loop de verificacao de saude."""
        while self._running:
            try:
                await self.check_all_proxies()
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def check_proxy(self, proxy_url: str) -> bool:
        """Verifica a saude de um proxy."""
        entry = self._proxies.get(proxy_url)
        if not entry:
            return False

        try:
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=self.config.health_check_timeout_seconds,
            ) as client:
                start = time.time()
                response = await client.get(self.config.health_check_url)
                response_time = (time.time() - start) * 1000

                if response.status_code == 200:
                    entry.stats.record_success(response_time)
                    entry.stats.last_checked_at = datetime.now(timezone.utc)
                    logger.debug(f"Proxy healthy: {proxy_url} ({response_time:.0f}ms)")
                    return True

                entry.stats.record_failure(f"HTTP {response.status_code}")
                return False

        except Exception as e:
            entry.stats.record_failure(str(e))
            self._maybe_blacklist(entry)
            logger.warning(f"Proxy check failed: {proxy_url} - {e}")
            return False

    async def check_all_proxies(self) -> Dict[str, bool]:
        """Verifica todos os proxies."""
        results = {}
        for proxy_url in list(self._proxies.keys()):
            results[proxy_url] = await self.check_proxy(proxy_url)
        return results

    def _maybe_blacklist(self, entry: ProxyEntry) -> None:
        """Coloca proxy em blacklist se exceder falhas."""
        if entry.stats.consecutive_failures >= self.config.max_consecutive_failures:
            entry.stats.is_healthy = False
            entry.stats.blacklisted_until = datetime.now(timezone.utc) + timedelta(
                seconds=self.config.blacklist_duration_seconds
            )
            logger.warning(
                f"Proxy blacklisted: {entry.config.host}:{entry.config.port} "
                f"for {self.config.blacklist_duration_seconds}s"
            )

    def _is_available(self, entry: ProxyEntry) -> bool:
        """Verifica se proxy esta disponivel."""
        if not entry.stats.is_healthy:
            # Check if blacklist expired
            if entry.stats.blacklisted_until:
                if datetime.now(timezone.utc) > entry.stats.blacklisted_until:
                    entry.stats.is_healthy = True
                    entry.stats.blacklisted_until = None
                    entry.stats.consecutive_failures = 0
                    return True
            return False
        return True

    def _get_available_proxies(self) -> List[ProxyEntry]:
        """Retorna lista de proxies disponiveis."""
        return [e for e in self._proxies.values() if self._is_available(e)]

    async def get_next(self) -> Optional[str]:
        """
        Retorna proximo proxy disponivel.

        Returns:
            URL do proxy ou None se nenhum disponivel
        """
        async with self._lock:
            available = self._get_available_proxies()
            if not available:
                logger.warning("No available proxies")
                return None

            if self.config.rotation_strategy == RotationStrategy.ROUND_ROBIN:
                return self._get_round_robin(available)
            elif self.config.rotation_strategy == RotationStrategy.RANDOM:
                return self._get_random(available)
            elif self.config.rotation_strategy == RotationStrategy.WEIGHTED:
                return self._get_weighted(available)
            elif self.config.rotation_strategy == RotationStrategy.LEAST_USED:
                return self._get_least_used(available)

            return self._get_round_robin(available)

    def _get_round_robin(self, available: List[ProxyEntry]) -> str:
        """Selecao round-robin."""
        idx = self._rotation_index % len(available)
        self._rotation_index += 1
        return available[idx].config.to_url()

    def _get_random(self, available: List[ProxyEntry]) -> str:
        """Selecao aleatoria."""
        return random.choice(available).config.to_url()

    def _get_weighted(self, available: List[ProxyEntry]) -> str:
        """Selecao por peso (baseado em saude)."""
        weights = []
        for entry in available:
            # Weight = base_weight * success_rate * (1 / avg_response_time)
            sr = entry.stats.success_rate()
            rt = max(entry.stats.avg_response_time_ms(), 100)  # Min 100ms
            weight = entry.weight * sr * (1000 / rt)
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight == 0:
            return self._get_random(available)

        r = random.uniform(0, total_weight)
        cumulative = 0
        for i, entry in enumerate(available):
            cumulative += weights[i]
            if r <= cumulative:
                return entry.config.to_url()

        return available[-1].config.to_url()

    def _get_least_used(self, available: List[ProxyEntry]) -> str:
        """Seleciona proxy menos usado."""
        min_entry = min(
            available,
            key=lambda e: e.stats.requests_success + e.stats.requests_failed
        )
        return min_entry.config.to_url()

    async def report_success(
        self,
        proxy_url: str,
        response_time_ms: float,
    ) -> None:
        """Reporta requisicao bem sucedida."""
        entry = self._proxies.get(proxy_url)
        if entry:
            entry.stats.record_success(response_time_ms)

    async def report_failure(
        self,
        proxy_url: str,
        error: str,
    ) -> None:
        """Reporta falha de requisicao."""
        entry = self._proxies.get(proxy_url)
        if entry:
            entry.stats.record_failure(error)
            self._maybe_blacklist(entry)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas de todos os proxies."""
        stats = {
            "total_proxies": len(self._proxies),
            "available_proxies": len(self._get_available_proxies()),
            "rotation_strategy": self.config.rotation_strategy.value,
            "proxies": {},
        }

        for url, entry in self._proxies.items():
            stats["proxies"][entry.config.name or url] = {
                "url": url,
                "is_available": self._is_available(entry),
                **entry.stats.to_dict(),
            }

        return stats

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Global instance
_manager: Optional[ProxyManager] = None


async def get_proxy_manager(
    config: Optional[ProxyManagerConfig] = None
) -> ProxyManager:
    """Retorna instancia global do gerenciador."""
    global _manager
    if _manager is None:
        _manager = ProxyManager(config)
        await _manager.start()
    return _manager
