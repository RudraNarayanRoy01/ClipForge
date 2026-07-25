import inspect
import sys
import types
from dataclasses import is_dataclass
from typing import Any, get_type_hints

from src.runtime.domain import runtime_decision_model


def test_runtime_decision_domain_is_pure_data():
    """
    Verify that the Runtime Decision Domain contains no behavioral logic,
    managers, or services.
    """
    forbidden_suffixes = ["Manager", "Service", "Engine", "Orchestrator", "Coordinator"]
    
    for name, obj in inspect.getmembers(runtime_decision_model):
        if inspect.isclass(obj) and obj.__module__ == runtime_decision_model.__name__:
            for suffix in forbidden_suffixes:
                assert not name.endswith(suffix), f"Forbidden architectural component found: {name}"


def test_runtime_decision_models_are_immutable():
    """
    Verify that all dataclasses in the Runtime Decision Domain are strictly frozen.
    """
    for name, obj in inspect.getmembers(runtime_decision_model):
        if inspect.isclass(obj) and is_dataclass(obj) and obj.__module__ == runtime_decision_model.__name__:
            assert obj.__dataclass_params__.frozen is True, f"{name} must be a frozen dataclass"


def test_runtime_decision_info_contains_only_identifiers():
    """
    Verify RuntimeDecisionInfo contains only immutable primitive types (identifiers, enums, dates).
    Must NEVER embed RuntimeDecision, RuntimeObservation, RuntimeSnapshot, etc.
    """
    hints = get_type_hints(runtime_decision_model.RuntimeDecisionInfo)
    
    forbidden_types = [
        "RuntimeDecision", "RuntimeObservation", "RuntimeSnapshot",
        "RuntimeExecutionInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo",
        "RuntimeReasoning", "RuntimeConfidence", "RuntimeRecommendation"
    ]
    
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        for forbidden in forbidden_types:
            assert type_name != forbidden, f"RuntimeDecisionInfo must not embed {forbidden}"


def test_runtime_decision_result_is_passive_transport_artifact():
    """
    Verify RuntimeDecisionResult contains no reasoning, confidence, recommendations,
    execution info, or metrics.
    """
    hints = get_type_hints(runtime_decision_model.RuntimeDecisionResult)
    
    forbidden_types = [
        "RuntimeReasoning", "RuntimeConfidence", "RuntimeRecommendation",
        "RuntimeExecutionInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo",
        "ProviderHealth", "ProviderFailover", "Metrics", "GPU", "CPU", "Memory"
    ]
    
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        for forbidden in forbidden_types:
            assert forbidden not in type_name, f"RuntimeDecisionResult must not embed {forbidden}"


def test_runtime_decision_no_forbidden_imports():
    """
    Verify the runtime decision domain does not import forbidden reasoning, confidence,
    recommendation, or execution modules, nor external network/concurrency primitives.
    """
    with open(runtime_decision_model.__file__, "r", encoding="utf-8") as f:
        content = f.read()
        
    forbidden_imports = [
        "asyncio", "threading", "multiprocessing", "requests", "http", "urllib", "aiohttp",
        "reasoning", "confidence", "recommendation", "coordinator", "intelligence_context",
        "metrics", "optimization", "learning"
    ]
    
    for forbidden in forbidden_imports:
        assert f"import {forbidden}" not in content
        assert f"from {forbidden}" not in content


def test_runtime_decision_artifact_is_passive():
    """
    Verify RuntimeDecision itself does not contain execution logic, orchestrator,
    or forbidden observation types.
    """
    hints = get_type_hints(runtime_decision_model.RuntimeDecision)
    
    forbidden_types = [
        "RuntimeObservation", "RuntimeSnapshot", "RuntimeExecutionInfo",
        "RuntimeRetryInfo", "RuntimeScheduleInfo", "RuntimeReasoning",
        "RuntimeConfidence", "RuntimeRecommendation", "ProviderHealth", "ProviderFailover"
    ]
    
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        for forbidden in forbidden_types:
            assert forbidden not in type_name, f"RuntimeDecision must not embed {forbidden}"
