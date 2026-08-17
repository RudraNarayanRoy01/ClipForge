import ast
import os
import pytest

def test_execution_planner_architecture_neutrality():
    """
    Test that execution_planner.py does not contain any forbidden imports
    that would violate its architectural boundary (Provider, Hardware, Scheduling,
    Policy, Execution neutrality).
    """
    # Adjust path if tests are run from different directories
    current_dir = os.path.dirname(__file__)
    # Path relative to backend/tests/architecture/runtime
    planner_path = os.path.join(current_dir, "..", "..", "..", "src", "runtime", "core", "execution_planner.py")
    
    # Fallback absolute-like path if not found (for robustness in different test running environments)
    if not os.path.exists(planner_path):
        planner_path = os.path.abspath(os.path.join(os.getcwd(), "backend", "src", "runtime", "core", "execution_planner.py"))

    assert os.path.exists(planner_path), f"execution_planner.py not found at {planner_path}"

    with open(planner_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    forbidden_modules = {
        "ollama", "openai", "gemini", "provider", "provider_factory",
        "cuda", "gpu", "hardware", "resource", "scheduler", "queue",
        "executor", "runtime_execution", "fastapi", "pydantic",
        "campaign_intelligence"
    }

    class ImportVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Import(self, node):
            for alias in node.names:
                for forbidden in forbidden_modules:
                    # We check if the forbidden term is a standalone module or part of the dot path.
                    # e.g., 'fastapi', 'src.hardware.gpu'
                    # Doing exact module checking, but catching parts like 'provider' in 'src.provider.x'
                    parts = alias.name.lower().split('.')
                    if forbidden in parts or forbidden == alias.name.lower():
                        self.violations.append(f"Forbidden import: {alias.name}")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module:
                for forbidden in forbidden_modules:
                    parts = node.module.lower().split('.')
                    if forbidden in parts or forbidden == node.module.lower():
                        self.violations.append(f"Forbidden from-import: {node.module}")
            self.generic_visit(node)

    visitor = ImportVisitor()
    visitor.visit(tree)

    assert not visitor.violations, f"Architectural violations found in execution_planner.py: {visitor.violations}"
