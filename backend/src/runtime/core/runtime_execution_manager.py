from typing import Dict, Optional
from datetime import datetime

from ..domain.runtime_execution_model import (
    RuntimeExecutionState,
    RuntimeExecutionTrigger,
    RuntimeExecutionDecision,
    RuntimeExecutionInfo,
    RuntimeExecutionResult,
    RUNTIME_EXECUTION_POLICY
)
from .runtime_scheduling_manager import RuntimeSchedulingManager

class RuntimeExecutionManager:
    """
    The canonical observational Runtime Execution Manager for the AI Clipping Platform.
    
    Responsibilities:
    - Permanently owns Execution Preparation, Execution State, Execution Validation, and Execution Recording.
    - Observes structural execution triggers and maps them to execution preparation states using the domain policy.
    - Answers "How has execution been structurally prepared?", NOT "How should execution occur?".
    
    Ownership:
    - Owns Runtime Execution Domain
    
    MUST NOT:
    - Evaluate temporal aspects: timers, cron, sleep, wait, delays.
    - Execute workloads, perform inference, launch workers, or spawn threads.
    - Perform scheduling, retry, failover, reason, or optimize workloads.
    - Import asyncio, threading, HTTP, or networking libraries.
    - Import Runtime Intelligence or Execution Engine.
    - Modify or duplicate Runtime Scheduling.
    - Hardcode or mutate execution rules (consumes immutable domain policy).
    """

    def __init__(self, runtime_scheduling_manager: RuntimeSchedulingManager) -> None:
        # Passively consumes RuntimeSchedulingManager for structural reference.
        # This dependency is strictly read-only and maintains the forward direction.
        self._runtime_scheduling_manager = runtime_scheduling_manager
        
        # Temporary in-memory collection.
        # Future architecture will introduce RuntimeExecutionStore for persistence.
        self._execution_records: Dict[str, RuntimeExecutionInfo] = {}

    def _validate_trigger(self, trigger: RuntimeExecutionTrigger) -> RuntimeExecutionState:
        """
        Validate trigger structurally using the centralized execution policy.
        """
        if trigger not in RUNTIME_EXECUTION_POLICY:
            raise ValueError(f"Unknown execution trigger: {trigger.name}")
        return RUNTIME_EXECUTION_POLICY[trigger]

    def register_provider(self, provider_id: str) -> RuntimeExecutionResult:
        """
        Register a new provider identity into the execution preparation tracking system.
        """
        if provider_id in self._execution_records:
            raise ValueError(f"Provider execution tracking for '{provider_id}' is already registered.")
        
        # We optionally validate existence via the upstream dependency (RuntimeSchedulingManager).
        # This ensures the dependency chain is respected and bounded-context separation is maintained.
        try:
            self._runtime_scheduling_manager.get_schedule(provider_id)
        except KeyError:
            raise ValueError(f"Provider '{provider_id}' not found in upstream Runtime Scheduling Manager.")
        
        now = datetime.utcnow()
        info = RuntimeExecutionInfo(
            provider_id=provider_id,
            current_state=RuntimeExecutionState.ABORTED,
            created_at=now,
            updated_at=now
        )
        self._execution_records[provider_id] = info
        
        return RuntimeExecutionResult(
            execution_info=info,
            operation_summary=f"Successfully registered execution preparation tracking for provider {provider_id}.",
            validation_result=True
        )

    def get_execution(self, provider_id: str) -> RuntimeExecutionInfo:
        """
        Retrieve the canonical execution info (execution preparation) for a provider.
        """
        if provider_id not in self._execution_records:
            raise KeyError(f"Execution record for provider '{provider_id}' not found.")
        return self._execution_records[provider_id]

    def get_state(self, provider_id: str) -> RuntimeExecutionState:
        """
        Retrieve just the current execution preparation state of a provider.
        """
        return self.get_execution(provider_id).current_state

    def prepare_execution(
        self, 
        provider_id: str, 
        trigger: RuntimeExecutionTrigger,
        reason: str = ""
    ) -> RuntimeExecutionResult:
        """
        Core observational preparation logic. Evaluates trigger against policy to determine execution preparation state.
        This does NOT execute the work, create timers, sleep, or wait.
        """
        info = self.get_execution(provider_id)
        current_state = info.current_state
        
        target_state = self._validate_trigger(trigger)
        
        now = datetime.utcnow()
        decision = RuntimeExecutionDecision(
            provider_id=provider_id,
            trigger=trigger,
            execution_state=target_state,
            timestamp=now
        )
        
        updated_info = RuntimeExecutionInfo(
            provider_id=provider_id,
            current_state=target_state,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=trigger,
            last_decision=decision,
            reason=reason
        )
        
        self._execution_records[provider_id] = updated_info
        
        return RuntimeExecutionResult(
            execution_info=updated_info,
            operation_summary=f"Successfully evaluated execution preparation for provider {provider_id} to {target_state.name}.",
            validation_result=True
        )

    def record_execution(
        self, 
        provider_id: str, 
        trigger: RuntimeExecutionTrigger,
        reason: str = ""
    ) -> RuntimeExecutionResult:
        """
        Records an explicit execution trigger that has been translated by a future Translation Layer.
        """
        return self.prepare_execution(provider_id, trigger, reason)

    def validate_execution(self, provider_id: str, trigger: RuntimeExecutionTrigger) -> bool:
        """
        Validates if a structural trigger is handled by the policy.
        """
        if provider_id not in self._execution_records:
            return False
        return trigger in RUNTIME_EXECUTION_POLICY

    def clear_execution(self, provider_id: str, reason: str = "Execution preparation cleared") -> RuntimeExecutionResult:
        """
        Resets the execution preparation state structurally back to ABORTED.
        """
        info = self.get_execution(provider_id)
        current_state = info.current_state
        
        now = datetime.utcnow()
        decision = RuntimeExecutionDecision(
            provider_id=provider_id,
            trigger=RuntimeExecutionTrigger.UNKNOWN,
            execution_state=RuntimeExecutionState.ABORTED,
            timestamp=now
        )
        
        updated_info = RuntimeExecutionInfo(
            provider_id=provider_id,
            current_state=RuntimeExecutionState.ABORTED,
            created_at=info.created_at,
            updated_at=now,
            previous_state=current_state,
            trigger=RuntimeExecutionTrigger.UNKNOWN,
            last_decision=decision,
            reason=reason
        )
        
        self._execution_records[provider_id] = updated_info
        
        return RuntimeExecutionResult(
            execution_info=updated_info,
            operation_summary=f"Successfully cleared execution preparation for {provider_id}.",
            validation_result=True
        )
