import ast
from pathlib import Path
import pytest

def test_capability_intent_preparation_architecture():
    """
    Architecture test for capability_intent_preparation.py
    
    Verifies that the module does NOT import or depend on prohibited execution,
    provider, hardware, or application-level concepts.
    """
    module_path = Path("backend/src/runtime/core/capability_intent_preparation.py")
    
    if not module_path.exists():
        pytest.fail(f"Module not found: {module_path}")
        
    source_code = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source_code)
    
    prohibited_substrings = [
        "ollama",
        "openai",
        "gemini",
        "provider",
        "provider_factory",
        "cuda",
        "gpu",
        "vram",
        "hardware",
        "resource_discovery",
        "executor",
        "scheduler",
        "queue",
        "planner",
        "strategy",
        "policy",
        "campaign_intelligence",
        "application",
        "fastapi",
        "startup",
        "pydantic"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for prohibited in prohibited_substrings:
                    if prohibited in alias.name.lower():
                        pytest.fail(f"Prohibited import found: {alias.name} (contains '{prohibited}')")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for prohibited in prohibited_substrings:
                    if prohibited in node.module.lower():
                        pytest.fail(f"Prohibited from-import found: {node.module} (contains '{prohibited}')")
            for alias in node.names:
                for prohibited in prohibited_substrings:
                    if prohibited in alias.name.lower():
                        pytest.fail(f"Prohibited from-import alias found: {alias.name} (contains '{prohibited}')")
