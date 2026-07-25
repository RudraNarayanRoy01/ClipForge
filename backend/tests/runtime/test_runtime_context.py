import pytest
import inspect

from src.runtime.core.context import RuntimeContext
from src.runtime.core.planner import RuntimeExecutionPlanner
from src.runtime.core.scheduler import RuntimeScheduler
from src.runtime.core.executor import RuntimeExecutor
from src.runtime.core.lifecycle import RuntimeLifecycle
from src.runtime.core.retry import RuntimeRetry
from src.runtime.core.observation import RuntimeObservation
from src.runtime.core.learning import RuntimeLearning
from src.runtime.core.optimization import RuntimeOptimization

def test_runtime_context_is_composition_root():
    """Verify RuntimeContext instantiates all components and is the sole composition root."""
    context = RuntimeContext()
    
    # Verify core composition
    assert context.metadata is not None
    assert context.lifecycle is not None
    
    # Verify Sprint 6.5 Pipeline components ownership
    assert isinstance(context.execution_planner, RuntimeExecutionPlanner)
    assert isinstance(context.scheduler, RuntimeScheduler)
    assert isinstance(context.executor, RuntimeExecutor)
    assert isinstance(context.runtime_lifecycle, RuntimeLifecycle)
    assert isinstance(context.runtime_retry, RuntimeRetry)
    assert isinstance(context.runtime_observation, RuntimeObservation)
    assert isinstance(context.runtime_learning, RuntimeLearning)
    assert isinstance(context.runtime_optimization, RuntimeOptimization)

def test_runtime_decision_environment_encapsulation():
    """
    Verify RuntimeContext acts as the Decision Environment and preserves
    dependency direction (components do not own the context).
    """
    context = RuntimeContext()
    
    # Ensure components exist independently but are exposed centrally
    pipeline_components = [
        context.execution_planner,
        context.scheduler,
        context.executor,
        context.runtime_lifecycle,
        context.runtime_retry,
        context.runtime_observation,
        context.runtime_learning,
        context.runtime_optimization
    ]
    
    for comp in pipeline_components:
        # Pipeline components should not have a reference back to RuntimeContext (one-way flow)
        assert not hasattr(comp, 'context')
        assert not hasattr(comp, '_context')

def test_runtime_context_passive_nature():
    """
    Verify RuntimeContext is passive. It must not have methods for scheduling,
    execution, or orchestration.
    """
    context = RuntimeContext()
    
    forbidden_methods = [
        'execute',
        'schedule',
        'route_workload',
        'optimize',
        'retry',
        'coordinate'
    ]
    
    for method in forbidden_methods:
        assert not hasattr(context, method), f"RuntimeContext must remain passive, found {method}"

def test_hardware_and_provider_independence():
    """
    Verify RuntimeContext does not leak hardware or provider details.
    """
    source = inspect.getsource(RuntimeContext)
    
    forbidden_terms = [
        "Gemini", "OpenAI", "Claude", "Ollama", "Mistral",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "VRAM"
    ]
    
    for term in forbidden_terms:
        assert term not in source, f"RuntimeContext must be independent, found {term}"
