from __future__ import annotations

from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class CaseClaimSchema(BaseModel):
    claim_id: str
    description: str
    truth_state: Optional[str] = None
    debunk_target_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class CaseResponse(BaseModel):
    case_id: str
    title: str
    summary: str
    theme: str
    tags: List[str]
    claims: List[CaseClaimSchema]
    timeline: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)
    debunk_summary: Dict = Field(default_factory=dict)


class CaseCollectionResponse(BaseModel):
    collection_id: str
    title: str
    description: str
    tags: List[str]
    case_ids: List[str]
