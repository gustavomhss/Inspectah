from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


def utcnow() -> datetime:
    return datetime.utcnow()


class FlowState(str, Enum):
    DRAFT = "draft"
    EM_TESTE = "em_teste"
    ATIVO = "ativo"
    PAUSADO = "pausado"
    DEPRECADO = "deprecado"


class FlowStepType(str, Enum):
    INTERPRETE = "interprete"
    CLASSIFICADOR = "classificador"
    ANALISTA = "analista"
    DEBUNKER = "debunker"
    DECISION_MAKER = "decision_maker"


class FlowExecutionStatus(str, Enum):
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    FALHOU = "falhou"
    CANCELADO = "cancelado"


class FlowStepExecutionStatus(str, Enum):
    PENDENTE = "pendente"
    OK = "ok"
    ERRO = "erro"
    SKIPPED = "skipped"


@dataclass
class FlowTemplate:
    id: str
    slug: str
    versao: str
    tipo_entrada: str
    estrutura: Dict
    ativo: bool = True
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class Flow:
    id: str
    nome: str
    slug: str
    tipo_entrada: str
    estado: FlowState
    domain: str = "generic"
    flow_version_id: Optional[str] = None
    active_version_id: Optional[str] = None
    test_version_id: Optional[str] = None
    flow_ops_profile_id: Optional[str] = None
    template_origem_id: Optional[str] = None
    percentual_teste: int = 0
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class FlowStep:
    id: str
    flow_id: str
    ordem: int
    tipo_etapa: FlowStepType
    agent_role: str
    agent_binding: Optional[str] = None
    config: Dict = field(default_factory=dict)
    flags: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class FlowExecution:
    id: str
    flow_id: str
    flow_version_id: Optional[str]
    operation_id: Optional[str]
    item_id: str
    tipo_entrada: str
    status: FlowExecutionStatus
    started_at: datetime = field(default_factory=utcnow)
    finished_at: Optional[datetime] = None
    erro_resumo: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class FlowStepExecution:
    id: str
    flow_execution_id: str
    step_id: str
    status: FlowStepExecutionStatus
    started_at: datetime = field(default_factory=utcnow)
    finished_at: Optional[datetime] = None
    output_resumo: Optional[str] = None
    erro_resumo: Optional[str] = None
    raw_ref: Optional[str] = None


@dataclass
class FlowOperationLog:
    id: str
    flow_id: str
    operacao: str
    payload: Dict = field(default_factory=dict)
    resultado: str = "ok"
    flow_version_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class FlowVersion:
    id: str
    flow_id: str
    version_id: str
    template_slug: str
    estado: str
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
