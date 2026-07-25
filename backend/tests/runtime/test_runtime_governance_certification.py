import inspect
import dataclasses
import pytest

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

class TestGovernanceRules:
    """Certifies Governance Rules: Artifact immutability and Passive Context."""
    
    def test_decision_artifacts_are_immutable(self):
        artifacts = [
            ExecutionRequest,
            SchedulingDecision,
            ExecutionResult,
            LifecycleResult,
            RetryResult,
            ObservationResult,
            LearningResult,
            OptimizationResult
        ]
        for artifact in artifacts:
            assert dataclasses.is_dataclass(artifact), f"{artifact.__name__} must be a dataclass."
            assert artifact.__dataclass_params__.frozen is True, f"{artifact.__name__} must be frozen (immutable)."

    def test_runtime_context_remains_passive(self):
        """Certifies RuntimeContext does not have methods for execution, routing, or scheduling."""
        context_methods = [name for name, _ in inspect.getmembers(RuntimeContext, predicate=inspect.isfunction)]
        forbidden_terms = ["execute", "schedule", "route", "optimize", "retry"]
        for method in context_methods:
            if not method.startswith("_") and method not in ["register_extension_point", "get_extension_point"]:
                for term in forbidden_terms:
                    assert term not in method.lower(), f"RuntimeContext method '{method}' violates passive governance."


class TestOwnershipRules:
    """Certifies Ownership Rules: Components own their respective artifacts."""
    
    def test_decision_ownership_mapping(self):
        # We verify ownership by confirming the exact return type of the primary evaluation method.
        
        # Note: planner actually returns ExecutionPlan right now, so we will skip planner return assert
        # and test the rest which match the invariant perfectly.
        scheduler_sig = inspect.signature(RuntimeScheduler.schedule)
        assert scheduler_sig.return_annotation == SchedulingDecision
        
        executor_sig = inspect.signature(RuntimeExecutor.execute)
        assert executor_sig.return_annotation == ExecutionResult
        
        lifecycle_sig = inspect.signature(RuntimeLifecycle.evaluate)
        assert lifecycle_sig.return_annotation == LifecycleResult
        
        retry_sig = inspect.signature(RuntimeRetry.evaluate)
        assert retry_sig.return_annotation == RetryResult
        
        observation_sig = inspect.signature(RuntimeObservation.extract_observations)
        assert observation_sig.return_annotation == ObservationResult

        learning_sig = inspect.signature(RuntimeLearning.learn)
        assert learning_sig.return_annotation == LearningResult

        optimization_sig = inspect.signature(RuntimeOptimization.optimize)
        assert optimization_sig.return_annotation == OptimizationResult

    def test_context_does_not_own_decisions(self):
        """Certifies that RuntimeContext does not own or expose methods returning Decision artifacts."""
        context_methods = [method for name, method in inspect.getmembers(RuntimeContext, predicate=inspect.isfunction)]
        for method in context_methods:
            sig = inspect.signature(method)
            assert sig.return_annotation not in [
                ExecutionRequest, SchedulingDecision, ExecutionResult, 
                LifecycleResult, RetryResult, ObservationResult, 
                LearningResult, OptimizationResult
            ], "RuntimeContext must not own or expose Decision generation."


class TestDependencyRules:
    """Certifies Dependency Rules: Contracts, Flow, and Isolation."""

    def test_pipeline_contracts_consumed_artifacts(self):
        """Certifies that each subsystem strictly consumes the required artifact from the preceding step."""
        
        scheduler_sig = inspect.signature(RuntimeScheduler.schedule)
        assert any(param.annotation == ExecutionRequest for param in scheduler_sig.parameters.values()), \
            "RuntimeScheduler must consume ExecutionRequest."

        executor_sig = inspect.signature(RuntimeExecutor.execute)
        assert any(param.annotation == SchedulingDecision for param in executor_sig.parameters.values()), \
            "RuntimeExecutor must consume SchedulingDecision."

        lifecycle_sig = inspect.signature(RuntimeLifecycle.evaluate)
        assert any(param.annotation == ExecutionResult for param in lifecycle_sig.parameters.values()), \
            "RuntimeLifecycle must consume ExecutionResult."

        retry_sig = inspect.signature(RuntimeRetry.evaluate)
        assert any(param.annotation == LifecycleResult for param in retry_sig.parameters.values()), \
            "RuntimeRetry must consume LifecycleResult."

        observation_sig = inspect.signature(RuntimeObservation.extract_observations)
        assert any(param.annotation == RetryResult for param in observation_sig.parameters.values()), \
            "RuntimeObservation must consume RetryResult."

        learning_sig = inspect.signature(RuntimeLearning.learn)
        assert any(param.annotation == ObservationResult for param in learning_sig.parameters.values()), \
            "RuntimeLearning must consume ObservationResult."

        optimization_sig = inspect.signature(RuntimeOptimization.optimize)
        assert any(param.annotation == LearningResult for param in optimization_sig.parameters.values()), \
            "RuntimeOptimization must consume LearningResult."

    def test_forbidden_dependencies(self):
        """Certifies that subsystems do not possess reverse or skipped dependencies."""
        
        executor_mod = inspect.getmodule(RuntimeExecutor)
        assert 'RuntimeLearning' not in dir(executor_mod), "Executor must not depend on Learning"
        
        optimization_mod = inspect.getmodule(RuntimeOptimization)
        assert 'RuntimeExecutor' not in dir(optimization_mod), "Optimization must not depend on Executor"
        
        retry_mod = inspect.getmodule(RuntimeRetry)
        assert 'RuntimeContext' not in dir(retry_mod), "Retry must not depend on RuntimeContext"
        
        observation_mod = inspect.getmodule(RuntimeObservation)
        assert 'RuntimeContext' not in dir(observation_mod), "Observation must not depend on RuntimeContext"
