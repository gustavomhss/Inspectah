from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.ingestion.models import IngestionMode, IngestionStatus, IngestionTrigger


class ManualRunRequest(BaseModel):
    trigger_origin: str = "manual_ui"
    force: bool = False


class ToggleModeRequest(BaseModel):
    mode: IngestionMode
    enabled: bool = True


class RunSummary(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    source_id: str
    status: IngestionStatus
    trigger: IngestionTrigger
    started_at: datetime
    finished_at: Optional[datetime] = None
    items_processed: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class RunDetail(RunSummary):
    payload_ref: Optional[str] = None


class RunsResponse(BaseModel):
    runs: List[RunSummary]
    pagination: dict = Field(default_factory=dict)


class ConfigResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    source_id: str
    enabled: bool
    mode: IngestionMode
    interval_minutes: int
    max_attempts: int
    timeout_seconds: int
    last_run_id: Optional[str] = None
    updated_at: datetime


class TriggerRunResponse(BaseModel):
    run_id: str
    status: IngestionStatus
    trigger: IngestionTrigger


class ErrorResponse(BaseModel):
    error: str
    detail: str
    trace_id: Optional[str] = None
