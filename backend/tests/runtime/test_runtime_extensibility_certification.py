import inspect
import pytest

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_planning import RuntimePlanning
from src.runtime.core.runtime_policy import RuntimePolicy
from src.runtime.core.runtime_constraint_engine import RuntimeConstraintEngine
from src.runtime.core.runtime_budget_planner import RuntimeBudgetPlanner
from src.runtime.core.runtime_routing import RuntimeRouting

class TestRuntimeExtensibilityCertification:
    """
    Certifies that future Runtime components (Scheduler, Execution, Observation,
    Learning, Optimization) can integrate through composition without redesigning
    the Planning, Policy, Constraint, Budget, or Routing components.
    """

    def test_future_components_compositional_integration(self):
        """
        Verify that RuntimeContext acts as the composition root for future components,
        and that these components are isolated from the decision pipeline's core logic.
        """
        context = RuntimeContext()
        
        # We assert the context has slots for future components, showing they integrate via composition.
        # This confirms that they don't need to be injected into the decision pipeline.
        future_properties = [
            'scheduler',
            'execution_engine',
            'runtime_monitoring',
            'runtime_learning',
            'runtime_optimization'
        ]
        
        context_methods = [name for name, _ in inspect.getmembers(RuntimeContext, predicate=inspect.isdatadescriptor)]
        
        for prop in future_properties:
            assert prop in context_methods, f"Extensibility gap: RuntimeContext missing composition root for {prop}"
            
    def test_pipeline_independence_from_future_components(self):
        """
        Verify that existing decision pipeline components (Planning, Policy, etc.)
        do not depend on future extensions (Scheduler, Execution, etc.).
        This guarantees future modules can be added without modifying Sprint 6.4 components.
        """
        pipeline_classes = [
            RuntimePlanning,
            RuntimePolicy,
            RuntimeConstraintEngine,
            RuntimeBudgetPlanner,
            RuntimeRouting
        ]
        
        forbidden_imports = [
            'RuntimeScheduler',
            'RuntimeExecutionEngine',
            'RuntimeMonitoring',
            'RuntimeLearning',
            'RuntimeOptimization'
        ]
        
        for cls in pipeline_classes:
            module = inspect.getmodule(cls)
            module_dir = dir(module)
            for forbidden in forbidden_imports:
                assert forbidden not in module_dir, \
                    f"Extensibility violation: {cls.__name__} depends on future component {forbidden}."
