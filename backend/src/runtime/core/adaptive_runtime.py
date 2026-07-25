from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .execution_result_model import ExecutionResult, ExecutionStatus, ExecutionOutcome

class AdaptationStatus(Enum):
    """
    Architectural status of an adaptation recommendation.
    
    This represents adaptation lifecycle ONLY.
    It MUST NEVER contain:
    - monitoring state
    - optimization state
    - learning state
    - execution state
    """
    NO_CHANGE = auto()
    ADAPT = auto()
    DEFER = auto()
    INVALID = auto()


@dataclass(frozen=True)
class StageAdaptationDecision:
    """
    Immutable adaptation recommendation for one execution stage.
    
    Represents a pure adaptation artifact.
    It MUST NEVER contain:
    - monitoring statistics
    - optimization information
    - benchmarking results
    - execution metrics
    - learning history
    - scheduling decisions
    - provider implementation details
    """
    stage_identifier: str
    stage_name: str
    status: AdaptationStatus
    rationale: str = ""
    adaptation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptationDecision:
    """
    Immutable Runtime canonical Adaptation artifact.
    
    AdaptationDecision represents Runtime recommendations for future executions.
    After creation it should never change. Future Runtime systems should consume
    AdaptationDecision rather than mutating it.
    
    It MUST NOT contain:
    - monitoring metrics
    - performance statistics
    - optimization data
    - benchmark results
    - provider implementation details
    - scheduling logic
    - allocation logic
    - hardware discovery information
    - Runtime metrics
    - learned knowledge
    - historical memory
    """
    session_id: str
    stage_decisions: List[StageAdaptationDecision] = field(default_factory=list)
    status: AdaptationStatus = AdaptationStatus.NO_CHANGE
    strategy: str = "DEFAULT_STRATEGY"
    rationale: str = ""
    adaptation_metadata: Dict[str, Any] = field(default_factory=dict)


class AdaptiveRuntime:
    """
    The canonical Runtime authority for execution adaptation.
    
    This subsystem is owned exclusively by RuntimeContext. Future Runtime components must
    obtain adaptation through RuntimeContext rather than constructing AdaptiveRuntime independently.
    
    Responsibilities:
    - Consume immutable ExecutionResult
    - Analyze execution outcomes
    - Produce immutable AdaptationDecision
    - Produce immutable StageAdaptationDecision
    - Preserve Runtime architectural boundaries
    - Remain deterministic, provider independent, and hardware independent
    
    Must NEVER:
    - Execute work
    - Modify ExecutionResult
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Build execution graphs
    - Allocate resources
    - Modify execution context
    - Modify orchestration
    - Retry execution
    - Monitor execution
    - Optimize execution
    - Benchmark hardware
    - Persist learning
    - Store historical intelligence
    """

    def __init__(self) -> None:
        pass

    def evaluate_execution(self, execution_result: ExecutionResult) -> AdaptationDecision:
        """
        Consume immutable ExecutionResult and produce immutable AdaptationDecision.
        Preserves architectural boundaries by strictly decoupling execution from adaptation.
        """
        if not execution_result:
            return AdaptationDecision(
                session_id="invalid",
                status=AdaptationStatus.INVALID,
                rationale="No execution result provided."
            )

        stage_decisions: List[StageAdaptationDecision] = []
        overall_status = AdaptationStatus.NO_CHANGE
        rationale = "Execution proceeded as expected. No adaptation required."
        
        # Analyze completed execution purely for adaptation
        if execution_result.status == ExecutionStatus.FAILED:
            stage_status = AdaptationStatus.ADAPT
            stage_rationale = f"Execution failed. Recommending strategy adaptation."
            overall_status = AdaptationStatus.ADAPT
            rationale = "Execution failures detected. Adapting future execution strategy."
        elif execution_result.status == ExecutionStatus.PENDING:
            stage_status = AdaptationStatus.DEFER
            stage_rationale = f"Execution was pending. Deferring adaptation."
        else:
            stage_status = AdaptationStatus.NO_CHANGE
            stage_rationale = f"Execution completed successfully. No adaptation needed."

        decision = StageAdaptationDecision(
            stage_identifier=execution_result.execution_identity.execution_id,
            stage_name=f"Execution_{execution_result.execution_identity.execution_id}",
            status=stage_status,
            rationale=stage_rationale,
            adaptation_metadata={"source": "deterministic_adaptation_evaluation"}
        )
        stage_decisions.append(decision)

        return AdaptationDecision(
            session_id=execution_result.execution_identity.execution_id,
            stage_decisions=stage_decisions,
            status=overall_status,
            strategy="RETRY_STRATEGY" if overall_status == AdaptationStatus.ADAPT else "DEFAULT_STRATEGY",
            rationale=rationale,
            adaptation_metadata={"evaluated_by": "AdaptiveRuntime"}
        )
