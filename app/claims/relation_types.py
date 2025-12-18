"""
S38-BE-020: Tipos de Relacoes entre Claims

Define os tipos de relacoes semanticas entre claims.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RelationType(str, Enum):
    """Tipos de relacao entre claims."""
    SUPPORTS = "supports"       # Claim A apoia claim B
    CONTRADICTS = "contradicts"  # Claim A contradiz claim B
    RELATED = "related"         # Claims relacionados mas nao diretamente
    DUPLICATE = "duplicate"     # Claims duplicados ou muito similares
    REFINES = "refines"         # Claim A refina/especifica claim B
    GENERALIZES = "generalizes"  # Claim A generaliza claim B


class InferenceMethod(str, Enum):
    """Metodo usado para inferir a relacao."""
    MANUAL = "manual"           # Anotacao manual
    EMBEDDING = "embedding"     # Similaridade por embedding
    LLM = "llm"                 # Classificacao por LLM
    RULE = "rule"               # Regra heuristica
    ENTITY = "entity"           # Match de entidades


@dataclass
class ClassificationResult:
    """Resultado da classificacao de relacao."""
    relation_type: RelationType
    confidence: float  # 0.0 a 1.0
    method: InferenceMethod
    indicators: Dict[str, Any] = field(default_factory=dict)

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        return self.confidence >= threshold


@dataclass
class RelationConfig:
    """Configuracao para inferencia de relacoes."""
    similarity_threshold: float = 0.7  # Minimo para considerar relacionado
    contradiction_threshold: float = 0.6  # Minimo para considerar contradicao
    duplicate_threshold: float = 0.95  # Minimo para considerar duplicado
    support_threshold: float = 0.85  # Minimo para considerar suporte
    confidence_threshold: float = 0.7  # Minimo para aceitar relacao
    negation_boost: float = 1.2  # Boost para deteccao de negacao
    max_relations_per_claim: int = 10  # Limite de relacoes por claim


@dataclass
class ClaimRelation:
    """Relacao entre dois claims."""
    source_claim_id: str
    target_claim_id: str
    relation_type: RelationType
    confidence: float
    method: InferenceMethod
    bidirectional: bool = False
    indicators: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "system"

    def inverse(self) -> "ClaimRelation":
        """Retorna relacao inversa."""
        inverse_type = self._get_inverse_type()
        return ClaimRelation(
            source_claim_id=self.target_claim_id,
            target_claim_id=self.source_claim_id,
            relation_type=inverse_type,
            confidence=self.confidence,
            method=self.method,
            bidirectional=self.bidirectional,
            indicators=self.indicators,
            created_by=self.created_by,
        )

    def _get_inverse_type(self) -> RelationType:
        """Retorna tipo inverso da relacao."""
        inverses = {
            RelationType.SUPPORTS: RelationType.SUPPORTS,
            RelationType.CONTRADICTS: RelationType.CONTRADICTS,
            RelationType.RELATED: RelationType.RELATED,
            RelationType.DUPLICATE: RelationType.DUPLICATE,
            RelationType.REFINES: RelationType.GENERALIZES,
            RelationType.GENERALIZES: RelationType.REFINES,
        }
        return inverses.get(self.relation_type, self.relation_type)


@dataclass
class ClaimCluster:
    """Cluster de claims relacionados."""
    cluster_id: str
    representative_id: str  # Claim representativo do cluster
    member_ids: List[str]
    avg_similarity: float
    topic: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> int:
        return len(self.member_ids)


# Indicadores de contradicao (palavras/padroes)
NEGATION_INDICATORS = [
    "nao", "não", "nunca", "jamais", "nem", "nenhum", "nenhuma",
    "falso", "mentira", "incorreto", "errado", "contrario",
    "nega", "desmente", "refuta", "contesta",
]

# Indicadores de suporte
SUPPORT_INDICATORS = [
    "confirma", "corrobora", "comprova", "atesta", "valida",
    "reforça", "sustenta", "apoia", "endossa",
    "verdade", "correto", "preciso", "exato",
]

# Conectivos de refinamento
REFINEMENT_INDICATORS = [
    "especificamente", "em particular", "mais precisamente",
    "ou seja", "isto e", "na verdade", "de fato",
]


def detect_negation_indicators(text: str) -> List[str]:
    """Detecta indicadores de negacao no texto."""
    text_lower = text.lower()
    found = []
    for indicator in NEGATION_INDICATORS:
        if indicator in text_lower:
            found.append(indicator)
    return found


def detect_support_indicators(text: str) -> List[str]:
    """Detecta indicadores de suporte no texto."""
    text_lower = text.lower()
    found = []
    for indicator in SUPPORT_INDICATORS:
        if indicator in text_lower:
            found.append(indicator)
    return found
