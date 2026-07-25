import pytest
from dataclasses import is_dataclass
import inspect

from src.runtime.core.optimization_model import (
    OptimizationCategory,
    OptimizationPriority,
    OptimizationDecision,
    OptimizationSummary,
    OptimizationResult
)
from src.runtime.core.optimization import RuntimeOptimization
from src.runtime.core.learning_model import (
    LearningCategory,
    LearningConfidence,
    LearningPattern,
    LearningSummary,
    LearningResult
)
from src.runtime.core.observation_model import ObservationIdentity

def test_optimization_artifacts_are_immutable():
    """Ensure Optimization artifacts are frozen dataclasses."""
    assert is_dataclass(OptimizationDecision)
    assert is_dataclass(OptimizationSummary)
    assert is_dataclass(OptimizationResult)
    
    assert OptimizationDecision.__dataclass_params__.frozen is True
    assert OptimizationSummary.__dataclass_params__.frozen is True
    assert OptimizationResult.__dataclass_params__.frozen is True

def test_optimization_category_is_pure_enum():
    """Ensure OptimizationCategory is an enum with expected values."""
    expected_categories = {
        "EXECUTION", "RETRY", "RESOURCE", "PERFORMANCE", "STABILITY", "SYSTEM", "UNKNOWN"
    }
    actual_categories = {c.value for c in OptimizationCategory}
    assert expected_categories.issubset(actual_categories)
    
    # Assert no methods other than enum built-ins
    methods = [m for m in dir(OptimizationCategory) if not m.startswith("_")]
    # Should only contain the enum values and possibly fromkeys etc, but no execution methods
    for m in methods:
        if not hasattr(str, m):
            assert m in expected_categories

def test_optimization_priority_is_pure_enum():
    """Ensure OptimizationPriority is an enum with expected values."""
    expected_priorities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    actual_priorities = {p.value for p in OptimizationPriority}
    assert expected_priorities.issubset(actual_priorities)

def test_runtime_optimization_has_no_execution_behavior():
    """Ensure RuntimeOptimization only has the optimize method."""
    methods = [m for m in dir(RuntimeOptimization) if not m.startswith("_")]
    
    assert "optimize" in methods
    
    forbidden_terms = [
        "execute", "schedule", "retry", "allocate", "dispatch",
        "invoke", "apply", "predict", "monitor", "observe", "learn"
    ]
    
    for method in methods:
        for term in forbidden_terms:
            assert term not in method.lower(), f"Forbidden behavior found: {method}"

def test_optimization_derivation():
    """Verify OptimizationResult is successfully derived from LearningResult without execution logic."""
    engine = RuntimeOptimization()
    
    # Construct a dummy learning result
    obs_id = ObservationIdentity(
        observation_id="obs-123",
        created_at=1000.0
    )
    
    summary = LearningSummary(
        summary="Test",
        pattern_count=1,
        high_confidence_count=1,
        medium_confidence_count=0,
        low_confidence_count=0
    )
    
    pattern = LearningPattern(
        category=LearningCategory.RESOURCE,
        confidence=LearningConfidence.HIGH,
        description="High memory usage detected repeatedly."
    )
    
    learning_result = LearningResult(
        learning_identity="learn-123",
        observation_identity=obs_id,
        summary=summary,
        patterns=[pattern],
        created_at=1000.0
    )
    
    optimization_result = engine.optimize(learning_result)
    
    assert optimization_result.learning_identity == "learn-123"
    assert len(optimization_result.decisions) == 1
    
    decision = optimization_result.decisions[0]
    assert decision.category == OptimizationCategory.RESOURCE
    assert decision.priority == OptimizationPriority.CRITICAL
    assert "Reduce resource pressure" in decision.description
    
    # Assert decision does not contain commands like "Set X"
    assert "Set" not in decision.description
    assert "Move" not in decision.description
