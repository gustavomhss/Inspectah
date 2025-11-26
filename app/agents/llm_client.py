"""Cliente stub para LLMs usado pela camada de agentes (S23).

Nesta sprint, o cliente apenas define interface e aplica política de modelo;
as chamadas reais a provedores ficam para sprints futuras.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.agents.models import AgentProfile, ModelUpgradePolicy


class LLMClient:
    def __init__(self, policy: Optional[ModelUpgradePolicy] = None):
        self.policy = policy or ModelUpgradePolicy()

    def resolve_model(self, agent: AgentProfile, now: Optional[datetime] = None) -> str:
        return self.policy.effective_model_for(agent, now=now)

    def generate(self, agent: AgentProfile, prompt: str, now: Optional[datetime] = None) -> Dict[str, Any]:
        model_used = self.resolve_model(agent, now=now)
        return {
            "model": model_used,
            "prompt_preview": prompt[:200],
            "output": "stubbed-response",
            "ts": datetime.utcnow().isoformat(),
        }
