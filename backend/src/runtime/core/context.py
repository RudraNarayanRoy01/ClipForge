from typing import Dict, Optional

from .metadata import RuntimeMetadata
from .lifecycle import RuntimeLifecycleCoordinator, RuntimeLifecycle
from .retry import RuntimeRetry
from .observation import RuntimeObservation
from .extension import IRuntimeExtensionPoint
from .capabilities import RuntimeCapabilityRegistry


from .discovery import RuntimeResourceDiscovery
from .providers import RuntimeProviderRegistry
from .provider_registry import ProviderRegistry
from .provider_capability_registry import ProviderCapabilityRegistry
from .model_registry import ModelRegistry
from .model_lifecycle_manager import ModelLifecycleManager
from .provider_health_manager import ProviderHealthManager
from .provider_failover_manager import ProviderFailoverManager
from .runtime_retry_manager import RuntimeRetryManager
from .runtime_scheduling_manager import RuntimeSchedulingManager
from .runtime_execution_manager import RuntimeExecutionManager
from .hardware import RuntimeHardwareDiscovery
from .selection import RuntimeProviderSelection
from .scheduler import RuntimeScheduler
from .planner import RuntimeExecutionPlanner
from .execution_graph import RuntimeExecutionGraphBuilder
from .resource_allocator import RuntimeResourceAllocator
from .execution_context import RuntimeExecutionContextFactory
from .orchestrator import RuntimeOrchestrator
from .adaptive_runtime import AdaptiveRuntime
from .runtime_monitoring import RuntimeMonitoring
from .runtime_telemetry import RuntimeTelemetry
from .runtime_metrics import RuntimeMetrics
from .runtime_health import RuntimeHealth
from .runtime_diagnostics import RuntimeDiagnostics
from .optimization import RuntimeOptimization
from .learning import RuntimeLearning
from .runtime_planning import RuntimePlanning, RuntimePlanningStrategy
from .runtime_policy import RuntimePolicy
from .runtime_constraint_engine import RuntimeConstraintEngine
from .runtime_budget_planner import RuntimeBudgetPlanner
from .runtime_routing import RuntimeRouting

