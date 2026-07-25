import pytest
import inspect
import dataclasses
import importlib
import sys
import re

def get_all_dataclasses_from_modules(module_names):
    dataclass_list = []
    for mod_name in module_names:
        mod = importlib.import_module(mod_name)
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if dataclasses.is_dataclass(obj) and obj.__module__ == mod_name:
                dataclass_list.append(obj)
    return dataclass_list

def get_intelligence_modules():
    return [
        "src.runtime.domain.runtime_intelligence_model",
        "src.runtime.domain.runtime_observation_model",
        "src.runtime.domain.runtime_decision_model",
        "src.runtime.domain.runtime_reasoning_model",
        "src.runtime.domain.runtime_confidence_model",
        "src.runtime.domain.runtime_recommendation_model",
        "src.runtime.domain.runtime_decision_coordinator_model",
        "src.runtime.domain.runtime_intelligence_context_model"
    ]

def strip_docstrings(source_code):
    """Remove docstrings from source code to avoid false positives in banned words check."""
    # This regex removes triple-quoted strings (both single and double quotes)
    return re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', source_code)

def test_runtime_intelligence_artifacts_are_immutable():
    """Verify that all dataclasses in the Runtime Intelligence pipeline are immutable."""
    modules = get_intelligence_modules()
    artifacts = get_all_dataclasses_from_modules(modules)
    
    assert len(artifacts) > 0, "No dataclasses found, check module imports."
    
    for artifact_cls in artifacts:
        assert getattr(artifact_cls, "__dataclass_params__").frozen is True, f"{artifact_cls.__name__} in {artifact_cls.__module__} must be frozen (immutable)."

def test_provider_and_hardware_independence():
    """Verify components contain no provider or hardware specific terminology in code."""
    banned_terms = [
        "Gemini", "OpenAI", "Anthropic", "Claude", "Ollama", "llama.cpp",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "TensorRT"
    ]
    
    modules = get_intelligence_modules()
    
    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        source_code = inspect.getsource(mod)
        clean_code = strip_docstrings(source_code)
        for term in banned_terms:
            assert term not in clean_code, f"Banned architectural term '{term}' found in {mod_name}."

def test_execution_boundary():
    """Verify components do not contain execution terminology in code."""
    banned_terms = [
        "Execution Engine", "Execution Planner", "Scheduling",
        "Monitoring", "Telemetry", "Optimization",
        "Learning", "Routing", "Provider Registry", "Model Lifecycle",
        "Policy Engine", "Task Queue", "Execution Workflow", "Worker Management",
        "execution APIs", "scheduling APIs", "retry APIs", "monitoring APIs",
        "telemetry APIs", "optimization APIs", "learning APIs", "provider APIs",
        "networking", "HTTP", "asyncio", "threading", "multiprocessing",
        "workflow execution", "behavioral logic", "execution orchestration",
        "provider routing", "provider invocation", "model invocation",
        "import asyncio", "import threading", "import multiprocessing",
        "import requests", "import httpx", "import aiohttp", "import urllib"
    ]
    
    modules = get_intelligence_modules()
    
    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        source_code = inspect.getsource(mod)
        clean_code = strip_docstrings(source_code)
        for term in banned_terms:
            assert term not in clean_code, f"Banned execution term '{term}' found in {mod_name}."

def test_snapshot_and_aggregation_certification():
    """Verify Runtime Intelligence Context follows snapshot and aggregation rules."""
    mod = importlib.import_module("src.runtime.domain.runtime_intelligence_context_model")
    context_cls = getattr(mod, "RuntimeIntelligenceContext")
    snapshot_cls = getattr(mod, "RuntimeIntelligenceSnapshot")
    
    context_fields = {f.name: f.type for f in dataclasses.fields(context_cls)}
    snapshot_fields = {f.name: f.type for f in dataclasses.fields(snapshot_cls)}
    
    banned_fields = ['memory', 'history', 'event_storage', 'telemetry', 'metrics', 'execution_history', 'previous_snapshots']
    
    for f in banned_fields:
        assert f not in context_fields, f"Context must not own '{f}'."
        assert f not in snapshot_fields, f"Snapshot must not own '{f}'."

def test_dependency_direction():
    """Verify that dependencies remain strictly forward-only and no reverse imports exist."""
    modules = get_intelligence_modules()
    
    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        for name, val in vars(mod).items():
            if isinstance(val, type) and val.__module__ is not None:
                if "execution" in val.__module__ or "scheduler" in val.__module__ or "monitoring" in val.__module__ or "optimization" in val.__module__ or "telemetry" in val.__module__ or "learning" in val.__module__:
                    pytest.fail(f"Module {mod_name} illegally imports from {val.__module__}")

def test_no_embedded_domain_objects():
    """Verify that artifacts only reference immutable identifiers (IDs) rather than embedding domain objects."""
    modules = get_intelligence_modules()
    artifacts = get_all_dataclasses_from_modules(modules)
    
    for artifact_cls in artifacts:
        fields = dataclasses.fields(artifact_cls)
        for field in fields:
            # The field type should not be another domain object from these modules (except Enums or metadata dictionaries)
            # A simple heuristic: if it's a dataclass from the intelligence modules, it's illegal.
            # (Context aggregates lists of IDs, etc. rather than instances of the model)
            if inspect.isclass(field.type) and dataclasses.is_dataclass(field.type):
                type_name = field.type.__name__.lower()
                if "domain" in field.type.__module__ and not any(allowed in type_name for allowed in ["metadata", "info", "snapshot", "summary"]):
                    # We might have composed metadata dataclasses which is fine, but embedding full domain objects like RuntimeObservation inside RuntimeReasoning is banned.
                    pytest.fail(f"Artifact {artifact_cls.__name__} illegally embeds domain object {field.type.__name__}. Must use immutable identifiers.")
