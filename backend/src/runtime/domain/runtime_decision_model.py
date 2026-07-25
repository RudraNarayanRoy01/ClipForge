from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class RuntimeDecisionState(Enum):
    """
    Lifecycle categorization of a Runtime Decision.
    Categorization only. No behavioral meaning, no evaluation logic.
    """
    INITIALIZED = "INITIALIZED"
    EVALUATING = "EVALUATING"
    SELECTED = "SELECTED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RuntimeDecisionType(Enum):
    """
    Categorizes the Runtime Decision.
    Categorization only. No reasoning, no execution, no coordination logic.
    """
    EXECUTE = "EXECUTE"
    RETRY = "RETRY"
    WAIT = "WAIT"
    FAILOVER = "FAILOVER"
    CANCEL = "CANCEL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeDecisionReason:
    """
    Immutable metadata detailing a decision reason.
    Contains metadata only. Must NEVER contain explanations, reasoning graphs,
    or justification logic.
    """
    decision_type: RuntimeDecisionType
    reason_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeDecision:
    """
    The canonical immutable representation of a Runtime Decision artifact.
    It does NOT define how a decision is produced, evaluated, reasoned about, or orchestrated.
    Must NEVER contain RuntimeObservation, RuntimeSnapshot, RuntimeExecutionInfo,
    RuntimeRetryInfo, RuntimeScheduleInfo, RuntimeReasoning, RuntimeConfidence,
    RuntimeRecommendation, ProviderHealth, ProviderFailover, or hardware/execution metrics.
    """
    decision_id: str
    observation_id: str
    decision_type: RuntimeDecisionType
    decision_state: RuntimeDecisionState
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeDecisionInfo:
    """
    Canonical immutable Runtime Decision metadata.
    References ONLY immutable identifiers.
    Must NEVER embed RuntimeDecision, RuntimeObservation, RuntimeSnapshot,
    RuntimeExecutionInfo, RuntimeRetryInfo, RuntimeScheduleInfo, RuntimeReasoning,
    RuntimeConfidence, or RuntimeRecommendation.
    """
    decision_id: str
    observation_id: str
    decision_state: RuntimeDecisionState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeDecisionResult:
    """
    Immutable transport artifact returned by future Runtime Decision operations.
    It is NOT the Runtime Decision itself.
    Must NEVER contain RuntimeReasoning, RuntimeConfidence, RuntimeRecommendation,
    RuntimeExecutionInfo, RuntimeRetryInfo, RuntimeScheduleInfo, ProviderHealth,
    ProviderFailover, or Runtime Metrics.
    """
    decision_info: RuntimeDecisionInfo
    decision_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
