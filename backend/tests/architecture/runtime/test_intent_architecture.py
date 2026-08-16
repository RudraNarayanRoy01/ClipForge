import ast
import os
from pathlib import Path

def get_ast_imports(filepath: str) -> set:
    """Extract all import and import-from names from a Python file using AST."""
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
        
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.add(f"{module}.{alias.name}")
                imports.add(module)
    return imports

def test_intent_architecture_imports():
    """
    Verify that ExecutionIntent boundary does not leak domain, hardware, provider, 
    scheduler, or executor dependencies via AST import inspection.
    """
    # Locate intent.py relative to the test directory
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    intent_path = base_dir / "src" / "runtime" / "core" / "intent.py"
    
    assert intent_path.exists(), f"intent.py not found at {intent_path}"
    
    imports = get_ast_imports(str(intent_path))
    
    # Check for forbidden dependencies
    forbidden_substrings = [
        # Providers
        "ollama", "openai", "gemini", "provider",
        
        # Hardware
        "cuda", "gpu", "hardware", "resource",
        
        # Execution & Scheduling
        "executor", "scheduler", "retry", "fallback",
        
        # Application / Domain
        "intelligence", "campaign", "reasoning", "extraction"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_substrings:
            assert forbidden not in imp_lower, (
                f"Architectural Violation: intent.py imports forbidden module '{imp}' "
                f"which contains restricted concept '{forbidden}'."
            )
