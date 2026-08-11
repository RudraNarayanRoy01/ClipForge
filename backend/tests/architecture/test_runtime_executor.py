import ast
import inspect
from dataclasses import is_dataclass
from enum import Enum
import pytest

from src.runtime.core.execution_result_model import (
    ExecutionResult,
    ExecutionSummary,
    ExecutionOutcome,
    ExecutionStatus
)
from src.runtime.core.executor import RuntimeExecutor

def test_execution_result_is_immutable_dataclass():
    """Verify ExecutionResult is a frozen dataclass."""
    assert is_dataclass(ExecutionResult), "ExecutionResult must be a dataclass"
    assert ExecutionResult.__dataclass_params__.frozen is True, "ExecutionResult must be frozen"

def test_execution_summary_is_immutable_dataclass():
    """Verify ExecutionSummary is a frozen dataclass."""
    assert is_dataclass(ExecutionSummary), "ExecutionSummary must be a dataclass"
    assert ExecutionSummary.__dataclass_params__.frozen is True, "ExecutionSummary must be frozen"

def test_execution_outcome_is_enum():
    """Verify ExecutionOutcome is an Enum."""
    assert issubclass(ExecutionOutcome, Enum), "ExecutionOutcome must be an Enum"

def test_execution_status_is_enum():
    """Verify ExecutionStatus is an Enum."""
    assert issubclass(ExecutionStatus, Enum), "ExecutionStatus must be an Enum"

def test_runtime_executor_isolation():
    """
    Verify RuntimeExecutor has no scheduling state and no forbidden methods.
    It should only have __init__, execute, and _execute_attempt.
    """
    executor_methods = [m[0] for m in inspect.getmembers(RuntimeExecutor, predicate=inspect.isfunction)]
    
    # Should only have execute, __init__, and _execute_attempt
    for method in executor_methods:
        assert method in ["__init__", "execute", "_execute_attempt"], f"RuntimeExecutor has forbidden method: {method}"

def test_forbidden_imports_in_executor():
    """
    Strict AST check to ensure RuntimeExecutor does NOT import:
    - lifecycle
    - scheduler
    - retry
    - observation
    - optimization
    - orchestrator
    """
    import os
    executor_file = os.path.join(os.path.dirname(__file__), '../../src/runtime/core/executor.py')
    
    with open(executor_file, 'r') as f:
        tree = ast.parse(f.read())
        
    forbidden_modules = [
        "lifecycle", "scheduler", "retry", "observation", "optimization", 
        "orchestrator", "resource_allocator", "adaptive_runtime",
        "runtime_learning", "runtime_monitoring", "queue"
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

def test_forbidden_imports_in_execution_result_model():
    """
    Strict AST check to ensure Execution Result Domain does NOT import forbidden modules.
    """
    import os
    result_model_file = os.path.join(os.path.dirname(__file__), '../../src/runtime/core/execution_result_model.py')
    
    with open(result_model_file, 'r') as f:
        tree = ast.parse(f.read())
        
    forbidden_modules = [
        "lifecycle", "scheduler", "retry", "observation", "optimization", 
        "orchestrator", "resource_allocator", "adaptive_runtime"
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


def test_runtime_executor_signature():
    """
    Verify RuntimeExecutor's public execute contract is exactly aligned with Batch 6A.7.7.
    """
    from src.runtime.core.scheduling_model import SchedulingDecision
    from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
    from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
    
    sig = inspect.signature(RuntimeExecutor.execute)
    
    # Must have exact parameters
    assert "self" in sig.parameters, "execute() must take 'self'"
    assert "scheduling_decision" in sig.parameters, "execute() must take 'scheduling_decision'"
    assert "identity" in sig.parameters, "execute() must take 'identity'"
    
    # Verify annotations
    decision_param = sig.parameters["scheduling_decision"]
    identity_param = sig.parameters["identity"]
    
    # Handle string annotations vs type objects
    decision_anno = decision_param.annotation
    if isinstance(decision_anno, str):
        assert "SchedulingDecision" in decision_anno
    else:
        assert decision_anno is SchedulingDecision
        
    identity_anno = identity_param.annotation
    if isinstance(identity_anno, str):
        assert "RuntimeExecutionIdentity" in identity_anno
    else:
        assert identity_anno is RuntimeExecutionIdentity
        
    return_anno = sig.return_annotation
    if isinstance(return_anno, str):
        assert "RuntimeExecutionResult" in return_anno
    else:
        assert return_anno is RuntimeExecutionResult
