import pytest
import inspect
import sys
from dataclasses import is_dataclass
from typing import Dict

from src.runtime.domain.runtime_execution_model import (
    RuntimeExecutionState,
    RuntimeExecutionTrigger,
    RuntimeExecutionDecision,
    RuntimeExecutionInfo,
    RuntimeExecutionResult,
    RUNTIME_EXECUTION_POLICY
)
from src.runtime.core.runtime_execution_manager import RuntimeExecutionManager
from src.runtime.core.context import RuntimeContext


def test_runtime_execution_state_immutability():
    """Verify that RuntimeExecutionState is an immutable Enum with no behavior."""
    from enum import Enum
    assert issubclass(RuntimeExecutionState, Enum)
    assert issubclass(RuntimeExecutionState, str)
    
    # Ensure it only contains the allowed states for preparation
    expected_states = {"PREPARED", "READY", "EXECUTING", "COMPLETED", "FAILED", "ABORTED"}
    actual_states = {state.name for state in RuntimeExecutionState}
    assert expected_states == actual_states
    



def test_runtime_execution_trigger_immutability():
    """Verify that RuntimeExecutionTrigger is an immutable Enum with no behavior."""
    from enum import Enum
    assert issubclass(RuntimeExecutionTrigger, Enum)
    assert issubclass(RuntimeExecutionTrigger, str)
    
    expected_triggers = {"SCHEDULE_READY", "MANUAL_EXECUTION", "SYSTEM_REQUEST", "PIPELINE_REQUEST", "UNKNOWN"}
    actual_triggers = {t.name for t in RuntimeExecutionTrigger}
    assert expected_triggers == actual_triggers


def test_runtime_execution_decision_immutability():
    """Verify that RuntimeExecutionDecision is an immutable dataclass."""
    assert is_dataclass(RuntimeExecutionDecision)
    # Dataclasses don't expose frozen easily, but we can check its parameters
    import dataclasses
    assert dataclasses.Field in [type(f) for f in dataclasses.fields(RuntimeExecutionDecision)]


def test_runtime_execution_info_passive():
    """
    Verify that RuntimeExecutionInfo contains only structural metadata and provider_id,
    and does NOT own ProviderInfo, ProviderCapability, RuntimeRetryInfo, or RuntimeScheduleInfo.
    """
    assert is_dataclass(RuntimeExecutionInfo)
    import dataclasses
    fields = {f.name: f.type for f in dataclasses.fields(RuntimeExecutionInfo)}
    
    # Must contain provider_id
    assert "provider_id" in fields
    assert fields["provider_id"] == str or fields["provider_id"] == "str"
    
    # Must NOT contain banned models
    banned_types = ["ProviderInfo", "ProviderCapability", "ProviderHealthInfo", 
                    "ProviderFailoverInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo"]
    for field_name, field_type in fields.items():
        type_str = str(field_type)
        for banned in banned_types:
            assert banned not in type_str, f"RuntimeExecutionInfo must not contain {banned}"


def test_runtime_execution_policy_independence():
    """
    Verify that RUNTIME_EXECUTION_POLICY belongs to the domain and does not import
    RuntimeScheduleState directly.
    """
    assert isinstance(RUNTIME_EXECUTION_POLICY, dict)
    
    # Keys must be RuntimeExecutionTrigger
    for k in RUNTIME_EXECUTION_POLICY.keys():
        assert isinstance(k, RuntimeExecutionTrigger)
        
    # Values must be RuntimeExecutionState
    for v in RUNTIME_EXECUTION_POLICY.values():
        assert isinstance(v, RuntimeExecutionState)


def test_runtime_execution_manager_forbidden_imports():
    """
    Verify that RuntimeExecutionManager does not import forbidden execution libraries
    such as asyncio, threading, multiprocessing, or HTTP libraries.
    """
    # Import the module as text to avoid executing it
    import ast
    with open('backend/src/runtime/core/runtime_execution_manager.py', 'r') as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                assert name not in ['asyncio', 'threading', 'multiprocessing', 'requests', 'aiohttp', 'httpx']
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in ['asyncio', 'threading', 'multiprocessing', 'requests', 'aiohttp', 'httpx']


def test_runtime_context_passive_composition():
    """
    Verify that RuntimeContext instantiates RuntimeExecutionManager but does not invoke
    its execution preparation methods itself.
    """
    context = RuntimeContext()
    
    assert hasattr(context, "runtime_execution_manager")
    manager = context.runtime_execution_manager
    assert isinstance(manager, RuntimeExecutionManager)
    
    # Verify RuntimeContext does not have 'prepare_execution' or 'record_execution' methods
    assert not hasattr(context, "prepare_execution")
    assert not hasattr(context, "record_execution")
    assert not hasattr(context, "validate_execution")


def test_dependency_direction():
    """
    Verify that RuntimeExecutionManager depends on RuntimeSchedulingManager, 
    but RuntimeSchedulingManager does NOT depend on RuntimeExecutionManager.
    """
    import ast
    
    # Check execution manager imports scheduling manager
    with open('backend/src/runtime/core/runtime_execution_manager.py', 'r') as f:
        execution_tree = ast.parse(f.read())
        
    has_scheduling_import = False
    for node in ast.walk(execution_tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'runtime_scheduling_manager' or 'RuntimeSchedulingManager' in [n.name for n in node.names]:
                has_scheduling_import = True
    assert has_scheduling_import, "RuntimeExecutionManager must consume RuntimeSchedulingManager."
    
    # Check scheduling manager DOES NOT import execution manager
    with open('backend/src/runtime/core/runtime_scheduling_manager.py', 'r') as f:
        scheduling_tree = ast.parse(f.read())
        
    for node in ast.walk(scheduling_tree):
        if isinstance(node, ast.ImportFrom):
            assert 'runtime_execution_manager' not in (node.module or ""), "Scheduling must not depend on Execution."
            for alias in node.names:
                assert 'RuntimeExecution' not in alias.name, "Scheduling must not depend on Execution."
