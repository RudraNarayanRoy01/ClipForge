import pytest
import inspect
from dataclasses import FrozenInstanceError

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_planner import ExecutionPlanner


@pytest.fixture
def valid_intent() -> ExecutionIntent:
    # Use an opaque object for payload to verify exact object preservation
    opaque_payload = {"some_opaque_key": "some_opaque_value", "nested": [1, 2, 3]}
    return ExecutionIntent(
        capability_id="test.capability.extract",
        payload=opaque_payload,
        output_contract="ExtractionSchema"
    )

@pytest.fixture
def default_context() -> PlanningContext:
    return PlanningContext()

@pytest.fixture
def planner() -> ExecutionPlanner:
    return ExecutionPlanner()

def test_valid_planning_produces_result(planner: ExecutionPlanner, valid_intent: ExecutionIntent, default_context: PlanningContext):
    """Test 1: A valid ExecutionIntent + PlanningContext produces a PlanningResult."""
    result = planner.plan(valid_intent, default_context)
    assert result is not None
    assert isinstance(result, PlanningResult)

def test_intent_preservation(planner: ExecutionPlanner, valid_intent: ExecutionIntent, default_context: PlanningContext):
    """Test 2: Verify result.intent is intent"""
    result = planner.plan(valid_intent, default_context)
    assert result.intent is valid_intent

def test_strategy_is_default(planner: ExecutionPlanner, valid_intent: ExecutionIntent, default_context: PlanningContext):
    """Test 3: Verify result.strategy == 'balanced_planning' with default context"""
    result = planner.plan(valid_intent, default_context)
    assert result.strategy == "balanced_planning"

def test_quality_preference(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 4: quality_preference='high' produces 'quality_first_planning'"""
    context = PlanningContext(quality_preference="high")
    result = planner.plan(valid_intent, context)
    assert result.strategy == "quality_first_planning"

def test_latency_preference(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 5: latency_preference='low' produces 'latency_first_planning'"""
    context = PlanningContext(latency_preference="low")
    result = planner.plan(valid_intent, context)
    assert result.strategy == "latency_first_planning"

def test_cost_preference(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 6: cost_preference='low' produces 'cost_aware_planning'"""
    context = PlanningContext(cost_preference="low")
    result = planner.plan(valid_intent, context)
    assert result.strategy == "cost_aware_planning"

def test_locality_preference(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 7: locality_preference='local' produces 'locality_preferred_planning'"""
    context = PlanningContext(locality_preference="local")
    result = planner.plan(valid_intent, context)
    assert result.strategy == "locality_preferred_planning"

def test_precedence(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 8: Verify Quality > Latency > Cost > Locality"""
    # Quality beats everything
    context_all = PlanningContext(
        quality_preference="high",
        latency_preference="low",
        cost_preference="low",
        locality_preference="local"
    )
    result = planner.plan(valid_intent, context_all)
    assert result.strategy == "quality_first_planning"

    # Latency beats Cost and Locality
    context_lat = PlanningContext(
        quality_preference="balanced",
        latency_preference="low",
        cost_preference="low",
        locality_preference="local"
    )
    result = planner.plan(valid_intent, context_lat)
    assert result.strategy == "latency_first_planning"

    # Cost beats Locality
    context_cost = PlanningContext(
        quality_preference="balanced",
        latency_preference="standard",
        cost_preference="low",
        locality_preference="local"
    )
    result = planner.plan(valid_intent, context_cost)
    assert result.strategy == "cost_aware_planning"

def test_requirements_are_empty(planner: ExecutionPlanner, valid_intent: ExecutionIntent, default_context: PlanningContext):
    """Test 9: Verify result.requirements == ()"""
    result = planner.plan(valid_intent, default_context)
    assert result.requirements == ()

def test_constraints_are_empty_and_not_converted(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 10: Verify result.constraints == {} and PlanningContext.constraints are ignored."""
    context = PlanningContext(constraints=("gpu_required", "some_constraint"))
    result = planner.plan(valid_intent, context)
    assert result.constraints == {}
    assert result.requirements == ()

def test_payload_opacity(planner: ExecutionPlanner, default_context: PlanningContext):
    """Test 11: Use arbitrary payloads to verify opacity and preservation."""
    payloads = [None, {}, object(), "string payload", [1, 2, 3]]
    for payload in payloads:
        intent = ExecutionIntent(capability_id="test", payload=payload)
        result = planner.plan(intent, default_context)
        assert result.intent.payload is payload

def test_intent_immutability(valid_intent: ExecutionIntent):
    """Test 12: Verify the Planner does not mutate the frozen intent."""
    with pytest.raises(FrozenInstanceError):
        valid_intent.capability_id = "mutated.id"

def test_context_immutability(default_context: PlanningContext):
    """Test 13: Verify context remains unchanged (frozen dataclass)."""
    with pytest.raises(FrozenInstanceError):
        default_context.quality_preference = "high"

def test_determinism(planner: ExecutionPlanner, valid_intent: ExecutionIntent, default_context: PlanningContext):
    """Test 14: Same intent + context produce equivalent planning results."""
    result1 = planner.plan(valid_intent, default_context)
    result2 = planner.plan(valid_intent, default_context)
    
    assert result1.intent is result2.intent
    assert result1.strategy == result2.strategy
    assert result1.requirements == result2.requirements
    assert result1.constraints == result2.constraints

def test_execution_neutrality(planner: ExecutionPlanner):
    """Test 15: The Planner must not invoke or instantiate execution machinery."""
    source_lines = inspect.getsource(planner.plan)
    
    forbidden_terms = [
        "execute", "run", "dispatch", "invoke", "load_model", "spawn", 
        "subprocess", "RuntimeExecutor", "inference"
    ]
    
    source_lower = source_lines.lower()
    for term in forbidden_terms:
        assert f"{term}(" not in source_lower, f"Forbidden term '{term}' called in plan()"
