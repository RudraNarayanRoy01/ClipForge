from .lifecycle import RuntimeLifecycleState
from .context import RuntimeContext


class RuntimeBootstrap:
    """
    The architectural entry point for the Adaptive AI Runtime.
    
    Responsibilities:
    - Establish Runtime subsystem ownership via RuntimeContext.
    - Define Runtime startup and shutdown responsibilities.
    
    It explicitly does NOT:
    - Execute Runtime logic.
    - Discover capabilities or hardware.
    - Manage lifecycle directly (delegates to Context).
    - Schedule execution or instantiate providers.
    """

    def __init__(self) -> None:
        # 1. Establish the canonical Runtime representation
        self._context = RuntimeContext()

    @property
    def context(self) -> RuntimeContext:
        """
        Expose the canonical RuntimeContext.
        Every future Runtime subsystem should communicate through this Context
        rather than directly referencing Bootstrap.
        """
        return self._context

    def startup(self) -> None:
        """
        Begin the Runtime lifecycle.
        Transitions the Runtime through its boot sequence.
        """
        # Transition from UNINITIALIZED -> BOOTSTRAPPING
        self._context.lifecycle.transition_to(RuntimeLifecycleState.BOOTSTRAPPING)
        
        # In the future, this phase would involve discovering registries,
        # verifying config schemas, etc., but NOT executing AI.
        
        # Transition from BOOTSTRAPPING -> INITIALIZED
        self._context.lifecycle.transition_to(RuntimeLifecycleState.INITIALIZED)

    def shutdown(self) -> None:
        """
        End the Runtime lifecycle.
        """
        self._context.lifecycle.transition_to(RuntimeLifecycleState.SHUTTING_DOWN)
        # Future: graceful teardown of planners, registries, etc.
        self._context.lifecycle.transition_to(RuntimeLifecycleState.SHUTDOWN)
