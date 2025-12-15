"""
S38-BE-032: Cache Invalidation Service

Servico de invalidacao de cache baseado em eventos.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from app.signals.cache_service import SignalCacheService
from app.signals.signal_types import SignalScope, SignalType

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos que disparam invalidacao."""
    CLAIM_CREATED = "claim_created"
    CLAIM_UPDATED = "claim_updated"
    CLAIM_VERDICT_CHANGED = "claim_verdict_changed"
    CLAIM_DELETED = "claim_deleted"
    SOURCE_HEALTH_CHANGED = "source_health_changed"
    SOURCE_INGESTION_COMPLETE = "source_ingestion_complete"
    ENTITY_MERGED = "entity_merged"
    RELATION_CREATED = "relation_created"
    RELATION_DELETED = "relation_deleted"
    POLICY_UPDATED = "policy_updated"
    MANUAL_INVALIDATION = "manual_invalidation"


@dataclass
class InvalidationEvent:
    """Evento de invalidacao."""
    event_type: EventType
    timestamp: datetime
    scope: SignalScope
    scope_id: Optional[str] = None
    affected_types: Optional[List[SignalType]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# Mapeamento: evento -> sinais afetados
EVENT_SIGNAL_MAPPING: Dict[EventType, List[SignalType]] = {
    EventType.CLAIM_CREATED: [
        SignalType.MENTIRAS_EM_CIRCULACAO,
        SignalType.VIRALIDADE,
        SignalType.CAMPO_BATALHA,
    ],
    EventType.CLAIM_UPDATED: [
        SignalType.FRAGILIDADE_NARRATIVA,
        SignalType.CONVERGENCIA,
    ],
    EventType.CLAIM_VERDICT_CHANGED: [
        SignalType.MENTIRAS_EM_CIRCULACAO,
        SignalType.FRAGILIDADE_NARRATIVA,
        SignalType.CREDIBILIDADE_FONTE,
    ],
    EventType.CLAIM_DELETED: [
        SignalType.MENTIRAS_EM_CIRCULACAO,
        SignalType.CAMPO_BATALHA,
    ],
    EventType.SOURCE_HEALTH_CHANGED: [
        SignalType.CREDIBILIDADE_FONTE,
        SignalType.RADAR_SILENCIO,
    ],
    EventType.SOURCE_INGESTION_COMPLETE: [
        SignalType.VIRALIDADE,
        SignalType.RADAR_SILENCIO,
        SignalType.CONVERGENCIA,
    ],
    EventType.ENTITY_MERGED: [
        SignalType.CAMPO_BATALHA,
        SignalType.CONVERGENCIA,
    ],
    EventType.RELATION_CREATED: [
        SignalType.CAMPO_BATALHA,
        SignalType.FRAGILIDADE_NARRATIVA,
        SignalType.CONVERGENCIA,
    ],
    EventType.RELATION_DELETED: [
        SignalType.CAMPO_BATALHA,
        SignalType.FRAGILIDADE_NARRATIVA,
    ],
    EventType.POLICY_UPDATED: list(SignalType),  # Invalida tudo
    EventType.MANUAL_INVALIDATION: list(SignalType),
}


class InvalidationStrategy:
    """Estrategia de invalidacao."""

    def get_keys_to_invalidate(
        self,
        event: InvalidationEvent,
        cache: SignalCacheService,
    ) -> List[str]:
        """Retorna lista de chaves a invalidar."""
        raise NotImplementedError


class TypeBasedStrategy(InvalidationStrategy):
    """Invalida por tipo de sinal."""

    def get_keys_to_invalidate(
        self,
        event: InvalidationEvent,
        cache: SignalCacheService,
    ) -> List[str]:
        affected = event.affected_types or EVENT_SIGNAL_MAPPING.get(event.event_type, [])
        keys = []
        for signal_type in affected:
            if event.scope_id:
                key = f"signal:{signal_type.value}:{event.scope.value}:{event.scope_id}"
            else:
                key = f"signal:{signal_type.value}:*"
            keys.append(key)
        return keys


class ScopeBasedStrategy(InvalidationStrategy):
    """Invalida por escopo."""

    def get_keys_to_invalidate(
        self,
        event: InvalidationEvent,
        cache: SignalCacheService,
    ) -> List[str]:
        if event.scope_id:
            return [f"signal:*:{event.scope.value}:{event.scope_id}"]
        return [f"signal:*:{event.scope.value}:*"]


class CacheInvalidationService:
    """
    Servico de invalidacao de cache de sinais.

    Coordena invalidacao baseada em eventos do sistema.

    Uso:
        service = CacheInvalidationService(cache_service)

        # Registrar handler customizado
        service.register_handler(EventType.CLAIM_CREATED, my_handler)

        # Processar evento
        await service.process_event(InvalidationEvent(...))
    """

    def __init__(
        self,
        cache_service: SignalCacheService,
        strategy: Optional[InvalidationStrategy] = None,
    ):
        self.cache = cache_service
        self.strategy = strategy or TypeBasedStrategy()
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._event_log: List[InvalidationEvent] = []
        self._max_log_size = 1000

    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[InvalidationEvent], None],
    ) -> None:
        """Registra handler customizado para tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def process_event(self, event: InvalidationEvent) -> int:
        """
        Processa evento de invalidacao.

        Returns:
            Numero de chaves invalidadas
        """
        logger.info(f"Processing invalidation event: {event.event_type}")

        # Log evento
        self._log_event(event)

        # Executar handlers customizados
        await self._run_handlers(event)

        # Invalidar cache
        invalidated = await self._invalidate(event)

        logger.info(f"Invalidated {invalidated} cache entries for {event.event_type}")
        return invalidated

    async def _invalidate(self, event: InvalidationEvent) -> int:
        """Executa invalidacao no cache."""
        keys = self.strategy.get_keys_to_invalidate(event, self.cache)
        total = 0

        for key in keys:
            if "*" in key:
                # Pattern-based deletion
                count = await self.cache.backend.delete_pattern(
                    f"{self.cache.PREFIX}{key}"
                )
                total += count
            else:
                if await self.cache.delete(key):
                    total += 1

        return total

    async def _run_handlers(self, event: InvalidationEvent) -> None:
        """Executa handlers registrados."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    def _log_event(self, event: InvalidationEvent) -> None:
        """Registra evento no log interno."""
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]

    async def invalidate_for_claim(
        self,
        claim_id: str,
        topic_id: Optional[str] = None,
    ) -> int:
        """Atalho para invalidar cache apos mudanca em claim."""
        event = InvalidationEvent(
            event_type=EventType.CLAIM_UPDATED,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.CLAIM,
            scope_id=claim_id,
            metadata={"topic_id": topic_id} if topic_id else None,
        )

        total = await self.process_event(event)

        # Se tem topic, invalida tambem no escopo do topic
        if topic_id:
            topic_event = InvalidationEvent(
                event_type=EventType.CLAIM_UPDATED,
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                scope=SignalScope.TOPIC,
                scope_id=topic_id,
            )
            total += await self.process_event(topic_event)

        return total

    async def invalidate_for_source(self, source_id: str) -> int:
        """Atalho para invalidar cache apos mudanca em fonte."""
        event = InvalidationEvent(
            event_type=EventType.SOURCE_HEALTH_CHANGED,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.SOURCE,
            scope_id=source_id,
        )
        return await self.process_event(event)

    async def invalidate_all(self) -> int:
        """Invalida todo o cache."""
        event = InvalidationEvent(
            event_type=EventType.MANUAL_INVALIDATION,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.GLOBAL,
        )
        return await self.process_event(event)

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna eventos recentes."""
        events = self._event_log[-limit:]
        return [
            {
                "event_type": e.event_type.value,
                "timestamp": e.timestamp.isoformat(),
                "scope": e.scope.value,
                "scope_id": e.scope_id,
            }
            for e in events
        ]


class SignalEventHandler:
    """
    Handler de eventos que integra com sistema de sinais.

    Pode ser usado como subscriber de eventos do sistema.
    """

    def __init__(self, invalidation_service: CacheInvalidationService):
        self.invalidation = invalidation_service

    async def on_claim_created(
        self,
        claim_id: str,
        verdict: Optional[str] = None,
        topic_id: Optional[str] = None,
    ) -> None:
        """Chamado quando claim e criado."""
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.CLAIM,
            scope_id=claim_id,
            metadata={
                "verdict": verdict,
                "topic_id": topic_id,
            }
        )
        await self.invalidation.process_event(event)

    async def on_claim_verdict_changed(
        self,
        claim_id: str,
        old_verdict: str,
        new_verdict: str,
    ) -> None:
        """Chamado quando veredicto de claim muda."""
        event = InvalidationEvent(
            event_type=EventType.CLAIM_VERDICT_CHANGED,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.CLAIM,
            scope_id=claim_id,
            metadata={
                "old_verdict": old_verdict,
                "new_verdict": new_verdict,
            }
        )
        await self.invalidation.process_event(event)

    async def on_source_ingestion_complete(
        self,
        source_id: str,
        documents_count: int,
    ) -> None:
        """Chamado quando ingestao de fonte completa."""
        event = InvalidationEvent(
            event_type=EventType.SOURCE_INGESTION_COMPLETE,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.SOURCE,
            scope_id=source_id,
            metadata={"documents_count": documents_count}
        )
        await self.invalidation.process_event(event)

    async def on_relation_created(
        self,
        source_claim_id: str,
        target_claim_id: str,
        relation_type: str,
    ) -> None:
        """Chamado quando relacao entre claims e criada."""
        event = InvalidationEvent(
            event_type=EventType.RELATION_CREATED,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            scope=SignalScope.CLAIM,
            scope_id=source_claim_id,
            metadata={
                "target_claim_id": target_claim_id,
                "relation_type": relation_type,
            }
        )
        await self.invalidation.process_event(event)
