import pytest
import inspect

from src.runtime.core.execution_model import ExecutionRequest
from src.runtime.core.planner import RuntimeExecutionPlanner
from src.runtime.core.scheduling_model import SchedulingDecision
from src.runtime.core.scheduler import RuntimeScheduler
from src.runtime.core.execution_result_model import ExecutionResult
from src.runtime.core.executor import RuntimeExecutor
from src.runtime.core.lifecycle_model import LifecycleResult
from src.runtime.core.lifecycle import RuntimeLifecycle
from src.runtime.core.retry_model import RetryResult
from src.runtime.core.retry import RuntimeRetry
from src.runtime.core.observation_model import ObservationResult
from src.runtime.core.observation import RuntimeObservation
from src.runtime.core.learning_model import LearningResult
from src.runtime.core.learning import RuntimeLearning
from src.runtime.core.optimization_model import OptimizationResult
from src.runtime.core.optimization import RuntimeOptimization

from src.runtime.core.context import RuntimeContext

class TestRuntimePipelineCertification:
    """
    Certifies the holistic integrity of the Runtime Decision Pipeline for Sprint 6.5.
    Ensures that there are no missing architectural responsibilities, no duplicated
    responsibilities, no architectural drift, and no hidden coupling.
    """

    def test_pipeline_completeness_and_uniqueness(self):
        """
        Certifies that the pipeline covers all stages exactly once and that there
        is no duplication of responsibilities across the architectural boundaries.
        """
        pipeline_stages = [
            (RuntimeScheduler, SchedulingDecision, 'schedule'),
            (RuntimeExecutor, ExecutionResult, 'execute'),
            (RuntimeLifecycle, LifecycleResult, 'evaluate'),
            (RuntimeRetry, RetryResult, 'evaluate'),
            (RuntimeObservation, ObservationResult, 'extract_observations'),
            (RuntimeLearning, LearningResult, 'learn'),
            (RuntimeOptimization, OptimizationResult, 'optimize')
        ]

        context_methods = [name for name, _ in inspect.getmembers(RuntimeContext, predicate=inspect.isdatadescriptor)]
        
        expected_context_properties = [
            'execution_planner',
            'scheduler',
            'executor',
            'runtime_lifecycle',
            'runtime_retry',
            'runtime_observation',
            'runtime_learning',
            'runtime_optimization'
        ]

        for prop in expected_context_properties:
            assert prop in context_methods, f"Pipeline missing expected stage property: {prop}"
            
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
            RuntimeExecutionPlanner,
            RuntimeScheduler,
            RuntimeExecutor,
            RuntimeLifecycle,
            RuntimeRetry,
            RuntimeObservation,
            RuntimeLearning,
            RuntimeOptimization
        ]
        
        for cls in pipeline_classes:
            if '__init__' in cls.__dict__:
                init_sig = inspect.signature(cls.__init__)
                assert len(init_sig.parameters) == 1, f"{cls.__name__} constructor must not take hidden dependencies."
            
            module = inspect.getmodule(cls)
            module_dir = dir(module)
            for other_cls in pipeline_classes:
                if other_cls != cls:
                    assert other_cls.__name__ not in module_dir, \
                        f"Hidden coupling: {cls.__name__} directly imports {other_cls.__name__}."
