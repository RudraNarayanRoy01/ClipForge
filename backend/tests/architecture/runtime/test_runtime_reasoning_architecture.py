import pytest
from dataclasses import is_dataclass
from typing import get_type_hints
from src.runtime.domain.runtime_reasoning_model import (
    RuntimeReasoningState,
    RuntimeReasoningType,
    RuntimeReasoningReason,
    RuntimeReasoning,
    RuntimeReasoningInfo,
    RuntimeReasoningResult
)


def test_runtime_reasoning_state_is_passive_enum():
    """Verify RuntimeReasoningState is a simple enumeration without behavior."""
    assert issubclass(RuntimeReasoningState, tuple) or hasattr(RuntimeReasoningState, "__members__")
    
    # Verify expected values exist
    expected_members = [
        "INITIALIZED", "GATHERING", "ANALYZING", 
        "SYNTHESIZED", "VALIDATED", "REJECTED", "FAILED"
    ]
    for member in expected_members:
        assert member in RuntimeReasoningState.__members__
        
    # Verify no behavioral methods exist
    methods = [m for m in dir(RuntimeReasoningState) if callable(getattr(RuntimeReasoningState, m)) and not m.startswith("__")]
    assert len(methods) == 0, f"State must be passive, found behavior: {methods}"


def test_runtime_reasoning_type_is_passive_enum():
    """Verify RuntimeReasoningType is a categorization enum without execution logic."""
    assert hasattr(RuntimeReasoningType, "__members__")
    
    expected_members = [
        "DIAGNOSTIC", "CAUSAL", "CONTEXTUAL", 
        "HEURISTIC", "VALIDATION", "UNKNOWN"
    ]
    for member in expected_members:
        assert member in RuntimeReasoningType.__members__


def test_runtime_reasoning_reason_is_immutable_metadata():
    """Verify RuntimeReasoningReason is purely immutable metadata."""
    assert is_dataclass(RuntimeReasoningReason)
    assert RuntimeReasoningReason.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeReasoningReason)
    assert "reasoning_type" in hints
    assert "reason_code" in hints
    assert "timestamp" in hints
    
    # Must NOT contain reasoning graph or execution logic
    for field in hints:
        assert "graph" not in field.lower()
        assert "logic" not in field.lower()
        assert "execute" not in field.lower()


def test_runtime_reasoning_contains_only_immutable_identifiers():
    """Verify RuntimeReasoning artifact holds only immutable primitives and identifiers."""
    assert is_dataclass(RuntimeReasoning)
    assert RuntimeReasoning.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeReasoning)
    assert "reasoning_id" in hints
    assert "decision_id" in hints
    assert "observation_id" in hints
    assert "reasoning_type" in hints
    assert "reasoning_state" in hints
    
    # Verify it does NOT contain complex forbidden objects
    forbidden_types = [
        "RuntimeObservation", "RuntimeSnapshot", "RuntimeDecision",
        "RuntimeExecutionInfo", "RuntimeRetryInfo", "RuntimeSchedulingInfo",
        "RuntimeConfidence", "RuntimeRecommendation", "RuntimeMetrics",
        "ProviderHealth", "ProviderFailover"
    ]
    
    for field, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_types:
            assert forbidden not in type_str, f"RuntimeReasoning must not embed {forbidden}"


def test_runtime_reasoning_info_contains_only_identifiers():
    """Verify RuntimeReasoningInfo acts purely as a relational identifier struct."""
    assert is_dataclass(RuntimeReasoningInfo)
    assert RuntimeReasoningInfo.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeReasoningInfo)
    
    # Verify exactly the allowed fields
    expected_fields = {
        "reasoning_id", "decision_id", "observation_id",
        "reasoning_state", "created_at", "updated_at"
    }
    
    actual_fields = set(hints.keys())
    assert actual_fields == expected_fields, f"Info structure mismatch. Expected {expected_fields}, got {actual_fields}"


def test_runtime_reasoning_result_is_passive_transport():
    """Verify RuntimeReasoningResult acts as an immutable transport envelope."""
    assert is_dataclass(RuntimeReasoningResult)
    assert RuntimeReasoningResult.__dataclass_params__.frozen is True
    
    hints = get_type_hints(RuntimeReasoningResult)
    
    # Verify allowed fields
    assert "reasoning_info" in hints
    assert "reasoning_summary" in hints
    assert "validation_result" in hints
    
    forbidden_terms = [
        "Confidence", "Recommendation", "Metrics", 
        "Health", "Failover", "Execution", "Scheduling", "Retry"
    ]
    
    for field, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_terms:
            assert forbidden not in type_str, f"Transport artifact must not contain {forbidden}"
