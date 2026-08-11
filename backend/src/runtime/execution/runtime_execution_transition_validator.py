from typing import Any
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus

class RuntimeExecutionTransitionValidator:
    """
    Stateless, deterministic validator for Runtime Execution Lifecycle transitions.
    
    Responsibilities:
    - Validates formal lifecycle transitions between RuntimeExecutionStatus states.
    - Represents the certified Batch 6A.8.2 transition matrix.
    
    Does NOT:
    - Mutate state.
    - Handle exceptions or outcomes (e.g. RuntimeExecutionOutcome).
    - Handle scheduling status.
    - Represent initialization (`None` -> `PREPARED`).
    """

    _VALID_TRANSITIONS = {
        (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY),
        (RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING),
        (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.COMPLETED),
        (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.FAILED),
    }

    def is_valid(
        self,
        current_status: Any,
        target_status: Any,
    ) -> bool:
        """
        Determine if the transition from current_status to target_status is valid.
        
        Returns False if the inputs are not valid RuntimeExecutionStatus instances,
        or if the transition is not explicitly permitted by the certified lifecycle contract.
        """
        if not isinstance(current_status, RuntimeExecutionStatus) or not isinstance(target_status, RuntimeExecutionStatus):
            return False

        return (current_status, target_status) in self._VALID_TRANSITIONS
