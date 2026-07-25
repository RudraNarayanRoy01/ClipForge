import ast
import inspect
from dataclasses import is_dataclass
from enum import Enum
import pytest

from src.runtime.core.lifecycle_model import (
    LifecycleResult,
    LifecycleSummary,
    LifecycleTransition,
    LifecycleState,
    LifecycleStage
)
from src.runtime.core.lifecycle import RuntimeLifecycle

def test_lifecycle_result_is_immutable_dataclass():
    """Verify LifecycleResult is a frozen dataclass."""
    assert is_dataclass(LifecycleResult), "LifecycleResult must be a dataclass"
    assert LifecycleResult.__dataclass_params__.frozen is True, "LifecycleResult must be frozen"

def test_lifecycle_summary_is_immutable_dataclass():
    """Verify LifecycleSummary is a frozen dataclass."""
    assert is_dataclass(LifecycleSummary), "LifecycleSummary must be a dataclass"
    assert LifecycleSummary.__dataclass_params__.frozen is True, "LifecycleSummary must be frozen"

def test_lifecycle_transition_is_immutable_dataclass():
    """Verify LifecycleTransition is a frozen dataclass."""
    assert is_dataclass(LifecycleTransition), "LifecycleTransition must be a dataclass"
    assert LifecycleTransition.__dataclass_params__.frozen is True, "LifecycleTransition must be frozen"

def test_lifecycle_state_is_enum():
    """Verify LifecycleState is an Enum."""
    assert issubclass(LifecycleState, Enum), "LifecycleState must be an Enum"

def test_lifecycle_stage_is_enum():
    """Verify LifecycleStage is an Enum."""
    assert issubclass(LifecycleStage, Enum), "LifecycleStage must be an Enum"

def test_runtime_lifecycle_isolation():
    """
    Verify RuntimeLifecycle only has evaluate and helper methods.
    """
    methods = [m[0] for m in inspect.getmembers(RuntimeLifecycle, predicate=inspect.isfunction)]
    
    for method in methods:
        assert method in ["evaluate", "_determine_state", "_determine_stage"], f"RuntimeLifecycle has forbidden method: {method}"

def test_forbidden_imports_in_lifecycle_domain():
    """
    Strict AST check to ensure Lifecycle Domain does NOT import forbidden modules.
    """
    import os
    model_file = os.path.join(os.path.dirname(__file__), '../../src/runtime/core/lifecycle_model.py')
    
    with open(model_file, 'r') as f:
        tree = ast.parse(f.read())
        
    forbidden_modules = [
        "scheduler", "retry", "observation", "optimization", 
        "orchestrator", "resource_allocator", "adaptive_runtime",
        "executor", "learning", "telemetry", "metrics"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                for forbidden in forbidden_modules:
                    assert forbidden not in name.name, f"Forbidden import found: {name.name}"
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for forbidden in forbidden_modules:
                assert forbidden not in module_name, f"Forbidden import found: {module_name}"

def test_forbidden_imports_in_lifecycle_engine():
    """
    Strict AST check to ensure RuntimeLifecycle does NOT import forbidden modules.
    """
    import os
    engine_file = os.path.join(os.path.dirname(__file__), '../../src/runtime/core/lifecycle.py')
    
    with open(engine_file, 'r') as f:
        tree = ast.parse(f.read())
        
    forbidden_modules = [
        "scheduler", "retry", "observation", "optimization", 
        "orchestrator", "resource_allocator", "adaptive_runtime",
        "executor", "learning", "telemetry", "metrics"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                for forbidden in forbidden_modules:
                    assert forbidden not in name.name, f"Forbidden import found: {name.name}"
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for forbidden in forbidden_modules:
                assert forbidden not in module_name, f"Forbidden import found: {module_name}"
