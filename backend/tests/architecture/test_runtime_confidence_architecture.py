import ast
import inspect
import sys
from pathlib import Path
from dataclasses import is_dataclass

from src.runtime.domain.runtime_confidence_model import (
    RuntimeConfidenceState,
    RuntimeConfidenceLevel,
    RuntimeConfidenceFactor,
    RuntimeConfidenceEvidence,
    RuntimeConfidence,
    RuntimeConfidenceInfo,
    RuntimeConfidenceResult
)


def test_runtime_confidence_models_are_immutable():
    """Verify all domain models are structurally immutable."""
    assert is_dataclass(RuntimeConfidenceFactor)
    assert RuntimeConfidenceFactor.__dataclass_params__.frozen is True

    assert is_dataclass(RuntimeConfidenceEvidence)
    assert RuntimeConfidenceEvidence.__dataclass_params__.frozen is True

    assert is_dataclass(RuntimeConfidence)
    assert RuntimeConfidence.__dataclass_params__.frozen is True

    assert is_dataclass(RuntimeConfidenceInfo)
    assert RuntimeConfidenceInfo.__dataclass_params__.frozen is True

    assert is_dataclass(RuntimeConfidenceResult)
    assert RuntimeConfidenceResult.__dataclass_params__.frozen is True


def test_runtime_confidence_contains_no_reasoning_or_observation():
    """Verify RuntimeConfidence does not embed active reasoning or observation artifacts."""
    confidence_fields = {f.name: f.type for f in RuntimeConfidence.__dataclass_fields__.values()}
    
    # Must only contain IDs
    assert "reasoning_id" in confidence_fields
    assert confidence_fields["reasoning_id"] == str
    
    # Must not contain complex objects
    forbidden_types = [
        "RuntimeReasoning", 
        "RuntimeObservation", 
        "RuntimeDecision",
        "RuntimeRecommendation",
        "RuntimeOptimization"
    ]
    
    for field_name, field_type in confidence_fields.items():
        type_str = str(field_type)
        for forbidden in forbidden_types:
            assert forbidden not in type_str, f"RuntimeConfidence must not contain {forbidden}"


def test_runtime_confidence_evidence_contains_only_references():
    """Verify RuntimeConfidenceEvidence permanently owns only references and metadata."""
    evidence_fields = {f.name: f.type for f in RuntimeConfidenceEvidence.__dataclass_fields__.values()}
    
    assert "evidence_id" in evidence_fields
    assert "reference_id" in evidence_fields
    assert "evidence_type" in evidence_fields
    
    forbidden_terms = ["score", "weight", "rank", "priority", "RuntimeReasoning", "RuntimeDecision"]
    
    for field_name, field_type in evidence_fields.items():
        type_str = str(field_type)
        for term in forbidden_terms:
            assert term not in field_name.lower(), f"Evidence must not own {term}"
            assert term not in type_str, f"Evidence must not embed {term}"


def test_runtime_confidence_imports_no_downstream_contexts():
    """Verify Runtime Confidence does not import Recommendation, Decision Coordinator, or Intelligence Context."""
    # Read the source file
    confidence_file = Path(sys.modules['src.runtime.domain.runtime_confidence_model'].__file__)
    
    with open(confidence_file, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.lower()
                assert "recommendation" not in name, "Runtime Confidence must not import Recommendation"
                assert "coordinator" not in name, "Runtime Confidence must not import Decision Coordinator"
                assert "context" not in name, "Runtime Confidence must not import Intelligence Context"
                assert "reasoning_model" not in name, "Runtime Confidence should only rely on string identifiers, not the reasoning model"
                
        elif isinstance(node, ast.ImportFrom):
            module = node.module.lower() if node.module else ""
            assert "recommendation" not in module, "Runtime Confidence must not import Recommendation"
            assert "coordinator" not in module, "Runtime Confidence must not import Decision Coordinator"
            assert "context" not in module, "Runtime Confidence must not import Intelligence Context"
            
            for alias in node.names:
                name = alias.name.lower()
                assert "recommendation" not in name, "Runtime Confidence must not import Recommendation"
                assert "coordinator" not in name, "Runtime Confidence must not import Decision Coordinator"


def test_runtime_confidence_no_behavioral_logic():
    """Verify the confidence model module contains only passive classes."""
    confidence_file = Path(sys.modules['src.runtime.domain.runtime_confidence_model'].__file__)
    
    with open(confidence_file, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # The only functions allowed are __init__ or other generated methods (though typically dataclasses have none explicit)
            assert False, f"Behavioral logic found: function {node.name} is not permitted in Runtime Confidence Domain"
