import pytest
import inspect
import sys
from dataclasses import is_dataclass
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import ast

from src.runtime.domain.provider_failover_model import (
    ProviderFailoverState,
    ProviderFailoverTrigger,
    ProviderFailoverDecision,
    ProviderFailoverInfo,
    ProviderFailoverResult,
    PROVIDER_FAILOVER_POLICY
)
from src.runtime.core.provider_failover_manager import ProviderFailoverManager
from src.runtime.core.context import RuntimeContext


def test_provider_failover_enums():
    import enum
    assert issubclass(ProviderFailoverState, enum.Enum), "ProviderFailoverState must be an Enum"
    assert issubclass(ProviderFailoverTrigger, enum.Enum), "ProviderFailoverTrigger must be an Enum"


def test_provider_failover_models_are_immutable():
    assert is_dataclass(ProviderFailoverDecision)
    assert ProviderFailoverDecision.__dataclass_params__.frozen == True, "ProviderFailoverDecision must be frozen"

    assert is_dataclass(ProviderFailoverInfo)
    assert ProviderFailoverInfo.__dataclass_params__.frozen == True, "ProviderFailoverInfo must be frozen"

    assert is_dataclass(ProviderFailoverResult)
    assert ProviderFailoverResult.__dataclass_params__.frozen == True, "ProviderFailoverResult must be frozen"


def test_provider_failover_policy_is_isolated():
    assert isinstance(PROVIDER_FAILOVER_POLICY, dict)
    
    # Ensure it defines the rules structurally mapped from triggers.
    assert ProviderFailoverTrigger.UNKNOWN in PROVIDER_FAILOVER_POLICY
    
    # Ensure it does NOT import ProviderHealthState
    import src.runtime.domain.provider_failover_model as pf_model
    policy_module_source = inspect.getsource(sys.modules[pf_model.__name__])
    assert "ProviderHealthState" not in policy_module_source, "ProviderFailoverPolicy must NEVER directly encode ProviderHealthState"

    # Ensure ProviderFailoverManager does not hardcode its own policy
    manager_source = inspect.getsource(ProviderFailoverManager)
    assert "PROVIDER_FAILOVER_POLICY" in manager_source, "Manager must consume the policy, not redefine it."
    
    # The manager must not mutate the policy
    assert ".append" not in manager_source
    assert "PROVIDER_FAILOVER_POLICY[" not in manager_source.replace("PROVIDER_FAILOVER_POLICY.get(", "").replace("PROVIDER_FAILOVER_POLICY]", "")


def test_provider_failover_info_does_not_own_other_domains():
    info_fields = ProviderFailoverInfo.__dataclass_fields__
    
    assert "provider_id" in info_fields, "ProviderFailoverInfo must reference provider_id"
    assert "provider_info" not in info_fields, "ProviderFailoverInfo must NEVER embed ProviderInfo"
    assert "provider_capability" not in info_fields, "ProviderFailoverInfo must NEVER embed ProviderCapability"
    assert "model_info" not in info_fields, "ProviderFailoverInfo must NEVER embed ModelInfo"
    assert "model_lifecycle" not in info_fields, "ProviderFailoverInfo must NEVER embed ModelLifecycleInfo"
    assert "provider_health" not in info_fields, "ProviderFailoverInfo must NEVER embed ProviderHealthInfo"


def test_provider_failover_manager_imports():
    manager_path = Path(__file__).parent.parent.parent / "src" / "runtime" / "core" / "provider_failover_manager.py"
    with open(manager_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    banned_imports = [
        "runtimeexecutor",
        "runtimescheduler",
        "runtimeretry",
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
                    assert banned not in name.name.lower(), f"ProviderFailoverManager must NEVER import {banned}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for banned in banned_imports:
                    assert banned not in node.module.lower(), f"ProviderFailoverManager must NEVER import {banned}"


def test_runtime_context_remains_passive():
    context_source = inspect.getsource(RuntimeContext)
    
    assert "ProviderFailoverManager" in context_source, "RuntimeContext must compose ProviderFailoverManager"
    
    # Ensure context does not actively call failover behavior
    assert "provider_failover_manager.evaluate_failover(" not in context_source, "RuntimeContext must not invoke failover evaluation"
    assert "provider_failover_manager.record_failover(" not in context_source, "RuntimeContext must not record failover"
    assert "provider_failover_manager.clear_failover(" not in context_source, "RuntimeContext must not clear failover"
