from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class RuntimeReasoningState(Enum):
    """
    Represents the immutable Runtime Reasoning lifecycle.
    Lifecycle categorization only. No behavior.
    """
    INITIALIZED = "INITIALIZED"
    GATHERING = "GATHERING"
    ANALYZING = "ANALYZING"
    SYNTHESIZED = "SYNTHESIZED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RuntimeReasoningType(Enum):
    """
    Represents immutable Runtime Reasoning categories.
    Categorization only. No reasoning engine. No execution.
    """
    DIAGNOSTIC = "DIAGNOSTIC"
    CAUSAL = "CAUSAL"
    CONTEXTUAL = "CONTEXTUAL"
    HEURISTIC = "HEURISTIC"
    VALIDATION = "VALIDATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeReasoningReason:
    """
    Represents immutable Runtime Reasoning metadata.
    Metadata only. No reasoning graph. No execution logic.
    """
    reasoning_type: RuntimeReasoningType
    reason_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeReasoning:
    """
    Canonical immutable Runtime Reasoning artifact.
    References only immutable upstream identifiers.
    Must NEVER contain RuntimeObservation, RuntimeSnapshot, RuntimeDecision,
    RuntimeExecutionInfo, RuntimeRetryInfo, RuntimeSchedulingInfo,
    RuntimeConfidence, RuntimeRecommendation, RuntimeMetrics, ProviderHealth,
    ProviderFailover, hardware metrics, or execution metrics.
    """
    reasoning_id: str
    decision_id: str
    observation_id: str
    reasoning_type: RuntimeReasoningType
    reasoning_state: RuntimeReasoningState
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeReasoningInfo:
    """
    Canonical immutable Runtime Reasoning metadata.
    Contains identifiers only. Never embed RuntimeDecision, RuntimeObservation,
    or RuntimeReasoning artifacts. Future Runtime Intelligence components
    resolve relationships.
    """
    reasoning_id: str
    decision_id: str
    observation_id: str
    reasoning_state: RuntimeReasoningState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeReasoningResult:
    """
    Immutable transport artifact returned by future Runtime Reasoning operations.
    It is NOT RuntimeReasoning itself.
    Must NEVER contain RuntimeConfidence, RuntimeRecommendation, RuntimeMetrics,
    ProviderHealth, ProviderFailover, execution metadata, etc.
    """
    reasoning_info: RuntimeReasoningInfo
    reasoning_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
