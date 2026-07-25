from typing import Dict, Optional
from datetime import datetime

from ..domain.provider_health_model import (
    ProviderHealthState,
    ProviderHealthTransition,
    ProviderHealthInfo,
    ProviderHealthResult,
    PROVIDER_HEALTH_TRANSITION_POLICY
)

class ProviderHealthManager:
    """
    The canonical observational Provider Health Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Record provider structural health states
    - Validate health transitions against PROVIDER_HEALTH_TRANSITION_POLICY
    - Maintain canonical health history
    - Remain purely observational
    
    Ownership:
    - Owns Provider Health State
    - Owns Provider Health Transition
    - Owns Provider Health Validation
    - Owns Provider Health History
    
    MUST NOT:
    - Execute HTTP requests, ping providers, or measure latency
    - Interpret health to make execution decisions
    - Retry or failover
    - Mutate, duplicate, or define the transition rules itself
    - Schedule resources or execute routing
    """

    def __init__(self) -> None:
        # Temporary in-memory collection. 
        # Future architecture will introduce ProviderHealthStore for persistence.
        self._health_records: Dict[str, ProviderHealthInfo] = {}

    def _validate_transition(self, current_state: ProviderHealthState, next_state: ProviderHealthState) -> bool:
        """
        Validate transition structurally using the centralized transition policy.
        """
        allowed_transitions = PROVIDER_HEALTH_TRANSITION_POLICY.get(current_state, [])
        return next_state in allowed_transitions

    def register_provider(self, provider_id: str) -> ProviderHealthResult:
        """
        Register a new provider identity into the health tracking system.
        """
        if provider_id in self._health_records:
            raise ValueError(f"Provider health for '{provider_id}' is already registered.")
        
        info = ProviderHealthInfo(
            provider_id=provider_id,
            current_state=ProviderHealthState.UNKNOWN,
            last_health_check=datetime.utcnow()
        )
        self._health_records[provider_id] = info
        
        return ProviderHealthResult(
            health_info=info,
            operation_summary=f"Successfully registered health tracking for provider {provider_id}.",
            validation_result=True
        )

    def get_health(self, provider_id: str) -> ProviderHealthInfo:
        """
        Retrieve the canonical health info for a provider.
        """
        if provider_id not in self._health_records:
            raise KeyError(f"Health record for provider '{provider_id}' not found.")
        return self._health_records[provider_id]

    def get_state(self, provider_id: str) -> ProviderHealthState:
        """
        Retrieve just the current health state of a provider.
        """
        return self.get_health(provider_id).current_state

    def transition_health(self, provider_id: str, next_state: ProviderHealthState, reason: str = "") -> ProviderHealthResult:
        """
        Core observational transition logic. Evaluates transition against policy.
        """
        info = self.get_health(provider_id)
        current_state = info.current_state
        
        if not self._validate_transition(current_state, next_state):
            raise ValueError(f"Invalid health transition from {current_state.name} to {next_state.name} for provider {provider_id}.")
        
        now = datetime.utcnow()
        transition = ProviderHealthTransition(
            from_state=current_state,
            to_state=next_state,
            transition_reason=reason,
            timestamp=now
        )
        
        updated_info = ProviderHealthInfo(
            provider_id=provider_id,
            current_state=next_state,
            previous_state=current_state,
            last_transition=transition,
            transition_reason=reason,
            last_health_check=now,
            created_at=info.created_at,
            updated_at=now
        )
        
        self._health_records[provider_id] = updated_info
        
        return ProviderHealthResult(
            health_info=updated_info,
            operation_summary=f"Successfully transitioned provider {provider_id} health to {next_state.name}.",
            validation_result=True
        )

    def mark_healthy(self, provider_id: str, reason: str = "Provider marked as healthy") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.HEALTHY, reason)

    def mark_degraded(self, provider_id: str, reason: str = "Provider marked as degraded") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.DEGRADED, reason)

    def mark_unhealthy(self, provider_id: str, reason: str = "Provider marked as unhealthy") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.UNHEALTHY, reason)

    def mark_offline(self, provider_id: str, reason: str = "Provider marked as offline") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.OFFLINE, reason)

    def start_maintenance(self, provider_id: str, reason: str = "Provider entering maintenance") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.MAINTENANCE, reason)

    def finish_maintenance(self, provider_id: str, reason: str = "Provider exiting maintenance") -> ProviderHealthResult:
        return self.transition_health(provider_id, ProviderHealthState.HEALTHY, reason)
