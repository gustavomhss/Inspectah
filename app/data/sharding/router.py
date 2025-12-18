"""
S39 - Shard Router

Routes claims to appropriate PostgreSQL shards based on domain.
Supports 4 shards: default, politica, economia, saude.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Domain(str, Enum):
    """Domain types for shard routing."""

    DEFAULT = "default"
    POLITICA = "politica"
    ECONOMIA = "economia"
    SAUDE = "saude"


@dataclass
class ShardConfig:
    """Configuration for a single shard."""

    shard_id: int
    domain: Domain
    host: str
    port: int
    database: str
    user: str = "inspectah"
    min_pool_size: int = 5
    max_pool_size: int = 50
    command_timeout: int = 30

    @property
    def dsn(self) -> str:
        """Generate DSN for asyncpg."""
        password = os.environ.get("POSTGRES_PASSWORD", "")
        return (
            f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.database}"
        )


# Shard configurations - matches docker-compose.shards.yml
SHARD_CONFIGS: Dict[Domain, ShardConfig] = {
    Domain.DEFAULT: ShardConfig(
        shard_id=0,
        domain=Domain.DEFAULT,
        host=os.environ.get("PG_SHARD_DEFAULT_HOST", "pg-shard-default"),
        port=int(os.environ.get("PG_SHARD_DEFAULT_PORT", "5432")),
        database="inspectah_default",
    ),
    Domain.POLITICA: ShardConfig(
        shard_id=1,
        domain=Domain.POLITICA,
        host=os.environ.get("PG_SHARD_POLITICA_HOST", "pg-shard-politica"),
        port=int(os.environ.get("PG_SHARD_POLITICA_PORT", "5432")),
        database="inspectah_politica",
    ),
    Domain.ECONOMIA: ShardConfig(
        shard_id=2,
        domain=Domain.ECONOMIA,
        host=os.environ.get("PG_SHARD_ECONOMIA_HOST", "pg-shard-economia"),
        port=int(os.environ.get("PG_SHARD_ECONOMIA_PORT", "5432")),
        database="inspectah_economia",
    ),
    Domain.SAUDE: ShardConfig(
        shard_id=3,
        domain=Domain.SAUDE,
        host=os.environ.get("PG_SHARD_SAUDE_HOST", "pg-shard-saude"),
        port=int(os.environ.get("PG_SHARD_SAUDE_PORT", "5432")),
        database="inspectah_saude",
    ),
}

# Keywords for automatic domain detection
DOMAIN_KEYWORDS: Dict[str, Domain] = {
    # Politica
    "eleição": Domain.POLITICA,
    "eleicao": Domain.POLITICA,
    "político": Domain.POLITICA,
    "politico": Domain.POLITICA,
    "governo": Domain.POLITICA,
    "congresso": Domain.POLITICA,
    "senado": Domain.POLITICA,
    "câmara": Domain.POLITICA,
    "camara": Domain.POLITICA,
    "deputado": Domain.POLITICA,
    "senador": Domain.POLITICA,
    "presidente": Domain.POLITICA,
    "ministro": Domain.POLITICA,
    "vereador": Domain.POLITICA,
    "prefeito": Domain.POLITICA,
    "governador": Domain.POLITICA,
    "lula": Domain.POLITICA,
    "bolsonaro": Domain.POLITICA,
    "pt": Domain.POLITICA,
    "psd": Domain.POLITICA,
    "mdb": Domain.POLITICA,
    "união brasil": Domain.POLITICA,
    "stf": Domain.POLITICA,
    "tse": Domain.POLITICA,
    # Economia
    "inflação": Domain.ECONOMIA,
    "inflacao": Domain.ECONOMIA,
    "pib": Domain.ECONOMIA,
    "dólar": Domain.ECONOMIA,
    "dolar": Domain.ECONOMIA,
    "bolsa": Domain.ECONOMIA,
    "juros": Domain.ECONOMIA,
    "selic": Domain.ECONOMIA,
    "banco central": Domain.ECONOMIA,
    "bacen": Domain.ECONOMIA,
    "copom": Domain.ECONOMIA,
    "ipca": Domain.ECONOMIA,
    "desemprego": Domain.ECONOMIA,
    "ibge": Domain.ECONOMIA,
    "bndes": Domain.ECONOMIA,
    "investimento": Domain.ECONOMIA,
    "mercado financeiro": Domain.ECONOMIA,
    # Saude
    "vacina": Domain.SAUDE,
    "covid": Domain.SAUDE,
    "coronavirus": Domain.SAUDE,
    "pandemia": Domain.SAUDE,
    "hospital": Domain.SAUDE,
    "médico": Domain.SAUDE,
    "medico": Domain.SAUDE,
    "sus": Domain.SAUDE,
    "anvisa": Domain.SAUDE,
    "saúde": Domain.SAUDE,
    "saude": Domain.SAUDE,
    "doença": Domain.SAUDE,
    "doenca": Domain.SAUDE,
    "tratamento": Domain.SAUDE,
    "medicamento": Domain.SAUDE,
    "remédio": Domain.SAUDE,
    "remedio": Domain.SAUDE,
    "epidemia": Domain.SAUDE,
    "surto": Domain.SAUDE,
    "dengue": Domain.SAUDE,
}


@dataclass
class ShardHealth:
    """Health status of a shard."""

    domain: Domain
    is_healthy: bool
    latency_ms: float
    connection_count: int
    error: Optional[str] = None


@dataclass
class ShardStats:
    """Statistics for a shard."""

    domain: Domain
    claims_count: int
    signals_count: int
    storage_bytes: int
    connections_active: int
    replication_lag_ms: int = 0


class ShardRouter:
    """
    Router for distributing claims across PostgreSQL shards.

    Routes based on domain keywords detected in claim text,
    or explicit domain specification.

    Usage:
        router = ShardRouter()
        await router.initialize(password="secret")

        domain = router.route("Lula anuncia novo programa social")
        # Returns Domain.POLITICA

        async with router.get_connection(domain) as conn:
            await conn.execute("INSERT INTO claims ...")

        await router.close()
    """

    def __init__(self, configs: Optional[Dict[Domain, ShardConfig]] = None):
        self._configs = configs or SHARD_CONFIGS
        self._pools: Dict[Domain, Any] = {}  # asyncpg.Pool
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if router is initialized."""
        return self._initialized

    async def initialize(self, password: Optional[str] = None) -> None:
        """
        Initialize connection pools for all shards.

        Args:
            password: PostgreSQL password (uses POSTGRES_PASSWORD env var if not provided)
        """
        if self._initialized:
            return

        try:
            import asyncpg
        except ImportError:
            raise ImportError("asyncpg is required for sharding. Install with: pip install asyncpg")

        if password:
            os.environ["POSTGRES_PASSWORD"] = password

        for domain, config in self._configs.items():
            try:
                pool = await asyncpg.create_pool(
                    host=config.host,
                    port=config.port,
                    database=config.database,
                    user=config.user,
                    password=os.environ.get("POSTGRES_PASSWORD", ""),
                    min_size=config.min_pool_size,
                    max_size=config.max_pool_size,
                    command_timeout=config.command_timeout,
                )
                self._pools[domain] = pool
                logger.info(f"Initialized pool for shard {domain.value}")
            except Exception as e:
                logger.error(f"Failed to initialize shard {domain.value}: {e}")
                raise

        self._initialized = True
        logger.info(f"ShardRouter initialized with {len(self._pools)} shards")

    def route(
        self,
        claim_text: str,
        explicit_domain: Optional[Domain] = None,
    ) -> Domain:
        """
        Determine the appropriate shard for a claim.

        Args:
            claim_text: The claim text to analyze
            explicit_domain: Override domain detection with explicit domain

        Returns:
            Domain for routing
        """
        if explicit_domain:
            return explicit_domain

        text_lower = claim_text.lower()

        # Check for domain keywords
        for keyword, domain in DOMAIN_KEYWORDS.items():
            if keyword in text_lower:
                logger.debug(f"Routed to {domain.value} based on keyword '{keyword}'")
                return domain

        return Domain.DEFAULT

    def get_shard_id(self, domain: Domain) -> int:
        """Get shard ID for a domain."""
        return self._configs[domain].shard_id

    def get_config(self, domain: Domain) -> ShardConfig:
        """Get configuration for a domain."""
        return self._configs[domain]

    def get_connection(self, domain: Domain):
        """
        Get a connection from the pool for a domain.

        Usage:
            async with router.get_connection(Domain.POLITICA) as conn:
                await conn.execute("SELECT * FROM claims")
        """
        if not self._initialized:
            raise RuntimeError("ShardRouter not initialized. Call initialize() first.")
        if domain not in self._pools:
            raise ValueError(f"Unknown domain: {domain}")
        return self._pools[domain].acquire()

    def get_pool(self, domain: Domain):
        """Get the connection pool for a domain."""
        if not self._initialized:
            raise RuntimeError("ShardRouter not initialized. Call initialize() first.")
        return self._pools.get(domain)

    async def execute_on_shard(
        self,
        domain: Domain,
        query: str,
        *args: Any,
    ) -> List[Dict[str, Any]]:
        """
        Execute a query on a specific shard.

        Args:
            domain: Target domain/shard
            query: SQL query to execute
            *args: Query parameters

        Returns:
            List of row dictionaries
        """
        async with self.get_connection(domain) as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute_on_all_shards(
        self,
        query: str,
        *args: Any,
        timeout: float = 5.0,
    ) -> Dict[Domain, List[Dict[str, Any]]]:
        """
        Execute a query on all shards in parallel.

        Args:
            query: SQL query to execute
            *args: Query parameters
            timeout: Timeout per shard in seconds

        Returns:
            Dict mapping domain to results
        """
        results: Dict[Domain, List[Dict[str, Any]]] = {}

        async def query_shard(domain: Domain):
            try:
                async with asyncio.timeout(timeout):
                    return domain, await self.execute_on_shard(domain, query, *args)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout querying shard {domain.value}")
                return domain, []
            except Exception as e:
                logger.error(f"Error querying shard {domain.value}: {e}")
                return domain, []

        shard_results = await asyncio.gather(
            *[query_shard(domain) for domain in Domain]
        )

        for domain, rows in shard_results:
            results[domain] = rows

        return results

    async def health_check(self, domain: Optional[Domain] = None) -> List[ShardHealth]:
        """
        Check health of shards.

        Args:
            domain: Specific domain to check, or None for all

        Returns:
            List of ShardHealth objects
        """
        import time

        domains = [domain] if domain else list(Domain)
        health_results = []

        for d in domains:
            start = time.time()
            try:
                async with self.get_connection(d) as conn:
                    await conn.fetchval("SELECT 1")
                    pool = self._pools[d]
                    health_results.append(
                        ShardHealth(
                            domain=d,
                            is_healthy=True,
                            latency_ms=(time.time() - start) * 1000,
                            connection_count=pool.get_size(),
                        )
                    )
            except Exception as e:
                health_results.append(
                    ShardHealth(
                        domain=d,
                        is_healthy=False,
                        latency_ms=(time.time() - start) * 1000,
                        connection_count=0,
                        error=str(e),
                    )
                )

        return health_results

    async def get_stats(self, domain: Domain) -> ShardStats:
        """
        Get statistics for a shard.

        Args:
            domain: Domain to get stats for

        Returns:
            ShardStats object
        """
        async with self.get_connection(domain) as conn:
            # Get counts
            claims_count = await conn.fetchval(
                "SELECT COUNT(*) FROM claims"
            ) or 0
            signals_count = await conn.fetchval(
                "SELECT COUNT(*) FROM signals"
            ) or 0

            # Get storage size
            storage_bytes = await conn.fetchval(
                "SELECT pg_database_size(current_database())"
            ) or 0

            # Get active connections
            connections = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            ) or 0

            return ShardStats(
                domain=domain,
                claims_count=claims_count,
                signals_count=signals_count,
                storage_bytes=storage_bytes,
                connections_active=connections,
            )

    async def close(self) -> None:
        """Close all connection pools."""
        for domain, pool in self._pools.items():
            try:
                await pool.close()
                logger.info(f"Closed pool for shard {domain.value}")
            except Exception as e:
                logger.warning(f"Error closing pool for {domain.value}: {e}")

        self._pools.clear()
        self._initialized = False
        logger.info("ShardRouter closed")


# Global singleton instance
router = ShardRouter()
