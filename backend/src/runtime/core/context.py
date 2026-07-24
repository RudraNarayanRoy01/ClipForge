from typing import Dict

from .metadata import RuntimeMetadata
from .lifecycle import RuntimeLifecycleCoordinator
from .extension import IRuntimeExtensionPoint
from .capabilities import RuntimeCapabilityRegistry


from .discovery import RuntimeResourceDiscovery
from .providers import RuntimeProviderRegistry
from .hardware import RuntimeHardwareDiscovery
from .selection import RuntimeProviderSelection
from .scheduler import RuntimeScheduler
from .planner import RuntimeExecutionPlanner

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
        self._resource_discovery = RuntimeResourceDiscovery()
        self._provider_registry = RuntimeProviderRegistry()
        self._hardware_discovery = RuntimeHardwareDiscovery()
        self._provider_selection = RuntimeProviderSelection(
            self._capability_registry,
            self._provider_registry,
            self._hardware_discovery
        )
        self._scheduler = RuntimeScheduler()
        self._execution_planner = RuntimeExecutionPlanner()

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

    @property
    def resource_discovery(self) -> RuntimeResourceDiscovery:
        """
        Expose the canonical resource discovery subsystem for this Runtime instance.
        
        Future Runtime systems should access discovery through this context
        rather than constructing independent discovery services.
        """
        return self._resource_discovery

    @property
    def provider_registry(self) -> RuntimeProviderRegistry:
        """
        Expose the canonical Provider Registry for this Runtime instance.
        
        Future Runtime systems should access the provider catalog through this context
        rather than constructing independent provider registries.
        """
        return self._provider_registry

    @property
    def hardware_discovery(self) -> RuntimeHardwareDiscovery:
        """
        Expose the canonical Hardware Discovery subsystem for this Runtime instance.
        
        This serves as the single source of truth for architectural knowledge of 
        available hardware resources.
        
        Future Runtime systems should access hardware information through this context
        rather than constructing independent hardware discovery services.
        """
        return self._hardware_discovery

    @property
    def provider_selection(self) -> RuntimeProviderSelection:
        """
        Expose the canonical Provider Selection subsystem for this Runtime instance.
        
        This serves as the single source of truth for architectural provider eligibility.
        Future Runtime systems should access Provider Selection through this context
        rather than constructing independent matching engines.
        """
        return self._provider_selection

    @property
    def scheduler(self) -> RuntimeScheduler:
        """
        Expose the canonical Scheduler subsystem for this Runtime instance.
        
        This serves as the single architectural authority for scheduling decisions.
        Future Runtime components must obtain scheduling services through RuntimeContext 
        rather than constructing independent Scheduler instances.
        """
        return self._scheduler

    @property
    def execution_planner(self) -> RuntimeExecutionPlanner:
        """
        Expose the canonical Execution Planner subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution planning.
        Future Runtime components must obtain planning services through RuntimeContext 
        rather than constructing independent RuntimeExecutionPlanner instances.
        """
        return self._execution_planner

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
