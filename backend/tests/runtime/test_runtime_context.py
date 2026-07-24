import pytest

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_planning import RuntimePlanningStrategy, RuntimePlanning
from src.runtime.core.runtime_policy import RuntimePolicy
from src.runtime.core.runtime_constraint_engine import RuntimeConstraintEngine
from src.runtime.core.runtime_budget_planner import RuntimeBudgetPlanner
from src.runtime.core.runtime_routing import RuntimeRouting


def test_runtime_context_is_composition_root():
    """Verify RuntimeContext instantiates all components and is the sole composition root."""
    context = RuntimeContext()
    
    # Verify core composition
    assert context.metadata is not None
    assert context.lifecycle is not None
    
    # Verify Decision Environment ownership
    assert isinstance(context.runtime_planning_strategy, RuntimePlanningStrategy)
    assert isinstance(context.runtime_planning, RuntimePlanning)
    assert isinstance(context.runtime_policy, RuntimePolicy)
    assert isinstance(context.runtime_constraint_engine, RuntimeConstraintEngine)
    assert isinstance(context.runtime_budget_planner, RuntimeBudgetPlanner)
    assert isinstance(context.runtime_routing, RuntimeRouting)

def test_runtime_decision_environment_encapsulation():
    """
    Verify RuntimeContext acts as the Decision Environment and preserves
    dependency direction (components do not own the context).
    """
    context = RuntimeContext()
    
    # Ensure components exist independently but are exposed centrally
    pipeline_components = [
        context.runtime_planning_strategy,
        context.runtime_planning,
        context.runtime_policy,
        context.runtime_constraint_engine,
        context.runtime_budget_planner,
        context.runtime_routing
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
    import inspect
    from src.runtime.core.context import RuntimeContext
    
    source = inspect.getsource(RuntimeContext)
    
    forbidden_terms = [
        "Gemini", "OpenAI", "Claude", "Ollama", "Mistral",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "VRAM"
    ]
    
    for term in forbidden_terms:
        assert term not in source, f"RuntimeContext must be independent, found {term}"
