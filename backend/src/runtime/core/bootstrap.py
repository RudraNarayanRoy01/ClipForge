from typing import Dict

from .lifecycle import RuntimeLifecycleCoordinator, RuntimeLifecycleState
from .extension import IRuntimeExtensionPoint


class RuntimeBootstrap:
    """
    The architectural entry point for the Adaptive AI Runtime.
    
    Responsibilities:
    - Establish Runtime subsystem ownership.
    - Initialize the RuntimeLifecycleCoordinator.
    - Expose Runtime Extension Points.
    - Define Runtime startup responsibilities.
    
    It explicitly does NOT:
    - Register extensions (that belongs to the future Capability Registry).
    - Load providers or hardware constraints.
    - Initialize models or execute AI workloads.
    """

    def __init__(self) -> None:
        # 1. Initialize the architectural lifecycle
        self._lifecycle_coordinator = RuntimeLifecycleCoordinator()
        
        # 2. Establish storage for extension points
        self._extension_points: Dict[str, IRuntimeExtensionPoint] = {}

    @property
    def lifecycle(self) -> RuntimeLifecycleCoordinator:
        """Expose the lifecycle coordinator for the Runtime."""
        return self._lifecycle_coordinator

    def register_extension_point(self, name: str, extension_point: IRuntimeExtensionPoint) -> None:
        """
        Register a new extension point owned by the Runtime.
        This allows the Runtime to define where future modules can plug in.
        """
        self._extension_points[name] = extension_point

    def get_extension_point(self, name: str) -> IRuntimeExtensionPoint:
        """Retrieve an extension point by name."""
        if name not in self._extension_points:
            raise KeyError(f"Extension point '{name}' not found.")
        return self._extension_points[name]

    def startup(self) -> None:
        """
        Begin the Runtime lifecycle.
        Transitions the Runtime through its boot sequence.
        """
        # Transition from UNINITIALIZED -> BOOTSTRAPPING
        self._lifecycle_coordinator.transition_to(RuntimeLifecycleState.BOOTSTRAPPING)
        
        # In the future, this phase would involve discovering registries,
        # verifying config schemas, etc., but NOT executing AI.
        
        # Transition from BOOTSTRAPPING -> INITIALIZED
        self._lifecycle_coordinator.transition_to(RuntimeLifecycleState.INITIALIZED)

    def shutdown(self) -> None:
        """
        End the Runtime lifecycle.
        """
        self._lifecycle_coordinator.transition_to(RuntimeLifecycleState.SHUTTING_DOWN)
        # Future: graceful teardown of planners, registries, etc.
        self._lifecycle_coordinator.transition_to(RuntimeLifecycleState.SHUTDOWN)
