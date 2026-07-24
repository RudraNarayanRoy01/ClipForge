from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Set, Optional

from .planner import ExecutionPlan


class GraphValidationStatus(Enum):
    """
    Architectural status of graph validation.
    
    Represents architectural validation only.
    Never execution status.
    """
    VALID = auto()
    INVALID_GRAPH = auto()
    CIRCULAR_DEPENDENCY = auto()
    ORPHAN_NODE = auto()
    DUPLICATE_STAGE = auto()
    INVALID_REFERENCE = auto()
    GRAPH_BUILD_FAILED = auto()


@dataclass(frozen=True)
class ExecutionGraphNode:
    """
    Immutable representation of exactly one logical execution stage.
    
    ExecutionGraphNode represents architecture only.
    It must NEVER contain:
    - Provider instances
    - Runtime state
    - Hardware allocation
    - Execution progress
    - Retry counters
    - Execution timing
    - Runtime metrics
    """
    stage_identifier: str
    stage_name: str
    stage_category: str
    stage_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionDependency:
    """
    Immutable representation of a directed dependency between stages.
    
    ExecutionDependency describes only: "This stage depends on that stage."
    
    It must NEVER describe:
    - scheduling
    - execution order
    - synchronization
    - thread ownership
    - provider ownership
    - execution timing
    """
    source_identifier: str
    target_identifier: str


@dataclass(frozen=True)
class ExecutionGraph:
    """
    Immutable Runtime canonical coordination artifact.
    
    Represents only dependency relationships.
    
    ExecutionGraph must NEVER contain:
    - Execution state
    - Runtime state
    - Provider instances
    - Hardware allocation
    - Resource ownership
    - Runtime metrics
    - Execution progress
    - Execution results
    - Optimization data
    - Monitoring information
    
    Future Runtime systems must consume ExecutionGraph rather than modifying it.
    """
    validation_status: GraphValidationStatus
    nodes: List[ExecutionGraphNode]
    dependencies: List[ExecutionDependency]
    graph_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeExecutionGraphBuilder:
    """
    The canonical Runtime authority for dependency modeling.
    
    This subsystem becomes the Runtime's single architectural authority for dependency modeling.
    It is owned exclusively by RuntimeContext.
    
    Responsibilities:
    - Consume immutable ExecutionPlan
    - Build immutable ExecutionGraph
    - Convert logical execution stages into graph nodes
    - Establish dependency relationships
    - Preserve planning intent
    - Validate graph correctness
    - Produce immutable graph artifact
    
    Must NEVER:
    - Execute work
    - Allocate hardware
    - Instantiate providers
    - Schedule execution
    - Modify ExecutionPlan
    - Retry workloads
    - Coordinate execution
    - Monitor execution
    - Optimize execution
    - Learn from execution
    """

    def __init__(self) -> None:
        pass

    def build(self, plan: ExecutionPlan) -> ExecutionGraph:
        """
        Consume immutable ExecutionPlan and build immutable ExecutionGraph.
        """
        if not plan or not plan.logical_execution_stages:
            return ExecutionGraph(
                validation_status=GraphValidationStatus.INVALID_GRAPH,
                nodes=[],
                dependencies=[],
                graph_metadata={"error": "Empty or missing execution plan."}
            )

        nodes: List[ExecutionGraphNode] = []
        dependencies: List[ExecutionDependency] = []
        node_identifiers: Set[str] = set()

        # Simple linear sequential mapping for Batch 6.2.3
        previous_identifier: Optional[str] = None
        for index, stage_name in enumerate(plan.logical_execution_stages):
            identifier = f"stage_{index}_{stage_name.lower().replace(' ', '_')}"
            
            if identifier in node_identifiers:
                return ExecutionGraph(
                    validation_status=GraphValidationStatus.DUPLICATE_STAGE,
                    nodes=[],
                    dependencies=[],
                    graph_metadata={"error": f"Duplicate stage identifier: {identifier}"}
                )
            
            node = ExecutionGraphNode(
                stage_identifier=identifier,
                stage_name=stage_name,
                stage_category="LogicalStage",
                stage_metadata={"original_index": index}
            )
            nodes.append(node)
            node_identifiers.add(identifier)

            if previous_identifier:
                # "This stage depends on that stage"
                # source_identifier depends on target_identifier
                # current stage depends on previous stage
                dependency = ExecutionDependency(
                    source_identifier=identifier,
                    target_identifier=previous_identifier
                )
                dependencies.append(dependency)
                
            previous_identifier = identifier

        # Validate
        status = self._validate_graph(nodes, dependencies)
        if status != GraphValidationStatus.VALID:
            return ExecutionGraph(
                validation_status=status,
                nodes=[],
                dependencies=[],
                graph_metadata={"error": "Graph validation failed."}
            )

        return ExecutionGraph(
            validation_status=GraphValidationStatus.VALID,
            nodes=nodes,
            dependencies=dependencies,
            graph_metadata={"plan_rationale": plan.planning_rationale}
        )

    def _validate_graph(self, nodes: List[ExecutionGraphNode], dependencies: List[ExecutionDependency]) -> GraphValidationStatus:
        """
        Perform lightweight architectural validation.
        Validates duplicate stage identifiers, circular dependencies, missing targets, orphan nodes, invalid references.
        """
        if not nodes:
            return GraphValidationStatus.INVALID_GRAPH

        node_ids = {node.stage_identifier for node in nodes}
        
        # Check invalid references
        for dep in dependencies:
            if dep.source_identifier not in node_ids or dep.target_identifier not in node_ids:
                return GraphValidationStatus.INVALID_REFERENCE
                
        # Check orphan nodes (in a connected graph, all nodes except maybe one should have incoming or outgoing edges)
        if len(nodes) > 1:
            connected_nodes = set()
            for dep in dependencies:
                connected_nodes.add(dep.source_identifier)
                connected_nodes.add(dep.target_identifier)
            
            if len(connected_nodes) != len(nodes):
                return GraphValidationStatus.ORPHAN_NODE

        # Check circular dependencies using DFS
        adjacency_list: Dict[str, List[str]] = {nid: [] for nid in node_ids}
        for dep in dependencies:
            adjacency_list[dep.source_identifier].append(dep.target_identifier)
            
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in adjacency_list[node_id]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node_id)
            return False

        for node_id in node_ids:
            if node_id not in visited:
                if is_cyclic(node_id):
                    return GraphValidationStatus.CIRCULAR_DEPENDENCY
                    
        return GraphValidationStatus.VALID
