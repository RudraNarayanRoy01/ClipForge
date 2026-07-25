from typing import Dict, Optional, List
from datetime import datetime

from ..domain.provider_failover_model import (
    ProviderFailoverState,
    ProviderFailoverTrigger,
    ProviderFailoverDecision,
    ProviderFailoverInfo,
    ProviderFailoverResult,
    PROVIDER_FAILOVER_POLICY
)
from .provider_health_manager import ProviderHealthManager

class ProviderFailoverManager:
    """
    The canonical observational Provider Failover Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Permanently owns Failover State, Validation, Recording, and Metadata.
    - Observes structural fallback triggers and maps them to failover states.
    
    Ownership:
    - Owns Provider Failover State
    - Owns Provider Failover Validation
    - Owns Provider Failover Recording
    
    MUST NOT:
    - Execute HTTP requests, route traffic, or monitor networks.
    - Make decisions about when to failover (owned by Runtime Intelligence).
    - Mutate Provider Health state (consumes it passively).
    """

    def __init__(self, provider_health_manager: ProviderHealthManager) -> None:
        # Passively consumes ProviderHealthManager for structural reference.
        self._provider_health_manager = provider_health_manager
        
        # Temporary in-memory collection. 
        # Future architecture will introduce ProviderFailoverStore for persistence.
        self._failover_records: Dict[str, ProviderFailoverInfo] = {}

    def _validate_trigger(self, trigger: ProviderFailoverTrigger) -> ProviderFailoverState:
        """
        Validate trigger structurally using the centralized failover policy.
        """
        if trigger not in PROVIDER_FAILOVER_POLICY:
            raise ValueError(f"Unknown failover trigger: {trigger.name}")
        return PROVIDER_FAILOVER_POLICY.get(trigger)

    def register_provider(self, provider_id: str) -> ProviderFailoverResult:
        """
        Register a new provider identity into the failover tracking system.
        """
        if provider_id in self._failover_records:
            raise ValueError(f"Provider failover for '{provider_id}' is already registered.")
        
        info = ProviderFailoverInfo(
            provider_id=provider_id,
            current_state=ProviderFailoverState.NOT_REQUIRED
        )
        self._failover_records[provider_id] = info
        
        return ProviderFailoverResult(
            failover_info=info,
            operation_summary=f"Successfully registered failover tracking for provider {provider_id}.",
            validation_result=True
        )

    def get_failover(self, provider_id: str) -> ProviderFailoverInfo:
        """
        Retrieve the canonical failover info for a provider.
        """
        if provider_id not in self._failover_records:
            raise KeyError(f"Failover record for provider '{provider_id}' not found.")
        return self._failover_records[provider_id]

    def get_state(self, provider_id: str) -> ProviderFailoverState:
        """
        Retrieve just the current failover state of a provider.
        """
        return self.get_failover(provider_id).current_state

    def evaluate_failover(
        self, 
        source_provider_id: str, 
        trigger: ProviderFailoverTrigger,
        reason: str = ""
    ) -> ProviderFailoverResult:
        """
        Core observational transition logic. Evaluates trigger against policy.
        This does NOT execute the failover, it merely sets the state for observation.
        """
        info = self.get_failover(source_provider_id)
        current_state = info.current_state
        
        target_state = self._validate_trigger(trigger)
        
        now = datetime.utcnow()
        decision = ProviderFailoverDecision(
            source_provider_id=source_provider_id,
            target_provider_id=None,  # Target provider not structurally decided here
            trigger=trigger,
            reason=reason,
            timestamp=now
        )
        
        updated_info = ProviderFailoverInfo(
            provider_id=source_provider_id,
            current_state=target_state,
            previous_state=current_state,
            last_decision=decision,
            reason=reason,
            created_at=info.created_at,
            updated_at=now
        )
        
        self._failover_records[source_provider_id] = updated_info
        
        return ProviderFailoverResult(
            failover_info=updated_info,
            operation_summary=f"Successfully evaluated failover for provider {source_provider_id} to {target_state.name}.",
            validation_result=True
        )

    def record_failover(
        self, 
        source_provider_id: str, 
        target_provider_id: str, 
        trigger: ProviderFailoverTrigger,
        reason: str = ""
    ) -> ProviderFailoverResult:
        """
        Records an explicit fallback definition that has been decided by Runtime Intelligence.
        """
        info = self.get_failover(source_provider_id)
        current_state = info.current_state
        
        # Verify the target is known to the health manager (structural validation only)
        try:
            self._provider_health_manager.get_state(target_provider_id)
        except KeyError:
            raise ValueError(f"Target provider '{target_provider_id}' is not registered in the Health Domain.")
        
        now = datetime.utcnow()
        decision = ProviderFailoverDecision(
            source_provider_id=source_provider_id,
            target_provider_id=target_provider_id,
            trigger=trigger,
            reason=reason,
            timestamp=now
        )
        
        updated_info = ProviderFailoverInfo(
            provider_id=source_provider_id,
            current_state=ProviderFailoverState.FAILED,
            previous_state=current_state,
            last_decision=decision,
            reason=reason,
            created_at=info.created_at,
            updated_at=now
        )
        
        self._failover_records[source_provider_id] = updated_info
        
        return ProviderFailoverResult(
            failover_info=updated_info,
            operation_summary=f"Successfully recorded failover from {source_provider_id} to {target_provider_id}.",
            validation_result=True
        )

    def validate_failover(self, source_provider_id: str, trigger: ProviderFailoverTrigger) -> bool:
        """
        Validates if a structural trigger is handled by the policy.
        """
        if source_provider_id not in self._failover_records:
            return False
        return trigger in PROVIDER_FAILOVER_POLICY

    def clear_failover(self, provider_id: str, reason: str = "Failover cleared") -> ProviderFailoverResult:
        """
        Resets the failover state structurally back to NOT_REQUIRED.
        """
        info = self.get_failover(provider_id)
        current_state = info.current_state
        
        now = datetime.utcnow()
        decision = ProviderFailoverDecision(
            source_provider_id=provider_id,
            target_provider_id=None,
            trigger=ProviderFailoverTrigger.UNKNOWN,
            reason=reason,
            timestamp=now
        )
        
        updated_info = ProviderFailoverInfo(
            provider_id=provider_id,
            current_state=ProviderFailoverState.NOT_REQUIRED,
            previous_state=current_state,
            last_decision=decision,
            reason=reason,
            created_at=info.created_at,
            updated_at=now
        )
        
        self._failover_records[provider_id] = updated_info
        
        return ProviderFailoverResult(
            failover_info=updated_info,
            operation_summary=f"Successfully cleared failover for {provider_id}.",
            validation_result=True
        )
