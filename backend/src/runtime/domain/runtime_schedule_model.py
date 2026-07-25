from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from datetime import datetime


class RuntimeScheduleState(str, Enum):
    """
    Immutable representation of Runtime Scheduling states.
    
    Categorization only.
    No behavior, no execution logic.
    Represents execution eligibility.
    """
    READY = "READY"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class RuntimeScheduleTrigger(str, Enum):
    """
    Represents structural scheduling triggers mapped from upstream layers
    (such as a future Translation Layer converting a RuntimeRetryState).
    
    Categorization only.
    No behavior, no execution logic.
    Must never reuse upstream states like ProviderFailoverState directly.
    """
    RETRY_READY = "RETRY_READY"
    DEPENDENCY_PENDING = "DEPENDENCY_PENDING"
    COOLDOWN = "COOLDOWN"
    MANUAL_SCHEDULE = "MANUAL_SCHEDULE"
    SYSTEM_DELAY = "SYSTEM_DELAY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeScheduleDecision:
    """
    Represents an immutable scheduling decision metadata.
    
    Contains structural metadata only representing execution eligibility.
    No execution behavior. No transition logic. No temporal scheduling.
    """
    provider_id: str
    trigger: RuntimeScheduleTrigger
    schedule_state: RuntimeScheduleState
    timestamp: datetime


@dataclass(frozen=True)
class RuntimeScheduleInfo:
    """
    Canonical immutable Runtime Scheduling metadata.
    
    Contains only provider_id values and scheduling-specific structural metadata.
    MUST NOT contain ProviderInfo, ProviderCapability, ProviderHealthInfo,
    ProviderFailoverInfo, or RuntimeRetryInfo.
    Must NOT contain execution metadata, timers, or queue state.
    """
    provider_id: str
    current_state: RuntimeScheduleState
    created_at: datetime
    updated_at: datetime
    previous_state: Optional[RuntimeScheduleState] = None
    trigger: RuntimeScheduleTrigger = RuntimeScheduleTrigger.UNKNOWN
    last_decision: Optional[RuntimeScheduleDecision] = None
    reason: str = ""


@dataclass(frozen=True)
class RuntimeScheduleResult:
    """
    Immutable artifact returned by scheduling operations.
    
    Contains RuntimeScheduleInfo, operation summary, and validation result.
    No mutable state. No behavior. No temporal implications.
    """
    schedule_info: RuntimeScheduleInfo
    operation_summary: str
    validation_result: bool


# The centralized immutable RuntimeSchedulePolicy.
# This policy permanently belongs to Runtime Scheduling Domain, NOT RuntimeSchedulingManager.
# Defines structural mappings from trigger to state representing execution eligibility.
RUNTIME_SCHEDULE_POLICY: Dict[RuntimeScheduleTrigger, RuntimeScheduleState] = {
    RuntimeScheduleTrigger.RETRY_READY: RuntimeScheduleState.READY,
    RuntimeScheduleTrigger.COOLDOWN: RuntimeScheduleState.WAITING,
    RuntimeScheduleTrigger.DEPENDENCY_PENDING: RuntimeScheduleState.BLOCKED,
    RuntimeScheduleTrigger.MANUAL_SCHEDULE: RuntimeScheduleState.READY,
    RuntimeScheduleTrigger.SYSTEM_DELAY: RuntimeScheduleState.DEFERRED,
    RuntimeScheduleTrigger.UNKNOWN: RuntimeScheduleState.DEFERRED
}
