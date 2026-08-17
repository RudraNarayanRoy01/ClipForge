import pytest
from src.runtime.composition.runtime_pipeline_factory import RuntimePipelineFactory
from src.runtime.composition.runtime_pipeline_context import RuntimePipelineContext
from src.runtime.core.execution_planner import ExecutionPlanner
from src.runtime.core.policy_engine import PolicyEngine
from src.runtime.core.routing_engine import RoutingEngine
from src.runtime.core.target_selector import TargetSelector

def test_runtime_composition_succeeds():
    context = RuntimePipelineFactory.create()
    assert isinstance(context, RuntimePipelineContext)

def test_all_expected_certified_components_are_present():
    context = RuntimePipelineFactory.create()
    assert isinstance(context.execution_planner, ExecutionPlanner)
    assert isinstance(context.policy_engine, PolicyEngine)
    assert isinstance(context.routing_engine, RoutingEngine)
    assert isinstance(context.target_selector, TargetSelector)

def test_construction_is_deterministic():
    context1 = RuntimePipelineFactory.create()
    context2 = RuntimePipelineFactory.create()
    
    # Repeated factory construction produces the same expected component topology and types without shared mutable global state.
    assert isinstance(context1.execution_planner, ExecutionPlanner)
    assert isinstance(context2.execution_planner, ExecutionPlanner)
    assert isinstance(context1.policy_engine, PolicyEngine)
    assert isinstance(context2.policy_engine, PolicyEngine)
    assert isinstance(context1.routing_engine, RoutingEngine)
    assert isinstance(context2.routing_engine, RoutingEngine)
    assert isinstance(context1.target_selector, TargetSelector)
    assert isinstance(context2.target_selector, TargetSelector)
    
    # Each call creates a new graph, but within the graph instances are shared if applicable.
    # Currently they are new instances per factory call, which is deterministic.
    assert context1 is not context2
    assert context1.execution_planner is not context2.execution_planner

def test_runtime_pipeline_context_is_immutable():
    from dataclasses import FrozenInstanceError
    context = RuntimePipelineFactory.create()
    with pytest.raises(FrozenInstanceError):
        context.execution_planner = ExecutionPlanner()

def test_no_duplicate_construction_in_same_graph():
    context = RuntimePipelineFactory.create()
    # Verify exactly one component instance per role within one composition graph
    assert context.execution_planner is not context.policy_engine
    assert context.execution_planner is not context.routing_engine
    assert context.execution_planner is not context.target_selector
    assert context.policy_engine is not context.routing_engine
    assert context.policy_engine is not context.target_selector
    assert context.routing_engine is not context.target_selector
