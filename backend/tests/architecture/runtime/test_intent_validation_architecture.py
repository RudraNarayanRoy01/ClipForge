import ast
import os
import pytest

def get_imports(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
            imports.append(module)
    return imports

def test_intent_validation_architecture_neutrality():
    module_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "src", "runtime", "core", "intent_validation.py"
    )
    
    assert os.path.exists(module_path), f"File not found: {module_path}"
    
    imports = get_imports(module_path)
    
    forbidden_substrings = [
        # Providers
        "ollama", "openai", "gemini", "providerfactory",
        # Hardware
        "cuda", "gpu", "vram", "hardware", "resource",
        # Planning
        "planner", "planning", "execution_plan", "execution_strategy", "policy",
        # Scheduling
        "scheduler", "queue", "retry", "fallback",
        # Execution
        "runtime_executor", "executor", "runtime_execution", "subprocess",
        # Application
        "campaign_intelligence", "fastapi", "application",
        # Schema
        "pydantic", "extraction_summary_schema"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_substrings:
            assert forbidden not in imp_lower, (
                f"Forbidden import '{imp}' contains '{forbidden}', "
                f"violating architectural neutrality in intent_validation.py."
            )
