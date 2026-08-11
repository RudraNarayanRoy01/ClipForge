from dataclasses import dataclass, field

from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_transition_engine import RuntimeExecutionTransitionEngine


@dataclass(frozen=True)
class RuntimeExecutionLifecycleState:
    """
    Immutable state-bearing boundary representing the current Runtime Execution Lifecycle status.
    
    Responsibilities:
    - Holds the authoritative `RuntimeExecutionStatus`.
    - Starts at `RuntimeExecutionStatus.PREPARED` by default.
    - Delegates transitions safely through `RuntimeExecutionTransitionEngine`.
    - Returns a new immutable `RuntimeExecutionLifecycleState` upon valid transition.
    
    Does NOT:
    - Duplicate the transition matrix.
    - Determine transition legality internally.
    - Hold execution or scheduling metadata.
    - Orchestrate or execute workloads.
    """
    current_status: RuntimeExecutionStatus = RuntimeExecutionStatus.PREPARED
    
    _engine: RuntimeExecutionTransitionEngine = field(
        default_factory=RuntimeExecutionTransitionEngine,
        compare=False,
        repr=False,
        hash=False
    )

    def transition_to(self, target_status: RuntimeExecutionStatus) -> 'RuntimeExecutionLifecycleState':
        """
        Transitions to a new lifecycle state via the certified Engine.
        
        Args:
            target_status: The target RuntimeExecutionStatus to transition to.
            
        Returns:
            A new RuntimeExecutionLifecycleState containing the resulting status.
            
        Raises:
            ValueError: If the transition is illegal or the target status is invalid.
        """
        # The Engine handles legality and type validation by delegating to Validator,
        # and raises ValueError if invalid.
        resulting_status = self._engine.transition(self.current_status, target_status)
        
        return RuntimeExecutionLifecycleState(
            current_status=resulting_status,
            _engine=self._engine
        )
