"""
S38-BE-005: Rate Limiter com Token Bucket

Implementa rate limiting para proteger fontes externas de sobrecarga.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Estrategias de rate limiting."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Configuracao de rate limit para uma fonte."""
    source_id: str
    requests_per_minute: int = 10
    burst_size: int = 5  # Maximo de requests em rajada
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    enabled: bool = True


@dataclass
class RateLimitState:
    """Estado atual do rate limiter para uma fonte."""
    source_id: str
    tokens: float
    last_refill: float
    requests_this_window: int = 0
    window_start: float = field(default_factory=time.time)


class TokenBucketRateLimiter:
    """
    Rate limiter usando algoritmo Token Bucket.

    - Tokens sao adicionados a uma taxa constante (requests_per_minute / 60)
    - Requests consomem tokens
    - Se nao houver tokens, request e bloqueado ou aguarda

    Uso:
        limiter = TokenBucketRateLimiter()
        limiter.configure("fonte_x", requests_per_minute=30)

        if limiter.acquire("fonte_x"):
            # fazer request
        else:
            # rate limited
    """

    def __init__(self):
        self._configs: Dict[str, RateLimitConfig] = {}
        self._states: Dict[str, RateLimitState] = {}
        self._lock = threading.Lock()

    def configure(
        self,
        source_id: str,
        requests_per_minute: int = 10,
        burst_size: int = 5,
    ) -> None:
        """Configura rate limit para uma fonte."""
        with self._lock:
            self._configs[source_id] = RateLimitConfig(
                source_id=source_id,
                requests_per_minute=requests_per_minute,
                burst_size=burst_size,
            )
            # Inicializar estado com bucket cheio
            self._states[source_id] = RateLimitState(
                source_id=source_id,
                tokens=float(burst_size),
                last_refill=time.time(),
            )
            logger.info(
                f"[rate_limiter] Configured {source_id}: "
                f"{requests_per_minute} rpm, burst={burst_size}"
            )

    def _refill_tokens(self, source_id: str) -> None:
        """Reabastece tokens baseado no tempo decorrido."""
        config = self._configs.get(source_id)
        state = self._states.get(source_id)
        if not config or not state:
            return

        now = time.time()
        elapsed = now - state.last_refill

        # Taxa de refill: requests_per_minute / 60 tokens por segundo
        refill_rate = config.requests_per_minute / 60.0
        new_tokens = elapsed * refill_rate

        state.tokens = min(config.burst_size, state.tokens + new_tokens)
        state.last_refill = now

    def acquire(
        self,
        source_id: str,
        tokens: float = 1.0,
        block: bool = False,
        timeout: float = 30.0,
    ) -> bool:
        """
        Tenta adquirir tokens para fazer um request.

        Args:
            source_id: ID da fonte
            tokens: Numero de tokens a consumir (default 1)
            block: Se True, aguarda tokens disponiveis
            timeout: Tempo maximo de espera se block=True

        Returns:
            True se conseguiu adquirir, False se rate limited
        """
        config = self._configs.get(source_id)
        if not config:
            # Sem config = sem limite
            logger.debug(f"[rate_limiter] No config for {source_id}, allowing")
            return True

        if not config.enabled:
            return True

        start_time = time.time()

        while True:
            with self._lock:
                self._refill_tokens(source_id)
                state = self._states[source_id]

                if state.tokens >= tokens:
                    state.tokens -= tokens
                    state.requests_this_window += 1
                    logger.debug(
                        f"[rate_limiter] {source_id}: acquired {tokens} token(s), "
                        f"remaining={state.tokens:.2f}"
                    )
                    return True

                if not block:
                    logger.warning(
                        f"[rate_limiter] {source_id}: rate limited, "
                        f"tokens={state.tokens:.2f}"
                    )
                    return False

            # Block mode: aguardar
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                logger.warning(f"[rate_limiter] {source_id}: timeout waiting for tokens")
                return False

            # Calcular tempo de espera ate proximo token
            wait_time = (tokens - state.tokens) / (config.requests_per_minute / 60.0)
            wait_time = min(wait_time, timeout - elapsed, 1.0)  # Max 1s por iteracao
            time.sleep(wait_time)

    def get_wait_time(self, source_id: str, tokens: float = 1.0) -> float:
        """Retorna tempo estimado de espera para adquirir tokens."""
        config = self._configs.get(source_id)
        state = self._states.get(source_id)

        if not config or not state:
            return 0.0

        with self._lock:
            self._refill_tokens(source_id)
            state = self._states[source_id]

            if state.tokens >= tokens:
                return 0.0

            # Tempo para refill
            needed = tokens - state.tokens
            refill_rate = config.requests_per_minute / 60.0
            return needed / refill_rate

    def get_stats(self, source_id: str) -> Optional[Dict]:
        """Retorna estatisticas do rate limiter para uma fonte."""
        config = self._configs.get(source_id)
        state = self._states.get(source_id)

        if not config or not state:
            return None

        with self._lock:
            self._refill_tokens(source_id)
            return {
                "source_id": source_id,
                "tokens_available": state.tokens,
                "burst_size": config.burst_size,
                "requests_per_minute": config.requests_per_minute,
                "requests_this_window": state.requests_this_window,
                "enabled": config.enabled,
            }

    def reset(self, source_id: str) -> None:
        """Reseta o estado do rate limiter para uma fonte."""
        config = self._configs.get(source_id)
        if config:
            with self._lock:
                self._states[source_id] = RateLimitState(
                    source_id=source_id,
                    tokens=float(config.burst_size),
                    last_refill=time.time(),
                )
            logger.info(f"[rate_limiter] Reset {source_id}")

    def disable(self, source_id: str) -> None:
        """Desabilita rate limiting para uma fonte."""
        if source_id in self._configs:
            self._configs[source_id].enabled = False
            logger.info(f"[rate_limiter] Disabled {source_id}")

    def enable(self, source_id: str) -> None:
        """Habilita rate limiting para uma fonte."""
        if source_id in self._configs:
            self._configs[source_id].enabled = True
            logger.info(f"[rate_limiter] Enabled {source_id}")


# Singleton global
_rate_limiter: Optional[TokenBucketRateLimiter] = None


def get_rate_limiter() -> TokenBucketRateLimiter:
    """Retorna instancia singleton do rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenBucketRateLimiter()
    return _rate_limiter
