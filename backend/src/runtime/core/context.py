from typing import Dict, Optional

from .execution_model import ExecutionRequest
from .execution_result_model import ExecutionStatus
from .scheduling_model import SchedulingDecision
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
from .runtime_optimization import RuntimeOptimization
from .runtime_learning import RuntimeLearning
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
        
        # Execution State (Passive References)
        self.active_execution_request: Optional[ExecutionRequest] = None
        self.active_execution_status: Optional[ExecutionStatus] = None
        self.active_scheduling_decision: Optional[SchedulingDecision] = None

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

    @property
    def execution_graph_builder(self) -> RuntimeExecutionGraphBuilder:
        """
        Expose the canonical Execution Graph Builder subsystem for this Runtime instance.
        
        This serves as the single architectural authority for dependency modeling.
        Future Runtime components must obtain graph-building services through RuntimeContext 
        rather than constructing independent RuntimeExecutionGraphBuilder instances.
        """
        return self._execution_graph_builder

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
    def execution_context_factory(self) -> RuntimeExecutionContextFactory:
        """
        Expose the canonical Execution Context Factory subsystem for this Runtime instance.
        
        This serves as the single architectural authority for execution preparation.
        Future Runtime components must obtain context creation services through RuntimeContext 
        rather than constructing independent RuntimeExecutionContextFactory instances.
        """
        return self._execution_context_factory

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
    def runtime_diagnostics(self) -> RuntimeDiagnostics:
        """
        Expose the canonical Runtime Diagnostics subsystem for this Runtime instance.
        
        This serves as the single architectural authority for diagnostic reasoning.
        Future Runtime components must obtain diagnostic services through RuntimeContext
        rather than constructing independent RuntimeDiagnostics instances.
        """
        return self._runtime_diagnostics

    @property
    def runtime_optimization(self) -> RuntimeOptimization:
        """
        Expose the canonical Runtime Optimization subsystem for this Runtime instance.
        
        This serves as the single architectural authority for optimization reasoning.
        Future Runtime components must obtain optimization services through RuntimeContext
        rather than constructing independent RuntimeOptimization instances.
        """
        return self._runtime_optimization

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
    def runtime_planning_strategy(self) -> RuntimePlanningStrategy:
        """
        Expose the canonical Runtime Planning Strategy subsystem for this Runtime instance.
        
        This serves as the single architectural authority for providing the planning philosophy.
        Future Runtime components must obtain planning strategy services through RuntimeContext
        rather than constructing independent RuntimePlanningStrategy instances.
        """
        return self._runtime_planning_strategy

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

    @property
    def runtime_constraint_engine(self) -> RuntimeConstraintEngine:
        """
        Expose the canonical Runtime Constraint Engine subsystem for this Runtime instance.
        
        This serves as the single architectural authority for runtime constraint boundaries.
        Future Runtime components must obtain constraint services through RuntimeContext
        rather than constructing independent RuntimeConstraintEngine instances.
        """
        return self._runtime_constraint_engine

    @property
    def runtime_budget_planner(self) -> RuntimeBudgetPlanner:
        """
        Expose the canonical Runtime Budget Planner subsystem for this Runtime instance.
        
        This serves as the single architectural authority for runtime execution budgets.
        Future Runtime components must obtain budget services through RuntimeContext
        rather than constructing independent RuntimeBudgetPlanner instances.
        """
        return self._runtime_budget_planner

    @property
    def runtime_routing(self) -> RuntimeRouting:
        """
        Expose the canonical Runtime Routing subsystem for this Runtime instance.
        
        This serves as the single architectural authority for runtime execution routing decisions.
        Future Runtime components must obtain routing services through RuntimeContext
        rather than constructing independent RuntimeRouting instances.
        """
        return self._runtime_routing

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
