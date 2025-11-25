from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

STATES = {
    "intro",
    "discover",
    "consultor",
    "autofill",
    "ask_missing",
    "review",
    "status_planning",
    "done",
    "editar_existente",
    "planejar_status",
}


@dataclass
class FSMState:
    name: str
    description: str


def next_state(form_state: Dict[str, object], intent: Optional[str] = None) -> FSMState:
    if intent == "consultor":
        return FSMState("consultor", "Responder dúvidas conceituais/táticas antes de preencher.")
    if form_state.get("source_id") and intent == "status":
        return FSMState("planejar_status", "Planejar mudança de status com confirmação.")
    if form_state.get("source_id"):
        return FSMState("editar_existente", "Editar fonte existente e propor diffs.")
    if not form_state.get("type"):
        return FSMState("discover", "Entender tipo de fonte e objetivo.")
    if not form_state.get("endpoint"):
        return FSMState("ask_missing", "Coletar endpoint/base.")
    if not form_state.get("refresh_interval"):
        return FSMState("autofill", "Preencher refresh e campos auxiliares.")
    return FSMState("review", "Pronto para revisar e salvar.")
