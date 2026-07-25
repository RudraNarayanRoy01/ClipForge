import pytest
import inspect
import dataclasses

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

def test_sprint_6_5_pipeline_artifacts_are_immutable():
    """Verify that all artifacts in the Sprint 6.5 pipeline are immutable."""
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
    
    for artifact_cls in artifacts:
        assert dataclasses.is_dataclass(artifact_cls), f"{artifact_cls.__name__} must be a dataclass."
        assert artifact_cls.__dataclass_params__.frozen is True, f"{artifact_cls.__name__} must be frozen (immutable)."

def test_runtime_context_ownership():
    """Verify RuntimeContext is the sole composition root and owns the subsystems."""
    context = RuntimeContext()
    
    # In Sprint 6.5, we certify the components and verify context owns them
    assert hasattr(context, 'execution_planner'), "RuntimeContext must own RuntimeExecutionPlanner"
    assert hasattr(context, 'scheduler'), "RuntimeContext must own RuntimeScheduler"
    
    # We assert it should own executor, but we know it's a defect. We'll add it to context.
    assert hasattr(context, 'executor') or hasattr(context, '_executor'), "RuntimeContext must own RuntimeExecutor"
    
    assert hasattr(context, 'runtime_lifecycle'), "RuntimeContext must own RuntimeLifecycle"
    assert hasattr(context, 'runtime_retry'), "RuntimeContext must own RuntimeRetry"
    assert hasattr(context, 'runtime_observation'), "RuntimeContext must own RuntimeObservation"
    assert hasattr(context, 'runtime_learning'), "RuntimeContext must own RuntimeLearning"
    assert hasattr(context, 'runtime_optimization'), "RuntimeContext must own RuntimeOptimization"

def test_one_component_one_artifact_mapping():
    """Verify one component maps strictly to its one primary artifact return type."""
    # Scheduler
    scheduler_sig = inspect.signature(RuntimeScheduler.schedule)
    assert scheduler_sig.return_annotation == SchedulingDecision
    assert scheduler_sig.parameters['request'].annotation == ExecutionRequest

    # Executor
    executor_sig = inspect.signature(RuntimeExecutor.execute)
    assert executor_sig.return_annotation == ExecutionResult
    assert executor_sig.parameters['scheduling_decision'].annotation == SchedulingDecision

    # Lifecycle
    lifecycle_sig = inspect.signature(RuntimeLifecycle.evaluate)
    assert lifecycle_sig.return_annotation == LifecycleResult
    assert lifecycle_sig.parameters['execution_result'].annotation == ExecutionResult

    # Retry
    retry_sig = inspect.signature(RuntimeRetry.evaluate)
    assert retry_sig.return_annotation == RetryResult
    assert retry_sig.parameters['lifecycle_result'].annotation == LifecycleResult

    # Observation
    observation_sig = inspect.signature(RuntimeObservation.extract_observations)
    assert observation_sig.return_annotation == ObservationResult
    assert observation_sig.parameters['retry_result'].annotation == RetryResult

    # Learning
    learning_sig = inspect.signature(RuntimeLearning.learn)
    assert learning_sig.return_annotation == LearningResult
    assert learning_sig.parameters['observation_result'].annotation == ObservationResult

    # Optimization
    optimization_sig = inspect.signature(RuntimeOptimization.optimize)
    assert optimization_sig.return_annotation == OptimizationResult
    assert optimization_sig.parameters['learning_result'].annotation == LearningResult

def test_dependency_direction():
    """Verify forward-only dependencies. No circular or reverse dependencies."""
    learning_mod = inspect.getmodule(RuntimeLearning)
    assert 'OptimizationResult' not in dir(learning_mod), "Learning must not depend on Optimization"
    
    optimization_mod = inspect.getmodule(RuntimeOptimization)
    assert 'RuntimeLearning' not in dir(optimization_mod), "Optimization must not depend on Learning"

def test_provider_and_hardware_independence():
    """Verify components contain no provider or hardware specific terminology."""
    banned_terms = [
        "Gemini", "OpenAI", "Ollama", "llama.cpp", "Claude",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "VRAM"
    ]
    
    subsystems = [
        RuntimeExecutionPlanner, RuntimeScheduler, RuntimeExecutor,
        RuntimeLifecycle, RuntimeRetry, RuntimeObservation,
        RuntimeLearning, RuntimeOptimization
    ]
    
    for subsystem in subsystems:
        source_code = inspect.getsource(subsystem)
        for term in banned_terms:
            assert term not in source_code, f"Banned architectural term '{term}' found in {subsystem.__name__}."
