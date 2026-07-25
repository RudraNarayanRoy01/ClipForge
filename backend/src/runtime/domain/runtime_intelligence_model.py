from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


class RuntimeIntelligenceState(Enum):
    """
    Categorizes the lifecycle of runtime intelligence.
    Categorization only. No behavioral meaning.
    """
    INITIALIZED = "INITIALIZED"
    READY = "READY"
    EVALUATING = "EVALUATING"
    DECIDED = "DECIDED"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"


class RuntimeDecisionType(Enum):
    """
    Categorizes the decisions. 
    Represents categories, not outcomes, reasoning, or execution.
    """
    EXECUTE = "EXECUTE"
    WAIT = "WAIT"
    RETRY = "RETRY"
    FAILOVER = "FAILOVER"
    ABORT = "ABORT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeDecisionReason:
    """
    Immutable metadata detailing a decision reason.
    Contains metadata only. Must NEVER contain reasoning chains, decision trees, 
    confidence, recommendations, observations, provider health, or execution state.
    """
    decision_type: RuntimeDecisionType
    reason_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Central immutable Runtime Intelligence policy.
# Belongs strictly to the Runtime Intelligence Domain.
# Defines mapping from RuntimeDecisionType -> RuntimeIntelligenceState
RUNTIME_INTELLIGENCE_POLICY: Dict[RuntimeDecisionType, RuntimeIntelligenceState] = {
    RuntimeDecisionType.EXECUTE: RuntimeIntelligenceState.DECIDED,
    RuntimeDecisionType.WAIT: RuntimeIntelligenceState.READY,
    RuntimeDecisionType.RETRY: RuntimeIntelligenceState.EVALUATING,
    RuntimeDecisionType.FAILOVER: RuntimeIntelligenceState.EVALUATING,
    RuntimeDecisionType.ABORT: RuntimeIntelligenceState.FAILED,
    RuntimeDecisionType.UNKNOWN: RuntimeIntelligenceState.FAILED,
}


@dataclass(frozen=True)
class RuntimeIntelligenceInfo:
    """
    Canonical immutable Runtime Intelligence metadata.
    References ONLY immutable provider_id values.
    Must NEVER contain ProviderInfo, ProviderCapability, ModelInfo, 
    RuntimeRetryInfo, RuntimeScheduleInfo, RuntimeExecutionInfo, 
    RuntimeObservation, RuntimeConfidence, RuntimeRecommendation, 
    or RuntimeReasoning.
    """
    decision_id: str
    provider_id: str
    decision_type: RuntimeDecisionType
    intelligence_state: RuntimeIntelligenceState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeDecisionResult:
    """
    Immutable transport artifact returned by Runtime Intelligence operations.
    It is NOT the Runtime Decision itself. It contains no mutable state or behavior.
    Must NEVER contain reasoning chains, confidence scores, recommendations, observations, 
    provider health, execution metadata, scheduling metadata, retry metadata, 
    hardware metrics, execution statistics, GPU information, or CPU information.
    """
    intelligence_info: RuntimeIntelligenceInfo
    decision_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
