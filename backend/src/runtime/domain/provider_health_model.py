from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

class ProviderHealthState(Enum):
    """
    Categorizes the structural health state of a provider.
    Categorization only. No behavioral meaning.
    Observational only - NEVER interpreted to make runtime execution decisions.
    """
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

@dataclass(frozen=True)
class ProviderHealthTransition:
    """
    Metadata detailing a provider health state transition.
    No transition logic. Observational metadata only.
    """
    from_state: ProviderHealthState
    to_state: ProviderHealthState
    transition_reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

# Centralized immutable transition policy permanently owned by the Health Domain.
# ProviderHealthManager queries this policy, but never defines or mutates it.
PROVIDER_HEALTH_TRANSITION_POLICY: Dict[ProviderHealthState, List[ProviderHealthState]] = {
    ProviderHealthState.UNKNOWN: [
        ProviderHealthState.HEALTHY,
        ProviderHealthState.DEGRADED,
        ProviderHealthState.UNHEALTHY,
        ProviderHealthState.OFFLINE,
        ProviderHealthState.MAINTENANCE
    ],
    ProviderHealthState.HEALTHY: [
        ProviderHealthState.DEGRADED,
        ProviderHealthState.UNHEALTHY,
        ProviderHealthState.OFFLINE,
        ProviderHealthState.MAINTENANCE
    ],
    ProviderHealthState.DEGRADED: [
        ProviderHealthState.HEALTHY,
        ProviderHealthState.UNHEALTHY,
        ProviderHealthState.OFFLINE,
        ProviderHealthState.MAINTENANCE
    ],
    ProviderHealthState.UNHEALTHY: [
        ProviderHealthState.HEALTHY,
        ProviderHealthState.DEGRADED,
        ProviderHealthState.OFFLINE,
        ProviderHealthState.MAINTENANCE
    ],
    ProviderHealthState.OFFLINE: [
        ProviderHealthState.HEALTHY,
        ProviderHealthState.MAINTENANCE
    ],
    ProviderHealthState.MAINTENANCE: [
        ProviderHealthState.HEALTHY,
        ProviderHealthState.OFFLINE
    ]
}

@dataclass(frozen=True)
class ProviderHealthInfo:
    """
    Canonical immutable provider health metadata.
    References ONLY `provider_id`.
    Never embeds ProviderInfo, ProviderCapability, ModelInfo, or ModelLifecycleInfo.
    Passive observational metadata. No execution behavior.
    """
    provider_id: str
    current_state: ProviderHealthState
    previous_state: Optional[ProviderHealthState] = None
    last_transition: Optional[ProviderHealthTransition] = None
    transition_reason: Optional[str] = None
    last_health_check: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ProviderHealthResult:
    """
    Immutable artifact returned by health operations.
    Contains `ProviderHealthInfo`, operation summary, and validation result.
    No mutable state. No behavior.
    """
    health_info: ProviderHealthInfo
    operation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
