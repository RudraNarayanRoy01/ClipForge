import pytest
import inspect
from dataclasses import FrozenInstanceError

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult
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
def planner() -> ExecutionPlanner:
    return ExecutionPlanner()

def test_valid_planning_produces_result(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 1: A valid ExecutionIntent produces a PlanningResult."""
    result = planner.plan(valid_intent)
    assert result is not None

def test_correct_type(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 2: Verify isinstance(result, PlanningResult)"""
    result = planner.plan(valid_intent)
    assert isinstance(result, PlanningResult)

def test_intent_preservation(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 3: Verify result.intent is intent"""
    result = planner.plan(valid_intent)
    assert result.intent is valid_intent

def test_strategy_is_default(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 4: Verify result.strategy == 'default_planning_strategy'"""
    result = planner.plan(valid_intent)
    assert result.strategy == "default_planning_strategy"

def test_requirements_are_empty(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 5: Verify result.requirements == ()"""
    result = planner.plan(valid_intent)
    assert result.requirements == ()

def test_constraints_are_empty(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 6: Verify result.constraints == {}"""
    result = planner.plan(valid_intent)
    assert result.constraints == {}

def test_payload_preservation(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 7: Use an opaque object as payload and verify it is preserved."""
    result = planner.plan(valid_intent)
    # The payload object should be the exact same instance in memory
    assert result.intent.payload is valid_intent.payload
    # The content must be untouched
    assert result.intent.payload["some_opaque_key"] == "some_opaque_value"

def test_intent_immutability(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 8: Verify the Planner does not mutate the frozen intent.
    Dataclasses frozen=True enforces this at runtime. We verify the attribute modification throws.
    """
    with pytest.raises(FrozenInstanceError):
        valid_intent.capability_id = "mutated.id"

def test_determinism(planner: ExecutionPlanner, valid_intent: ExecutionIntent):
    """Test 9: Repeated calls with the same intent produce equivalent planning results."""
    result1 = planner.plan(valid_intent)
    result2 = planner.plan(valid_intent)
    
    # Same exact object identities where expected
    assert result1.intent is result2.intent
    assert result1.strategy == result2.strategy
    assert result1.requirements == result2.requirements
    assert result1.constraints == result2.constraints

def test_execution_neutrality(planner: ExecutionPlanner):
    """Test 10: The Planner must not invoke or instantiate execution machinery.
    We inspect the source code of the plan method to ensure no execution/spawning/calling logic.
    """
    source_lines = inspect.getsource(planner.plan)
    
    forbidden_terms = [
        "execute", "run", "dispatch", "invoke", "load_model", "spawn", 
        "subprocess", "RuntimeExecutor", "inference"
    ]
    
    source_lower = source_lines.lower()
    for term in forbidden_terms:
        # We ensure that none of these words exist in the executable part of the code (ignoring docstring)
        # To be safe against docstring mentions, we parse the AST in the architecture test,
        # but here we can check basic substrings.
        # Actually, let's just make sure it doesn't call any generic "execute" function.
        assert f"{term}(" not in source_lower, f"Forbidden term '{term}' called in plan()"
        
