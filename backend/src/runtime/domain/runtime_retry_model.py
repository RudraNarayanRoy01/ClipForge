from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime


class RuntimeRetryState(str, Enum):
    """
    Immutable representation of Runtime Retry states.
    
    Categorization only.
    No behavior, no execution logic.
    """
    NOT_REQUIRED = "NOT_REQUIRED"
    ELIGIBLE = "ELIGIBLE"
    WAITING = "WAITING"
    EXHAUSTED = "EXHAUSTED"
    FAILED = "FAILED"


class RuntimeRetryTrigger(str, Enum):
    """
    Represents structural retry triggers mapped from upstream layers
    (such as Provider Failover states translating to triggers).
    
    Categorization only.
    No behavior, no execution logic.
    Must never reuse ProviderHealthState or ProviderFailoverState directly.
    """
    FAILOVER_AVAILABLE = "FAILOVER_AVAILABLE"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    MANUAL_RETRY = "MANUAL_RETRY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeRetryDecision:
    """
    Represents an immutable retry decision metadata.
    
    Contains structural metadata only.
    No execution behavior. No transition logic.
    """
    provider_id: str
    trigger: RuntimeRetryTrigger
    retry_attempt: int
    timestamp: datetime


@dataclass(frozen=True)
class RuntimeRetryInfo:
    """
    Canonical immutable Runtime Retry metadata.
    
    Contains only provider_id values and retry-specific structural metadata.
    MUST NOT contain ProviderInfo, ProviderCapability, ModelInfo, 
    LifecycleInfo, ProviderHealthInfo, or ProviderFailoverInfo.
    """
    provider_id: str
    current_state: RuntimeRetryState
    max_retry_attempts: int
    created_at: datetime
    updated_at: datetime
    previous_state: Optional[RuntimeRetryState] = None
    trigger: RuntimeRetryTrigger = RuntimeRetryTrigger.UNKNOWN
    retry_attempts: int = 0
    last_decision: Optional[RuntimeRetryDecision] = None
    reason: str = ""


@dataclass(frozen=True)
class RuntimeRetryResult:
    """
    Immutable artifact returned by retry operations.
    
    Contains RuntimeRetryInfo, operation summary, and validation result.
    No mutable state. No behavior.
    """
    retry_info: RuntimeRetryInfo
    operation_summary: str
    validation_result: bool


# The centralized immutable RuntimeRetryPolicy.
# This policy permanently belongs to Runtime Retry Domain, NOT RuntimeRetryManager.
# Defines structural mappings from trigger to state.
RUNTIME_RETRY_POLICY: Dict[RuntimeRetryTrigger, RuntimeRetryState] = {
    RuntimeRetryTrigger.FAILOVER_AVAILABLE: RuntimeRetryState.ELIGIBLE,
    RuntimeRetryTrigger.TRANSIENT_FAILURE: RuntimeRetryState.ELIGIBLE,
    RuntimeRetryTrigger.RATE_LIMIT: RuntimeRetryState.WAITING,
    RuntimeRetryTrigger.TIMEOUT: RuntimeRetryState.ELIGIBLE,
    RuntimeRetryTrigger.MANUAL_RETRY: RuntimeRetryState.ELIGIBLE,
    RuntimeRetryTrigger.UNKNOWN: RuntimeRetryState.FAILED
}
