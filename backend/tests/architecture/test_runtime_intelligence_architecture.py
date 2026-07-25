import inspect
import sys
from dataclasses import is_dataclass
from typing import get_type_hints

import pytest

from src.runtime.domain import runtime_intelligence_model
from src.runtime.domain.runtime_intelligence_model import (
    RuntimeIntelligenceState,
    RuntimeDecisionType,
    RuntimeDecisionReason,
    RUNTIME_INTELLIGENCE_POLICY,
    RuntimeIntelligenceInfo,
    RuntimeDecisionResult
)

def test_runtime_intelligence_state_is_enum():
    assert issubclass(RuntimeIntelligenceState, runtime_intelligence_model.Enum)
    
def test_runtime_decision_type_is_enum():
    assert issubclass(RuntimeDecisionType, runtime_intelligence_model.Enum)

def test_runtime_decision_reason_is_immutable():
    assert is_dataclass(RuntimeDecisionReason)
    assert RuntimeDecisionReason.__dataclass_params__.frozen is True

def test_runtime_intelligence_info_is_immutable():
    assert is_dataclass(RuntimeIntelligenceInfo)
    assert RuntimeIntelligenceInfo.__dataclass_params__.frozen is True

def test_runtime_decision_result_is_immutable():
    assert is_dataclass(RuntimeDecisionResult)
    assert RuntimeDecisionResult.__dataclass_params__.frozen is True

def test_runtime_intelligence_policy_is_domain_owned():
    # Verify the mapping explicitly covers all expected DecisionTypes
    expected_keys = {
        RuntimeDecisionType.EXECUTE,
        RuntimeDecisionType.WAIT,
        RuntimeDecisionType.RETRY,
        RuntimeDecisionType.FAILOVER,
        RuntimeDecisionType.ABORT,
        RuntimeDecisionType.UNKNOWN,
    }
    assert set(RUNTIME_INTELLIGENCE_POLICY.keys()) == expected_keys
    
    # Ensure all values are from RuntimeIntelligenceState
    for val in RUNTIME_INTELLIGENCE_POLICY.values():
        assert isinstance(val, RuntimeIntelligenceState)

def test_runtime_intelligence_info_references():
    hints = get_type_hints(RuntimeIntelligenceInfo)
    # Ensure provider_id is just a string reference
    assert hints["provider_id"] == str
    
    # Ensure it doesn't contain forbidden complex objects
    forbidden_terms = [
        "ProviderInfo", "ProviderCapability", "ModelInfo", "ProviderHealthInfo",
        "ProviderFailoverInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo", 
        "RuntimeExecutionInfo", "RuntimeObservation", "RuntimeConfidence", 
        "RuntimeRecommendation", "RuntimeReasoning"
    ]
    for field_name, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_terms:
            assert forbidden not in type_str, f"RuntimeIntelligenceInfo must NOT contain {forbidden}"

def test_runtime_decision_result_references():
    hints = get_type_hints(RuntimeDecisionResult)
    forbidden_terms = [
        "RuntimeObservation", "ProviderHealth", "RuntimeExecutionInfo", 
        "RuntimeScheduleInfo", "RuntimeRetryInfo", "RuntimeConfidence", 
        "RuntimeRecommendation", "Reasoning"
    ]
    for field_name, field_type in hints.items():
        type_str = str(field_type)
        for forbidden in forbidden_terms:
            assert forbidden not in type_str, f"RuntimeDecisionResult must NOT contain {forbidden}"

def test_no_forbidden_imports():
    import ast
    with open(runtime_intelligence_model.__file__, "r") as f:
        content = f.read()
        
    forbidden_imports = [
        "asyncio", "threading", "multiprocessing", "socket", "requests", "http",
        "urllib", "aiohttp", "httpx", "RuntimeExecutionState", "RuntimeObservation",
        "RuntimeDecisionEngine"
    ]
    
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden not in alias.name, f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in forbidden_imports:
                    assert forbidden not in node.module, f"Forbidden import: {node.module}"
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden not in alias.name, f"Forbidden import: {alias.name}"

def test_no_managers_or_services():
    classes = [m[0] for m in inspect.getmembers(runtime_intelligence_model, inspect.isclass)]
    for cls_name in classes:
        assert "Manager" not in cls_name, f"Domain must not contain managers: {cls_name}"
        assert "Service" not in cls_name, f"Domain must not contain services: {cls_name}"
        assert "Engine" not in cls_name, f"Domain must not contain engines: {cls_name}"

def test_dependency_direction_is_one_way():
    """
    Ensure the intelligence domain does not depend on downstream observation modules
    if they were to exist.
    """
    # Since this is the initial creation, we simply check that there are no
    # upward/downward imports to future modules.
    with open(runtime_intelligence_model.__file__, "r") as f:
        content = f.read()
        
    # The file should only import from stdlib (enum, dataclasses, typing, datetime)
    # It must not import from any other src.runtime modules (which would violate isolation)
    assert "from src.runtime" not in content, "Domain must not import other runtime modules directly to preserve boundaries"
    assert "import src.runtime" not in content
