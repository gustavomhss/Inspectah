"""Comandos protegidos contra canetada no write path.

Todos os caminhos de alteração de estado passam por aqui para garantir
registro de causa (claim/disputa) e evitar `force_set_state` escondido.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from inspectah.truthdb.models import TruthDB
from inspectah.truthdb.state_machine import FactState


@dataclass(slots=True)
class OverrideEvent:
    fact_id: str
    requested_state: str
    permitted: bool
    reason: str
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    meta: Dict[str, object] = field(default_factory=dict)
    flags: Tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, object]:
        return {
            "fact_id": self.fact_id,
            "requested_state": self.requested_state,
            "permitted": self.permitted,
            "reason": self.reason,
            "registered_at": self.registered_at.isoformat().replace("+00:00", "Z"),
            "meta": self.meta or {},
            "flags": list(self.flags),
        }


_override_log: List[OverrideEvent] = []


class OverrideViolation(RuntimeError):
    """Tentativa de canetada sem trilha formal."""


def audit_trail() -> List[Dict[str, object]]:
    return [event.to_dict() for event in _override_log]


def apply_state_change(
    db: TruthDB,
    *,
    fact_id: str,
    new_state: str,
    cause: Mapping[str, object],
    allow_override: bool = False,
) -> None:
    """Atualiza estado garantindo que há causa formal e trilha auditável."""
    flags: List[str] = []
    if not cause or ("claim_id" not in cause and "dispute_id" not in cause):
        flags.append("missing_cause")
        _register_override(fact_id, new_state, permitted=False, reason="causa_ausente", meta=dict(cause or {}), flags=flags)
        raise OverrideViolation("Atualização rejeitada: falta claim_id ou dispute_id.")
    if cause.get("override_request") and not allow_override:
        flags.append("override_bloqueado")
        _register_override(fact_id, new_state, permitted=False, reason="override_bloqueado", meta=dict(cause), flags=flags)
        raise OverrideViolation("Override explícito precisa virar disputa formal.")
    if allow_override and not cause.get("override_request"):
        flags.append("override_sem_flag")

    fact_state = FactState(str(new_state))
    db.update_estado(fact_id, fact_state, justificativa=str(cause))
    _register_override(fact_id, new_state, permitted=True, reason="via_fluxo_formal", meta=dict(cause), flags=flags)


def _register_override(
    fact_id: str,
    requested_state: str,
    *,
    permitted: bool,
    reason: str,
    meta: Optional[Dict[str, object]] = None,
    flags: Sequence[str] | None = None,
) -> None:
    _override_log.append(
        OverrideEvent(
            fact_id=fact_id,
            requested_state=requested_state,
            permitted=permitted,
            reason=reason,
            meta=meta or {},
            flags=tuple(flags or ()),
        )
    )


__all__ = ["apply_state_change", "OverrideViolation", "audit_trail", "OverrideEvent"]
