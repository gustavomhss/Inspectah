from __future__ import annotations

from enum import Enum


class TruthState(str, Enum):
    """
    Estados formais da Verdade/Fato v1.5.

    UNKNOWN: claim registrada sem decisão ou evidência.
    CLAIMED: claim declarada, aguardando validação inicial.
    UNDER_REVIEW: em análise ativa (camadas, comitês, debunker).
    PROVISIONAL: verdade provisória com prudência explícita.
    ESTABLISHED_FACT: aceita como fato/verdade operacional.
    UNDER_DISPUTE: contestada ou com conflito relevante.
    RETRACTED: retraída/superada; mantida só para histórico.
    """

    UNKNOWN = "UNKNOWN"
    CLAIMED = "CLAIMED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PROVISIONAL = "PROVISIONAL"
    ESTABLISHED_FACT = "ESTABLISHED_FACT"
    UNDER_DISPUTE = "UNDER_DISPUTE"
    RETRACTED = "RETRACTED"


class TruthEventType(str, Enum):
    """Tipos simples de eventos de mudança de estado."""

    PROMOTION = "PROMOTION"
    DOWNGRADE = "DOWNGRADE"
    CORRECTION = "CORRECTION"
    FREEZE = "FREEZE"
