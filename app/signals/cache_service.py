"""
S38-BE-031: Signal Cache Service

Servico de cache para sinais com suporte a Redis e memoria.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.signals.signal_types import SignalScope, SignalType, SignalValue

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Interface para backends de cache."""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass


class MemoryCacheBackend(CacheBackend):
    """Cache em memoria para desenvolvimento/testes."""

    def __init__(self):
        self._cache: Dict[str, tuple[str, datetime]] = {}

    async def get(self, key: str) -> Optional[str]:
        if key not in self._cache:
            return None

        value, expires_at = self._cache[key]
        if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
            del self._cache[key]
            return None

        return value

    async def set(self, key: str, value: str, ttl: int) -> bool:
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=ttl)
        self._cache[key] = (value, expires_at)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def delete_pattern(self, pattern: str) -> int:
        import fnmatch
        keys_to_delete = [
            k for k in self._cache.keys()
            if fnmatch.fnmatch(k, pattern.replace("*", "*"))
        ]
        for k in keys_to_delete:
            del self._cache[k]
        return len(keys_to_delete)

    async def exists(self, key: str) -> bool:
        if key not in self._cache:
            return False
        _, expires_at = self._cache[key]
        return datetime.now(timezone.utc).replace(tzinfo=None) <= expires_at


class RedisCacheBackend(CacheBackend):
    """Cache com Redis."""

    def __init__(self, redis_client):
        self._redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int) -> bool:
        try:
            await self._redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis delete pattern error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False


class SignalCacheService:
    """
    Servico de cache especializado para sinais.

    Suporta:
    - TTL baseado em prioridade do sinal
    - Invalidacao por tipo/escopo
    - Serialization/deserialization de SignalValue

    Uso:
        cache = SignalCacheService(RedisCacheBackend(redis))
        await cache.set("signal:key", signal_value, ttl=300)
        signal = await cache.get("signal:key")
    """

    PREFIX = "inspectah:signal:"

    def __init__(self, backend: Optional[CacheBackend] = None):
        self.backend = backend or MemoryCacheBackend()

    def _full_key(self, key: str) -> str:
        """Adiciona prefixo ao key."""
        if key.startswith(self.PREFIX):
            return key
        return f"{self.PREFIX}{key}"

    async def get(self, key: str) -> Optional[SignalValue]:
        """Busca sinal do cache."""
        full_key = self._full_key(key)
        data = await self.backend.get(full_key)

        if not data:
            return None

        try:
            return self._deserialize(data)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to deserialize signal: {e}")
            await self.backend.delete(full_key)
            return None

    async def set(self, key: str, signal: SignalValue, ttl: int) -> bool:
        """Salva sinal no cache."""
        full_key = self._full_key(key)
        try:
            data = self._serialize(signal)
            return await self.backend.set(full_key, data, ttl)
        except (TypeError, ValueError, AttributeError) as e:
            logger.error(f"Failed to serialize signal: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove sinal do cache."""
        full_key = self._full_key(key)
        return await self.backend.delete(full_key)

    async def invalidate_by_type(self, signal_type: SignalType) -> int:
        """Invalida todos os sinais de um tipo."""
        pattern = f"{self.PREFIX}signal:{signal_type.value}:*"
        return await self.backend.delete_pattern(pattern)

    async def invalidate_by_scope(
        self,
        scope: SignalScope,
        scope_id: Optional[str] = None,
    ) -> int:
        """Invalida sinais por escopo."""
        if scope_id:
            pattern = f"{self.PREFIX}signal:*:{scope.value}:{scope_id}"
        else:
            pattern = f"{self.PREFIX}signal:*:{scope.value}:*"
        return await self.backend.delete_pattern(pattern)

    async def invalidate_all(self) -> int:
        """Invalida todo o cache de sinais."""
        pattern = f"{self.PREFIX}*"
        return await self.backend.delete_pattern(pattern)

    async def get_many(self, keys: List[str]) -> Dict[str, Optional[SignalValue]]:
        """Busca multiplos sinais."""
        results = {}
        for key in keys:
            results[key] = await self.get(key)
        return results

    async def set_many(
        self,
        signals: Dict[str, SignalValue],
        ttl: int,
    ) -> Dict[str, bool]:
        """Salva multiplos sinais."""
        results = {}
        for key, signal in signals.items():
            results[key] = await self.set(key, signal, ttl)
        return results

    def _serialize(self, signal: SignalValue) -> str:
        """Serializa SignalValue para JSON."""
        data = {
            "signal_type": signal.signal_type.value,
            "scope": signal.scope.value,
            "scope_id": signal.scope_id,
            "value": signal.value,
            "confidence": signal.confidence,
            "sample_size": signal.sample_size,
            "calculated_at": signal.calculated_at.isoformat(),
            "expires_at": signal.expires_at.isoformat(),
            "metadata": signal.metadata,
        }
        return json.dumps(data)

    def _deserialize(self, data: str) -> SignalValue:
        """Deserializa JSON para SignalValue."""
        obj = json.loads(data)
        return SignalValue(
            signal_type=SignalType(obj["signal_type"]),
            scope=SignalScope(obj["scope"]),
            scope_id=obj["scope_id"],
            value=obj["value"],
            confidence=obj["confidence"],
            sample_size=obj["sample_size"],
            calculated_at=datetime.fromisoformat(obj["calculated_at"]),
            expires_at=datetime.fromisoformat(obj["expires_at"]),
            metadata=obj.get("metadata", {}),
        )


class CacheStats:
    """Estatisticas de cache."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": self.hit_rate,
        }


class InstrumentedCacheService(SignalCacheService):
    """Cache service com instrumentacao."""

    def __init__(self, backend: Optional[CacheBackend] = None):
        super().__init__(backend)
        self.stats = CacheStats()

    async def get(self, key: str) -> Optional[SignalValue]:
        result = await super().get(key)
        if result:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        return result

    async def set(self, key: str, signal: SignalValue, ttl: int) -> bool:
        result = await super().set(key, signal, ttl)
        if result:
            self.stats.sets += 1
        return result

    async def delete(self, key: str) -> bool:
        result = await super().delete(key)
        if result:
            self.stats.deletes += 1
        return result

    def get_stats(self) -> Dict[str, Any]:
        return self.stats.to_dict()
