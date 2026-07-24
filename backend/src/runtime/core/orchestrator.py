from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .execution_context import ExecutionContext, ContextValidationStatus


class StageOrchestrationStatus(Enum):
    """
    Architectural status of stage orchestration readiness.
    
    This represents orchestration state only, NEVER execution outcome.
    """
    PENDING = auto()
    READY = auto()
    BLOCKED = auto()
    WAITING_FOR_DEPENDENCIES = auto()
    FAILED_DEPENDENCY = auto()


class SessionValidationStatus(Enum):
    """
    Architectural status of session validation.
    
    Validation verifies coordination correctness only. It NEVER performs:
    - hardware validation
    - provider validation
    - execution validation
    - runtime validation
    """
    VALID = auto()
    INVALID_SESSION = auto()
    INVALID_CONTEXT = auto()
    INVALID_DEPENDENCY = auto()
    INCOMPLETE_CONTEXT = auto()
    VALIDATION_FAILED = auto()


@dataclass(frozen=True)
class StageExecutionState:
    """
    Immutable representation of orchestration readiness for one execution stage.
    
    Represents a pure coordination artifact.
    It MUST NEVER contain:
    - provider instances
    - physical GPU/CPU/RAM handles
    - execution state or results
    - hardware identifiers
    - monitoring or optimization information
    """
    stage_identifier: str
    stage_name: str
    dependency_readiness: StageOrchestrationStatus
    allocation_reference: str
    capability_requirements: List[str] = field(default_factory=list)
    orchestration_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionSession:
    """
    Immutable Runtime canonical Execution Coordination artifact.
    
    ExecutionSession represents execution coordination rather than execution.
    After creation it should never change. Future Runtime systems should consume
    ExecutionSession rather than mutating it.
    
    It MUST NOT contain:
    - execution state or results
    - provider instances
    - hardware reservations
    - GPU/CPU/memory handles
    - runtime metrics
    - monitoring/optimization information
    """
    validation_status: SessionValidationStatus
    stage_states: List[StageExecutionState] = field(default_factory=list)
    orchestration_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeOrchestrator:
    """
    The canonical Runtime authority for execution coordination.
    
    This subsystem is owned exclusively by RuntimeContext. Future Runtime components must
    obtain orchestration through RuntimeContext rather than constructing RuntimeOrchestrator independently.
    
    Responsibilities:
    - Consume immutable ExecutionContext
    - Evaluate dependency readiness
    - Determine coordination order
    - Preserve dependency relationships
    - Validate coordination readiness
    - Produce immutable ExecutionSession
    
    Must NEVER:
    - Execute workloads or invoke providers
    - Reserve hardware
    - Launch inference or render media
    - Monitor or optimize execution
    - Learn from execution
    """

    def __init__(self) -> None:
        pass

    def create_session(self, context: ExecutionContext) -> ExecutionSession:
        """
        Consume immutable ExecutionContext and produce immutable ExecutionSession.
        """
        if not context or not getattr(context, 'stage_contexts', None):
            return ExecutionSession(
                validation_status=SessionValidationStatus.INCOMPLETE_CONTEXT,
                orchestration_metadata={"error": "Empty or missing execution context."}
            )

        if context.validation_status != ContextValidationStatus.VALID:
            return ExecutionSession(
                validation_status=SessionValidationStatus.INVALID_CONTEXT,
                orchestration_metadata={"error": f"Context is invalid: {context.validation_status}"}
            )

        stage_states: List[StageExecutionState] = []
        seen_identifiers = set()

        for stage_ctx in context.stage_contexts:
            identifier = stage_ctx.stage_identifier
            
            if identifier in seen_identifiers:
                return ExecutionSession(
                    validation_status=SessionValidationStatus.INVALID_SESSION,
                    orchestration_metadata={"error": f"Duplicate stage identifier in context: {identifier}"}
                )
            
            seen_identifiers.add(identifier)
            
            # Base readiness evaluation
            # If dependencies are empty, it's READY. If not, WAITING_FOR_DEPENDENCIES.
            # Real dependency evaluation logic would live here or in a dedicated evaluator.
            readiness = StageOrchestrationStatus.READY
            if stage_ctx.dependency_references:
                readiness = StageOrchestrationStatus.WAITING_FOR_DEPENDENCIES
                
            state = StageExecutionState(
                stage_identifier=identifier,
                stage_name=stage_ctx.stage_name,
                dependency_readiness=readiness,
                allocation_reference=stage_ctx.allocation_reference,
                capability_requirements=list(stage_ctx.capability_requirements),
                orchestration_metadata={"prepared_from": "execution_context"}
            )
            stage_states.append(state)

        status = self._validate_session(stage_states, context)
        if status != SessionValidationStatus.VALID:
            return ExecutionSession(
                validation_status=status,
                orchestration_metadata={"error": "Session validation failed."}
            )

        return ExecutionSession(
            validation_status=SessionValidationStatus.VALID,
            stage_states=stage_states,
            orchestration_metadata={"source_context_status": "VALID"}
        )

    def _validate_session(self, stage_states: List[StageExecutionState], context: ExecutionContext) -> SessionValidationStatus:
        """
        Perform lightweight architectural validation.
        Validates missing stages, empty sessions, invalid dependencies.
        """
        if not stage_states:
            return SessionValidationStatus.INCOMPLETE_CONTEXT
            
        if len(stage_states) != len(context.stage_contexts):
            return SessionValidationStatus.INVALID_SESSION

        # Validate that all dependencies in the original context refer to existing stages
        identifiers = {state.stage_identifier for state in stage_states}
        
        for stage_ctx in context.stage_contexts:
            for dep in stage_ctx.dependency_references:
                if dep not in identifiers:
                    return SessionValidationStatus.INVALID_DEPENDENCY

        return SessionValidationStatus.VALID
