"""
Guardian API Schemas.

This module defines Pydantic schemas for the Guardian system API,
including request/response models for orchestration, committee details,
voting, and threshold configuration.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class ThresholdConfigSchema(BaseModel):
    """
    Threshold configuration for committee decisions.

    Defines the voting thresholds required for different risk levels
    and decision outcomes.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "risk_level": "HIGH",
                "min_agents": 5,
                "consensus_threshold": 0.8,
                "veto_threshold": 0.2
            }
        }
    )

    risk_level: str = Field(
        ...,
        description="Risk level: LOW, MEDIUM, or HIGH"
    )
    min_agents: int = Field(
        ...,
        description="Minimum number of agents required",
        ge=1
    )
    consensus_threshold: float = Field(
        ...,
        description="Threshold for consensus (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    veto_threshold: Optional[float] = Field(
        None,
        description="Threshold for veto (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class VoteResponse(BaseModel):
    """
    Individual agent vote response.

    Represents a single vote from an agent in the committee,
    including the decision, confidence, and reasoning.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "agent_id": "fact_checker_01",
                "vote": "APPROVE",
                "confidence": 0.85,
                "reasoning": "Evidence strongly supports the claim",
                "processing_time_ms": 1250
            }
        }
    )

    agent_id: str = Field(
        ...,
        description="Unique identifier for the agent"
    )
    vote: str = Field(
        ...,
        description="Vote outcome: APPROVE, REJECT, or ABSTAIN"
    )
    confidence: float = Field(
        ...,
        description="Confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        ...,
        description="Explanation for the vote decision"
    )
    processing_time_ms: int = Field(
        ...,
        description="Time taken to process this vote in milliseconds",
        ge=0
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the vote"
    )


class CommitteeDetails(BaseModel):
    """
    Details about the committee that made the decision.

    Contains information about the committee composition,
    voting statistics, and configuration.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "committee_id": "committee_20250101_abc123",
                "agent_ids": ["fact_checker_01", "bias_detector_02", "source_validator_03"],
                "total_agents": 3,
                "votes_approve": 2,
                "votes_reject": 1,
                "votes_abstain": 0,
                "formed_at": "2025-12-19T10:30:00Z"
            }
        }
    )

    committee_id: str = Field(
        ...,
        description="Unique identifier for this committee instance"
    )
    agent_ids: List[str] = Field(
        ...,
        description="List of agent IDs in the committee"
    )
    total_agents: int = Field(
        ...,
        description="Total number of agents in committee",
        ge=1
    )
    votes_approve: int = Field(
        ...,
        description="Number of approve votes",
        ge=0
    )
    votes_reject: int = Field(
        ...,
        description="Number of reject votes",
        ge=0
    )
    votes_abstain: int = Field(
        ...,
        description="Number of abstain votes",
        ge=0
    )
    formed_at: datetime = Field(
        ...,
        description="Timestamp when committee was formed"
    )
    dissolved_at: Optional[datetime] = Field(
        None,
        description="Timestamp when committee was dissolved"
    )


class OrchestrateRequest(BaseModel):
    """
    Request to orchestrate a Guardian decision.

    Contains all necessary information to initiate a committee
    decision-making process for a claim.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "claim_id": "claim_abc123",
                "domain": "politics",
                "risk_level": "HIGH",
                "context": {
                    "source_url": "https://example.com/article",
                    "claim_text": "The policy was enacted in 2024",
                    "additional_info": "Election context"
                }
            }
        }
    )

    claim_id: str = Field(
        ...,
        description="Unique identifier for the claim to evaluate"
    )
    domain: str = Field(
        ...,
        description="Domain of the claim (e.g., politics, health, science)"
    )
    risk_level: str = Field(
        ...,
        description="Risk level: LOW, MEDIUM, or HIGH"
    )
    context: Dict[str, Any] = Field(
        ...,
        description="Additional context for the claim evaluation"
    )
    priority: Optional[int] = Field(
        None,
        description="Priority level for processing (higher = more urgent)",
        ge=0,
        le=10
    )
    timeout_ms: Optional[int] = Field(
        None,
        description="Maximum time allowed for orchestration in milliseconds",
        ge=1000
    )


class OrchestrateResponse(BaseModel):
    """
    Response from Guardian orchestration.

    Contains the complete result of the committee decision process,
    including outcome, votes, and performance metrics.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "decision_id": "decision_20250101_xyz789",
                "claim_id": "claim_abc123",
                "outcome": "APPROVED",
                "committee": {
                    "committee_id": "committee_20250101_abc123",
                    "agent_ids": ["fact_checker_01", "bias_detector_02"],
                    "total_agents": 2,
                    "votes_approve": 2,
                    "votes_reject": 0,
                    "votes_abstain": 0,
                    "formed_at": "2025-12-19T10:30:00Z"
                },
                "votes": [],
                "threshold_used": {
                    "risk_level": "HIGH",
                    "min_agents": 2,
                    "consensus_threshold": 0.8,
                    "veto_threshold": 0.2
                },
                "processing_time_ms": 3500,
                "completed_at": "2025-12-19T10:30:03Z"
            }
        }
    )

    decision_id: str = Field(
        ...,
        description="Unique identifier for this decision"
    )
    claim_id: str = Field(
        ...,
        description="Claim ID that was evaluated"
    )
    outcome: str = Field(
        ...,
        description="Final decision outcome: APPROVED, REJECTED, or INCONCLUSIVE"
    )
    committee: CommitteeDetails = Field(
        ...,
        description="Details about the committee that made the decision"
    )
    votes: List[VoteResponse] = Field(
        ...,
        description="Individual votes from committee members"
    )
    threshold_used: ThresholdConfigSchema = Field(
        ...,
        description="Threshold configuration used for this decision"
    )
    processing_time_ms: int = Field(
        ...,
        description="Total time taken for orchestration in milliseconds",
        ge=0
    )
    completed_at: datetime = Field(
        ...,
        description="Timestamp when decision was completed"
    )
    confidence_score: Optional[float] = Field(
        None,
        description="Overall confidence in the decision (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for the decision"
    )
