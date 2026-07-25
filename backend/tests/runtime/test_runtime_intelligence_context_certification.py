import pytest
import inspect
import dataclasses
import typing
from enum import Enum
import importlib

from src.runtime.domain.runtime_intelligence_context_model import (
    RuntimeIntelligenceContextState,
    RuntimeIntelligenceSnapshot,
    RuntimeIntelligenceSummary,
    RuntimeIntelligenceContext,
    RuntimeIntelligenceContextInfo,
    RuntimeIntelligenceContextResult
)


def test_runtime_intelligence_context_models_are_immutable():
    """Verify that all Runtime Intelligence Context artifacts are immutable."""
    
    # Check Enum
    assert issubclass(RuntimeIntelligenceContextState, Enum), "RuntimeIntelligenceContextState must be an Enum."
    
    artifacts = [
        RuntimeIntelligenceSnapshot,
        RuntimeIntelligenceSummary,
        RuntimeIntelligenceContext,
        RuntimeIntelligenceContextInfo,
        RuntimeIntelligenceContextResult
    ]
    
    for artifact_cls in artifacts:
        assert dataclasses.is_dataclass(artifact_cls), f"{artifact_cls.__name__} must be a dataclass."
        assert artifact_cls.__dataclass_params__.frozen is True, f"{artifact_cls.__name__} must be frozen (immutable)."

def test_snapshot_owns_only_identifiers_not_objects():
    """Verify that RuntimeIntelligenceSnapshot only uses identifiers, and does NOT embed upstream domains."""
    hints = typing.get_type_hints(RuntimeIntelligenceSnapshot)
    
    forbidden_types = [
        "RuntimeObservation",
        "RuntimeDecision",
        "RuntimeReasoning",
        "RuntimeConfidence",
        "RuntimeRecommendation",
        "RuntimeDecisionCoordinator"
    ]
    
    for field_name, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_types:
            assert forbidden not in type_str, f"RuntimeIntelligenceSnapshot must not embed {forbidden}. Found in {field_name}."

def test_context_owns_only_identifiers_not_objects():
    """Verify that RuntimeIntelligenceContext does NOT embed upstream domains."""
    hints = typing.get_type_hints(RuntimeIntelligenceContext)
    
    forbidden_types = [
        "RuntimeObservation",
        "RuntimeDecision",
        "RuntimeReasoning",
        "RuntimeConfidence",
        "RuntimeRecommendation",
        "RuntimeDecisionCoordinator"
    ]
    
    for field_name, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_types:
            assert forbidden not in type_str, f"RuntimeIntelligenceContext must not embed {forbidden}. Found in {field_name}."


def test_provider_and_hardware_independence():
    """Verify components contain no provider or hardware specific terminology."""
    banned_terms = [
        "Gemini", "OpenAI", "Ollama", "llama.cpp", "Claude",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "VRAM"
    ]
    
    import src.runtime.domain.runtime_intelligence_context_model as ric_module
    
    source_code = inspect.getsource(ric_module)
    for term in banned_terms:
        assert term not in source_code, f"Banned architectural term '{term}' found in runtime_intelligence_context_model.py."

def test_no_execution_or_orchestration_logic():
    """Verify that Runtime Intelligence Context does not contain execution or orchestration methods."""
    artifacts = [
        RuntimeIntelligenceSnapshot,
        RuntimeIntelligenceSummary,
        RuntimeIntelligenceContext,
        RuntimeIntelligenceContextInfo,
        RuntimeIntelligenceContextResult
    ]
    
    forbidden_method_terms = [
        "execute", "run", "schedule", "retry", "optimize", "learn", 
        "monitor", "orchestrate", "route", "select_provider", "plan"
    ]
    
    for artifact_cls in artifacts:
        methods = inspect.getmembers(artifact_cls, predicate=inspect.isfunction)
        for method_name, _ in methods:
            for forbidden in forbidden_method_terms:
                assert forbidden not in method_name.lower(), f"Forbidden behavioral logic '{method_name}' found in {artifact_cls.__name__}."

def test_dependency_direction():
    """Verify forward-only dependencies. No reverse imports."""
    import src.runtime.domain.runtime_intelligence_context_model as ric_module
    
    source_code = inspect.getsource(ric_module)
    
    assert "execution" not in source_code.lower()
    assert "schedule" not in source_code.lower()
    assert "retry" not in source_code.lower()
    assert "optimizer" not in source_code.lower()
    assert "learning" not in source_code.lower()
    
    # Ensure upstream models are not imported
    assert "RuntimeObservation" not in source_code
    assert "RuntimeDecision" not in source_code
    assert "RuntimeRecommendation" not in source_code
    assert "RuntimeReasoning" not in source_code
    assert "RuntimeConfidence" not in source_code
    assert "RuntimeDecisionCoordinator" not in source_code
