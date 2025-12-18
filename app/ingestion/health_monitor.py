"""
S38-BE-006: Health Monitor para Fontes

Monitora a saude das fontes de dados e emite alertas.
"""
from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Status de saude de uma fonte."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthProbeConfig:
    """Configuracao de probe de saude."""
    source_id: str
    probe_url: str
    probe_method: str = "GET"
    timeout_seconds: float = 10.0
    interval_seconds: float = 300.0  # 5 minutos
    healthy_threshold: int = 2  # Sucessos para considerar healthy
    unhealthy_threshold: int = 3  # Falhas para considerar unhealthy
    expected_status_codes: List[int] = field(default_factory=lambda: [200, 201, 204])
    content_check: Optional[str] = None  # String que deve estar na resposta
    enabled: bool = True


@dataclass
class HealthRecord:
    """Registro de verificacao de saude."""
    source_id: str
    status: HealthStatus
    latency_ms: float
    checked_at: datetime
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    content_valid: bool = True


@dataclass
class HealthStats:
    """Estatisticas de saude de uma fonte."""
    source_id: str
    current_status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    avg_latency_ms: float = 0.0
    total_checks: int = 0
    total_failures: int = 0
    uptime_percent: float = 100.0
    error_message: Optional[str] = None


class HealthMonitor:
    """
    Monitor de saude das fontes de dados.

    Funcionalidades:
    - Probes periodicos (HTTP GET/HEAD)
    - Validacao de conteudo
    - Alertas configuraveis
    - Metricas de latencia e uptime

    Uso:
        monitor = HealthMonitor()
        monitor.register_source(
            source_id="gov_br",
            probe_url="https://api.portaldatransparencia.gov.br/api-de-dados/",
            interval_seconds=300,
        )

        # Verificar status
        status = monitor.get_status("gov_br")

        # Iniciar monitoramento em background
        monitor.start()
    """

    def __init__(self):
        self._configs: Dict[str, HealthProbeConfig] = {}
        self._stats: Dict[str, HealthStats] = {}
        self._history: Dict[str, List[HealthRecord]] = {}
        self._alert_handlers: List[Callable[[str, HealthStatus, str], None]] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._max_history = 100

    def register_source(
        self,
        source_id: str,
        probe_url: str,
        interval_seconds: float = 300.0,
        timeout_seconds: float = 10.0,
        content_check: Optional[str] = None,
    ) -> None:
        """Registra uma fonte para monitoramento."""
        with self._lock:
            self._configs[source_id] = HealthProbeConfig(
                source_id=source_id,
                probe_url=probe_url,
                interval_seconds=interval_seconds,
                timeout_seconds=timeout_seconds,
                content_check=content_check,
            )
            self._stats[source_id] = HealthStats(source_id=source_id)
            self._history[source_id] = []
            logger.info(
                f"[health_monitor] Registered {source_id}: {probe_url} "
                f"(interval={interval_seconds}s)"
            )

    def add_alert_handler(
        self,
        handler: Callable[[str, HealthStatus, str], None],
    ) -> None:
        """Adiciona handler para alertas de mudanca de status."""
        self._alert_handlers.append(handler)

    def _probe_source(self, source_id: str) -> HealthRecord:
        """Executa probe de saude em uma fonte."""
        config = self._configs.get(source_id)
        if not config:
            return HealthRecord(
                source_id=source_id,
                status=HealthStatus.UNKNOWN,
                latency_ms=0.0,
                checked_at=datetime.now(timezone.utc),
                error_message="Config not found",
            )

        start_time = time.time()
        error_message = None
        status_code = None
        content_valid = True

        try:
            response = httpx.request(
                method=config.probe_method,
                url=config.probe_url,
                timeout=config.timeout_seconds,
                follow_redirects=True,
            )
            status_code = response.status_code
            latency_ms = (time.time() - start_time) * 1000

            # Verificar status code
            if status_code not in config.expected_status_codes:
                error_message = f"Unexpected status: {status_code}"
                status = HealthStatus.UNHEALTHY
            # Verificar conteudo se configurado
            elif config.content_check:
                if config.content_check not in response.text:
                    content_valid = False
                    error_message = "Content check failed"
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.HEALTHY
            else:
                status = HealthStatus.HEALTHY

        except httpx.TimeoutException:
            latency_ms = config.timeout_seconds * 1000
            error_message = "Timeout"
            status = HealthStatus.UNHEALTHY
        except httpx.HTTPError as e:
            latency_ms = (time.time() - start_time) * 1000
            error_message = str(e)
            status = HealthStatus.UNHEALTHY
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_message = str(e)
            status = HealthStatus.UNHEALTHY

        return HealthRecord(
            source_id=source_id,
            status=status,
            latency_ms=latency_ms,
            checked_at=datetime.now(timezone.utc),
            error_message=error_message,
            status_code=status_code,
            content_valid=content_valid,
        )

    def check_source(self, source_id: str) -> HealthStatus:
        """Executa verificacao de saude e atualiza estatisticas."""
        record = self._probe_source(source_id)

        with self._lock:
            stats = self._stats.get(source_id)
            config = self._configs.get(source_id)
            if not stats or not config:
                return HealthStatus.UNKNOWN

            # Atualizar estatisticas
            stats.total_checks += 1
            stats.last_check = record.checked_at

            # Atualizar media de latencia
            if stats.avg_latency_ms == 0:
                stats.avg_latency_ms = record.latency_ms
            else:
                stats.avg_latency_ms = (stats.avg_latency_ms + record.latency_ms) / 2

            # Contadores de sucesso/falha
            old_status = stats.current_status
            if record.status == HealthStatus.HEALTHY:
                stats.consecutive_successes += 1
                stats.consecutive_failures = 0
                stats.last_success = record.checked_at
                stats.error_message = None

                # Transicao para HEALTHY
                if stats.consecutive_successes >= config.healthy_threshold:
                    stats.current_status = HealthStatus.HEALTHY
            else:
                stats.consecutive_failures += 1
                stats.consecutive_successes = 0
                stats.total_failures += 1
                stats.last_failure = record.checked_at
                stats.error_message = record.error_message

                # Transicao para UNHEALTHY ou DEGRADED
                if stats.consecutive_failures >= config.unhealthy_threshold:
                    stats.current_status = HealthStatus.UNHEALTHY
                elif stats.consecutive_failures >= 1:
                    if stats.current_status == HealthStatus.HEALTHY:
                        stats.current_status = HealthStatus.DEGRADED

            # Calcular uptime
            if stats.total_checks > 0:
                stats.uptime_percent = (
                    (stats.total_checks - stats.total_failures) / stats.total_checks * 100
                )

            # Adicionar ao historico
            self._history[source_id].append(record)
            if len(self._history[source_id]) > self._max_history:
                self._history[source_id] = self._history[source_id][-self._max_history:]

            # Emitir alerta se status mudou
            if old_status != stats.current_status:
                self._emit_alert(source_id, stats.current_status, record.error_message)

            logger.debug(
                f"[health_monitor] {source_id}: {stats.current_status.value} "
                f"(latency={record.latency_ms:.0f}ms)"
            )

            return stats.current_status

    def _emit_alert(
        self,
        source_id: str,
        status: HealthStatus,
        message: Optional[str],
    ) -> None:
        """Emite alerta para handlers registrados."""
        logger.warning(
            f"[health_monitor] ALERT: {source_id} status changed to {status.value}"
        )
        for handler in self._alert_handlers:
            try:
                handler(source_id, status, message or "")
            except Exception as e:
                logger.error(f"[health_monitor] Alert handler error: {e}")

    def get_status(self, source_id: str) -> HealthStatus:
        """Retorna status atual de uma fonte."""
        with self._lock:
            stats = self._stats.get(source_id)
            return stats.current_status if stats else HealthStatus.UNKNOWN

    def get_stats(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Retorna estatisticas de uma fonte."""
        with self._lock:
            stats = self._stats.get(source_id)
            if not stats:
                return None

            return {
                "source_id": source_id,
                "status": stats.current_status.value,
                "consecutive_successes": stats.consecutive_successes,
                "consecutive_failures": stats.consecutive_failures,
                "last_check": stats.last_check.isoformat() if stats.last_check else None,
                "last_success": stats.last_success.isoformat() if stats.last_success else None,
                "last_failure": stats.last_failure.isoformat() if stats.last_failure else None,
                "avg_latency_ms": stats.avg_latency_ms,
                "total_checks": stats.total_checks,
                "total_failures": stats.total_failures,
                "uptime_percent": stats.uptime_percent,
                "error_message": stats.error_message,
            }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estatisticas de todas as fontes."""
        result = {}
        for source_id in self._configs:
            stats = self.get_stats(source_id)
            if stats:
                result[source_id] = stats
        return result

    def get_history(
        self,
        source_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retorna historico de verificacoes de uma fonte."""
        with self._lock:
            history = self._history.get(source_id, [])
            records = history[-limit:]
            return [
                {
                    "status": r.status.value,
                    "latency_ms": r.latency_ms,
                    "checked_at": r.checked_at.isoformat(),
                    "error_message": r.error_message,
                    "status_code": r.status_code,
                }
                for r in records
            ]

    def _monitor_loop(self) -> None:
        """Loop principal de monitoramento."""
        last_checks: Dict[str, float] = {}

        while self._running:
            now = time.time()

            for source_id, config in list(self._configs.items()):
                if not config.enabled:
                    continue

                last_check = last_checks.get(source_id, 0)
                if now - last_check >= config.interval_seconds:
                    try:
                        self.check_source(source_id)
                        last_checks[source_id] = now
                    except Exception as e:
                        logger.error(f"[health_monitor] Error checking {source_id}: {e}")

            time.sleep(1)  # Check every second for scheduling

    def start(self) -> None:
        """Inicia monitoramento em background."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("[health_monitor] Started background monitoring")

    def stop(self) -> None:
        """Para monitoramento."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[health_monitor] Stopped background monitoring")

    def enable_source(self, source_id: str) -> None:
        """Habilita monitoramento de uma fonte."""
        with self._lock:
            if source_id in self._configs:
                self._configs[source_id].enabled = True

    def disable_source(self, source_id: str) -> None:
        """Desabilita monitoramento de uma fonte."""
        with self._lock:
            if source_id in self._configs:
                self._configs[source_id].enabled = False


# Singleton global
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Retorna instancia singleton do health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
