from datetime import datetime
from types import MappingProxyType

from .scheduling_model import SchedulingDecision

from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity

class RuntimeExecutor:
    """
    The canonical Runtime execution engine.
    
    Performs exactly one responsibility:
    SchedulingDecision + RuntimeExecutionIdentity -> RuntimeExecutionResult
    
    It is NOT:
    - a Workflow Engine
    - a Scheduler
    - a Lifecycle Manager
    - a Retry Coordinator
    - an Observation Service
    - an Optimization Engine
    - a Resource Manager
    - an Orchestrator
    """

    def __init__(self) -> None:
        pass

    def _execute_attempt(self) -> None:
        """
        Placeholder for actual execution logic.
        For now, we simulate execution success.
        """
        pass

    def execute(
        self, 
        scheduling_decision: SchedulingDecision, 
        identity: RuntimeExecutionIdentity
    ) -> RuntimeExecutionResult:
        """
        Consumes SchedulingDecision.
        Validates input.
        Executes approved Runtime work.
        Produces immutable RuntimeExecutionResult.
        """
        if not scheduling_decision:
            raise ValueError("scheduling_decision is required")
        if not identity:
            raise ValueError("identity is required")

        started_at = datetime.utcnow()
        outcome = RuntimeExecutionOutcome.SUCCESS
        failure_reason = None
        
        try:
            self._execute_attempt()
        except Exception as e:
            outcome = RuntimeExecutionOutcome.FAILED
            failure_reason = f"Execution failed: {type(e).__name__} - {str(e)}"
            
        completed_at = datetime.utcnow()
        duration_seconds = max(0.0, (completed_at - started_at).total_seconds())

        return RuntimeExecutionResult(
            identity=identity,
            outcome=outcome,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            failure_reason=failure_reason,
            metadata=MappingProxyType({})
        )
