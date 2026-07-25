from enum import Enum, auto
from typing import List

from ..contracts.lifecycle_aware import ILifecycleAware

from .lifecycle_model import (
    LifecycleResult,
    LifecycleState,
    LifecycleStage,
    LifecycleSummary,
    LifecycleIdentity,
    LifecycleTransition
)
from .execution_result_model import ExecutionResult, ExecutionOutcome, ExecutionStatus

# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================
# The following components manage the startup and shutdown of the Runtime 
# Application itself. They do NOT manage execution lifecycle progression.
# =============================================================================

class RuntimeLifecycleState(Enum):
    """
    Represents the complete lifecycle of the Adaptive AI Runtime.
    """
    UNINITIALIZED = auto()
    BOOTSTRAPPING = auto()
    INITIALIZED = auto()
    SHUTTING_DOWN = auto()
    SHUTDOWN = auto()


class RuntimeLifecycleCoordinator:
    """
    Architectural coordinator for the Runtime lifecycle.
    
    Responsible for transitioning between lifecycle states and notifying
    registered ILifecycleAware components. It does NOT manage execution logic.
    """

    def __init__(self) -> None:
        self._state = RuntimeLifecycleState.UNINITIALIZED
        self._components: List[ILifecycleAware] = []

    @property
    def current_state(self) -> RuntimeLifecycleState:
        return self._state

    def register_component(self, component: ILifecycleAware) -> None:
        """Register a component to receive lifecycle notifications."""
        if component not in self._components:
            self._components.append(component)

    def transition_to(self, target_state: RuntimeLifecycleState) -> None:
        """
        Transition the Runtime to a new state and notify components.
        
        Note: In a mature implementation, this would enforce valid state 
        machine transitions (e.g., cannot go from SHUTDOWN to INITIALIZED).
        """
        self._state = target_state

        if self._state == RuntimeLifecycleState.BOOTSTRAPPING:
            self._notify_bootstrap()
        elif self._state == RuntimeLifecycleState.INITIALIZED:
            self._notify_initialize()
        elif self._state == RuntimeLifecycleState.SHUTTING_DOWN:
            self._notify_shutdown()
        # SHUTDOWN and UNINITIALIZED typically don't have explicit notification phases

    def _notify_bootstrap(self) -> None:
        for component in self._components:
            component.on_bootstrap()

    def _notify_initialize(self) -> None:
        for component in self._components:
            component.on_initialize()

    def _notify_shutdown(self) -> None:
        for component in reversed(self._components):
            component.on_shutdown()


# =============================================================================
# EXECUTION LIFECYCLE
# =============================================================================
# The following components manage the lifecycle progression of completed
# Runtime executions. They evaluate ExecutionResult to produce LifecycleResult.
# They do NOT manage application startup/shutdown.
# =============================================================================

import time
import uuid

class RuntimeLifecycle:
    """
    The Runtime Execution Lifecycle Engine.
    
    Defines "How lifecycle progression is evaluated."
    Performs exactly one responsibility: ExecutionResult -> LifecycleResult.
    
    It is NOT an executor, scheduler, retry engine, observation service, 
    optimization engine, workflow engine, queue manager, or resource manager.
    """
    
    def evaluate(self, execution_result: ExecutionResult) -> LifecycleResult:
        """
        Evaluate an ExecutionResult and produce an immutable LifecycleResult.
        """
        # Determine LifecycleState based on ExecutionStatus and ExecutionOutcome
        state = self._determine_state(execution_result)
        
        # Determine LifecycleStage based on ExecutionStatus
        stage = self._determine_stage(execution_result)
        
        # Build Summary
        summary = LifecycleSummary(
            summary=f"Lifecycle evaluated for {execution_result.execution_identity.execution_id}",
            reason="Execution completed",
            transition_count=1,
            warnings=[]
        )
        
        now = time.time()
        
        # Build Initial Transition
        transition = LifecycleTransition(
            previous_state=LifecycleState.CREATED,
            current_state=state,
            transition_reason="Execution evaluated",
            timestamp=now
        )
        
        # Generate identity
        lifecycle_id = f"lc-{uuid.uuid4().hex[:8]}"
        lifecycle_identity = LifecycleIdentity(
            lifecycle_id=lifecycle_id,
            created_at=now
        )
        
        # Produce Result
        return LifecycleResult(
            lifecycle_identity=lifecycle_identity,
            execution_identity=execution_result.execution_identity,
            state=state,
            stage=stage,
            summary=summary,
            transitions=[transition],
            started_at=execution_result.started_at or now,
            updated_at=now,
            metadata={}
        )
        
    def _determine_state(self, execution_result: ExecutionResult) -> LifecycleState:
        """Map execution result status to lifecycle state."""
        if execution_result.status == ExecutionStatus.COMPLETED:
            if execution_result.outcome == ExecutionOutcome.SUCCESS:
                return LifecycleState.COMPLETED
            elif execution_result.outcome == ExecutionOutcome.PARTIAL:
                return LifecycleState.COMPLETED
            else:
                return LifecycleState.FAILED
        elif execution_result.status == ExecutionStatus.FAILED:
            return LifecycleState.FAILED
        elif execution_result.status == ExecutionStatus.CANCELLED:
            return LifecycleState.TERMINATED
        
        return LifecycleState.FAILED
        
    def _determine_stage(self, execution_result: ExecutionResult) -> LifecycleStage:
        """Map execution result status to lifecycle stage."""
        if execution_result.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED):
            return LifecycleStage.POST_EXECUTION
        return LifecycleStage.EXECUTION

