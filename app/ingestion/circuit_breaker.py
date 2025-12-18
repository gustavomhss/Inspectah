"""
S38-BE-005b: Circuit Breaker para APIs Externas

Implementa o padrao Circuit Breaker para proteger contra falhas em cascata.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, Optional, TypeVar, Generic

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"      # Normal, requests passam
    OPEN = "open"          # Falhas detectadas, requests bloqueados
    HALF_OPEN = "half_open"  # Testando recuperacao


@dataclass
class CircuitConfig:
    """Configuracao do circuit breaker."""
    source_id: str
    failure_threshold: int = 5  # Falhas para abrir o circuito
    success_threshold: int = 3  # Sucessos para fechar em half-open
    timeout_seconds: float = 60.0  # Tempo em open antes de half-open
    half_open_max_requests: int = 3  # Max requests em half-open


@dataclass
class CircuitStats:
    """Estatisticas do circuit breaker."""
    source_id: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changed_at: float = field(default_factory=time.time)
    total_requests: int = 0
    total_failures: int = 0
    total_successes: int = 0
    half_open_requests: int = 0


class CircuitBreakerError(Exception):
    """Erro quando circuito esta aberto."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker para proteger contra falhas em cascata.

    Estados:
    - CLOSED: Normal, requests passam. Conta falhas.
    - OPEN: Muitas falhas, requests bloqueados por timeout_seconds.
    - HALF_OPEN: Permite alguns requests de teste para verificar recuperacao.

    Uso:
        breaker = CircuitBreaker()
        breaker.configure("api_x", failure_threshold=5, timeout_seconds=60)

        try:
            result = breaker.call("api_x", lambda: make_request())
        except CircuitBreakerError:
            # Circuito aberto, usar fallback
            result = get_cached_data()
    """

    def __init__(self):
        self._configs: Dict[str, CircuitConfig] = {}
        self._stats: Dict[str, CircuitStats] = {}
        self._lock = threading.Lock()

    def configure(
        self,
        source_id: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Configura circuit breaker para uma fonte."""
        with self._lock:
            self._configs[source_id] = CircuitConfig(
                source_id=source_id,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout_seconds=timeout_seconds,
            )
            self._stats[source_id] = CircuitStats(source_id=source_id)
            logger.info(
                f"[circuit_breaker] Configured {source_id}: "
                f"fail_threshold={failure_threshold}, timeout={timeout_seconds}s"
            )

    def _get_state(self, source_id: str) -> CircuitState:
        """Retorna estado atual do circuito, atualizando se necessario."""
        stats = self._stats.get(source_id)
        if not stats:
            return CircuitState.CLOSED

        config = self._configs.get(source_id)
        if not config:
            return CircuitState.CLOSED

        # Verificar transicao OPEN -> HALF_OPEN
        if stats.state == CircuitState.OPEN:
            elapsed = time.time() - stats.state_changed_at
            if elapsed >= config.timeout_seconds:
                stats.state = CircuitState.HALF_OPEN
                stats.state_changed_at = time.time()
                stats.half_open_requests = 0
                logger.info(f"[circuit_breaker] {source_id}: OPEN -> HALF_OPEN")

        return stats.state

    def is_available(self, source_id: str) -> bool:
        """Verifica se o circuito permite requests."""
        with self._lock:
            state = self._get_state(source_id)
            if state == CircuitState.CLOSED:
                return True
            if state == CircuitState.HALF_OPEN:
                config = self._configs.get(source_id)
                stats = self._stats.get(source_id)
                if config and stats:
                    return stats.half_open_requests < config.half_open_max_requests
            return False

    def record_success(self, source_id: str) -> None:
        """Registra sucesso de um request."""
        with self._lock:
            stats = self._stats.get(source_id)
            config = self._configs.get(source_id)
            if not stats or not config:
                return

            stats.success_count += 1
            stats.total_successes += 1
            stats.last_success_time = time.time()
            stats.failure_count = 0  # Reset failure count on success

            if stats.state == CircuitState.HALF_OPEN:
                if stats.success_count >= config.success_threshold:
                    stats.state = CircuitState.CLOSED
                    stats.state_changed_at = time.time()
                    stats.success_count = 0
                    logger.info(f"[circuit_breaker] {source_id}: HALF_OPEN -> CLOSED")

    def record_failure(self, source_id: str, error: Optional[str] = None) -> None:
        """Registra falha de um request."""
        with self._lock:
            stats = self._stats.get(source_id)
            config = self._configs.get(source_id)
            if not stats or not config:
                return

            stats.failure_count += 1
            stats.total_failures += 1
            stats.last_failure_time = time.time()
            stats.success_count = 0  # Reset success count on failure

            if stats.state == CircuitState.CLOSED:
                if stats.failure_count >= config.failure_threshold:
                    stats.state = CircuitState.OPEN
                    stats.state_changed_at = time.time()
                    logger.warning(
                        f"[circuit_breaker] {source_id}: CLOSED -> OPEN "
                        f"(failures={stats.failure_count})"
                    )

            elif stats.state == CircuitState.HALF_OPEN:
                # Qualquer falha em half-open volta para open
                stats.state = CircuitState.OPEN
                stats.state_changed_at = time.time()
                logger.warning(f"[circuit_breaker] {source_id}: HALF_OPEN -> OPEN")

    def call(
        self,
        source_id: str,
        func: Callable[[], T],
        fallback: Optional[Callable[[], T]] = None,
    ) -> T:
        """
        Executa funcao protegida pelo circuit breaker.

        Args:
            source_id: ID da fonte
            func: Funcao a executar
            fallback: Funcao de fallback se circuito aberto

        Returns:
            Resultado da funcao ou fallback

        Raises:
            CircuitBreakerError: Se circuito aberto e sem fallback
        """
        if not self.is_available(source_id):
            if fallback:
                logger.info(f"[circuit_breaker] {source_id}: using fallback")
                return fallback()
            raise CircuitBreakerError(f"Circuit open for {source_id}")

        # Incrementar contador de requests em half-open
        with self._lock:
            stats = self._stats.get(source_id)
            if stats and stats.state == CircuitState.HALF_OPEN:
                stats.half_open_requests += 1
            if stats:
                stats.total_requests += 1

        try:
            result = func()
            self.record_success(source_id)
            return result
        except Exception as e:
            self.record_failure(source_id, str(e))
            if fallback:
                logger.info(f"[circuit_breaker] {source_id}: using fallback after error")
                return fallback()
            raise

    def get_stats(self, source_id: str) -> Optional[Dict]:
        """Retorna estatisticas do circuit breaker."""
        with self._lock:
            stats = self._stats.get(source_id)
            config = self._configs.get(source_id)
            if not stats:
                return None

            state = self._get_state(source_id)
            return {
                "source_id": source_id,
                "state": state.value,
                "failure_count": stats.failure_count,
                "success_count": stats.success_count,
                "total_requests": stats.total_requests,
                "total_failures": stats.total_failures,
                "total_successes": stats.total_successes,
                "failure_threshold": config.failure_threshold if config else 0,
                "last_failure_time": stats.last_failure_time,
                "last_success_time": stats.last_success_time,
            }

    def reset(self, source_id: str) -> None:
        """Reseta o circuit breaker para uma fonte."""
        with self._lock:
            if source_id in self._stats:
                self._stats[source_id] = CircuitStats(source_id=source_id)
                logger.info(f"[circuit_breaker] Reset {source_id}")

    def force_open(self, source_id: str) -> None:
        """Forca abertura do circuito (para manutencao)."""
        with self._lock:
            stats = self._stats.get(source_id)
            if stats:
                stats.state = CircuitState.OPEN
                stats.state_changed_at = time.time()
                logger.info(f"[circuit_breaker] Force opened {source_id}")

    def force_close(self, source_id: str) -> None:
        """Forca fechamento do circuito."""
        with self._lock:
            stats = self._stats.get(source_id)
            if stats:
                stats.state = CircuitState.CLOSED
                stats.state_changed_at = time.time()
                stats.failure_count = 0
                logger.info(f"[circuit_breaker] Force closed {source_id}")


# Singleton global
_circuit_breaker: Optional[CircuitBreaker] = None


def get_circuit_breaker() -> CircuitBreaker:
    """Retorna instancia singleton do circuit breaker."""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreaker()
    return _circuit_breaker
