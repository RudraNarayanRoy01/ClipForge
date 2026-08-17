import ast
from pathlib import Path


def test_policy_boundary_neutrality():
    """
    AST-based architecture test to ensure PolicyEngine and PolicyDecision
    do not import forbidden modules or semantics.
    """
    forbidden_terms = {
        "ollama", "openai", "gemini", "google", "generativeai",
        "provider", "providerfactory", "cuda", "gpu", "hardware", "device",
        "resource", "scheduler", "queue", "worker", "executor", "runtime.execution",
        "execution_engine", "dispatch", "telemetry", "metrics", "monitoring",
        "adaptation", "fastapi", "pydantic", "application"
    }

    core_dir = Path(__file__).resolve().parents[4] / "src" / "runtime" / "core"
    
    files_to_check = [
        core_dir / "policy_decision.py",
        core_dir / "policy_engine.py"
    ]

    for file_path in files_to_check:
        if not file_path.exists():
            continue
            
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            # Check Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name_lower = alias.name.lower()
                    for term in forbidden_terms:
                        assert term not in name_lower, f"Forbidden import '{alias.name}' in {file_path}"
            
            # Check ImportFrom
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module.lower() if node.module else ""
                for term in forbidden_terms:
                    assert term not in module_name, f"Forbidden from-import '{node.module}' in {file_path}"
                for alias in node.names:
                    name_lower = alias.name.lower()
                    for term in forbidden_terms:
                        assert term not in name_lower, f"Forbidden from-import alias '{alias.name}' in {file_path}"
