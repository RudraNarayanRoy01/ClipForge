import inspect
from dataclasses import is_dataclass
from typing import get_type_hints

from src.runtime.domain import runtime_recommendation_model


def test_runtime_recommendation_domain_is_pure_data():
    """
    Verify that the Runtime Recommendation Domain contains no behavioral logic,
    managers, or services, and remains strictly an advisory bounding context.
    """
    forbidden_suffixes = ["Manager", "Service", "Engine", "Orchestrator", "Coordinator", "Router"]
    
    for name, obj in inspect.getmembers(runtime_recommendation_model):
        if inspect.isclass(obj) and obj.__module__ == runtime_recommendation_model.__name__:
            for suffix in forbidden_suffixes:
                assert not name.endswith(suffix), f"Forbidden architectural component found: {name}"


def test_runtime_recommendation_models_are_immutable():
    """
    Verify that all dataclasses in the Runtime Recommendation Domain are strictly frozen.
    """
    for name, obj in inspect.getmembers(runtime_recommendation_model):
        if inspect.isclass(obj) and is_dataclass(obj) and obj.__module__ == runtime_recommendation_model.__name__:
            assert obj.__dataclass_params__.frozen is True, f"{name} must be a frozen dataclass"


def test_runtime_recommendation_does_not_embed_upstream_artifacts():
    """
    Verify RuntimeRecommendation only uses identifiers for upstream references.
    Must NEVER embed RuntimeObservation, RuntimeDecision, RuntimeReasoning, RuntimeConfidence.
    """
    hints = get_type_hints(runtime_recommendation_model.RuntimeRecommendation)
    
    forbidden_types = [
        "RuntimeObservation", "RuntimeDecision", "RuntimeReasoning", "RuntimeConfidence",
        "RuntimeExecutionInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo"
    ]
    
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        for forbidden in forbidden_types:
            assert forbidden not in type_name, f"RuntimeRecommendation must not embed {forbidden}"


def test_runtime_recommendation_is_provider_agnostic():
    """
    Verify that Runtime Recommendation remains provider agnostic and does not mention
    specific providers or models in its domain.
    """
    with open(runtime_recommendation_model.__file__, "r", encoding="utf-8") as f:
        content = f.read()
        
    forbidden_terms = [
        "Gemini", "OpenAI", "Ollama", "llama.cpp", "CUDA", "CPU", "GPU"
    ]
    
    for term in forbidden_terms:
        assert term not in content, f"Forbidden provider/hardware term '{term}' found in runtime_recommendation_model.py"


def test_runtime_recommendation_no_forbidden_imports():
    """
    Verify the runtime recommendation domain does not import forbidden modules
    or execution primitives.
    """
    with open(runtime_recommendation_model.__file__, "r", encoding="utf-8") as f:
        content = f.read()
        
    forbidden_imports = [
        "asyncio", "threading", "multiprocessing", "requests", "http", "urllib", "aiohttp",
        "coordinator", "intelligence_context", "metrics", "optimization", "learning",
        "RuntimeExecution", "RuntimeScheduler", "RuntimeRetry", "ProviderRegistry"
    ]
    
    for forbidden in forbidden_imports:
        assert f"import {forbidden}" not in content
        assert f"from {forbidden}" not in content


def test_runtime_recommendation_info_contains_only_identifiers():
    """
    Verify RuntimeRecommendationInfo contains only immutable primitive types (identifiers, enums, dates).
    """
    hints = get_type_hints(runtime_recommendation_model.RuntimeRecommendationInfo)
    
    forbidden_types = [
        "RuntimeRecommendation", "RuntimeObservation", "RuntimeDecision",
        "RuntimeReasoning", "RuntimeConfidence"
    ]
    
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        for forbidden in forbidden_types:
            assert type_name != forbidden, f"RuntimeRecommendationInfo must not embed {forbidden}"


def test_runtime_recommendation_result_is_passive_transport_artifact():
    """
    Verify RuntimeRecommendationResult contains no active execution or logic artifacts.
    """
    hints = get_type_hints(runtime_recommendation_model.RuntimeRecommendationResult)
    
    forbidden_types = [
        "RuntimeReasoning", "RuntimeConfidence", "RuntimeRecommendation", 
        "RuntimeExecutionInfo", "RuntimeRetryInfo", "RuntimeScheduleInfo"
    ]
    
    # Note: It embeds RuntimeRecommendationInfo and primitive types, not RuntimeRecommendation itself
    for field_name, field_type in hints.items():
        type_name = getattr(field_type, '__name__', str(field_type))
        if field_name != "recommendation_info": # It explicitly should contain info
            for forbidden in forbidden_types:
                assert forbidden not in type_name, f"RuntimeRecommendationResult must not embed {forbidden} in {field_name}"
