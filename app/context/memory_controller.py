"""
S38-BE-041: Memory Controller

Controlador de memoria de contexto para agentes e fluxos.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class MemoryScope(str, Enum):
    """Escopo de memoria."""
    SESSION = "session"       # Memoria de sessao (curto prazo)
    AGENT = "agent"           # Memoria do agente
    FLOW = "flow"             # Memoria do fluxo
    CASE = "case"             # Memoria do caso
    USER = "user"             # Memoria do usuario
    GLOBAL = "global"         # Memoria global do sistema


class MemoryType(str, Enum):
    """Tipos de memoria."""
    CONTEXT = "context"       # Contexto atual
    FACT = "fact"             # Fato aprendido
    DECISION = "decision"     # Decisao tomada
    OBSERVATION = "observation"  # Observacao
    SUMMARY = "summary"       # Resumo
    REFERENCE = "reference"   # Referencia a outros dados


class RetentionPolicy(str, Enum):
    """Politica de retencao."""
    EPHEMERAL = "ephemeral"   # Deletar ao fim da sessao
    SHORT = "short"           # 1 dia
    MEDIUM = "medium"         # 7 dias
    LONG = "long"             # 30 dias
    PERMANENT = "permanent"   # Nunca deletar


RETENTION_TTL = {
    RetentionPolicy.EPHEMERAL: timedelta(hours=1),
    RetentionPolicy.SHORT: timedelta(days=1),
    RetentionPolicy.MEDIUM: timedelta(days=7),
    RetentionPolicy.LONG: timedelta(days=30),
    RetentionPolicy.PERMANENT: timedelta(days=36500),  # ~100 years
}


@dataclass
class MemoryEntry:
    """Uma entrada de memoria."""
    entry_id: str
    scope: MemoryScope
    scope_id: str  # ID do escopo (session_id, agent_id, etc)
    memory_type: MemoryType
    key: str
    value: Any
    retention: RetentionPolicy
    created_at: datetime
    expires_at: datetime
    accessed_at: datetime
    access_count: int = 0
    importance: float = 0.5  # 0.0 a 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.expires_at

    def touch(self) -> None:
        """Atualiza ultimo acesso."""
        self.accessed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "scope": self.scope.value,
            "scope_id": self.scope_id,
            "memory_type": self.memory_type.value,
            "key": self.key,
            "value": self.value,
            "retention": self.retention.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "importance": self.importance,
            "tags": self.tags,
        }


@dataclass
class MemoryContext:
    """Contexto de memoria para uma sessao/fluxo."""
    context_id: str
    scope: MemoryScope
    scope_id: str
    entries: Dict[str, MemoryEntry] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    def get_active_entries(self) -> List[MemoryEntry]:
        """Retorna entradas nao expiradas."""
        return [e for e in self.entries.values() if not e.is_expired()]


@dataclass
class MemoryStats:
    """Estatisticas de uso de memoria."""
    total_entries: int
    active_entries: int
    expired_entries: int
    by_scope: Dict[str, int]
    by_type: Dict[str, int]
    by_retention: Dict[str, int]
    total_access_count: int
    avg_importance: float


class MemoryRepository:
    """Repositorio em memoria."""

    def __init__(self):
        self._entries: Dict[str, MemoryEntry] = {}
        self._by_scope: Dict[str, Dict[str, Set[str]]] = {}  # scope -> scope_id -> entry_ids
        self._by_key: Dict[str, Set[str]] = {}  # key -> entry_ids

    def save(self, entry: MemoryEntry) -> None:
        self._entries[entry.entry_id] = entry

        # Index by scope
        if entry.scope.value not in self._by_scope:
            self._by_scope[entry.scope.value] = {}
        if entry.scope_id not in self._by_scope[entry.scope.value]:
            self._by_scope[entry.scope.value][entry.scope_id] = set()
        self._by_scope[entry.scope.value][entry.scope_id].add(entry.entry_id)

        # Index by key
        if entry.key not in self._by_key:
            self._by_key[entry.key] = set()
        self._by_key[entry.key].add(entry.entry_id)

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)

    def get_by_scope(
        self,
        scope: MemoryScope,
        scope_id: str,
    ) -> List[MemoryEntry]:
        entry_ids = self._by_scope.get(scope.value, {}).get(scope_id, set())
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]

    def get_by_key(self, key: str) -> List[MemoryEntry]:
        entry_ids = self._by_key.get(key, set())
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]

    def delete(self, entry_id: str) -> bool:
        if entry_id not in self._entries:
            return False

        entry = self._entries.pop(entry_id)

        # Remove from indexes
        if entry.scope.value in self._by_scope:
            if entry.scope_id in self._by_scope[entry.scope.value]:
                self._by_scope[entry.scope.value][entry.scope_id].discard(entry_id)

        if entry.key in self._by_key:
            self._by_key[entry.key].discard(entry_id)

        return True

    def get_all(self) -> List[MemoryEntry]:
        return list(self._entries.values())


class MemoryController:
    """
    Controlador de memoria de contexto.

    Gerencia memoria de curto e longo prazo para:
    - Sessoes de usuario
    - Execucao de agentes
    - Fluxos de trabalho
    - Casos de investigacao

    Uso:
        controller = MemoryController()

        # Armazenar memoria
        controller.remember(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
            key="last_decision",
            value={"action": "approve", "reason": "High confidence"},
            memory_type=MemoryType.DECISION,
        )

        # Recuperar memoria
        decisions = controller.recall(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
            memory_type=MemoryType.DECISION,
        )

        # Construir contexto
        context = controller.build_context(
            scope=MemoryScope.FLOW,
            scope_id="flow_123",
        )
    """

    def __init__(
        self,
        repository: Optional[MemoryRepository] = None,
        max_entries_per_scope: int = 1000,
        auto_cleanup: bool = True,
    ):
        self.repository = repository or MemoryRepository()
        self.max_entries_per_scope = max_entries_per_scope
        self.auto_cleanup = auto_cleanup
        self._cleanup_callbacks: List[Callable[[MemoryEntry], None]] = []

    def remember(
        self,
        scope: MemoryScope,
        scope_id: str,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.CONTEXT,
        retention: RetentionPolicy = RetentionPolicy.MEDIUM,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """
        Armazena uma memoria.

        Args:
            scope: Escopo da memoria
            scope_id: ID do escopo
            key: Chave identificadora
            value: Valor a armazenar
            memory_type: Tipo de memoria
            retention: Politica de retencao
            importance: Importancia (0-1)
            tags: Tags para busca
            metadata: Metadados adicionais

        Returns:
            Entrada de memoria criada
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        ttl = RETENTION_TTL[retention]
        expires_at = now + ttl

        entry = MemoryEntry(
            entry_id=f"mem_{uuid4().hex[:12]}",
            scope=scope,
            scope_id=scope_id,
            memory_type=memory_type,
            key=key,
            value=value,
            retention=retention,
            created_at=now,
            expires_at=expires_at,
            accessed_at=now,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.repository.save(entry)

        # Cleanup if needed
        if self.auto_cleanup:
            self._maybe_cleanup(scope, scope_id)

        logger.debug(f"Remembered {key} in {scope.value}:{scope_id}")
        return entry

    def recall(
        self,
        scope: MemoryScope,
        scope_id: str,
        key: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: int = 100,
        include_expired: bool = False,
    ) -> List[MemoryEntry]:
        """
        Recupera memorias.

        Args:
            scope: Escopo da memoria
            scope_id: ID do escopo
            key: Chave especifica (opcional)
            memory_type: Filtrar por tipo
            tags: Filtrar por tags
            min_importance: Importancia minima
            limit: Limite de resultados
            include_expired: Incluir expiradas

        Returns:
            Lista de entradas correspondentes
        """
        entries = self.repository.get_by_scope(scope, scope_id)

        # Apply filters
        results = []
        for entry in entries:
            if not include_expired and entry.is_expired():
                continue
            if key and entry.key != key:
                continue
            if memory_type and entry.memory_type != memory_type:
                continue
            if entry.importance < min_importance:
                continue
            if tags and not any(t in entry.tags for t in tags):
                continue

            entry.touch()
            results.append(entry)

        # Sort by importance and recency
        results.sort(
            key=lambda e: (e.importance, e.accessed_at),
            reverse=True,
        )

        return results[:limit]

    def recall_by_key(self, key: str, include_expired: bool = False) -> List[MemoryEntry]:
        """Recupera todas as memorias com uma chave."""
        entries = self.repository.get_by_key(key)
        if not include_expired:
            entries = [e for e in entries if not e.is_expired()]
        for e in entries:
            e.touch()
        return entries

    def forget(
        self,
        scope: MemoryScope,
        scope_id: str,
        key: Optional[str] = None,
    ) -> int:
        """
        Esquece memorias.

        Args:
            scope: Escopo
            scope_id: ID do escopo
            key: Chave especifica (None = todas do escopo)

        Returns:
            Numero de entradas removidas
        """
        entries = self.repository.get_by_scope(scope, scope_id)
        count = 0

        for entry in entries:
            if key and entry.key != key:
                continue
            if self.repository.delete(entry.entry_id):
                count += 1
                for callback in self._cleanup_callbacks:
                    callback(entry)

        logger.info(f"Forgot {count} entries from {scope.value}:{scope_id}")
        return count

    def build_context(
        self,
        scope: MemoryScope,
        scope_id: str,
        include_types: Optional[List[MemoryType]] = None,
        max_entries: int = 50,
    ) -> MemoryContext:
        """
        Constroi contexto de memoria para uso em agentes/fluxos.

        Args:
            scope: Escopo
            scope_id: ID do escopo
            include_types: Tipos a incluir
            max_entries: Maximo de entradas

        Returns:
            Contexto de memoria construido
        """
        entries = self.recall(
            scope=scope,
            scope_id=scope_id,
            memory_type=None,
            limit=max_entries,
        )

        if include_types:
            entries = [e for e in entries if e.memory_type in include_types]

        context = MemoryContext(
            context_id=f"ctx_{uuid4().hex[:8]}",
            scope=scope,
            scope_id=scope_id,
            entries={e.key: e for e in entries},
        )

        return context

    def summarize(
        self,
        scope: MemoryScope,
        scope_id: str,
        summarizer: Optional[Callable[[List[MemoryEntry]], str]] = None,
    ) -> MemoryEntry:
        """
        Cria resumo das memorias de um escopo.

        O resumo e armazenado como nova memoria de tipo SUMMARY.
        """
        entries = self.recall(scope=scope, scope_id=scope_id, limit=500)

        if summarizer:
            summary_text = summarizer(entries)
        else:
            summary_text = self._default_summarize(entries)

        return self.remember(
            scope=scope,
            scope_id=scope_id,
            key=f"summary_{datetime.now(timezone.utc).replace(tzinfo=None).strftime('%Y%m%d_%H%M')}",
            value=summary_text,
            memory_type=MemoryType.SUMMARY,
            retention=RetentionPolicy.LONG,
            importance=0.8,
        )

    def _default_summarize(self, entries: List[MemoryEntry]) -> str:
        """Sumarizacao padrao."""
        by_type: Dict[str, List[str]] = {}
        for e in entries:
            if e.memory_type.value not in by_type:
                by_type[e.memory_type.value] = []
            by_type[e.memory_type.value].append(e.key)

        parts = []
        for mtype, keys in by_type.items():
            parts.append(f"{mtype}: {len(keys)} entries ({', '.join(keys[:5])}...)")

        return "; ".join(parts)

    def cleanup_expired(self) -> int:
        """Remove todas as entradas expiradas."""
        entries = self.repository.get_all()
        count = 0

        for entry in entries:
            if entry.is_expired():
                if self.repository.delete(entry.entry_id):
                    count += 1
                    for callback in self._cleanup_callbacks:
                        callback(entry)

        logger.info(f"Cleaned up {count} expired entries")
        return count

    def _maybe_cleanup(self, scope: MemoryScope, scope_id: str) -> None:
        """Limpa entradas se exceder limite."""
        entries = self.repository.get_by_scope(scope, scope_id)

        if len(entries) > self.max_entries_per_scope:
            # Remove least important expired entries first
            to_remove = sorted(
                entries,
                key=lambda e: (not e.is_expired(), e.importance, e.accessed_at),
            )
            excess = len(entries) - self.max_entries_per_scope
            for entry in to_remove[:excess]:
                self.repository.delete(entry.entry_id)

    def get_stats(self) -> MemoryStats:
        """Retorna estatisticas de uso."""
        entries = self.repository.get_all()
        active = [e for e in entries if not e.is_expired()]
        expired = [e for e in entries if e.is_expired()]

        by_scope: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        by_retention: Dict[str, int] = {}
        total_access = 0
        total_importance = 0.0

        for e in entries:
            by_scope[e.scope.value] = by_scope.get(e.scope.value, 0) + 1
            by_type[e.memory_type.value] = by_type.get(e.memory_type.value, 0) + 1
            by_retention[e.retention.value] = by_retention.get(e.retention.value, 0) + 1
            total_access += e.access_count
            total_importance += e.importance

        return MemoryStats(
            total_entries=len(entries),
            active_entries=len(active),
            expired_entries=len(expired),
            by_scope=by_scope,
            by_type=by_type,
            by_retention=by_retention,
            total_access_count=total_access,
            avg_importance=total_importance / len(entries) if entries else 0.0,
        )

    def register_cleanup_callback(
        self,
        callback: Callable[[MemoryEntry], None],
    ) -> None:
        """Registra callback para quando entradas sao removidas."""
        self._cleanup_callbacks.append(callback)

    def export_context(
        self,
        scope: MemoryScope,
        scope_id: str,
    ) -> Dict[str, Any]:
        """Exporta contexto como dict para serializacao."""
        context = self.build_context(scope, scope_id)
        return {
            "context_id": context.context_id,
            "scope": context.scope.value,
            "scope_id": context.scope_id,
            "entries": [e.to_dict() for e in context.entries.values()],
            "created_at": context.created_at.isoformat(),
        }

    def import_context(
        self,
        data: Dict[str, Any],
        scope: MemoryScope,
        scope_id: str,
    ) -> int:
        """Importa contexto de dict."""
        count = 0
        for entry_data in data.get("entries", []):
            self.remember(
                scope=scope,
                scope_id=scope_id,
                key=entry_data["key"],
                value=entry_data["value"],
                memory_type=MemoryType(entry_data["memory_type"]),
                retention=RetentionPolicy(entry_data["retention"]),
                importance=entry_data.get("importance", 0.5),
                tags=entry_data.get("tags", []),
            )
            count += 1
        return count
