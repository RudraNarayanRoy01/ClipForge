import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Tuple

from src.domain.campaign_entities import Campaign
from src.reasoning.recommendation.models import Recommendation
from src.domain.entities import VideoAsset, TimelineContext
from src.transcription.dtos import Transcript


class ExecutionStatus(Enum):
    """
    Immutable enumeration representing the execution plan's lifecycle state.
    """
    DRAFT = auto()
    VALIDATED = auto()
    APPROVED = auto()
    REJECTED = auto()


@dataclass(frozen=True)
class ExecutionRequest:
    """
    Represents an application request to begin execution planning.
    Contains identifiers only. Does not include business state.
    """
    request_id: uuid.UUID
    campaign_id: uuid.UUID
    recommendation_id: uuid.UUID
    media_asset_id: uuid.UUID


@dataclass(frozen=True)
class ExecutionInput:
    """
    Represents the immutable planning context.
    Contains references to the upstream domain models required to produce an execution plan.
    Does not duplicate upstream domain state or calculate derived values.
    """
    campaign: Campaign
    recommendation: Recommendation
    media_asset: VideoAsset
    transcript: Transcript
    timeline_intelligence: TimelineContext


@dataclass(frozen=True)
class ExecutionSegment:
    """
    Represents a candidate piece of source content.
    It describes content, not editing. Must not contain renderer operations.
    """
    source_asset_id: uuid.UUID
    start_time: float
    end_time: float
    purpose: str
    tags: Tuple[str, ...]
    reasoning: str


@dataclass(frozen=True)
class ExecutionStrategy:
    """
    Represents high-level editing intent.
    Must remain abstract and must never contain renderer-specific operations.
    """
    hook_style: str
    pacing: str
    narrative_flow: str
    subtitle_style: str
    cta_style: str
    aspect_ratio_preference: str


@dataclass(frozen=True)
class ExecutionValidation:
    """
    Represents the result of execution plan validation.
    No validation logic or business decisions here.
    """
    is_valid: bool
    warnings: Tuple[str, ...]
    issues: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Represents immutable planning metadata.
    """
    planner_version: str
    plan_version: str
    generated_by: str
    generated_at: datetime


@dataclass(frozen=True)
class ExecutionPlan:
    """
    ExecutionPlan is the Aggregate Root.
    It aggregates the intent of what should be produced without specifying how.
    Must remain immutable. No construction logic inside the model.
    """
    plan_id: uuid.UUID
    execution_input: ExecutionInput
    execution_strategy: ExecutionStrategy
    validation: ExecutionValidation
    segments: Tuple[ExecutionSegment, ...]
    metadata: ExecutionMetadata
    status: ExecutionStatus
