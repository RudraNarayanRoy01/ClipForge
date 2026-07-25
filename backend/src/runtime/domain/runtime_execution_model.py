from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from datetime import datetime


class RuntimeExecutionState(str, Enum):
    """
    Immutable representation of Runtime Execution states.
    
    Categorization only.
    No behavior, no execution logic.
    Represents execution preparation.
    """
    PREPARED = "PREPARED"
    READY = "READY"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class RuntimeExecutionTrigger(str, Enum):
    """
    Represents structural execution triggers mapped from upstream layers
    by a future Translation Layer.
    
    Categorization only.
    No behavior, no execution logic.
    Must never reuse RuntimeScheduleState or ProviderFailoverState directly.
    """
    SCHEDULE_READY = "SCHEDULE_READY"
    MANUAL_EXECUTION = "MANUAL_EXECUTION"
    SYSTEM_REQUEST = "SYSTEM_REQUEST"
    PIPELINE_REQUEST = "PIPELINE_REQUEST"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeExecutionDecision:
    """
    Represents an immutable execution decision metadata.
    
    Contains structural metadata only representing execution preparation.
    No execution behavior. No transition logic. No temporal scheduling.
    """
    provider_id: str
    trigger: RuntimeExecutionTrigger
    execution_state: RuntimeExecutionState
    timestamp: datetime


@dataclass(frozen=True)
class RuntimeExecutionInfo:
    """
    Canonical immutable Runtime Execution metadata.
    
    Contains only provider_id values and execution-specific structural metadata.
    MUST NOT contain ProviderInfo, ProviderCapability, ProviderHealthInfo,
    ProviderFailoverInfo, RuntimeRetryInfo, or RuntimeScheduleInfo.
    Must NOT contain execution statistics, metrics, memory usage, or hardware info.
    """
    provider_id: str
    current_state: RuntimeExecutionState
    created_at: datetime
    updated_at: datetime
    previous_state: Optional[RuntimeExecutionState] = None
    trigger: RuntimeExecutionTrigger = RuntimeExecutionTrigger.UNKNOWN
    last_decision: Optional[RuntimeExecutionDecision] = None
    reason: str = ""


@dataclass(frozen=True)
class RuntimeExecutionResult:
    """
    Immutable artifact returned by execution preparation operations.
    
    Contains RuntimeExecutionInfo, operation summary, and validation result.
    No mutable state. No behavior. No execution engine properties.
    """
    execution_info: RuntimeExecutionInfo
    operation_summary: str
    validation_result: bool


# The centralized immutable RuntimeExecutionPolicy.
# This policy permanently belongs to Runtime Execution Domain, NOT RuntimeExecutionManager.
# Defines structural mappings from trigger to state representing execution preparation.
# Must NEVER directly map RuntimeScheduleState.
RUNTIME_EXECUTION_POLICY: Dict[RuntimeExecutionTrigger, RuntimeExecutionState] = {
    RuntimeExecutionTrigger.SCHEDULE_READY: RuntimeExecutionState.READY,
    RuntimeExecutionTrigger.MANUAL_EXECUTION: RuntimeExecutionState.PREPARED,
    RuntimeExecutionTrigger.SYSTEM_REQUEST: RuntimeExecutionState.READY,
    RuntimeExecutionTrigger.PIPELINE_REQUEST: RuntimeExecutionState.PREPARED,
    RuntimeExecutionTrigger.UNKNOWN: RuntimeExecutionState.ABORTED
}
