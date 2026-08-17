import ast
import os
from pathlib import Path

def test_planning_context_architecture_neutrality():
    """
    Architecture test verifying that PlanningContext does not couple to providers,
    hardware, scheduling, execution, application-domain semantics, or telemetry.
    """
    file_path = Path(__file__).parent.parent.parent.parent / "src" / "runtime" / "core" / "planning_context.py"
    
    assert file_path.exists(), f"File not found: {file_path}"
    
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    allowed_modules = {"typing", "dataclasses"}
    
    forbidden_substrings = [
        # Providers
        "ollama", "openai", "gemini", "providerfactory", "provider",
        # Hardware/resource
        "cuda", "gpu", "hardware", "resource", "device",
        # Scheduling
        "scheduler", "queue", "worker", "priority",
        # Execution
        "executor", "runtime.execution", "execution_engine", "dispatch",
        # Application/framework
        "fastapi", "pydantic", "application", "service",
        # Telemetry/adaptation
        "telemetry", "metrics", "monitoring", "adaptation"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name_lower = alias.name.lower()
                
                # Check A: Only allowed modules can be imported
                base_module = name_lower.split('.')[0]
                assert base_module in allowed_modules, f"Import of module '{alias.name}' is not allowed in this abstract contract."
                
                # Check B-G: Explicit forbidden checks
                for forbidden in forbidden_substrings:
                    assert forbidden not in name_lower, f"Forbidden import found: {alias.name}"
                    
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_lower = node.module.lower()
                
                # Check A: Only allowed modules can be imported
                base_module = module_lower.split('.')[0]
                assert base_module in allowed_modules, f"Import from module '{node.module}' is not allowed in this abstract contract."
                
                # Check B-G: Explicit forbidden checks
                for forbidden in forbidden_substrings:
                    assert forbidden not in module_lower, f"Forbidden from-import found: {node.module}"

