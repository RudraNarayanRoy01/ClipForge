import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.resource_allocator import (
    AllocationResult,
    AllocationValidationStatus,
    StageAllocation,
    LogicalResourceProfile
)
from src.runtime.core.execution_context import (
    ContextValidationStatus,
    StageExecutionContext,
    ExecutionContext,
    RuntimeExecutionContextFactory
)
from src.runtime.core.context import RuntimeContext


def test_stage_execution_context_immutability():
    """Verify StageExecutionContext is immutable to protect architectural boundaries."""
    ctx = StageExecutionContext(
        stage_identifier="test-stage-1",
        stage_name="Test Stage",
        allocation_reference="test-stage-1",
        dependency_references=["dep-1"],
        capability_requirements=["CUDA"],
        execution_preparation_metadata={"prepared_from": "test"}
    )
    
    with pytest.raises(FrozenInstanceError):
        ctx.stage_identifier = "mutated"
        
    with pytest.raises(FrozenInstanceError):
        ctx.execution_preparation_metadata = {}


def test_execution_context_immutability():
    """Verify ExecutionContext is immutable to protect architectural boundaries."""
    ctx = ExecutionContext(
        validation_status=ContextValidationStatus.VALID,
        stage_contexts=[],
        preparation_metadata={"source": "test"}
    )
    
    with pytest.raises(FrozenInstanceError):
        ctx.validation_status = ContextValidationStatus.INVALID_CONTEXT
        
    with pytest.raises(FrozenInstanceError):
        ctx.preparation_metadata = {}


def test_runtime_context_exposes_factory():
    """Verify RuntimeContext owns and exposes RuntimeExecutionContextFactory."""
    context = RuntimeContext()
    assert hasattr(context, 'execution_context_factory')
    
    factory = context.execution_context_factory
    assert isinstance(factory, RuntimeExecutionContextFactory)
    assert factory is context.execution_context_factory  # Should return the same instance


def test_factory_consumes_allocation_result():
    """Verify factory successfully consumes valid AllocationResult and produces ExecutionContext."""
    allocations = [
        StageAllocation(
            stage_identifier="stage-1",
            stage_name="Stage 1",
            logical_compute_profile=LogicalResourceProfile.STANDARD_COMPUTE,
            logical_memory_profile=LogicalResourceProfile.STANDARD_MEMORY,
            capability_requirements=["CPU"]
        ),
        StageAllocation(
            stage_identifier="stage-2",
            stage_name="Stage 2",
            logical_compute_profile=LogicalResourceProfile.GPU_PREFERRED,
            logical_memory_profile=LogicalResourceProfile.HIGH_MEMORY,
            capability_requirements=["CUDA"]
        )
    ]
    
    allocation_result = AllocationResult(
        validation_status=AllocationValidationStatus.VALID,
        stage_allocations=allocations,
        allocation_metadata={}
    )
    
    factory = RuntimeExecutionContextFactory()
    context = factory.create_context(allocation_result)
    
    assert isinstance(context, ExecutionContext)
    assert context.validation_status == ContextValidationStatus.VALID
    assert len(context.stage_contexts) == 2
    
    # Verify mapping
    assert context.stage_contexts[0].stage_identifier == "stage-1"
    assert "CPU" in context.stage_contexts[0].capability_requirements
    assert context.stage_contexts[1].stage_identifier == "stage-2"
    assert "CUDA" in context.stage_contexts[1].capability_requirements


def test_factory_detects_incomplete_allocation():
    """Verify factory architectural validation detects incomplete allocation input."""
    # Create an invalid allocation result
    invalid_allocation = AllocationResult(
        validation_status=AllocationValidationStatus.INCOMPLETE_GRAPH,
        stage_allocations=[],
        allocation_metadata={}
    )
    
    factory = RuntimeExecutionContextFactory()
    context = factory.create_context(invalid_allocation)
    
    assert context.validation_status == ContextValidationStatus.INCOMPLETE_ALLOCATION
    assert len(context.stage_contexts) == 0


def test_factory_detects_duplicate_stage_contexts():
    """Verify factory validation catches duplicate stages."""
    allocations = [
        StageAllocation(
            stage_identifier="dup-stage",
            stage_name="Stage 1",
            logical_compute_profile=LogicalResourceProfile.STANDARD_COMPUTE,
            logical_memory_profile=LogicalResourceProfile.STANDARD_MEMORY
        ),
        StageAllocation(
            stage_identifier="dup-stage",  # Duplicate
            stage_name="Stage 2",
            logical_compute_profile=LogicalResourceProfile.STANDARD_COMPUTE,
            logical_memory_profile=LogicalResourceProfile.STANDARD_MEMORY
        )
    ]
    
    # Assume validation bypass or graph error allowed this through somehow
    allocation_result = AllocationResult(
        validation_status=AllocationValidationStatus.VALID,
        stage_allocations=allocations,
        allocation_metadata={}
    )
    
    factory = RuntimeExecutionContextFactory()
    context = factory.create_context(allocation_result)
    
    assert context.validation_status == ContextValidationStatus.INVALID_CONTEXT
    assert "Duplicate stage identifier" in context.preparation_metadata.get("error", "")


def test_execution_context_contains_no_execution_state():
    """Verify architectural boundaries: context must not contain execution or hardware state."""
    allocations = [
        StageAllocation(
            stage_identifier="stage-1",
            stage_name="Stage 1",
            logical_compute_profile=LogicalResourceProfile.STANDARD_COMPUTE,
            logical_memory_profile=LogicalResourceProfile.STANDARD_MEMORY
        )
    ]
    allocation_result = AllocationResult(
        validation_status=AllocationValidationStatus.VALID,
        stage_allocations=allocations
    )
    
    factory = RuntimeExecutionContextFactory()
    context = factory.create_context(allocation_result)
    
    # Assert properties don't exist
    assert not hasattr(context, "execution_state")
    assert not hasattr(context, "provider_instances")
    assert not hasattr(context, "hardware_handles")
    assert not hasattr(context, "gpu_identifiers")
    assert not hasattr(context, "cpu_identifiers")
    
    for stage_ctx in context.stage_contexts:
        assert not hasattr(stage_ctx, "execution_state")
        assert not hasattr(stage_ctx, "provider_instances")
        assert not hasattr(stage_ctx, "hardware_handles")
        assert not hasattr(stage_ctx, "cuda_objects")
