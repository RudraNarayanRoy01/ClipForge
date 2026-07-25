from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .scheduling_model import SchedulingDecision


class PlanningStatus(Enum):
    """
    Architectural status of a planning outcome.
    
    This represents architectural planning outcomes only.
    It must NEVER describe execution state, provider health,
    or runtime metrics.
    """
    PLANNED = auto()
    INVALID_REQUEST = auto()
    UNSUPPORTED_WORKLOAD = auto()
    PLANNING_DEFERRED = auto()
    PLANNING_FAILED = auto()


@dataclass(frozen=True)
class PlanningRequest:
    """
    Immutable representation of the Runtime's planning input.
    
    This object represents a pure planning contract containing the 
    execution intent, planning constraints, and workload identity.
    
    It MUST NOT contain:
    - execution state
    - provider instances
    - runtime metrics
    - execution graph
    - allocated resources
    - retry information
    - optimization hints
    - monitoring information
    - execution progress
    
    After creation, this request remains completely immutable.
    """
    scheduling_decision: 'SchedulingDecision'
    execution_intent: str
    workload_identity: str
    planning_constraints: Dict[str, Any] = field(default_factory=dict)
    planning_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Immutable representation of architectural planning intent.
    
    ExecutionPlan is the Runtime's canonical planning artifact. It defines
    only "What work exists?" and "In what logical order should it happen?".
    
    It MUST NOT contain:
    - execution graph (nodes, edges, topology)
    - allocated hardware / reservations
    - runtime / execution state
    - provider instances
    - runtime metrics
    - optimization decisions
    - execution results
    - monitoring information
    - execution handles / threads
    
    Future Runtime systems should consume ExecutionPlan rather than 
    extending or mutating it.
    """
    status: PlanningStatus
    logical_execution_stages: List[str]
    planning_rationale: str
    planning_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeExecutionPlanner:
    """
    The canonical Runtime planning subsystem.
    
    This subsystem converts scheduling decisions into immutable execution blueprints.
    It explicitly performs **Execution Design** only.
    
    It SHOULD:
    - consume SchedulerResult
    - validate planning inputs
    - define logical execution stages
    - produce immutable ExecutionPlan
    - record planning rationale
    
    It MUST NOT:
    - execute providers or instantiate them
    - allocate hardware
    - build execution graphs (topology, dependency edges, synchronization)
    - coordinate execution
    - retry workloads
    - optimize execution
    - monitor runtime
    - perform adaptive learning
    
    Future Runtime components must obtain planning services through RuntimeContext 
    rather than constructing independent RuntimeExecutionPlanner instances.
    """
    def __init__(self) -> None:
        pass

    def plan(self, request: PlanningRequest) -> ExecutionPlan:
        """
        Evaluate the PlanningRequest and transform the scheduling decision 
        into an immutable ExecutionPlan containing logical execution stages.
        """
        # Validate planning inputs
        if request.scheduling_decision is None:
            return ExecutionPlan(
                status=PlanningStatus.INVALID_REQUEST,
                logical_execution_stages=[],
                planning_rationale="PlanningRequest must contain a valid SchedulingDecision.",
                planning_metadata={}
            )

        # In this foundation batch, planning defines a basic, naive sequence of logical stages
        # based on the requested execution intent.
        
        # Example naive logical execution stages mapping
        logical_stages = []
        if request.execution_intent == "VIDEO_PROCESSING":
            logical_stages = [
                "Speech Recognition",
                "Scene Detection",
                "Timeline Analysis",
                "Rendering"
            ]
        elif request.execution_intent == "AUDIO_TRANSCRIPTION":
            logical_stages = [
                "Audio Extraction",
                "Speech Recognition",
                "Transcript Normalization"
            ]
        else:
            logical_stages = [
                "Generic Capability Execution"
            ]

        rationale = f"Planned {len(logical_stages)} logical stages for intent '{request.execution_intent}' based on scheduling outcome '{request.scheduling_decision.status.name}'."

        return ExecutionPlan(
            status=PlanningStatus.PLANNED,
            logical_execution_stages=logical_stages,
            planning_rationale=rationale,
            planning_metadata={
                "workload_identity": request.workload_identity,
                "scheduling_identity": request.scheduling_decision.identity.schedule_id
            }
        )
