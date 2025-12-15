"""
S38-BE-040: Policy Version Service

Servico de versionamento de politicas com audit trail.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from app.policies.models import PolicyDecision, PromotionPolicyConfig

logger = logging.getLogger(__name__)


class PolicyStatus(str, Enum):
    """Status de uma versao de policy."""
    DRAFT = "draft"           # Em elaboracao
    PENDING_REVIEW = "pending_review"  # Aguardando revisao
    APPROVED = "approved"     # Aprovada
    ACTIVE = "active"         # Em producao
    DEPRECATED = "deprecated"  # Descontinuada
    ARCHIVED = "archived"     # Arquivada


class ChangeType(str, Enum):
    """Tipos de mudanca em policy."""
    CREATE = "create"
    UPDATE = "update"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    DEPRECATE = "deprecate"
    ARCHIVE = "archive"
    ROLLBACK = "rollback"


@dataclass
class PolicyVersion:
    """Uma versao especifica de uma policy."""
    version_id: str
    policy_id: str
    version_number: int
    config: PromotionPolicyConfig
    status: PolicyStatus
    created_at: datetime
    created_by: str
    content_hash: str
    parent_version_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    changelog: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "policy_id": self.policy_id,
            "version_number": self.version_number,
            "config": asdict(self.config),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "content_hash": self.content_hash,
            "parent_version_id": self.parent_version_id,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "deactivated_at": self.deactivated_at.isoformat() if self.deactivated_at else None,
            "changelog": self.changelog,
        }


@dataclass
class PolicyAuditEntry:
    """Entrada de audit log para mudancas em policy."""
    audit_id: str
    policy_id: str
    version_id: str
    change_type: ChangeType
    changed_at: datetime
    changed_by: str
    old_status: Optional[PolicyStatus] = None
    new_status: Optional[PolicyStatus] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "policy_id": self.policy_id,
            "version_id": self.version_id,
            "change_type": self.change_type.value,
            "changed_at": self.changed_at.isoformat(),
            "changed_by": self.changed_by,
            "old_status": self.old_status.value if self.old_status else None,
            "new_status": self.new_status.value if self.new_status else None,
            "details": self.details,
        }


@dataclass
class PolicyComparison:
    """Resultado de comparacao entre versoes."""
    version_a: str
    version_b: str
    differences: List[Dict[str, Any]]
    summary: str


class PolicyVersionRepository:
    """Repositorio em memoria para versoes de policy."""

    def __init__(self):
        self._versions: Dict[str, PolicyVersion] = {}
        self._audit_log: List[PolicyAuditEntry] = []
        self._active_by_domain: Dict[str, str] = {}  # domain -> version_id

    def save_version(self, version: PolicyVersion) -> None:
        self._versions[version.version_id] = version

    def get_version(self, version_id: str) -> Optional[PolicyVersion]:
        return self._versions.get(version_id)

    def get_versions_for_policy(self, policy_id: str) -> List[PolicyVersion]:
        return [v for v in self._versions.values() if v.policy_id == policy_id]

    def get_active_version(self, domain: str) -> Optional[PolicyVersion]:
        version_id = self._active_by_domain.get(domain)
        return self._versions.get(version_id) if version_id else None

    def set_active_version(self, domain: str, version_id: str) -> None:
        self._active_by_domain[domain] = version_id

    def add_audit_entry(self, entry: PolicyAuditEntry) -> None:
        self._audit_log.append(entry)

    def get_audit_log(
        self,
        policy_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[PolicyAuditEntry]:
        entries = self._audit_log
        if policy_id:
            entries = [e for e in entries if e.policy_id == policy_id]
        return entries[-limit:]


class PolicyVersionService:
    """
    Servico de versionamento de politicas.

    Gerencia ciclo de vida:
    - Criacao de versoes
    - Aprovacao
    - Ativacao/Desativacao
    - Rollback
    - Audit trail

    Uso:
        service = PolicyVersionService(repository)
        version = service.create_version(config, "user@example.com")
        service.approve(version.version_id, "admin@example.com")
        service.activate(version.version_id, "admin@example.com")
    """

    def __init__(
        self,
        repository: Optional[PolicyVersionRepository] = None,
        approval_required: bool = True,
    ):
        self.repository = repository or PolicyVersionRepository()
        self.approval_required = approval_required
        self._validators: List[Callable[[PromotionPolicyConfig], List[str]]] = []

    def register_validator(
        self,
        validator: Callable[[PromotionPolicyConfig], List[str]],
    ) -> None:
        """Registra validador customizado de policy."""
        self._validators.append(validator)

    def create_version(
        self,
        config: PromotionPolicyConfig,
        created_by: str,
        changelog: str = "",
        parent_version_id: Optional[str] = None,
    ) -> PolicyVersion:
        """
        Cria nova versao de policy.

        Returns:
            Nova versao em status DRAFT
        """
        # Validate config
        errors = self._validate_config(config)
        if errors:
            raise ValueError(f"Invalid policy config: {'; '.join(errors)}")

        # Determine version number
        policy_id = f"policy:{config.domain}:{config.name}"
        existing = self.repository.get_versions_for_policy(policy_id)
        version_number = max([v.version_number for v in existing], default=0) + 1

        # Create version
        version_id = f"pv_{uuid4().hex[:12]}"
        content_hash = self._compute_hash(config)

        version = PolicyVersion(
            version_id=version_id,
            policy_id=policy_id,
            version_number=version_number,
            config=config,
            status=PolicyStatus.DRAFT,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            created_by=created_by,
            content_hash=content_hash,
            parent_version_id=parent_version_id,
            changelog=changelog,
        )

        self.repository.save_version(version)
        self._log_change(version, ChangeType.CREATE, created_by)

        logger.info(f"Created policy version {version_id} for {policy_id}")
        return version

    def submit_for_review(
        self,
        version_id: str,
        submitted_by: str,
    ) -> PolicyVersion:
        """Submete versao para revisao."""
        version = self.repository.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != PolicyStatus.DRAFT:
            raise ValueError(f"Version must be in DRAFT status, got {version.status}")

        old_status = version.status
        version.status = PolicyStatus.PENDING_REVIEW
        self.repository.save_version(version)
        self._log_change(
            version, ChangeType.UPDATE, submitted_by,
            old_status=old_status, new_status=version.status,
        )

        return version

    def approve(
        self,
        version_id: str,
        approved_by: str,
        comments: str = "",
    ) -> PolicyVersion:
        """Aprova versao de policy."""
        version = self.repository.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if version.status != PolicyStatus.PENDING_REVIEW:
            raise ValueError(f"Version must be PENDING_REVIEW, got {version.status}")

        old_status = version.status
        version.status = PolicyStatus.APPROVED
        version.approved_at = datetime.now(timezone.utc).replace(tzinfo=None)
        version.approved_by = approved_by

        self.repository.save_version(version)
        self._log_change(
            version, ChangeType.UPDATE, approved_by,
            old_status=old_status, new_status=version.status,
            details={"comments": comments},
        )

        logger.info(f"Approved policy version {version_id}")
        return version

    def activate(
        self,
        version_id: str,
        activated_by: str,
    ) -> PolicyVersion:
        """
        Ativa versao de policy.

        Desativa automaticamente versao anterior do mesmo dominio.
        """
        version = self.repository.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        if self.approval_required and version.status != PolicyStatus.APPROVED:
            raise ValueError(f"Version must be APPROVED to activate, got {version.status}")

        # Deactivate current active version
        current_active = self.repository.get_active_version(version.config.domain)
        if current_active and current_active.version_id != version_id:
            self._deactivate(current_active, activated_by, "Superseded by new version")

        # Activate new version
        old_status = version.status
        version.status = PolicyStatus.ACTIVE
        version.activated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        self.repository.save_version(version)
        self.repository.set_active_version(version.config.domain, version_id)

        self._log_change(
            version, ChangeType.ACTIVATE, activated_by,
            old_status=old_status, new_status=version.status,
        )

        logger.info(f"Activated policy version {version_id} for domain {version.config.domain}")
        return version

    def deactivate(
        self,
        version_id: str,
        deactivated_by: str,
        reason: str = "",
    ) -> PolicyVersion:
        """Desativa versao de policy."""
        version = self.repository.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")

        return self._deactivate(version, deactivated_by, reason)

    def _deactivate(
        self,
        version: PolicyVersion,
        deactivated_by: str,
        reason: str,
    ) -> PolicyVersion:
        """Internal deactivation."""
        old_status = version.status
        version.status = PolicyStatus.DEPRECATED
        version.deactivated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        self.repository.save_version(version)
        self._log_change(
            version, ChangeType.DEACTIVATE, deactivated_by,
            old_status=old_status, new_status=version.status,
            details={"reason": reason},
        )

        return version

    def rollback(
        self,
        domain: str,
        target_version_id: str,
        rolled_back_by: str,
        reason: str,
    ) -> PolicyVersion:
        """
        Faz rollback para uma versao anterior.

        Cria uma nova versao baseada na versao alvo.
        """
        target = self.repository.get_version(target_version_id)
        if not target:
            raise ValueError(f"Target version {target_version_id} not found")

        if target.config.domain != domain:
            raise ValueError(f"Version {target_version_id} is not for domain {domain}")

        # Create new version based on target
        new_version = self.create_version(
            config=target.config,
            created_by=rolled_back_by,
            changelog=f"Rollback to v{target.version_number}: {reason}",
            parent_version_id=target_version_id,
        )

        # Fast-track approval for rollback if needed
        if self.approval_required:
            new_version.status = PolicyStatus.APPROVED
            new_version.approved_at = datetime.now(timezone.utc).replace(tzinfo=None)
            new_version.approved_by = rolled_back_by
            self.repository.save_version(new_version)

        # Activate
        activated = self.activate(new_version.version_id, rolled_back_by)

        self._log_change(
            activated, ChangeType.ROLLBACK, rolled_back_by,
            details={"target_version": target_version_id, "reason": reason},
        )

        return activated

    def get_active_policy(self, domain: str) -> Optional[PromotionPolicyConfig]:
        """Retorna policy ativa para um dominio."""
        version = self.repository.get_active_version(domain)
        return version.config if version else None

    def get_version_history(
        self,
        domain: str,
        name: Optional[str] = None,
    ) -> List[PolicyVersion]:
        """Retorna historico de versoes."""
        if name:
            policy_id = f"policy:{domain}:{name}"
        else:
            policy_id = f"policy:{domain}"

        versions = []
        for v in self.repository._versions.values():
            if v.policy_id.startswith(policy_id):
                versions.append(v)

        return sorted(versions, key=lambda v: v.version_number, reverse=True)

    def compare_versions(
        self,
        version_a_id: str,
        version_b_id: str,
    ) -> PolicyComparison:
        """Compara duas versoes de policy."""
        version_a = self.repository.get_version(version_a_id)
        version_b = self.repository.get_version(version_b_id)

        if not version_a or not version_b:
            raise ValueError("Both versions must exist")

        differences = []
        config_a = asdict(version_a.config)
        config_b = asdict(version_b.config)

        for key in set(config_a.keys()) | set(config_b.keys()):
            val_a = config_a.get(key)
            val_b = config_b.get(key)
            if val_a != val_b:
                differences.append({
                    "field": key,
                    "version_a": val_a,
                    "version_b": val_b,
                })

        summary = f"{len(differences)} differences found"
        return PolicyComparison(
            version_a=version_a_id,
            version_b=version_b_id,
            differences=differences,
            summary=summary,
        )

    def get_audit_log(
        self,
        policy_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[PolicyAuditEntry]:
        """Retorna audit log."""
        return self.repository.get_audit_log(policy_id, limit)

    def _validate_config(self, config: PromotionPolicyConfig) -> List[str]:
        """Valida configuracao de policy."""
        errors = []

        if not config.name:
            errors.append("Policy name is required")
        if not config.domain:
            errors.append("Policy domain is required")
        if config.min_confidence < 0 or config.min_confidence > 1:
            errors.append("min_confidence must be between 0 and 1")
        if config.min_sources < 0:
            errors.append("min_sources must be >= 0")

        # Run custom validators
        for validator in self._validators:
            errors.extend(validator(config))

        return errors

    def _compute_hash(self, config: PromotionPolicyConfig) -> str:
        """Computa hash do conteudo da policy."""
        content = json.dumps(asdict(config), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _log_change(
        self,
        version: PolicyVersion,
        change_type: ChangeType,
        changed_by: str,
        old_status: Optional[PolicyStatus] = None,
        new_status: Optional[PolicyStatus] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra mudanca no audit log."""
        entry = PolicyAuditEntry(
            audit_id=f"pa_{uuid4().hex[:12]}",
            policy_id=version.policy_id,
            version_id=version.version_id,
            change_type=change_type,
            changed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            changed_by=changed_by,
            old_status=old_status,
            new_status=new_status,
            details=details or {},
        )
        self.repository.add_audit_entry(entry)
