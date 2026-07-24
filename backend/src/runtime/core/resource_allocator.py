from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional

from .execution_graph import ExecutionGraph, GraphValidationStatus


class LogicalResourceProfile(Enum):
    """
    Hardware-independent architectural representation of logical resource requirements.
    
    These describe architectural requirements only.
    They must never represent:
    - physical hardware
    - actual reservations
    - available devices
    - execution decisions
    """
    LOW_COMPUTE = auto()
    STANDARD_COMPUTE = auto()
    HIGH_COMPUTE = auto()
    LOW_MEMORY = auto()
    STANDARD_MEMORY = auto()
    HIGH_MEMORY = auto()
    CPU_PREFERRED = auto()
    GPU_PREFERRED = auto()
    HYBRID_COMPUTE = auto()


class AllocationValidationStatus(Enum):
    """
    Architectural status of allocation validation.
    
    Validation verifies architectural correctness only, NEVER execution status.
    It does not perform hardware, provider, or scheduling validation.
    """
    VALID = auto()
    INVALID_ALLOCATION = auto()
    INCOMPLETE_GRAPH = auto()
    MISSING_REQUIREMENTS = auto()
    UNSUPPORTED_PROFILE = auto()
    DUPLICATE_STAGE = auto()
    VALIDATION_FAILED = auto()


@dataclass(frozen=True)
class StageAllocation:
    """
    Immutable representation of exactly one execution stage's logical resource requirements.
    
    StageAllocation represents a pure architectural representation of resource intent.
    
    It must NEVER contain:
    - physical GPU/CPU/RAM handles
    - hardware identifiers
    - CUDA/Vulkan/DirectML objects
    - provider instances
    - execution state
    - runtime state
    - monitoring information
    - optimization information
    """
    stage_identifier: str
    stage_name: str
    logical_compute_profile: LogicalResourceProfile
    logical_memory_profile: LogicalResourceProfile
    capability_requirements: List[str] = field(default_factory=list)
    preferred_execution_class: Optional[str] = None
    resource_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AllocationResult:
    """
    Immutable Runtime canonical Resource Coordination artifact.
    
    Represents architectural allocation intent rather than runtime allocation.
    After creation it should never change.
    
    It must NOT contain:
    - execution state
    - runtime state
    - provider instances
    - hardware reservations
    - GPU/CPU/memory handles
    - runtime metrics
    - execution progress/results
    - monitoring/optimization information
    """
    validation_status: AllocationValidationStatus
    stage_allocations: List[StageAllocation] = field(default_factory=list)
    allocation_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeResourceAllocator:
    """
    The canonical Runtime authority for logical resource allocation.
    
    This subsystem becomes the Runtime's single architectural authority for 
    logical resource allocation. It is owned exclusively by RuntimeContext.
    
    Responsibilities:
    - Consume immutable ExecutionGraph
    - Analyze stage requirements
    - Determine logical resource profiles
    - Validate allocation integrity
    - Preserve dependency relationships and planning intent
    - Produce immutable AllocationResult
    
    Must NEVER:
    - Reserve GPU memory / CPU resources / RAM
    - Allocate hardware
    - Instantiate providers
    - Create execution contexts
    - Launch workloads
    - Coordinate / monitor / optimize execution
    - Perform adaptive learning
    """

    def __init__(self) -> None:
        pass

    def allocate(self, graph: ExecutionGraph) -> AllocationResult:
        """
        Consume immutable ExecutionGraph and produce immutable AllocationResult.
        """
        if not graph or not getattr(graph, 'nodes', None):
            return AllocationResult(
                validation_status=AllocationValidationStatus.INCOMPLETE_GRAPH,
                allocation_metadata={"error": "Empty or missing execution graph."}
            )

        if graph.validation_status != GraphValidationStatus.VALID:
            return AllocationResult(
                validation_status=AllocationValidationStatus.INCOMPLETE_GRAPH,
                allocation_metadata={"error": f"Graph is invalid: {graph.validation_status}"}
            )

        allocations: List[StageAllocation] = []
        seen_identifiers = set()

        for node in graph.nodes:
            identifier = node.stage_identifier
            
            if identifier in seen_identifiers:
                return AllocationResult(
                    validation_status=AllocationValidationStatus.DUPLICATE_STAGE,
                    allocation_metadata={"error": f"Duplicate stage identifier: {identifier}"}
                )
            
            seen_identifiers.add(identifier)
            
            # Simple heuristic mapping for Batch 6.2.4 based on stage_category or name
            # Real allocation logic would use plan rationale, capability requirements, etc.
            compute_profile = LogicalResourceProfile.STANDARD_COMPUTE
            memory_profile = LogicalResourceProfile.STANDARD_MEMORY
            
            name_lower = node.stage_name.lower()
            if "gpu" in name_lower or "render" in name_lower or "inference" in name_lower:
                compute_profile = LogicalResourceProfile.GPU_PREFERRED
                memory_profile = LogicalResourceProfile.HIGH_MEMORY
            elif "cpu" in name_lower or "light" in name_lower:
                compute_profile = LogicalResourceProfile.CPU_PREFERRED
                memory_profile = LogicalResourceProfile.LOW_MEMORY

            allocation = StageAllocation(
                stage_identifier=identifier,
                stage_name=node.stage_name,
                logical_compute_profile=compute_profile,
                logical_memory_profile=memory_profile,
                resource_metadata={"derived_from": "heuristic"}
            )
            allocations.append(allocation)

        status = self._validate_allocation(allocations, graph)
        if status != AllocationValidationStatus.VALID:
            return AllocationResult(
                validation_status=status,
                allocation_metadata={"error": "Allocation validation failed."}
            )

        return AllocationResult(
            validation_status=AllocationValidationStatus.VALID,
            stage_allocations=allocations,
            allocation_metadata={"source_graph_status": "VALID"}
        )

    def _validate_allocation(self, allocations: List[StageAllocation], graph: ExecutionGraph) -> AllocationValidationStatus:
        """
        Perform lightweight architectural validation.
        Validates duplicate stage identifiers, missing requirements, empty allocations.
        """
        if not allocations:
            return AllocationValidationStatus.INVALID_ALLOCATION
            
        if len(allocations) != len(graph.nodes):
            return AllocationValidationStatus.MISSING_REQUIREMENTS

        identifiers = set()
        for alloc in allocations:
            if not alloc.logical_compute_profile or not alloc.logical_memory_profile:
                return AllocationValidationStatus.MISSING_REQUIREMENTS
                
            if alloc.stage_identifier in identifiers:
                return AllocationValidationStatus.DUPLICATE_STAGE
                
            identifiers.add(alloc.stage_identifier)

        return AllocationValidationStatus.VALID
