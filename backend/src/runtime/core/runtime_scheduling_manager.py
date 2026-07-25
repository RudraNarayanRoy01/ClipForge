from typing import Dict, Optional
from datetime import datetime

from ..domain.runtime_schedule_model import (
    RuntimeScheduleState,
    RuntimeScheduleTrigger,
    RuntimeScheduleDecision,
    RuntimeScheduleInfo,
    RuntimeScheduleResult,
    RUNTIME_SCHEDULE_POLICY
)
from .runtime_retry_manager import RuntimeRetryManager

class RuntimeSchedulingManager:
    """
    The canonical observational Runtime Scheduling Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Permanently owns Execution Eligibility, Scheduling State, Scheduling Validation, and Scheduling Recording.
    - Observes structural schedule triggers and maps them to schedule states using the domain policy.
    
    Ownership:
    - Owns Runtime Scheduling Domain
    
    MUST NOT:
    - Evaluate temporal aspects: timers, cron, sleep, wait, delays.
    - Import temporal scheduling libraries (except datetime for immutable timestamps).
    - Be a Scheduler Engine, Queue Manager, Async Scheduler, or Runtime Intelligence.
    - Execute HTTP requests, networking, or API calls.
    - Modify or duplicate Runtime Retry, Provider Failover, or Provider Health.
    - Hardcode or mutate scheduling rules (consumes immutable domain policy).
    """

    def __init__(self, runtime_retry_manager: RuntimeRetryManager) -> None:
        # Passively consumes RuntimeRetryManager for structural reference.
        # This dependency is strictly read-only.
        self._runtime_retry_manager = runtime_retry_manager
        
        # Temporary in-memory collection. 
        # Future architecture will introduce RuntimeScheduleStore for persistence.
        self._schedule_records: Dict[str, RuntimeScheduleInfo] = {}

    def _validate_trigger(self, trigger: RuntimeScheduleTrigger) -> RuntimeScheduleState:
        """
        Validate trigger structurally using the centralized scheduling policy.
        """
        if trigger not in RUNTIME_SCHEDULE_POLICY:
            raise ValueError(f"Unknown schedule trigger: {trigger.name}")
        return RUNTIME_SCHEDULE_POLICY[trigger]

    def register_provider(self, provider_id: str) -> RuntimeScheduleResult:
        """
        Register a new provider identity into the execution eligibility tracking system.
        """
        if provider_id in self._schedule_records:
            raise ValueError(f"Provider scheduling tracking for '{provider_id}' is already registered.")
        
        # We optionally validate existence via the upstream dependency, though purely structurally.
        # The true owner of identity is ProviderRegistry, but we check Retry existence 
        # to ensure the dependency chain is respected.
        try:
            self._runtime_retry_manager.get_retry(provider_id)
        except KeyError:
            raise ValueError(f"Provider '{provider_id}' not found in upstream Runtime Retry Manager.")
        
        now = datetime.utcnow()
        info = RuntimeScheduleInfo(
            provider_id=provider_id,
            current_state=RuntimeScheduleState.DEFERRED,
            created_at=now,
            updated_at=now
        )
        self._schedule_records[provider_id] = info
        
        return RuntimeScheduleResult(
            schedule_info=info,
            operation_summary=f"Successfully registered scheduling tracking for provider {provider_id}.",
            validation_result=True
        )

    def get_schedule(self, provider_id: str) -> RuntimeScheduleInfo:
        """
        Retrieve the canonical schedule info (execution eligibility) for a provider.
        """
        if provider_id not in self._schedule_records:
            raise KeyError(f"Schedule record for provider '{provider_id}' not found.")
        return self._schedule_records[provider_id]

    def get_state(self, provider_id: str) -> RuntimeScheduleState:
        """
        Retrieve just the current schedule state (execution eligibility) of a provider.
        """
        return self.get_schedule(provider_id).current_state

    def evaluate_schedule(
        self, 
        provider_id: str, 
        trigger: RuntimeScheduleTrigger,
        reason: str = ""
    ) -> RuntimeScheduleResult:
        """
        Core observational transition logic. Evaluates trigger against policy to determine execution eligibility.
        This does NOT execute the work, create timers, sleep, or wait.
        """
        info = self.get_schedule(provider_id)
        current_state = info.current_state
        
        target_state = self._validate_trigger(trigger)
        
        now = datetime.utcnow()
        decision = RuntimeScheduleDecision(
            provider_id=provider_id,
            trigger=trigger,
            schedule_state=target_state,
            timestamp=now
        )
        
        updated_info = RuntimeScheduleInfo(
            provider_id=provider_id,
            current_state=target_state,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=trigger,
            last_decision=decision,
            reason=reason
        )
        
        self._schedule_records[provider_id] = updated_info
        
        return RuntimeScheduleResult(
            schedule_info=updated_info,
            operation_summary=f"Successfully evaluated execution eligibility for provider {provider_id} to {target_state.name}.",
            validation_result=True
        )

    def record_schedule(
        self, 
        provider_id: str, 
        trigger: RuntimeScheduleTrigger,
        reason: str = ""
    ) -> RuntimeScheduleResult:
        """
        Records an explicit schedule trigger that has been translated by a future Translation Layer.
        """
        return self.evaluate_schedule(provider_id, trigger, reason)

    def validate_schedule(self, provider_id: str, trigger: RuntimeScheduleTrigger) -> bool:
        """
        Validates if a structural trigger is handled by the policy.
        """
        if provider_id not in self._schedule_records:
            return False
        return trigger in RUNTIME_SCHEDULE_POLICY

    def clear_schedule(self, provider_id: str, reason: str = "Schedule cleared") -> RuntimeScheduleResult:
        """
        Resets the schedule state structurally back to DEFERRED.
        """
        info = self.get_schedule(provider_id)
        current_state = info.current_state
        
        now = datetime.utcnow()
        decision = RuntimeScheduleDecision(
            provider_id=provider_id,
            trigger=RuntimeScheduleTrigger.UNKNOWN,
            schedule_state=RuntimeScheduleState.DEFERRED,
            timestamp=now
        )
        
        updated_info = RuntimeScheduleInfo(
            provider_id=provider_id,
            current_state=RuntimeScheduleState.DEFERRED,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=RuntimeScheduleTrigger.UNKNOWN,
            last_decision=decision,
            reason=reason
        )
        
        self._schedule_records[provider_id] = updated_info
        
        return RuntimeScheduleResult(
            schedule_info=updated_info,
            operation_summary=f"Successfully cleared schedule (execution eligibility) for {provider_id}.",
            validation_result=True
        )
