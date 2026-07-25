import dataclasses
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime


class RuntimeIntelligenceContextState(Enum):
    """
    Represents the immutable lifecycle state of a Runtime Intelligence Context.
    
    Lifecycle only. No behavior.
    """
    INITIALIZED = "INITIALIZED"
    COMPOSED = "COMPOSED"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


@dataclasses.dataclass(frozen=True)
class RuntimeIntelligenceSnapshot:
    """
    Represents the canonical immutable Runtime Intelligence snapshot.
    
    Contains only immutable identifiers. Never embeds Runtime domain objects.
    Ownership remains strictly with the upstream subsystems.
    """
    snapshot_id: UUID
    observation_id: Optional[UUID]
    decision_id: Optional[UUID]
    reasoning_id: Optional[UUID]
    confidence_id: Optional[UUID]
    recommendation_ids: Tuple[UUID, ...]
    decision_coordinator_id: Optional[UUID]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclasses.dataclass(frozen=True)
class RuntimeIntelligenceSummary:
    """
    Represents immutable Runtime Intelligence metadata and aggregated descriptions.
    
    Summary only. No behavior.
    """
    summary_id: UUID
    observation_summary: Optional[str]
    decision_summary: Optional[str]
    reasoning_summary: Optional[str]
    confidence_summary: Optional[str]
    recommendation_summary: Optional[str]
    coordination_summary: Optional[str]
    metadata: Dict[str, Any]


@dataclasses.dataclass(frozen=True)
class RuntimeIntelligenceContext:
    """
    Canonical immutable Runtime Intelligence artifact.
    
    Aggregation ONLY. Aggregation NEVER means ownership.
    Contains immutable references only. Never embeds Runtime domain objects.
    """
    context_id: UUID
    state: RuntimeIntelligenceContextState
    snapshot_id: UUID
    summary_id: UUID
    created_at: datetime
    metadata: Dict[str, Any]


@dataclasses.dataclass(frozen=True)
class RuntimeIntelligenceContextInfo:
    """
    Immutable metadata for Runtime Intelligence Context.
    """
    context_id: UUID
    state: RuntimeIntelligenceContextState
    timestamps: Dict[str, datetime]
    metadata: Dict[str, Any]


@dataclasses.dataclass(frozen=True)
class RuntimeIntelligenceContextResult:
    """
    Immutable transport artifact containing the Runtime Intelligence Context state.
    """
    info: RuntimeIntelligenceContextInfo
    snapshot: RuntimeIntelligenceSnapshot
    summary: RuntimeIntelligenceSummary
