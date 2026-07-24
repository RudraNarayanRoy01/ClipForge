from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional

from .resource_allocator import AllocationResult, AllocationValidationStatus


class ContextValidationStatus(Enum):
    """
    Architectural status of context validation.
    
    Validation verifies architectural correctness only, NEVER execution status.
    It does not perform hardware validation, provider validation, scheduling validation,
    orchestration validation, or runtime performance validation.
    """
    VALID = auto()
    INVALID_CONTEXT = auto()
    INCOMPLETE_ALLOCATION = auto()
    MISSING_STAGE = auto()
    INVALID_DEPENDENCY = auto()
    VALIDATION_FAILED = auto()


@dataclass(frozen=True)
class StageExecutionContext:
    """
    Immutable representation of one prepared execution stage.
    
    StageExecutionContext represents a pure architectural representation of execution preparation.
    
    It must NEVER contain:
    - provider instances
    - physical GPU/CPU/RAM handles
    - hardware identifiers
    - CUDA/Vulkan/DirectML objects
    - execution state
    - runtime state
    - monitoring information
    - optimization information
    """
    stage_identifier: str
    stage_name: str
    allocation_reference: str  # Reference back to the StageAllocation
    dependency_references: List[str] = field(default_factory=list)
    capability_requirements: List[str] = field(default_factory=list)
    execution_preparation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable Runtime canonical Execution Preparation artifact.
    
    ExecutionContext represents architectural execution preparation rather than runtime execution.
    After creation, it should never change. Future Runtime systems should consume ExecutionContext 
    rather than mutating it.
    
    It must NOT contain:
    - execution state
    - runtime state
    - provider instances
    - hardware reservations
    - GPU/CPU/memory handles
    - runtime metrics
    - execution progress/results
    - monitoring/optimization information
    - orchestration state
    """
    validation_status: ContextValidationStatus
    stage_contexts: List[StageExecutionContext] = field(default_factory=list)
    preparation_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeExecutionContextFactory:
    """
    The canonical Runtime authority for execution preparation.
    
    This subsystem is owned exclusively by RuntimeContext. Future Runtime components must obtain
    ExecutionContext creation through RuntimeContext rather than constructing RuntimeExecutionContextFactory
    independently.
    
    Responsibilities:
    - Consume immutable AllocationResult
    - Assemble StageExecutionContext objects
    - Preserve dependency relationships
    - Preserve allocation intent
    - Validate architectural completeness
    - Produce immutable ExecutionContext
    
    Must NEVER:
    - Reserve hardware (GPU/CPU/RAM)
    - Instantiate providers
    - Launch execution
    - Coordinate execution
    - Schedule execution
    - Monitor execution
    - Optimize execution
    - Perform adaptive learning
    """

    def __init__(self) -> None:
        pass

    def create_context(self, allocation: AllocationResult) -> ExecutionContext:
        """
        Consume immutable AllocationResult and produce immutable ExecutionContext.
        """
        if not allocation or not getattr(allocation, 'stage_allocations', None):
            return ExecutionContext(
                validation_status=ContextValidationStatus.INCOMPLETE_ALLOCATION,
                preparation_metadata={"error": "Empty or missing allocation result."}
            )

        if allocation.validation_status != AllocationValidationStatus.VALID:
            return ExecutionContext(
                validation_status=ContextValidationStatus.INCOMPLETE_ALLOCATION,
                preparation_metadata={"error": f"Allocation is invalid: {allocation.validation_status}"}
            )

        stage_contexts: List[StageExecutionContext] = []
        seen_identifiers = set()

        for alloc_stage in allocation.stage_allocations:
            identifier = alloc_stage.stage_identifier
            
            if identifier in seen_identifiers:
                return ExecutionContext(
                    validation_status=ContextValidationStatus.INVALID_CONTEXT,
                    preparation_metadata={"error": f"Duplicate stage identifier: {identifier}"}
                )
            
            seen_identifiers.add(identifier)
            
            # Here we preserve capability requirements and add preparation metadata
            stage_ctx = StageExecutionContext(
                stage_identifier=identifier,
                stage_name=alloc_stage.stage_name,
                allocation_reference=identifier,
                dependency_references=[],  # Graph dependency references would be resolved here in a fully integrated flow
                capability_requirements=list(alloc_stage.capability_requirements),
                execution_preparation_metadata={"prepared_from": "allocation_result"}
            )
            stage_contexts.append(stage_ctx)

        status = self._validate_context(stage_contexts, allocation)
        if status != ContextValidationStatus.VALID:
            return ExecutionContext(
                validation_status=status,
                preparation_metadata={"error": "Context validation failed."}
            )

        return ExecutionContext(
            validation_status=ContextValidationStatus.VALID,
            stage_contexts=stage_contexts,
            preparation_metadata={"source_allocation_status": "VALID"}
        )

    def _validate_context(self, stage_contexts: List[StageExecutionContext], allocation: AllocationResult) -> ContextValidationStatus:
        """
        Perform lightweight architectural validation.
        Validates missing stage contexts, empty execution context, incomplete allocations.
        """
        if not stage_contexts:
            return ContextValidationStatus.INVALID_CONTEXT
            
        if len(stage_contexts) != len(allocation.stage_allocations):
            return ContextValidationStatus.MISSING_STAGE

        identifiers = set()
        for ctx in stage_contexts:
            if not ctx.allocation_reference:
                return ContextValidationStatus.INCOMPLETE_ALLOCATION
                
            if ctx.stage_identifier in identifiers:
                return ContextValidationStatus.INVALID_CONTEXT
                
            identifiers.add(ctx.stage_identifier)

        return ContextValidationStatus.VALID
