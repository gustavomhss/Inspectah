"""
S38-BE-030: Signal Types

Tipos e estruturas para sinais do mercado de verdade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SignalType(str, Enum):
    """Tipos de sinais do mercado de verdade."""
    MENTIRAS_EM_CIRCULACAO = "mentiras_em_circulacao"  # Volume de claims falsos ativos
    CAMPO_BATALHA = "campo_batalha"                    # Temas em disputa narrativa
    RADAR_SILENCIO = "radar_silencio"                  # Temas ausentes ou suprimidos
    FRAGILIDADE_NARRATIVA = "fragilidade_narrativa"    # Narrativas vulneraveis a refutacao
    CREDIBILIDADE_FONTE = "credibilidade_fonte"        # Score de credibilidade de fontes
    VIRALIDADE = "viralidade"                          # Velocidade de propagacao
    CONVERGENCIA = "convergencia"                      # Alinhamento entre fontes
    TENSAO_TEMPORAL = "tensao_temporal"                # Volatilidade de narrativas


class SignalScope(str, Enum):
    """Escopo de calculo do sinal."""
    GLOBAL = "global"           # Todo o sistema
    TOPIC = "topic"             # Por topico/tema
    ENTITY = "entity"           # Por entidade
    SOURCE = "source"           # Por fonte
    CLAIM = "claim"             # Por claim especifico
    CLUSTER = "cluster"         # Por cluster de claims


class SignalPriority(str, Enum):
    """Prioridade de calculo/cache."""
    CRITICAL = "critical"   # Cache 1min, calculo prioritario
    HIGH = "high"           # Cache 5min
    NORMAL = "normal"       # Cache 15min
    LOW = "low"             # Cache 1h
    BATCH = "batch"         # Calculo em batch, cache longo


@dataclass
class SignalConfig:
    """Configuracao de um tipo de sinal."""
    signal_type: SignalType
    priority: SignalPriority = SignalPriority.NORMAL
    cache_ttl_seconds: int = 900  # 15 min default
    min_data_points: int = 3      # Minimo de pontos para calcular
    decay_factor: float = 0.95    # Fator de decaimento temporal
    thresholds: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def default_configs(cls) -> Dict[SignalType, "SignalConfig"]:
        """Retorna configuracoes padrao para cada tipo de sinal."""
        return {
            SignalType.MENTIRAS_EM_CIRCULACAO: cls(
                signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
                priority=SignalPriority.CRITICAL,
                cache_ttl_seconds=60,
                thresholds={"alert": 0.7, "critical": 0.9}
            ),
            SignalType.CAMPO_BATALHA: cls(
                signal_type=SignalType.CAMPO_BATALHA,
                priority=SignalPriority.HIGH,
                cache_ttl_seconds=300,
                thresholds={"active": 0.5, "intense": 0.8}
            ),
            SignalType.RADAR_SILENCIO: cls(
                signal_type=SignalType.RADAR_SILENCIO,
                priority=SignalPriority.NORMAL,
                cache_ttl_seconds=900,
                thresholds={"suspicious": 0.6, "anomaly": 0.85}
            ),
            SignalType.FRAGILIDADE_NARRATIVA: cls(
                signal_type=SignalType.FRAGILIDADE_NARRATIVA,
                priority=SignalPriority.HIGH,
                cache_ttl_seconds=300,
                thresholds={"vulnerable": 0.4, "critical": 0.7}
            ),
            SignalType.CREDIBILIDADE_FONTE: cls(
                signal_type=SignalType.CREDIBILIDADE_FONTE,
                priority=SignalPriority.LOW,
                cache_ttl_seconds=3600,
                thresholds={"low": 0.3, "medium": 0.6, "high": 0.8}
            ),
            SignalType.VIRALIDADE: cls(
                signal_type=SignalType.VIRALIDADE,
                priority=SignalPriority.CRITICAL,
                cache_ttl_seconds=60,
                decay_factor=0.9,
                thresholds={"trending": 0.5, "viral": 0.8}
            ),
            SignalType.CONVERGENCIA: cls(
                signal_type=SignalType.CONVERGENCIA,
                priority=SignalPriority.NORMAL,
                cache_ttl_seconds=900,
                thresholds={"aligned": 0.7, "consensus": 0.9}
            ),
            SignalType.TENSAO_TEMPORAL: cls(
                signal_type=SignalType.TENSAO_TEMPORAL,
                priority=SignalPriority.HIGH,
                cache_ttl_seconds=300,
                thresholds={"elevated": 0.5, "high": 0.75}
            ),
        }


@dataclass
class SignalValue:
    """Valor calculado de um sinal."""
    signal_type: SignalType
    scope: SignalScope
    scope_id: Optional[str]  # ID do escopo (topic_id, entity_id, etc)
    value: float             # 0.0 a 1.0
    confidence: float        # Confianca no valor
    sample_size: int         # Tamanho da amostra usada
    calculated_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at

    def get_level(self, config: SignalConfig) -> str:
        """Retorna nivel baseado nos thresholds."""
        thresholds = sorted(config.thresholds.items(), key=lambda x: x[1], reverse=True)
        for level, threshold in thresholds:
            if self.value >= threshold:
                return level
        return "normal"


@dataclass
class SignalBatch:
    """Lote de sinais calculados juntos."""
    batch_id: str
    signals: List[SignalValue]
    calculated_at: datetime
    calculation_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def signal_count(self) -> int:
        return len(self.signals)

    def get_by_type(self, signal_type: SignalType) -> List[SignalValue]:
        return [s for s in self.signals if s.signal_type == signal_type]

    def get_by_scope(self, scope: SignalScope, scope_id: Optional[str] = None) -> List[SignalValue]:
        results = [s for s in self.signals if s.scope == scope]
        if scope_id:
            results = [s for s in results if s.scope_id == scope_id]
        return results


@dataclass
class SignalRequest:
    """Request para calculo de sinal."""
    signal_types: List[SignalType]
    scope: SignalScope = SignalScope.GLOBAL
    scope_ids: Optional[List[str]] = None
    force_refresh: bool = False
    include_metadata: bool = False


@dataclass
class SignalAlert:
    """Alerta gerado por sinal."""
    alert_id: str
    signal_type: SignalType
    scope: SignalScope
    scope_id: Optional[str]
    level: str          # warning, alert, critical
    value: float
    threshold: float
    message: str
    created_at: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
