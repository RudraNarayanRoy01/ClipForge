import pytest
from src.runtime.core.resource_allocator import (
    RuntimeResourceAllocator,
    AllocationResult,
    StageAllocation,
    LogicalResourceProfile,
    AllocationValidationStatus,
)
from src.runtime.core.execution_graph import (
    ExecutionGraph,
    GraphValidationStatus,
    ExecutionGraphNode,
    ExecutionDependency,
)
from src.runtime.core.context import RuntimeContext


def test_allocation_result_immutability():
    """Verify AllocationResult is architecturally immutable."""
    result = AllocationResult(
        validation_status=AllocationValidationStatus.VALID,
        stage_allocations=[],
        allocation_metadata={"test": "data"}
    )
    
    with pytest.raises(Exception):
        # dataclass(frozen=True) prevents mutation
        result.validation_status = AllocationValidationStatus.INVALID_ALLOCATION


def test_stage_allocation_immutability():
    """Verify StageAllocation is architecturally immutable."""
    alloc = StageAllocation(
        stage_identifier="test_stage",
        stage_name="Test Stage",
        logical_compute_profile=LogicalResourceProfile.STANDARD_COMPUTE,
        logical_memory_profile=LogicalResourceProfile.STANDARD_MEMORY
    )
    
    with pytest.raises(Exception):
        # dataclass(frozen=True) prevents mutation
        alloc.stage_name = "Mutated Stage"


def test_runtime_context_exposes_resource_allocator():
    """Verify RuntimeContext owns and exposes RuntimeResourceAllocator."""
    context = RuntimeContext()
    assert context.resource_allocator is not None
    assert isinstance(context.resource_allocator, RuntimeResourceAllocator)


def test_allocator_consumes_graph_and_produces_result():
    """Verify the primary boundary: Graph in -> AllocationResult out."""
    nodes = [
        ExecutionGraphNode("stage_1", "Transcription", "Audio"),
        ExecutionGraphNode("stage_2", "Analysis", "NLP")
    ]
    dependencies = [
        ExecutionDependency("stage_2", "stage_1")
    ]
    graph = ExecutionGraph(
        validation_status=GraphValidationStatus.VALID,
        nodes=nodes,
        dependencies=dependencies,
        graph_metadata={}
    )
    
    allocator = RuntimeResourceAllocator()
    result = allocator.allocate(graph)
    
    assert isinstance(result, AllocationResult)
    assert result.validation_status == AllocationValidationStatus.VALID
    assert len(result.stage_allocations) == 2


def test_allocation_validation_detects_incomplete_graph():
    """Verify allocator rejects invalid graphs."""
    graph = ExecutionGraph(
        validation_status=GraphValidationStatus.CIRCULAR_DEPENDENCY,
        nodes=[],
        dependencies=[],
        graph_metadata={}
    )
    
    allocator = RuntimeResourceAllocator()
    result = allocator.allocate(graph)
    
    assert result.validation_status == AllocationValidationStatus.INCOMPLETE_GRAPH


def test_allocation_validation_detects_empty_graph():
    """Verify allocator rejects graphs with no nodes."""
    graph = ExecutionGraph(
        validation_status=GraphValidationStatus.VALID,
        nodes=[],
        dependencies=[],
        graph_metadata={}
    )
    
    allocator = RuntimeResourceAllocator()
    result = allocator.allocate(graph)
    
    assert result.validation_status == AllocationValidationStatus.INCOMPLETE_GRAPH


def test_allocation_validation_detects_duplicate_stages():
    """Verify allocator detects duplicate stage identifiers during mapping."""
    nodes = [
        ExecutionGraphNode("stage_1", "Transcription", "Audio"),
        ExecutionGraphNode("stage_1", "Duplicate", "Audio")
    ]
    graph = ExecutionGraph(
        validation_status=GraphValidationStatus.VALID,
        nodes=nodes,
        dependencies=[],
        graph_metadata={}
    )
    
    allocator = RuntimeResourceAllocator()
    result = allocator.allocate(graph)
    
    assert result.validation_status == AllocationValidationStatus.DUPLICATE_STAGE


def test_allocation_result_contains_logical_profiles_only():
    """
    Verify AllocationResult contains no execution state,
    hardware handles, or provider instances.
    """
    nodes = [
        ExecutionGraphNode("stage_1", "GPU Heavy Render", "Video")
    ]
    graph = ExecutionGraph(
        validation_status=GraphValidationStatus.VALID,
        nodes=nodes,
        dependencies=[],
        graph_metadata={}
    )
    
    allocator = RuntimeResourceAllocator()
    result = allocator.allocate(graph)
    
    assert result.validation_status == AllocationValidationStatus.VALID
    
    stage = result.stage_allocations[0]
    
    # Must contain logical profiles
    assert isinstance(stage.logical_compute_profile, LogicalResourceProfile)
    assert isinstance(stage.logical_memory_profile, LogicalResourceProfile)
    
    # Must NOT contain provider instances or hardware handles
    assert not hasattr(stage, 'provider')
    assert not hasattr(stage, 'cuda_context')
    assert not hasattr(stage, 'gpu_handle')
    assert not hasattr(stage, 'execution_state')
