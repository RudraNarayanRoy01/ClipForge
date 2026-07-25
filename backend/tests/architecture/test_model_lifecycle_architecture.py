import ast
import inspect
from pathlib import Path
import pytest
from dataclasses import is_dataclass

from src.runtime.domain.model_lifecycle_model import (
    ModelLifecycleState,
    ModelLifecycleTransition,
    ModelLifecycleInfo,
    ModelLifecycleResult,
    MODEL_LIFECYCLE_TRANSITION_POLICY
)
from src.runtime.core.model_lifecycle_manager import ModelLifecycleManager
from src.runtime.core.context import RuntimeContext


def test_model_lifecycle_domain_immutability():
    """Verify all domain objects are frozen dataclasses."""
    assert is_dataclass(ModelLifecycleTransition)
    assert ModelLifecycleTransition.__dataclass_params__.frozen

    assert is_dataclass(ModelLifecycleInfo)
    assert ModelLifecycleInfo.__dataclass_params__.frozen

    assert is_dataclass(ModelLifecycleResult)
    assert ModelLifecycleResult.__dataclass_params__.frozen


def test_model_lifecycle_info_ownership():
    """Verify ModelLifecycleInfo does not embed ModelInfo or ProviderInfo."""
    fields = ModelLifecycleInfo.__dataclass_fields__
    
    assert "model_id" in fields, "ModelLifecycleInfo must reference model_id"
    assert "model_info" not in fields, "ModelLifecycleInfo must NOT embed ModelInfo"
    assert "provider_info" not in fields, "ModelLifecycleInfo must NOT embed ProviderInfo"
    assert "provider_capability" not in fields, "ModelLifecycleInfo must NOT embed ProviderCapability"


def test_model_lifecycle_manager_transition_validation():
    """Verify ModelLifecycleManager enforces the structural transition policy."""
    manager = ModelLifecycleManager()
    manager.register_model("test-model-1")
    
    # Valid transition
    result = manager.initialize_model("test-model-1")
    assert result.validation_result
    assert manager.get_state("test-model-1") == ModelLifecycleState.INITIALIZING
    
    # Invalid transition (INITIALIZING -> BUSY is invalid)
    with pytest.raises(ValueError, match="Invalid transition"):
        manager.transition_state("test-model-1", ModelLifecycleState.BUSY)
        
    # Another valid transition
    manager.mark_ready("test-model-1")
    assert manager.get_state("test-model-1") == ModelLifecycleState.READY


def test_model_lifecycle_manager_imports():
    """Verify ModelLifecycleManager does not import forbidden Runtime Intelligence layers."""
    manager_path = Path(__file__).parent.parent.parent / "src" / "runtime" / "core" / "model_lifecycle_manager.py"
    
    with open(manager_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                assert "executor" not in name.name.lower()
                assert "scheduler" not in name.name.lower()
                assert "health" not in name.name.lower()
                assert "failover" not in name.name.lower()
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert "executor" not in node.module.lower()
                assert "scheduler" not in node.module.lower()
                assert "health" not in node.module.lower()
                assert "failover" not in node.module.lower()


def test_runtime_context_passive_lifecycle():
    """Verify RuntimeContext exposes ModelLifecycleManager but does not invoke lifecycle behavior itself."""
    context_path = Path(__file__).parent.parent.parent / "src" / "runtime" / "core" / "context.py"
    
    with open(context_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # RuntimeContext should not be calling .transition_state, .mark_ready, etc on anything
                forbidden_methods = [
                    "transition_state", "mark_ready", "mark_busy", "mark_idle",
                    "initialize_model", "start_update", "finish_update"
                ]
                assert node.func.attr not in forbidden_methods, f"RuntimeContext calls forbidden lifecycle method {node.func.attr}"

def test_transition_policy_ownership():
    """Verify the transition rules live in the policy, not hardcoded in the manager."""
    manager_path = Path(__file__).parent.parent.parent / "src" / "runtime" / "core" / "model_lifecycle_manager.py"
    
    with open(manager_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # The manager must query MODEL_LIFECYCLE_TRANSITION_POLICY
    assert "MODEL_LIFECYCLE_TRANSITION_POLICY" in content
