import inspect
import ast
import os
from pathlib import Path

from src.runtime.domain.provider_capability_model import (
    ProviderCapability,
    CapabilityLimits,
    ProviderCapabilityResult,
    CapabilityType
)
from src.runtime.core.provider_capability_registry import ProviderCapabilityRegistry
from src.runtime.core.context import RuntimeContext


def test_provider_capability_is_immutable():
    """Verify ProviderCapability is immutable."""
    assert ProviderCapability.__dataclass_params__.frozen is True

def test_capability_limits_is_immutable():
    """Verify CapabilityLimits is immutable."""
    assert CapabilityLimits.__dataclass_params__.frozen is True

def test_provider_capability_result_is_immutable():
    """Verify ProviderCapabilityResult is immutable."""
    assert ProviderCapabilityResult.__dataclass_params__.frozen is True

def test_provider_capability_does_not_own_provider_info():
    """Verify ProviderCapability only references provider_id and does not own ProviderInfo."""
    fields = ProviderCapability.__dataclass_fields__
    assert "provider_id" in fields
    assert fields["provider_id"].type == "str" or fields["provider_id"].type == str
    
    # Ensure ProviderInfo is not referenced anywhere in the fields
    for field_name, field_def in fields.items():
        assert "ProviderInfo" not in str(field_def.type)
        assert field_name != "provider_info"

def test_provider_capability_registry_owns_only_metadata():
    """Verify ProviderCapabilityRegistry only owns capability metadata."""
    registry = ProviderCapabilityRegistry()
    assert hasattr(registry, "register_capability")
    assert hasattr(registry, "update_capability")
    assert hasattr(registry, "remove_capability")
    assert hasattr(registry, "get_capability")
    assert hasattr(registry, "list_capabilities")
    assert hasattr(registry, "capability_exists")
    
    # Verify no execution methods exist
    methods = [m[0] for m in inspect.getmembers(registry, predicate=inspect.ismethod)]
    forbidden = ["execute", "schedule", "route", "rank", "score", "evaluate"]
    for method in methods:
        for f in forbidden:
            assert f not in method.lower()

def test_registry_does_not_import_execution_components():
    """Verify ProviderCapabilityRegistry never imports Runtime execution components."""
    file_path = inspect.getfile(ProviderCapabilityRegistry)
    
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert "executor" not in module
            assert "scheduler" not in module
            assert "orchestrator" not in module
            assert "lifecycle" not in module
            
            for name in node.names:
                assert "Execution" not in name.name
                assert "Scheduler" not in name.name
        elif isinstance(node, ast.Import):
            for name in node.names:
                assert "executor" not in name.name

def test_runtime_context_composes_registry_passively():
    """Verify RuntimeContext only composes ProviderCapabilityRegistry and never invokes behavior."""
    context = RuntimeContext()
    assert hasattr(context, "provider_capability_registry")
    assert isinstance(context.provider_capability_registry, ProviderCapabilityRegistry)
    
    file_path = inspect.getfile(RuntimeContext)
    with open(file_path, "r") as f:
        content = f.read()
        
    # Check that it doesn't call methods on it, only instantiates it
    assert "self._provider_capability_registry.register_capability" not in content
    assert "self._provider_capability_registry.update" not in content
    assert "self._provider_capability_registry.remove" not in content
