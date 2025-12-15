"""
S38-BE-030: Signal Service

Servico principal de calculo e gerenciamento de sinais.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from app.signals.signal_types import (
    SignalAlert,
    SignalBatch,
    SignalConfig,
    SignalPriority,
    SignalRequest,
    SignalScope,
    SignalType,
    SignalValue,
)

logger = logging.getLogger(__name__)


class SignalCalculator:
    """Interface para calculadores de sinais especificos."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        raise NotImplementedError


class MentirasEmCirculacaoCalculator(SignalCalculator):
    """Calcula volume de claims falsos em circulacao."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        # Buscar claims ativos com verdict FALSE
        total_claims = context.get("total_claims", 0)
        false_claims = context.get("false_claims", 0)
        recent_false = context.get("recent_false_24h", 0)

        if total_claims == 0:
            value = 0.0
        else:
            # Combina proporcao + tendencia recente
            proportion = false_claims / total_claims
            trend_factor = min(1.0, recent_false / max(1, false_claims) * 2)
            value = (proportion * 0.6) + (trend_factor * 0.4)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        config = SignalConfig.default_configs()[SignalType.MENTIRAS_EM_CIRCULACAO]

        return SignalValue(
            signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
            scope=scope,
            scope_id=scope_id,
            value=min(1.0, value),
            confidence=0.8 if total_claims >= 10 else 0.5,
            sample_size=total_claims,
            calculated_at=now,
            expires_at=now + timedelta(seconds=config.cache_ttl_seconds),
            metadata={
                "total_claims": total_claims,
                "false_claims": false_claims,
                "recent_false_24h": recent_false,
            }
        )


class CampoBatalhaCalculator(SignalCalculator):
    """Calcula intensidade de disputa narrativa em temas."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        # Analisa contradicoes e debates ativos
        contradictions = context.get("contradictions", 0)
        supports = context.get("supports", 0)
        total_relations = contradictions + supports

        if total_relations == 0:
            value = 0.0
        else:
            # Mais contradicoes = mais disputa
            contradiction_ratio = contradictions / total_relations
            activity_factor = min(1.0, total_relations / 100)
            value = (contradiction_ratio * 0.7) + (activity_factor * 0.3)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        config = SignalConfig.default_configs()[SignalType.CAMPO_BATALHA]

        return SignalValue(
            signal_type=SignalType.CAMPO_BATALHA,
            scope=scope,
            scope_id=scope_id,
            value=min(1.0, value),
            confidence=0.7 if total_relations >= 5 else 0.4,
            sample_size=total_relations,
            calculated_at=now,
            expires_at=now + timedelta(seconds=config.cache_ttl_seconds),
            metadata={
                "contradictions": contradictions,
                "supports": supports,
            }
        )


class RadarSilencioCalculator(SignalCalculator):
    """Detecta temas suspeitos por ausencia de cobertura."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        # Analisa gaps de cobertura
        expected_coverage = context.get("expected_coverage", 1.0)
        actual_coverage = context.get("actual_coverage", 1.0)
        source_diversity = context.get("source_diversity", 1.0)

        if expected_coverage == 0:
            value = 0.0
        else:
            coverage_gap = max(0, expected_coverage - actual_coverage) / expected_coverage
            diversity_penalty = 1.0 - source_diversity
            value = (coverage_gap * 0.6) + (diversity_penalty * 0.4)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        config = SignalConfig.default_configs()[SignalType.RADAR_SILENCIO]

        return SignalValue(
            signal_type=SignalType.RADAR_SILENCIO,
            scope=scope,
            scope_id=scope_id,
            value=min(1.0, value),
            confidence=0.6,
            sample_size=int(actual_coverage * 100),
            calculated_at=now,
            expires_at=now + timedelta(seconds=config.cache_ttl_seconds),
            metadata={
                "expected_coverage": expected_coverage,
                "actual_coverage": actual_coverage,
                "source_diversity": source_diversity,
            }
        )


class FragilidadeNarrativaCalculator(SignalCalculator):
    """Detecta narrativas vulneraveis a refutacao."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        # Analisa qualidade de evidencias e contradicoes pendentes
        evidence_quality = context.get("evidence_quality", 1.0)
        unaddressed_contradictions = context.get("unaddressed_contradictions", 0)
        source_credibility = context.get("avg_source_credibility", 1.0)

        weakness = (1.0 - evidence_quality) * 0.4
        contradiction_factor = min(1.0, unaddressed_contradictions / 10) * 0.35
        credibility_factor = (1.0 - source_credibility) * 0.25

        value = weakness + contradiction_factor + credibility_factor

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        config = SignalConfig.default_configs()[SignalType.FRAGILIDADE_NARRATIVA]

        return SignalValue(
            signal_type=SignalType.FRAGILIDADE_NARRATIVA,
            scope=scope,
            scope_id=scope_id,
            value=min(1.0, value),
            confidence=0.65,
            sample_size=unaddressed_contradictions,
            calculated_at=now,
            expires_at=now + timedelta(seconds=config.cache_ttl_seconds),
            metadata={
                "evidence_quality": evidence_quality,
                "unaddressed_contradictions": unaddressed_contradictions,
                "avg_source_credibility": source_credibility,
            }
        )


