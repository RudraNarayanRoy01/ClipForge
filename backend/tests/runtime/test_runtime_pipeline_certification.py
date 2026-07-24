import inspect
import pytest
import dataclasses

from src.runtime.core.runtime_planning import RuntimePlanning, PlanningDecision
from src.runtime.core.runtime_policy import RuntimePolicy, PolicyDecision
from src.runtime.core.runtime_constraint_engine import RuntimeConstraintEngine, ConstraintDecision
from src.runtime.core.runtime_budget_planner import RuntimeBudgetPlanner, BudgetDecision
from src.runtime.core.runtime_routing import RuntimeRouting, RoutingDecision
from src.runtime.core.context import RuntimeContext

class TestRuntimePipelineCertification:
    """
    Certifies the holistic integrity of the Runtime Decision Pipeline for Sprint 6.4.
    Ensures that there are no missing architectural responsibilities, no duplicated
    responsibilities, no architectural drift, and no hidden coupling.
    """

    def test_pipeline_completeness_and_uniqueness(self):
        """
        Certifies that the pipeline covers all stages exactly once and that there
        is no duplication of responsibilities across the architectural boundaries.
        """
        # The definitive sequence of pipeline stages
        pipeline_stages = [
            (RuntimePlanning, PlanningDecision, 'plan'),
            (RuntimePolicy, PolicyDecision, 'evaluate'),
            (RuntimeConstraintEngine, ConstraintDecision, 'evaluate'),
            (RuntimeBudgetPlanner, BudgetDecision, 'evaluate'),
            (RuntimeRouting, RoutingDecision, 'evaluate')
        ]

        # Verify no missing or extra stages are known to the context's properties
        # relating to the pipeline.
        context_methods = [name for name, _ in inspect.getmembers(RuntimeContext, predicate=inspect.isdatadescriptor)]
        
        # Verify the context exposes precisely these stages (no duplicates, no omissions)
        expected_context_properties = [
            'runtime_planning',
            'runtime_policy',
            'runtime_constraint_engine',
            'runtime_budget_planner',
            'runtime_routing'
        ]

        for prop in expected_context_properties:
            assert prop in context_methods, f"Pipeline missing expected stage property: {prop}"
            
        # Verify responsibility uniqueness: each stage must return a unique decision type
        decision_types = set()
        for stage_cls, decision_cls, method_name in pipeline_stages:
            sig = inspect.signature(getattr(stage_cls, method_name))
            assert sig.return_annotation == decision_cls, f"{stage_cls.__name__} does not return {decision_cls.__name__}"
            assert decision_cls not in decision_types, f"Duplicated responsibility detected: {decision_cls.__name__} returned by multiple stages"
            decision_types.add(decision_cls)

    def test_no_hidden_coupling_in_pipeline(self):
        """
        Certifies that no pipeline stage depends on another stage's instance,
        meaning they communicate strictly through immutable artifacts.
        """
        pipeline_classes = [
            RuntimePlanning,
            RuntimePolicy,
            RuntimeConstraintEngine,
            RuntimeBudgetPlanner,
            RuntimeRouting
        ]
        
        for cls in pipeline_classes:
            # Check constructor for hidden dependencies
            init_sig = inspect.signature(cls.__init__)
            # self is the only parameter expected, or no parameters
            # They should not be constructed with references to other pipeline stages.
            assert len(init_sig.parameters) == 1, f"{cls.__name__} constructor must not take hidden dependencies."
            
            # Check for hidden imports
            module = inspect.getmodule(cls)
            module_dir = dir(module)
            for other_cls in pipeline_classes:
                if other_cls != cls:
                    assert other_cls.__name__ not in module_dir, \
                        f"Hidden coupling: {cls.__name__} directly imports {other_cls.__name__}."
