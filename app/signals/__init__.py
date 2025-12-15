"""Signals package — S37 Motor de Sinais + S38 On-Demand Cache."""

from app.signals.batch_calculator import BatchSignalCalculator
from app.signals.signal_repository import SignalRepository
from app.signals.calculators import (
    BattlegroundCalculator,
    BattlegroundResult,
    LiesInCirculationCalculator,
    LiesInCirculationResult,
    NarrativeFragilityCalculator,
    NarrativeFragilityResult,
    SilenceRadarCalculator,
    SilenceRadarResult,
)

# S38: On-Demand Cache & Invalidation
from app.signals.signal_types import (
    SignalType,
    SignalScope,
    SignalPriority,
    SignalConfig,
    SignalValue,
    SignalBatch,
    SignalRequest,
    SignalAlert,
)
from app.signals.signal_service import SignalService
from app.signals.cache_service import (
    SignalCacheService,
    MemoryCacheBackend,
    RedisCacheBackend,
    InstrumentedCacheService,
)
from app.signals.invalidation_service import (
    CacheInvalidationService,
    SignalEventHandler,
    EventType,
    InvalidationEvent,
)

__all__ = [
    # S37 - Batch calculators
    "BatchSignalCalculator",
    "SignalRepository",
    "LiesInCirculationCalculator",
    "LiesInCirculationResult",
    "BattlegroundCalculator",
    "BattlegroundResult",
    "SilenceRadarCalculator",
    "SilenceRadarResult",
    "NarrativeFragilityCalculator",
    "NarrativeFragilityResult",
    # S38 - Types
    "SignalType",
    "SignalScope",
    "SignalPriority",
    "SignalConfig",
    "SignalValue",
    "SignalBatch",
    "SignalRequest",
    "SignalAlert",
    # S38 - Services
    "SignalService",
    "SignalCacheService",
    "MemoryCacheBackend",
    "RedisCacheBackend",
    "InstrumentedCacheService",
    # S38 - Invalidation
    "CacheInvalidationService",
    "SignalEventHandler",
    "EventType",
    "InvalidationEvent",
]
