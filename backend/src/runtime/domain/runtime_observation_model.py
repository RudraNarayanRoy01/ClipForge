from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


class RuntimeObservationState(Enum):
    """
    Lifecycle categorization of a Runtime Observation.
    Categorization only. No behavioral meaning.
    """
    INITIALIZED = "INITIALIZED"
    COLLECTING = "COLLECTING"
    CAPTURED = "CAPTURED"
    VALIDATED = "VALIDATED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


class RuntimeObservationType(Enum):
    """
    Categorizes the Runtime Observation.
    Categorization only. No reasoning, no execution.
    """
    EXECUTION = "EXECUTION"
    RESOURCE = "RESOURCE"
    MODEL = "MODEL"
    PROVIDER = "PROVIDER"
    RUNTIME = "RUNTIME"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeObservationReason:
    """
    Immutable metadata detailing an observation reason.
    Contains metadata only. No explanation engine, no reasoning tree, no behavior.
    """
    observation_type: RuntimeObservationType
    reason_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RuntimeSignal(Enum):
    """
    Runtime observation vocabulary.
    Vocabulary only.
    """
    READY = "READY"
    BUSY = "BUSY"
    IDLE = "IDLE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeSnapshot:
    """
    Canonical immutable Runtime snapshot.
    Metadata only. Must never contain ProviderInfo, ProviderCapability, ModelInfo, 
    RuntimeExecutionInfo, RuntimeRetryInfo, RuntimeScheduleInfo, RuntimeDecision, 
    RuntimeReasoning, RuntimeConfidence, RuntimeRecommendation, Execution statistics, 
    GPU metrics, CPU metrics, Latency, Duration.
    References only primitive identifier: provider_id.
    """
    snapshot_id: str
    provider_id: str
    observation_type: RuntimeObservationType
    observation_state: RuntimeObservationState
    captured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeObservationInfo:
    """
    Canonical immutable Runtime Observation metadata.
    References only immutable identifiers. 
    It must never directly embed RuntimeSnapshot, RuntimeExecutionInfo, RuntimeRetryInfo, 
    RuntimeScheduleInfo, RuntimeDecisionResult, RuntimeReasoning, RuntimeConfidence, 
    RuntimeRecommendation. Identifiers only.
    """
    observation_id: str
    snapshot_id: str
    provider_id: str
    signal: RuntimeSignal
    observation_state: RuntimeObservationState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeObservationResult:
    """
    Immutable transport artifact returned by future Runtime Observation components.
    This is NOT a Runtime Decision, Runtime Recommendation, or Runtime Reasoning.
    Must never contain reasoning, confidence, recommendations, execution metadata, 
    retry metadata, scheduling metadata, provider health, decision metadata, GPU metrics, 
    CPU metrics, Latency, Duration.
    """
    observation_info: RuntimeObservationInfo
    observation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