class RuntimeContext:
    """
    The canonical Runtime Decision Environment.
    
    This is the central architectural object shared across future Runtime components.
    It provides a stable composition of the Runtime's core services and formally owns
    the Runtime Decision Pipeline.
    
    Responsibilities:
    - Runtime service composition
    - Runtime Decision Pipeline ownership
    - Runtime lifecycle ownership
    - Runtime governance ownership
    
    It strictly remains a passive composition root. It does NOT coordinate, orchestrate,
    execute, schedule, route, or optimize workloads. It merely owns the architectural 
    environment in which these decisions occur.
    
    After construction, these references remain stable. 
    Future modules should consume these references rather than replacing them.
    """

    def __init__(self) -> None:
        self._metadata = RuntimeMetadata()
        self._lifecycle_coordinator = RuntimeLifecycleCoordinator()
        self._runtime_lifecycle = RuntimeLifecycle()
        self._runtime_retry = RuntimeRetry()
        self._runtime_observation = RuntimeObservation()
        self._extension_points: Dict[str, IRuntimeExtensionPoint] = {}
        self._capability_registry = RuntimeCapabilityRegistry()
        self._resource_discovery = RuntimeResourceDiscovery()
        self._provider_registry = RuntimeProviderRegistry()
        self._ai_provider_registry = ProviderRegistry()
        self._provider_capability_registry = ProviderCapabilityRegistry()
        self._model_registry = ModelRegistry()
        self._model_lifecycle_manager = ModelLifecycleManager()
        self._provider_health_manager = ProviderHealthManager()
        self._provider_failover_manager = ProviderFailoverManager(self._provider_health_manager)
        self._runtime_retry_manager = RuntimeRetryManager(self._provider_failover_manager)
        self._runtime_scheduling_manager = RuntimeSchedulingManager(self._runtime_retry_manager)
        self._runtime_execution_manager = RuntimeExecutionManager(self._runtime_scheduling_manager)
        self._hardware_discovery = RuntimeHardwareDiscovery()
        self._provider_selection = RuntimeProviderSelection(
            self._capability_registry,
            self._provider_registry,
            self._hardware_discovery
        )
        self._scheduler = RuntimeScheduler()
        self._execution_planner = RuntimeExecutionPlanner()
        self._execution_graph_builder = RuntimeExecutionGraphBuilder()
        self._resource_allocator = RuntimeResourceAllocator()
        self._execution_context_factory = RuntimeExecutionContextFactory()
        self._orchestrator = RuntimeOrchestrator()
        self._adaptive_runtime = AdaptiveRuntime()
        self._runtime_monitoring = RuntimeMonitoring()
        self._runtime_telemetry = RuntimeTelemetry()
        self._runtime_metrics = RuntimeMetrics()
        self._runtime_health = RuntimeHealth()
        self._runtime_diagnostics = RuntimeDiagnostics()
        self._runtime_optimization = RuntimeOptimization()
        self._runtime_learning = RuntimeLearning()
        self._runtime_planning_strategy = RuntimePlanningStrategy()
        self._runtime_planning = RuntimePlanning()
        self._runtime_policy = RuntimePolicy()
        self._runtime_constraint_engine = RuntimeConstraintEngine()
        self._runtime_budget_planner = RuntimeBudgetPlanner()
        self._runtime_routing = RuntimeRouting()
        
        from .executor import RuntimeExecutor
        self._executor = RuntimeExecutor()
        

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
    def provider_health_manager(self) -> ProviderHealthManager:
        """
        Expose the canonical observational Provider Health Manager for this Runtime instance.
        
        This serves as the single source of truth for external provider structural health states in Sprint 6.6.
        RuntimeContext acts as a passive composition root and does not own health behavior.
        """
        return self._provider_health_manager

    @property
    def provider_failover_manager(self) -> ProviderFailoverManager:
        """
        Expose the canonical observational Provider Failover Manager for this Runtime instance.
        
        This serves as the single source of truth for structural provider failover definitions in Sprint 6.6.
        RuntimeContext acts as a passive composition root and does not own failover behavior.
        """
        return self._provider_failover_manager

    @property
    def runtime_retry_manager(self) -> RuntimeRetryManager:
        """
        Expose the canonical observational Runtime Retry Manager for this Runtime instance.
        
        This serves as the single source of truth for structural retry policies in Sprint 6.6.
        RuntimeContext acts as a passive composition root and does not own retry behavior.
        """
        return self._runtime_retry_manager


    @property
    def runtime_execution_manager(self) -> RuntimeExecutionManager:
        """
        Expose the canonical observational Runtime Execution Manager for this Runtime instance.
        
        This serves as the single source of truth for structural execution preparation in Sprint 6.6.
        RuntimeContext acts as a passive composition root and does not own execution behavior.
        """
        return self._runtime_execution_manager

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
    def scheduler(self) -> RuntimeScheduler:
        """
        Expose the canonical Scheduler subsystem for this Runtime instance.
        
        This serves as the single architectural authority for scheduling decisions.
        Future Runtime components must obtain scheduling services through RuntimeContext 
        rather than constructing independent Scheduler instances.
        """
        return self._scheduler

    @property
    def executor(self) -> 'RuntimeExecutor':
        """
        Expose the canonical Executor subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution decisions.
        Future Runtime components must obtain execution services through RuntimeContext
        rather than constructing independent RuntimeExecutor instances.
        """
        return self._executor

    @property
    def execution_planner(self) -> RuntimeExecutionPlanner:
        """
        Expose the canonical Execution Planner subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution planning.
        Future Runtime components must obtain planning services through RuntimeContext 
        rather than constructing independent RuntimeExecutionPlanner instances.
        """
        return self._execution_planner


    @property
    def resource_allocator(self) -> RuntimeResourceAllocator:
        """
        Expose the canonical Resource Allocator subsystem for this Runtime instance.
        
        This serves as the single architectural authority for logical resource allocation.
        Future Runtime components must obtain allocation services through RuntimeContext 
        rather than constructing independent RuntimeResourceAllocator instances.
        """
        return self._resource_allocator


    @property
    def orchestrator(self) -> RuntimeOrchestrator:
        """
        Expose the canonical Runtime Orchestrator subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution coordination.
        Future Runtime components must obtain orchestration services through RuntimeContext 
        rather than constructing independent RuntimeOrchestrator instances.
        """
        return self._orchestrator

    @property
    def adaptive_runtime(self) -> AdaptiveRuntime:
        """
        Expose the canonical Adaptive Runtime subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution adaptation.
        Future Runtime components must obtain adaptation services through RuntimeContext 
        rather than constructing independent AdaptiveRuntime instances.
        """
        return self._adaptive_runtime

    @property
    def runtime_monitoring(self) -> RuntimeMonitoring:
        """
        Expose the canonical Runtime Monitoring subsystem for this Runtime instance.
        
        This serves as the single architectural authority for observation of execution and adaptation.
        Future Runtime components must obtain monitoring services through RuntimeContext 
        rather than constructing independent RuntimeMonitoring instances.
        """
        return self._runtime_monitoring

    @property
    def runtime_telemetry(self) -> RuntimeTelemetry:
        """
        Expose the canonical Runtime Telemetry subsystem for this Runtime instance.
        
        This serves as the single architectural authority for signal capture.
        Future Runtime components must obtain telemetry services through RuntimeContext 
        rather than constructing independent RuntimeTelemetry instances.
        """
        return self._runtime_telemetry

    @property
    def runtime_metrics(self) -> RuntimeMetrics:
        """
        Expose the canonical Runtime Metrics subsystem for this Runtime instance.
        
        This serves as the single architectural authority for quantitative measurement.
        Future Runtime components must obtain metrics services through RuntimeContext 
        rather than constructing independent RuntimeMetrics instances.
        """
        return self._runtime_metrics

    @property
    def runtime_health(self) -> RuntimeHealth:
        """
        Expose the canonical Runtime Health subsystem for this Runtime instance.
        
        This serves as the single architectural authority for operational evaluation.
        Future Runtime components must obtain health services through RuntimeContext 
        rather than constructing independent RuntimeHealth instances.
        """
        return self._runtime_health


    @property
    def runtime_learning(self) -> RuntimeLearning:
        """
        Expose the canonical Runtime Learning subsystem for this Runtime instance.
        
        This serves as the single architectural authority for knowledge persistence.
        Future Runtime components must obtain knowledge services through RuntimeContext
        rather than constructing independent RuntimeLearning instances.
        """
        return self._runtime_learning

    # -------------------------------------------------------------------------
    # Runtime Decision Pipeline Ownership
    # -------------------------------------------------------------------------
    # RuntimeContext owns the composition and lifecycle of the Decision Pipeline,
    # but does NOT own the decisions themselves (e.g. PlanningDecision, PolicyDecision).
    # RuntimeKnowledge remains an independent artifact consumed by this pipeline.
    

    @property
    def runtime_planning(self) -> RuntimePlanning:
        """
        Expose the canonical Runtime Planning subsystem for this Runtime instance.
        
        This serves as the single architectural authority for runtime planning decisions.
        Future Runtime components must obtain planning services through RuntimeContext
        rather than constructing independent RuntimePlanning instances.
        """
        return self._runtime_planning

    @property
    def runtime_policy(self) -> RuntimePolicy:
        """
        Expose the canonical Runtime Policy subsystem for this Runtime instance.
        
        This serves as the single architectural authority for runtime policy decisions.
        Future Runtime components must obtain policy services through RuntimeContext
        rather than constructing independent RuntimePolicy instances.
        """
        return self._runtime_policy


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
