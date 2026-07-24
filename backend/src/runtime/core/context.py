from typing import Dict

from .metadata import RuntimeMetadata
from .lifecycle import RuntimeLifecycleCoordinator
from .extension import IRuntimeExtensionPoint
from .capabilities import RuntimeCapabilityRegistry


class RuntimeContext:
    """
    The canonical representation of a Runtime instance.
    
    This is the central architectural object shared across future Runtime components.
    It provides a stable composition of the Runtime's core services.
    
    After construction, these references remain stable. 
    Future modules should consume these references rather than replacing them.
    """

    def __init__(self) -> None:
        self._metadata = RuntimeMetadata()
        self._lifecycle_coordinator = RuntimeLifecycleCoordinator()
        self._extension_points: Dict[str, IRuntimeExtensionPoint] = {}
        self._capability_registry = RuntimeCapabilityRegistry()

    @property
    def metadata(self) -> RuntimeMetadata:
        """Expose descriptive metadata about this Runtime instance."""
        return self._metadata

    @property
    def lifecycle(self) -> RuntimeLifecycleCoordinator:
        """Expose the canonical lifecycle coordinator for this Runtime instance."""
        return self._lifecycle_coordinator

    @property
    def capability_registry(self) -> RuntimeCapabilityRegistry:
        """
        Expose the canonical capability registry for this Runtime instance.
        
        This serves as the single source of truth for architectural capabilities
        understood by this Runtime.
        """
        return self._capability_registry

    def register_extension_point(self, name: str, extension_point: IRuntimeExtensionPoint) -> None:
        """
        Register a new extension point owned by the Runtime Context.
        
        Extension Points expose Runtime integration surfaces and define extensibility,
        supporting the Open/Closed Principle. They do NOT execute logic or discover resources.
        """
        if name in self._extension_points:
            raise ValueError(f"Extension point '{name}' is already registered.")
        self._extension_points[name] = extension_point

    def get_extension_point(self, name: str) -> IRuntimeExtensionPoint:
        """Retrieve an extension point by name."""
        if name not in self._extension_points:
            raise KeyError(f"Extension point '{name}' not found.")
        return self._extension_points[name]
