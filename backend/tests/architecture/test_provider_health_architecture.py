import pytest
import inspect
import sys
from dataclasses import is_dataclass
from typing import Dict, List, Optional
from datetime import datetime

# Assuming these exist, adjust if imports are slightly different
from src.runtime.domain.provider_health_model import (
    ProviderHealthState,
    ProviderHealthTransition,
    ProviderHealthInfo,
    ProviderHealthResult,
    PROVIDER_HEALTH_TRANSITION_POLICY
)
from src.runtime.core.provider_health_manager import ProviderHealthManager
from src.runtime.core.context import RuntimeContext


def test_provider_health_state_is_enum():
    import enum
    assert issubclass(ProviderHealthState, enum.Enum), "ProviderHealthState must be an Enum"


def test_provider_health_models_are_immutable():
    assert is_dataclass(ProviderHealthTransition)
    assert ProviderHealthTransition.__dataclass_params__.frozen == True, "ProviderHealthTransition must be frozen"

    assert is_dataclass(ProviderHealthInfo)
    assert ProviderHealthInfo.__dataclass_params__.frozen == True, "ProviderHealthInfo must be frozen"

    assert is_dataclass(ProviderHealthResult)
    assert ProviderHealthResult.__dataclass_params__.frozen == True, "ProviderHealthResult must be frozen"


def test_provider_health_policy_is_isolated():
    assert isinstance(PROVIDER_HEALTH_TRANSITION_POLICY, dict)
    
    # Ensure it defines the rules.
    assert ProviderHealthState.UNKNOWN in PROVIDER_HEALTH_TRANSITION_POLICY
    
    # Ensure ProviderHealthManager does not hardcode its own policy
    manager_source = inspect.getsource(ProviderHealthManager)
    assert "PROVIDER_HEALTH_TRANSITION_POLICY" in manager_source, "Manager must consume the policy, not redefine it."
    
    # The manager must not mutate the policy
    assert ".append" not in manager_source
    assert "PROVIDER_HEALTH_TRANSITION_POLICY[" not in manager_source.replace("PROVIDER_HEALTH_TRANSITION_POLICY.get(", "")


def test_provider_health_info_does_not_own_other_domains():
    info_fields = ProviderHealthInfo.__dataclass_fields__
    
    assert "provider_id" in info_fields, "ProviderHealthInfo must reference provider_id"
    assert "provider_info" not in info_fields, "ProviderHealthInfo must NEVER embed ProviderInfo"
    assert "provider_capability" not in info_fields, "ProviderHealthInfo must NEVER embed ProviderCapability"
    assert "model_info" not in info_fields, "ProviderHealthInfo must NEVER embed ModelInfo"
    assert "model_lifecycle" not in info_fields, "ProviderHealthInfo must NEVER embed ModelLifecycleInfo"


def test_provider_health_manager_does_not_import_execution():
    from pathlib import Path
    import ast
    
    manager_path = Path(__file__).parent.parent.parent / "src" / "runtime" / "core" / "provider_health_manager.py"
    with open(manager_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    banned_imports = [
        "runtimeexecutor",
        "runtimescheduler",
        "runtimeretry",
        "providerfailover",
        "requests",
        "http",
        "httpx",
        "aiohttp",
        "socket",
        "urllib"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                for banned in banned_imports:
                    assert banned not in name.name.lower(), f"ProviderHealthManager must NEVER import {banned}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for banned in banned_imports:
                    assert banned not in node.module.lower(), f"ProviderHealthManager must NEVER import {banned}"


def test_runtime_context_remains_passive():
    context_source = inspect.getsource(RuntimeContext)
    
    assert "ProviderHealthManager" in context_source, "RuntimeContext must compose ProviderHealthManager"
    
    # Ensure context does not actively call health behavior
    assert "provider_health_manager.transition_health(" not in context_source, "RuntimeContext must not invoke health transitions"
    assert "provider_health_manager.mark_healthy(" not in context_source, "RuntimeContext must not invoke mark_healthy"
    assert "provider_health_manager.mark_unhealthy(" not in context_source, "RuntimeContext must not invoke mark_unhealthy"
