from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult


class RuntimeExecutionTerminalConsistencyValidator:
    """
    Determines if a lifecycle state is semantically consistent with an execution result.
    
    This is an observational, stateless, and immutable boundary.
    It does not mutate state or result, nor does it perform lifecycle transitions.
    
    ABORTED is a structural reset state, not an execution attempt outcome, and has no certified result mapping.
    CANCELLED is a legitimate execution outcome, but has no certified lifecycle-state mapping.
    """

    def is_consistent(
        self,
        lifecycle_state: RuntimeExecutionLifecycleState,
        result: RuntimeExecutionResult
    ) -> bool:
        """
        Evaluate semantic consistency between a lifecycle state and a finalized execution result.
        
        Args:
            lifecycle_state: The current RuntimeExecutionLifecycleState.
            result: The finalized RuntimeExecutionResult.
            
        Returns:
            True if the state and result can legitimately describe the same execution attempt,
            False otherwise (including invalid input types).
        """
        # Type enforcement: Inputs must be valid instances of the expected domain types
        if not isinstance(lifecycle_state, RuntimeExecutionLifecycleState) or not isinstance(result, RuntimeExecutionResult):
            return False

        status = lifecycle_state.current_status
        outcome = result.outcome

        # The only certified mappings are COMPLETED <-> SUCCESS and FAILED <-> FAILED.
        if status == RuntimeExecutionStatus.COMPLETED and outcome == RuntimeExecutionOutcome.SUCCESS:
            return True
            
        if status == RuntimeExecutionStatus.FAILED and outcome == RuntimeExecutionOutcome.FAILED:
            return True

        # All other combinations are invalid, unsupported, or represent contradictory semantics.
        # This includes:
        # - Any active state (PREPARED, READY, EXECUTING) with any result.
        # - ABORTED status with any result.
        # - Any status with CANCELLED outcome.
        return False
