from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

class ProviderFailoverState(Enum):
    """
    Categorizes the structural failover state.
    Categorization only. No behavioral meaning.
    """
    NOT_REQUIRED = "NOT_REQUIRED"
    EVALUATING = "EVALUATING"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"

class ProviderFailoverTrigger(Enum):
    """
    Independent structural trigger decoupling Failover from Health.
    """
    HEALTH_DEGRADED = "HEALTH_DEGRADED"
    PROVIDER_OFFLINE = "PROVIDER_OFFLINE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    ADMIN_REQUEST = "ADMIN_REQUEST"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class ProviderFailoverDecision:
    """
    Immutable metadata detailing a failover decision structurally.
    """
    source_provider_id: str
    target_provider_id: Optional[str]
    trigger: ProviderFailoverTrigger
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

# Future-proofed structural rules mapping triggers to states.
# Belongs strictly to the Domain, not the Manager.
PROVIDER_FAILOVER_POLICY: Dict[ProviderFailoverTrigger, ProviderFailoverState] = {
    ProviderFailoverTrigger.HEALTH_DEGRADED: ProviderFailoverState.AVAILABLE,
    ProviderFailoverTrigger.PROVIDER_OFFLINE: ProviderFailoverState.AVAILABLE,
    ProviderFailoverTrigger.MODEL_UNAVAILABLE: ProviderFailoverState.AVAILABLE,
    ProviderFailoverTrigger.MANUAL_OVERRIDE: ProviderFailoverState.AVAILABLE,
    ProviderFailoverTrigger.ADMIN_REQUEST: ProviderFailoverState.AVAILABLE,
    ProviderFailoverTrigger.UNKNOWN: ProviderFailoverState.EVALUATING
}

@dataclass(frozen=True)
class ProviderFailoverInfo:
    """
    Canonical immutable provider failover metadata.
    References ONLY immutable provider_id values.
    Never embeds ProviderInfo, ProviderCapability, or ProviderHealthInfo.
    """
    provider_id: str
    current_state: ProviderFailoverState
    previous_state: Optional[ProviderFailoverState] = None
    last_decision: Optional[ProviderFailoverDecision] = None
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ProviderFailoverResult:
    """
    Immutable artifact returned by failover operations.
    No mutable state. No behavior.
    """
    failover_info: ProviderFailoverInfo
    operation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