class ViralidadeCalculator(SignalCalculator):
    """Calcula velocidade de propagacao de claims."""

    def calculate(
        self,
        scope: SignalScope,
        scope_id: Optional[str],
        context: Dict[str, Any],
    ) -> SignalValue:
        mentions_1h = context.get("mentions_1h", 0)
        mentions_24h = context.get("mentions_24h", 0)
        unique_sources = context.get("unique_sources", 0)

        if mentions_24h == 0:
            value = 0.0
        else:
            # Aceleracao recente
            acceleration = mentions_1h / max(1, mentions_24h / 24) if mentions_24h > 0 else 0
            spread = min(1.0, unique_sources / 20)
            value = (min(1.0, acceleration / 5) * 0.6) + (spread * 0.4)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        config = SignalConfig.default_configs()[SignalType.VIRALIDADE]

        return SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=scope,
            scope_id=scope_id,
            value=min(1.0, value),
            confidence=0.75,
            sample_size=mentions_24h,
            calculated_at=now,
            expires_at=now + timedelta(seconds=config.cache_ttl_seconds),
            metadata={
                "mentions_1h": mentions_1h,
                "mentions_24h": mentions_24h,
                "unique_sources": unique_sources,
            }
        )


class SignalService:
    """
    Servico principal de sinais.

    Coordena calculo, caching e alertas de sinais do mercado de verdade.

    Uso:
        service = SignalService(cache_service, data_provider)
        signals = await service.get_signals(SignalRequest(...))
    """

    def __init__(
        self,
        cache_service: Optional["SignalCacheService"] = None,
        data_provider: Optional[Callable] = None,
    ):
        self.cache = cache_service
        self.data_provider = data_provider
        self.configs = SignalConfig.default_configs()

        # Registrar calculadores
        self._calculators: Dict[SignalType, SignalCalculator] = {
            SignalType.MENTIRAS_EM_CIRCULACAO: MentirasEmCirculacaoCalculator(),
            SignalType.CAMPO_BATALHA: CampoBatalhaCalculator(),
            SignalType.RADAR_SILENCIO: RadarSilencioCalculator(),
            SignalType.FRAGILIDADE_NARRATIVA: FragilidadeNarrativaCalculator(),
            SignalType.VIRALIDADE: ViralidadeCalculator(),
        }

    async def get_signals(self, request: SignalRequest) -> SignalBatch:
        """
        Obtem sinais conforme request.

        Verifica cache primeiro, calcula sob demanda se necessario.
        """
        start_time = time.time()
        signals: List[SignalValue] = []
        scope_ids = request.scope_ids or [None]

        for signal_type in request.signal_types:
            for scope_id in scope_ids:
                signal = await self._get_or_calculate(
                    signal_type=signal_type,
                    scope=request.scope,
                    scope_id=scope_id,
                    force_refresh=request.force_refresh,
                    include_metadata=request.include_metadata,
                )
                if signal:
                    signals.append(signal)

        calculation_time = (time.time() - start_time) * 1000

        return SignalBatch(
            batch_id=str(uuid4()),
            signals=signals,
            calculated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            calculation_time_ms=calculation_time,
        )

    async def _get_or_calculate(
        self,
        signal_type: SignalType,
        scope: SignalScope,
        scope_id: Optional[str],
        force_refresh: bool,
        include_metadata: bool,
    ) -> Optional[SignalValue]:
        """Busca em cache ou calcula sinal."""
        cache_key = self._build_cache_key(signal_type, scope, scope_id)

        # Tentar cache primeiro
        if not force_refresh and self.cache:
            cached = await self.cache.get(cache_key)
            if cached and not cached.is_expired():
                logger.debug(f"Cache hit for {cache_key}")
                return cached

        # Calcular
        signal = await self._calculate_signal(signal_type, scope, scope_id)

        # Salvar em cache
        if signal and self.cache:
            config = self.configs.get(signal_type)
            ttl = config.cache_ttl_seconds if config else 900
            await self.cache.set(cache_key, signal, ttl)

        # Limpar metadata se nao solicitado
        if signal and not include_metadata:
            signal.metadata = {}

        return signal

    async def _calculate_signal(
        self,
        signal_type: SignalType,
        scope: SignalScope,
        scope_id: Optional[str],
    ) -> Optional[SignalValue]:
        """Calcula sinal usando calculador especifico."""
        calculator = self._calculators.get(signal_type)
        if not calculator:
            logger.warning(f"No calculator for signal type: {signal_type}")
            return None

        # Buscar contexto de dados
        context = await self._get_data_context(signal_type, scope, scope_id)

        try:
            return calculator.calculate(scope, scope_id, context)
        except Exception as e:
            logger.error(f"Error calculating {signal_type}: {e}")
            return None

    async def _get_data_context(
        self,
        signal_type: SignalType,
        scope: SignalScope,
        scope_id: Optional[str],
    ) -> Dict[str, Any]:
        """Busca dados necessarios para calculo do sinal."""
        if self.data_provider:
            return await self.data_provider(signal_type, scope, scope_id)

        # Contexto mock para testes
        return self._mock_context(signal_type)

    def _mock_context(self, signal_type: SignalType) -> Dict[str, Any]:
        """Contexto mock para desenvolvimento."""
        contexts = {
            SignalType.MENTIRAS_EM_CIRCULACAO: {
                "total_claims": 100,
                "false_claims": 15,
                "recent_false_24h": 3,
            },
            SignalType.CAMPO_BATALHA: {
                "contradictions": 12,
                "supports": 45,
            },
            SignalType.RADAR_SILENCIO: {
                "expected_coverage": 1.0,
                "actual_coverage": 0.7,
                "source_diversity": 0.6,
            },
            SignalType.FRAGILIDADE_NARRATIVA: {
                "evidence_quality": 0.6,
                "unaddressed_contradictions": 4,
                "avg_source_credibility": 0.7,
            },
            SignalType.VIRALIDADE: {
                "mentions_1h": 50,
                "mentions_24h": 200,
                "unique_sources": 15,
            },
        }
        return contexts.get(signal_type, {})

    def _build_cache_key(
        self,
        signal_type: SignalType,
        scope: SignalScope,
        scope_id: Optional[str],
    ) -> str:
        """Constroi chave de cache para sinal."""
        parts = ["signal", signal_type.value, scope.value]
        if scope_id:
            parts.append(scope_id)
        return ":".join(parts)

    def check_alerts(self, signals: List[SignalValue]) -> List[SignalAlert]:
        """Verifica sinais contra thresholds e gera alertas."""
        alerts = []

        for signal in signals:
            config = self.configs.get(signal.signal_type)
            if not config or not config.thresholds:
                continue

            level = signal.get_level(config)
            if level != "normal":
                threshold = config.thresholds.get(level, 0)
                alert = SignalAlert(
                    alert_id=str(uuid4()),
                    signal_type=signal.signal_type,
                    scope=signal.scope,
                    scope_id=signal.scope_id,
                    level=level,
                    value=signal.value,
                    threshold=threshold,
                    message=f"{signal.signal_type.value} reached {level} level ({signal.value:.2f} >= {threshold})",
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
                alerts.append(alert)

        return alerts

    async def get_dashboard_signals(self) -> Dict[str, Any]:
        """Retorna sinais para dashboard principal."""
        request = SignalRequest(
            signal_types=list(SignalType),
            scope=SignalScope.GLOBAL,
            include_metadata=True,
        )

        batch = await self.get_signals(request)
        alerts = self.check_alerts(batch.signals)

        return {
            "signals": [
                {
                    "type": s.signal_type.value,
                    "value": s.value,
                    "confidence": s.confidence,
                    "level": s.get_level(self.configs[s.signal_type]),
                    "calculated_at": s.calculated_at.isoformat(),
                }
                for s in batch.signals
            ],
            "alerts": [
                {
                    "id": a.alert_id,
                    "type": a.signal_type.value,
                    "level": a.level,
                    "message": a.message,
                }
                for a in alerts
            ],
            "calculation_time_ms": batch.calculation_time_ms,
        }
