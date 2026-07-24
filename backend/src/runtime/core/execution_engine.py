from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .orchestrator import ExecutionSession, StageOrchestrationStatus


class ExecutionStatus(Enum):
    """
    Architectural status of stage execution.
    
    This represents deterministic execution lifecycle ONLY.
    It MUST NEVER contain:
    - monitoring state
    - adaptive state
    - optimization state
    - learning state
    """
    NOT_STARTED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(frozen=True)
class StageExecutionResult:
    """
    Immutable outcome for one execution stage.
    
    Represents a pure execution artifact.
    It MUST NEVER contain:
    - monitoring statistics
    - optimization information
    - adaptive information
    - benchmark information
    - scheduling decisions
    - orchestration metadata
    - provider selection data
    """
    stage_identifier: str
    stage_name: str
    status: ExecutionStatus
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable Runtime canonical Execution artifact.
    
    ExecutionResult represents deterministic execution completion.
    After creation it should never change. Future Runtime systems should consume
    ExecutionResult rather than mutating it.
    
    It MUST NOT contain:
    - monitoring metrics
    - performance metrics
    - optimization information
    - adaptive decisions
    - scheduling information
    - provider selection information
    - resource allocation information
    - hardware discovery information
    - learning information
    """
    session_id: str
    stage_results: List[StageExecutionResult] = field(default_factory=list)
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeExecutionEngine:
    """
    The canonical Runtime authority for deterministic execution.
    
    This subsystem is owned exclusively by RuntimeContext. Future Runtime components must
    obtain execution through RuntimeContext rather than constructing RuntimeExecutionEngine independently.
    
    Responsibilities:
    - Consume immutable ExecutionSession
    - Execute READY stages
    - Preserve orchestration ordering
    - Preserve dependency ordering
    - Produce immutable StageExecutionResult
    - Produce immutable ExecutionResult
    
    Must NEVER:
    - Reorder stages
    - Modify dependencies
    - Perform provider selection
    - Allocate hardware
    - Optimize execution
    - Retry failures
    - Adapt execution
    - Monitor execution
    """

    def __init__(self) -> None:
        pass

    def execute_session(self, session: ExecutionSession) -> ExecutionResult:
        """
        Consume immutable ExecutionSession and produce immutable ExecutionResult.
        Preserves orchestration and dependency ordering exactly as prepared.
        """
        if not session or not session.stage_states:
            return ExecutionResult(
                session_id="invalid-session",
                status=ExecutionStatus.FAILED,
                execution_metadata={"error": "Empty or missing execution session."}
            )

        stage_results: List[StageExecutionResult] = []
        overall_status = ExecutionStatus.COMPLETED
        
        # We execute exactly what Orchestrator prepared.
        # In a real engine, we would respect StageOrchestrationStatus.READY vs BLOCKED.
        # For this architectural mock, we assume all READY stages execute.
        for stage_state in session.stage_states:
            if stage_state.dependency_readiness == StageOrchestrationStatus.READY:
                # Mock successful execution
                stage_status = ExecutionStatus.COMPLETED
                stage_metadata = {"outcome": "executed"}
            else:
                # Mock blocked/waiting execution
                stage_status = ExecutionStatus.NOT_STARTED
                stage_metadata = {"outcome": f"skipped_due_to_orchestration_status_{stage_state.dependency_readiness.name}"}
                overall_status = ExecutionStatus.FAILED
                
            result = StageExecutionResult(
                stage_identifier=stage_state.stage_identifier,
                stage_name=stage_state.stage_name,
                status=stage_status,
                execution_metadata=stage_metadata
            )
            stage_results.append(result)

        return ExecutionResult(
            session_id="simulated-session-id",
            stage_results=stage_results,
            status=overall_status,
            execution_metadata={"source": "deterministic_execution"}
        )
