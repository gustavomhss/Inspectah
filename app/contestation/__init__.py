"""
Contestation Module — S41

Módulo de contestação para o sistema de governança do Inspectah.
Implementa o fluxo completo de contestação de decisões com Acordão MAC.

Componentes principais:
- DisputeCase: FSM para casos de contestação
- Acordao: Decisão final da contestação via MAC
- TensorEtico: Cálculo de impacto ético
- AppealService: Gerenciamento de recursos
- ContestationService: Orquestração completa do fluxo

Referências:
- Playbook S41 v5.0, Capítulo 4 (Execução & Cenários)
- Guia Conceitual: MAC (Máquina Adiabática de Consenso)
- Guia Conceitual: Tensor de Deformação Semântica
"""

from __future__ import annotations

# Models
from app.contestation.models import (
    AcordaoModel,
    AcordaoOutcome,
    AppealType,
    DisputeCaseModel,
    DisputeGround,
    DisputeStatus,
    EvidenceRef,
    EvidenceType,
    TensorEticoResult,
    VoteRecord,
)

# Dispute Case FSM
from app.contestation.dispute_case import (
    DisputeCase,
    TransitionRecord,
    TransitionResult,
    VALID_TRANSITIONS,
)

# Tensor Ético
from app.contestation.tensor_ethic import (
    TensorEthicCalculator,
    TensorInput,
    calculate_tensor_etico,
    get_tensor_calculator,
)

# Acordao Service
from app.contestation.acordao import (
    AcordaoRequest,
    AcordaoService,
    ConsensusMetrics,
    get_acordao_service,
    reset_acordao_service,
)

# Appeal Service
from app.contestation.appeal import (
    AppealBasis,
    AppealModel,
    AppealService,
    AppealStatus,
    get_appeal_service,
    reset_appeal_service,
)

# Main Service
from app.contestation.service import (
    ContestationService,
    ContestationStats,
    get_contestation_service,
    reset_contestation_service,
)

__version__ = "1.0.0"
__all__ = [
    # Models
    "AcordaoModel",
    "AcordaoOutcome",
    "AppealType",
    "DisputeCaseModel",
    "DisputeGround",
    "DisputeStatus",
    "EvidenceRef",
    "EvidenceType",
    "TensorEticoResult",
    "VoteRecord",
    # Dispute Case
    "DisputeCase",
    "TransitionRecord",
    "TransitionResult",
    "VALID_TRANSITIONS",
    # Tensor Ético
    "TensorEthicCalculator",
    "TensorInput",
    "calculate_tensor_etico",
    "get_tensor_calculator",
    # Acordao
    "AcordaoRequest",
    "AcordaoService",
    "ConsensusMetrics",
    "get_acordao_service",
    "reset_acordao_service",
    # Appeal
    "AppealBasis",
    "AppealModel",
    "AppealService",
    "AppealStatus",
    "get_appeal_service",
    "reset_appeal_service",
    # Main Service
    "ContestationService",
    "ContestationStats",
    "get_contestation_service",
    "reset_contestation_service",
    # Legacy compatibility
    "ContestationModule",
    "create_contestation_module",
]


class ContestationModule:
    """
    Módulo de contestação - configuração e status.

    Fornece acesso unificado aos serviços de contestação.
    """

    def __init__(self) -> None:
        """Inicializa o módulo de contestação."""
        self.version = __version__
        self.enabled = False  # Será controlado por feature flag
        self._service: ContestationService | None = None
        self._acordao_service: AcordaoService | None = None
        self._appeal_service: AppealService | None = None

    def get_version(self) -> str:
        """Retorna a versão do módulo."""
        return self.version

    def is_enabled(self) -> bool:
        """Verifica se o módulo está habilitado."""
        return self.enabled

    def enable(self) -> None:
        """Habilita o módulo."""
        self.enabled = True

    def disable(self) -> None:
        """Desabilita o módulo."""
        self.enabled = False

    @property
    def service(self) -> ContestationService:
        """Retorna o serviço de contestação."""
        if self._service is None:
            self._service = get_contestation_service()
        return self._service

    @property
    def acordao_service(self) -> AcordaoService:
        """Retorna o serviço de acordãos."""
        if self._acordao_service is None:
            self._acordao_service = get_acordao_service()
        return self._acordao_service

    @property
    def appeal_service(self) -> AppealService:
        """Retorna o serviço de recursos."""
        if self._appeal_service is None:
            self._appeal_service = get_appeal_service()
        return self._appeal_service


# Factory function
def create_contestation_module() -> ContestationModule:
    """
    Cria uma instância do módulo de contestação.

    Returns:
        ContestationModule configurado
    """
    return ContestationModule()
