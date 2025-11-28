from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from app.sources.models import SourceState


class IngestionMode(str, Enum):
    MANUAL_ONLY = "MANUAL_ONLY"
    AUTOMATIC = "AUTOMATIC"


class IngestionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAIL = "FAIL"


class IngestionTrigger(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"
    REPROCESS = "REPROCESS"


MIN_INTERVAL = 15
MAX_INTERVAL = 10080  # 7 dias
MIN_TIMEOUT = 5


@dataclass
class IngestionConfig:
    id: str
    source_id: str
    enabled: bool
    mode: IngestionMode
    interval_minutes: int
    max_attempts: int
    timeout_seconds: int
    last_run_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    @classmethod
    def create(
        cls,
        *,
        id: str,
        source_id: str,
        source_state: SourceState,
        enabled: bool,
        mode: IngestionMode,
        interval_minutes: int,
        max_attempts: int,
        timeout_seconds: int,
        created_by: str,
        updated_by: Optional[str] = None,
        last_run_id: Optional[str] = None,
    ) -> "IngestionConfig":
        _validate_config_params(
            source_state=source_state,
            enabled=enabled,
            mode=mode,
            interval_minutes=interval_minutes,
            max_attempts=max_attempts,
            timeout_seconds=timeout_seconds,
        )
        now = datetime.utcnow()
        return cls(
            id=id,
            source_id=source_id,
            enabled=enabled,
            mode=mode,
            interval_minutes=interval_minutes,
            max_attempts=max_attempts,
            timeout_seconds=timeout_seconds,
            last_run_id=last_run_id,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=updated_by or created_by,
        )


@dataclass
class IngestionRun:
    id: str
    config_id: str
    source_id: str
    trigger: IngestionTrigger
    status: IngestionStatus
    started_at: datetime
    finished_at: Optional[datetime]
    items_processed: int
    error_code: Optional[str]
    error_message: Optional[str]
    payload_ref: Optional[str]
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        *,
        id: str,
        config: IngestionConfig,
        trigger: IngestionTrigger,
        status: IngestionStatus = IngestionStatus.PENDING,
        started_at: Optional[datetime] = None,
        items_processed: int = 0,
        payload_ref: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "IngestionRun":
        if status not in {IngestionStatus.PENDING, IngestionStatus.RUNNING}:
            raise ValueError("Run inicial deve nascer em PENDING ou RUNNING (INV-4).")
        run = cls(
            id=id,
            config_id=config.id,
            source_id=config.source_id,
            trigger=trigger,
            status=status,
            started_at=started_at or datetime.utcnow(),
            finished_at=None,
            items_processed=items_processed,
            error_code=None,
            error_message=None,
            payload_ref=payload_ref,
            meta=meta or {},
        )
        validate_run_invariants(run, config)
        return run


def _validate_config_params(
    *,
    source_state: SourceState,
    enabled: bool,
    mode: IngestionMode,
    interval_minutes: int,
    max_attempts: int,
    timeout_seconds: int,
) -> None:
    if interval_minutes < MIN_INTERVAL or interval_minutes > MAX_INTERVAL:
        raise ValueError("interval_minutes fora do intervalo permitido (INV-3).")
    if timeout_seconds < MIN_TIMEOUT:
        raise ValueError("timeout_seconds deve ser >= 5 (INV-3).")
    if max_attempts < 1:
        raise ValueError("max_attempts deve ser >= 1 (INV-3).")
    if mode == IngestionMode.AUTOMATIC and source_state not in {SourceState.ACTIVE, SourceState.TESTING}:
        raise ValueError("Fonte não suporta modo AUTOMATIC no estado atual (INV-2).")
    if not enabled and mode == IngestionMode.AUTOMATIC:
        # Mesmo fonte ativa, config desabilitada deve ser tratada explicitamente
        return


def validate_run_invariants(run: IngestionRun, config: IngestionConfig, running_count_for_source: int = 0) -> None:
    if run.source_id != config.source_id:
        raise ValueError("Run deve apontar para mesma fonte da config (INV-11).")
    if running_count_for_source > 0 and run.status == IngestionStatus.RUNNING:
        raise ValueError("Já existe run RUNNING para a fonte (INV-6).")
    if run.status in {IngestionStatus.SUCCESS, IngestionStatus.PARTIAL_SUCCESS, IngestionStatus.FAIL} and run.finished_at is None:
        raise ValueError("Runs finalizados exigem finished_at (INV-5).")
    if run.status == IngestionStatus.RUNNING and run.started_at is None:
        raise ValueError("Run RUNNING exige started_at (INV-7).")
    if run.finished_at and run.finished_at <= run.started_at:
        raise ValueError("finished_at deve ser maior que started_at (INV-8).")
    if run.status in {IngestionStatus.SUCCESS, IngestionStatus.PARTIAL_SUCCESS} and not run.payload_ref:
        raise ValueError("Runs de sucesso precisam de payload_ref (INV-9).")
    if run.status in {IngestionStatus.FAIL, IngestionStatus.PARTIAL_SUCCESS} and not (run.error_code or run.error_message):
        raise ValueError("Runs com erro precisam de código/mensagem (INV-10).")
    if run.status == IngestionStatus.PENDING and run.finished_at is not None:
        raise ValueError("Run PENDING não pode ter finished_at preenchido.")
