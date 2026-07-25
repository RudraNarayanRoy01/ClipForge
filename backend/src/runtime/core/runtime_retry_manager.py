from typing import Dict, Optional
from datetime import datetime

from ..domain.runtime_retry_model import (
    RuntimeRetryState,
    RuntimeRetryTrigger,
    RuntimeRetryDecision,
    RuntimeRetryInfo,
    RuntimeRetryResult,
    RUNTIME_RETRY_POLICY
)
from .provider_failover_manager import ProviderFailoverManager

class RuntimeRetryManager:
    """
    The canonical observational Runtime Retry Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Permanently owns Retry State, Retry Validation, Retry Recording, and Retry Metadata.
    - Observes structural retry triggers and maps them to retry states using the domain policy.
    
    Ownership:
    - Owns Runtime Retry State
    - Owns Runtime Retry Validation
    - Owns Runtime Retry Recording
    
    MUST NOT:
    - Execute HTTP requests, perform retries, sleep, wait, or measure latency.
    - Be a Retry Executor, Backoff Engine, Scheduler, Execution Engine, 
      Provider Selector, Load Balancer, Network Monitor, or Runtime Intelligence.
    - Modify or duplicate Provider Failover.
    - Mutate retry rules (consumes immutable domain policy).
    """

    def __init__(self, provider_failover_manager: ProviderFailoverManager) -> None:
        # Passively consumes ProviderFailoverManager for structural reference.
        # This dependency is strictly read-only.
        self._provider_failover_manager = provider_failover_manager
        
        # Temporary in-memory collection. 
        # Future architecture will introduce RuntimeRetryStore for persistence.
        self._retry_records: Dict[str, RuntimeRetryInfo] = {}

    def _validate_trigger(self, trigger: RuntimeRetryTrigger) -> RuntimeRetryState:
        """
        Validate trigger structurally using the centralized retry policy.
        """
        if trigger not in RUNTIME_RETRY_POLICY:
            raise ValueError(f"Unknown retry trigger: {trigger.name}")
        return RUNTIME_RETRY_POLICY[trigger]

    def register_provider(self, provider_id: str, max_retry_attempts: int = 3) -> RuntimeRetryResult:
        """
        Register a new provider identity into the retry tracking system.
        """
        if provider_id in self._retry_records:
            raise ValueError(f"Provider retry tracking for '{provider_id}' is already registered.")
        
        now = datetime.utcnow()
        info = RuntimeRetryInfo(
            provider_id=provider_id,
            current_state=RuntimeRetryState.NOT_REQUIRED,
            max_retry_attempts=max_retry_attempts,
            created_at=now,
            updated_at=now
        )
        self._retry_records[provider_id] = info
        
        return RuntimeRetryResult(
            retry_info=info,
            operation_summary=f"Successfully registered retry tracking for provider {provider_id}.",
            validation_result=True
        )

    def get_retry(self, provider_id: str) -> RuntimeRetryInfo:
        """
        Retrieve the canonical retry info for a provider.
        """
        if provider_id not in self._retry_records:
            raise KeyError(f"Retry record for provider '{provider_id}' not found.")
        return self._retry_records[provider_id]

    def get_state(self, provider_id: str) -> RuntimeRetryState:
        """
        Retrieve just the current retry state of a provider.
        """
        return self.get_retry(provider_id).current_state

    def evaluate_retry(
        self, 
        provider_id: str, 
        trigger: RuntimeRetryTrigger,
        reason: str = ""
    ) -> RuntimeRetryResult:
        """
        Core observational transition logic. Evaluates trigger against policy.
        This does NOT execute the retry, it merely sets the state for observation.
        """
        info = self.get_retry(provider_id)
        current_state = info.current_state
        
        # If we are already FAILED or EXHAUSTED and trigger isn't explicitly resetting, 
        # we might just log it, but the policy mapping is strict.
        target_state = self._validate_trigger(trigger)
        
        now = datetime.utcnow()
        decision = RuntimeRetryDecision(
            provider_id=provider_id,
            trigger=trigger,
            retry_attempt=info.retry_attempts + 1 if target_state in (RuntimeRetryState.ELIGIBLE, RuntimeRetryState.WAITING) else info.retry_attempts,
            timestamp=now
        )
        
        new_attempts = decision.retry_attempt
        if target_state == RuntimeRetryState.ELIGIBLE and new_attempts > info.max_retry_attempts:
            target_state = RuntimeRetryState.EXHAUSTED
        
        updated_info = RuntimeRetryInfo(
            provider_id=provider_id,
            current_state=target_state,
            max_retry_attempts=info.max_retry_attempts,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=trigger,
            retry_attempts=new_attempts,
            last_decision=decision,
            reason=reason
        )
        
        self._retry_records[provider_id] = updated_info
        
        return RuntimeRetryResult(
            retry_info=updated_info,
            operation_summary=f"Successfully evaluated retry for provider {provider_id} to {target_state.name}.",
            validation_result=True
        )

    def record_retry(
        self, 
        provider_id: str, 
        trigger: RuntimeRetryTrigger,
        reason: str = ""
    ) -> RuntimeRetryResult:
        """
        Records an explicit retry definition that has been decided by Runtime Intelligence.
        """
        return self.evaluate_retry(provider_id, trigger, reason)

    def validate_retry(self, provider_id: str, trigger: RuntimeRetryTrigger) -> bool:
        """
        Validates if a structural trigger is handled by the policy.
        """
        if provider_id not in self._retry_records:
            return False
        return trigger in RUNTIME_RETRY_POLICY

    def clear_retry(self, provider_id: str, reason: str = "Retry cleared") -> RuntimeRetryResult:
        """
        Resets the retry state structurally back to NOT_REQUIRED.
        """
        info = self.get_retry(provider_id)
        current_state = info.current_state
        
        now = datetime.utcnow()
        decision = RuntimeRetryDecision(
            provider_id=provider_id,
            trigger=RuntimeRetryTrigger.UNKNOWN,
            retry_attempt=0,
            timestamp=now
        )
        
        updated_info = RuntimeRetryInfo(
            provider_id=provider_id,
            current_state=RuntimeRetryState.NOT_REQUIRED,
            max_retry_attempts=info.max_retry_attempts,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=RuntimeRetryTrigger.UNKNOWN,
            retry_attempts=0,
            last_decision=decision,
            reason=reason
        )
        
        self._retry_records[provider_id] = updated_info
        
        return RuntimeRetryResult(
            retry_info=updated_info,
            operation_summary=f"Successfully cleared retry for {provider_id}.",
            validation_result=True
        )
