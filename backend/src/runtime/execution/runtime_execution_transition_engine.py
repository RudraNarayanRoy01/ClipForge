from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_transition_validator import RuntimeExecutionTransitionValidator

class RuntimeExecutionTransitionEngine:
    """
    Stateless boundary that applies a validated Runtime Execution Lifecycle transition.
    
    Responsibilities:
    - Receives a requested lifecycle transition.
    - Delegates legality determination exclusively to RuntimeExecutionTransitionValidator.
    - If valid, returns the target RuntimeExecutionStatus.
    - If invalid, raises ValueError.
    
    Does NOT:
    - Determine transition legality internally.
    - Mutate session, state, or other lifecycle models.
    - Orchestrate, execute, or schedule workloads.
    """
    
    def __init__(self, validator: RuntimeExecutionTransitionValidator = None):
        self._validator = (
            validator 
            if validator is not None 
            else RuntimeExecutionTransitionValidator()
        )

    def transition(
        self,
        current_status: RuntimeExecutionStatus,
        target_status: RuntimeExecutionStatus,
    ) -> RuntimeExecutionStatus:
        """
        Applies the requested transition from current_status to target_status.
        
        Args:
            current_status: The current RuntimeExecutionStatus.
            target_status: The target RuntimeExecutionStatus.
            
        Returns:
            The target RuntimeExecutionStatus if the transition is legal.
            
        Raises:
            ValueError: If the transition is illegal or input types are invalid.
        """
        if not self._validator.is_valid(current_status, target_status):
            raise ValueError(
                f"Invalid Runtime Execution transition from {current_status} to {target_status}"
            )
            
        return target_status
