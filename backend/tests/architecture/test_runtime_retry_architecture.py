import pytest
import inspect
import sys
import os
import ast

from dataclasses import is_dataclass

from src.runtime.domain.runtime_retry_model import (
    RuntimeRetryState,
    RuntimeRetryTrigger,
    RuntimeRetryDecision,
    RuntimeRetryInfo,
    RuntimeRetryResult,
    RUNTIME_RETRY_POLICY
)
from src.runtime.core.runtime_retry_manager import RuntimeRetryManager
from src.runtime.core.context import RuntimeContext
from src.runtime.domain.provider_failover_model import ProviderFailoverState

def test_runtime_retry_domain_immutability():
    """Verify that Runtime Retry domain models are strictly immutable."""
    
    # Assert they are dataclasses
    assert is_dataclass(RuntimeRetryDecision)
    assert is_dataclass(RuntimeRetryInfo)
    assert is_dataclass(RuntimeRetryResult)
    
    # Assert they are frozen (immutable)
    assert RuntimeRetryDecision.__dataclass_params__.frozen is True
    assert RuntimeRetryInfo.__dataclass_params__.frozen is True
    assert RuntimeRetryResult.__dataclass_params__.frozen is True

def test_runtime_retry_policy_immutability():
    """Verify that RUNTIME_RETRY_POLICY is defined and is a dict."""
    assert isinstance(RUNTIME_RETRY_POLICY, dict)
    # Ensure it only maps Triggers to States
    for k, v in RUNTIME_RETRY_POLICY.items():
        assert isinstance(k, RuntimeRetryTrigger)
        assert isinstance(v, RuntimeRetryState)

def test_runtime_retry_info_no_foreign_ownership():
    """Verify that RuntimeRetryInfo only holds references, not foreign domain objects."""
    fields = RuntimeRetryInfo.__dataclass_fields__
    
    # MUST contain provider_id
    assert "provider_id" in fields
    assert fields["provider_id"].type == "str" or fields["provider_id"].type == str
    
    # MUST NOT contain upstream complex objects
    forbidden_types = [
        "ProviderInfo", 
        "ProviderCapability", 
        "ProviderHealthInfo", 
        "ProviderFailoverInfo"
    ]
    
    for field_name, field_def in fields.items():
        field_type_str = str(field_def.type)
        for forbidden in forbidden_types:
            assert forbidden not in field_type_str, f"RuntimeRetryInfo must not own {forbidden}"

def test_runtime_retry_manager_methods():
    """Verify the allowed methods on RuntimeRetryManager and absence of execution methods."""
    manager_methods = [m[0] for m in inspect.getmembers(RuntimeRetryManager, predicate=inspect.isfunction)]
    
    # Allowed structural methods
    allowed_methods = [
        "__init__",
        "_validate_trigger",
        "register_provider",
        "get_retry",
        "get_state",
        "evaluate_retry",
        "record_retry",
        "validate_retry",
        "clear_retry"
    ]
    
    for method in manager_methods:
        assert method in allowed_methods, f"Method {method} is not allowed on RuntimeRetryManager."
        
    # Explicitly verify NO execution methods
    forbidden_terms = ["execute", "wait", "sleep", "backoff", "schedule", "http", "request"]
    for method in manager_methods:
        for term in forbidden_terms:
            assert term not in method.lower(), f"Manager must not contain operational method: {method}"

def _analyze_imports(filepath: str) -> set:
    """Helper to extract imported module names from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)
        
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

def test_runtime_retry_manager_dependencies():
    """Verify RuntimeRetryManager doesn't import forbidden operational modules."""
    filepath = os.path.join("d:\\", "My Data", "Precious Data", "Vibe Code", "AI Clipping Platform", 
                            "backend", "src", "runtime", "core", "runtime_retry_manager.py")
    
    if not os.path.exists(filepath):
        # Fallback for cross-platform/dynamic paths if running in different environment
        import src.runtime.core.runtime_retry_manager as manager_mod
        filepath = manager_mod.__file__
        
    imports = _analyze_imports(filepath)
    
    # MUST NOT import network, scheduling, execution, http
    forbidden_imports = [
        "http", "requests", "urllib", "asyncio", "socket", 
        "scheduler", "executor", "runtime_execution"
    ]
    
    for imp in imports:
        for forbidden in forbidden_imports:
            assert forbidden not in imp.lower(), f"RuntimeRetryManager must not import {imp}"

def test_runtime_retry_policy_no_failover_state_import():
    """Verify RuntimeRetryPolicy (in domain model) does NOT import ProviderFailoverState."""
    filepath = os.path.join("d:\\", "My Data", "Precious Data", "Vibe Code", "AI Clipping Platform", 
                            "backend", "src", "runtime", "domain", "runtime_retry_model.py")
    
    if not os.path.exists(filepath):
        import src.runtime.domain.runtime_retry_model as domain_mod
        filepath = domain_mod.__file__
        
    imports = _analyze_imports(filepath)
    
    # MUST NOT import provider_failover_model or state
    for imp in imports:
        assert "provider_failover" not in imp.lower(), "Runtime Retry Domain must not import Provider Failover Domain"

def test_runtime_context_composition():
    """Verify RuntimeContext wires the manager but contains no retry logic."""
    context = RuntimeContext()
    
    # Verify manager is exposed
    assert hasattr(context, "runtime_retry_manager")
    assert isinstance(context.runtime_retry_manager, RuntimeRetryManager)
    
    # Verify no execution methods on context related to retry
    context_methods = [m[0] for m in inspect.getmembers(RuntimeContext, predicate=inspect.isfunction)]
    forbidden_context_methods = ["evaluate_retry", "record_retry", "execute_retry"]
    
    for method in context_methods:
        assert method not in forbidden_context_methods, f"RuntimeContext must not implement {method}"
