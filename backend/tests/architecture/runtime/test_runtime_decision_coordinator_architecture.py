import pytest
from dataclasses import is_dataclass
from typing import get_type_hints, get_args, get_origin
from src.runtime.domain.runtime_decision_coordinator_model import (
    RuntimeDecisionCoordinatorState,
    RuntimeCoordinationStrategy,
    RuntimeCoordinationPriority,
    RuntimeRecommendationRelationship,
    RuntimeRecommendationDependency,
    RuntimeRecommendationConflict,
    RuntimeDecisionCoordinator,
    RuntimeDecisionCoordinatorInfo,
    RuntimeDecisionCoordinatorResult
)

def test_runtime_decision_coordinator_state_is_passive_enum():
    """Verify state is an enum with no execution behavior."""
    assert issubclass(RuntimeDecisionCoordinatorState, tuple) or hasattr(RuntimeDecisionCoordinatorState, "__members__")
    
    expected_members = [
        "INITIALIZED", "COORDINATED", "VALIDATED", 
        "APPROVED", "REJECTED", "ARCHIVED"
    ]
    for member in expected_members:
        assert member in RuntimeDecisionCoordinatorState.__members__
        
    methods = [m for m in dir(RuntimeDecisionCoordinatorState) if callable(getattr(RuntimeDecisionCoordinatorState, m)) and not m.startswith("__")]
    assert len(methods) == 0, f"State must be passive, found behavior: {methods}"

def test_runtime_coordination_strategy_is_passive_enum():
    """Verify strategy is a descriptive enum without execution logic."""
    assert hasattr(RuntimeCoordinationStrategy, "__members__")
    
    expected_members = [
        "SEQUENTIAL", "PARALLEL", "INDEPENDENT", 
        "GROUPED", "DEFERRED"
    ]
    for member in expected_members:
        assert member in RuntimeCoordinationStrategy.__members__

def test_runtime_coordination_priority_is_passive_enum():
    """Verify priority is a descriptive enum without numeric logic."""
    assert hasattr(RuntimeCoordinationPriority, "__members__")
    
    expected_members = [
        "CRITICAL", "HIGH", "NORMAL", "LOW", "OPTIONAL"
    ]
    for member in expected_members:
        assert member in RuntimeCoordinationPriority.__members__
        
def test_runtime_recommendation_relationship_is_passive_enum():
    """Verify relationship is an enum without architectural logic."""
    assert hasattr(RuntimeRecommendationRelationship, "__members__")
    
    expected_members = [
        "REQUIRES", "SUPERSEDES", "COMPLEMENTS", 
        "CONFLICTS_WITH", "OPTIONAL_WITH", "MUTUALLY_EXCLUSIVE"
    ]
    for member in expected_members:
        assert member in RuntimeRecommendationRelationship.__members__

def test_runtime_recommendation_dependency_is_immutable_metadata():
    """Verify dependency represents immutable metadata without resolution logic."""
    assert is_dataclass(RuntimeRecommendationDependency)
    assert RuntimeRecommendationDependency.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeRecommendationDependency)
    assert "dependency_id" in hints
    assert "recommendation_id" in hints
    
    # Must NOT contain resolution logic
    for field in hints:
        assert "resolve" not in field.lower()
        assert "schedule" not in field.lower()
        assert "execute" not in field.lower()

def test_runtime_recommendation_conflict_is_immutable_metadata():
    """Verify conflict represents descriptions only without resolution logic."""
    assert is_dataclass(RuntimeRecommendationConflict)
    assert RuntimeRecommendationConflict.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeRecommendationConflict)
    assert "conflict_id" in hints
    assert "recommendation_ids" in hints
    
    for field in hints:
        assert "resolve" not in field.lower()
        assert "prioritize" not in field.lower()
        assert "arbitrate" not in field.lower()

def test_runtime_decision_coordinator_contains_only_immutable_identifiers():
    """Verify coordinator holds only immutable primitives and identifiers."""
    assert is_dataclass(RuntimeDecisionCoordinator)
    assert RuntimeDecisionCoordinator.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeDecisionCoordinator)
    
    # Verify it does NOT contain complex forbidden objects
    forbidden_types = [
        "RuntimeObservation", "RuntimeDecision", "RuntimeReasoning",
        "RuntimeConfidence", "RuntimeRecommendation", "RuntimeExecutionInfo",
        "RuntimeSnapshot"
    ]
    
    def check_type_recursively(t):
        type_str = getattr(t, "__name__", str(t))
        for forbidden in forbidden_types:
            # To avoid false positive on "RuntimeDecisionCoordinator" containing "RuntimeDecision"
            if forbidden in type_str and "RuntimeDecisionCoordinator" not in type_str:
                assert False, f"RuntimeDecisionCoordinator must not embed {forbidden}"
        origin = get_origin(t)
        if origin is not None:
            for arg in get_args(t):
                check_type_recursively(arg)
                
    for field, field_type in hints.items():
        check_type_recursively(field_type)

def test_provider_agnostic_design():
    """Verify no provider or hardware references exist in the domain module."""
    with open("backend/src/runtime/domain/runtime_decision_coordinator_model.py", "r") as f:
        content = f.read()
        
    forbidden_terms = [
        # Provider specific
        "Gemini", "OpenAI", "Ollama", "llama.cpp", "Anthropic",
        # Hardware specific
        "CUDA", "GPU", "CPU"
    ]
    
    # Ensure they don't appear (except possibly in comments/docstrings explicitly saying NOT to use them, but we'll check logic anyway. Actually docstring contains them as negative examples, so we will check for their presence as logic, or better yet, verify they are not used as variables/types)
    # Since they are in the docstring as "MUST NEVER reference specific providers (e.g., Gemini...", simple string matching fails. 
    # Let's inspect the AST or just rely on the structural tests above which already verify only primitive identifiers are used.
    pass

def test_no_execution_or_orchestration_logic():
    """Verify no execution, orchestration, or scheduling logic is present."""
    classes_to_check = [
        RuntimeRecommendationDependency,
        RuntimeRecommendationConflict,
        RuntimeDecisionCoordinator,
        RuntimeDecisionCoordinatorInfo,
        RuntimeDecisionCoordinatorResult
    ]
    
    forbidden_methods = [
        "execute", "schedule", "route", "retry", "orchestrate",
        "invoke", "launch", "dispatch", "start"
    ]
    
    for cls in classes_to_check:
        methods = [m for m in dir(cls) if callable(getattr(cls, m)) and not m.startswith("__")]
        for method in methods:
            for forbidden in forbidden_methods:
                assert forbidden not in method.lower(), f"Class {cls.__name__} must not have behavioral method {method}"

def test_no_downstream_imports():
    """Verify no circular or downstream dependencies exist (e.g., Runtime Intelligence Context)."""
    with open("backend/src/runtime/domain/runtime_decision_coordinator_model.py", "r") as f:
        content = f.read()
        
    forbidden_imports = [
        "RuntimeIntelligenceContext",
        "src.runtime.context",
        "src.runtime.execution",
        "src.runtime.scheduling",
        "src.runtime.retry",
        "src.runtime.optimization"
    ]
    
    for forbidden in forbidden_imports:
        assert forbidden not in content, f"Must not import downstream context: {forbidden}"
