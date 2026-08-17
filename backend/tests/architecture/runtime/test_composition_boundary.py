import ast
import os
from pathlib import Path
import pytest

def test_composition_boundary_exists():
    """Fail if the composition boundary disappears."""
    base_path = Path(__file__).parent.parent.parent.parent / "src" / "runtime" / "composition"
    assert (base_path / "runtime_pipeline_context.py").exists(), "Composition Context must exist"
    assert (base_path / "runtime_pipeline_factory.py").exists(), "Composition Factory must exist"

def test_composition_has_no_illegal_imports():
    """Verify the composition boundary has no illegal coupling."""
    base_path = Path(__file__).parent.parent.parent.parent / "src" / "runtime" / "composition"
    
    illegal_substrings = [
        "openai", "gemini", "ollama", "provider", "hardware",
        "scheduler", "telemetry", "adaptation", "metrics",
        "monitoring", "queue", "execution_engine"
    ]
    
    for filename in ["runtime_pipeline_context.py", "runtime_pipeline_factory.py"]:
        file_path = base_path / filename
        assert file_path.exists(), f"Required composition file missing: {file_path}"

            
        tree = ast.parse(file_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for illegal in illegal_substrings:
                        assert illegal not in alias.name.lower(), f"Illegal import {alias.name} in {filename}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for illegal in illegal_substrings:
                        assert illegal not in node.module.lower(), f"Illegal import from {node.module} in {filename}"

def test_runtime_core_does_not_depend_on_composition():
    """Verify runtime core does not import composition."""
    base_path = Path(__file__).parent.parent.parent.parent / "src" / "runtime" / "core"
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                tree = ast.parse(file_path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            assert "composition.runtime_pipeline_context" not in alias.name
                            assert "composition.runtime_pipeline_factory" not in alias.name
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            assert "composition.runtime_pipeline_context" not in node.module
                            assert "composition.runtime_pipeline_factory" not in node.module

def test_composition_does_not_execute_anything():
    """Verify composition factory does not have execution methods."""
    factory_path = Path(__file__).parent.parent.parent.parent / "src" / "runtime" / "composition" / "runtime_pipeline_factory.py"
    assert factory_path.exists(), f"Required composition factory missing: {factory_path}"

        
    tree = ast.parse(factory_path.read_text())
    
    # Check that methods named execute, run, submit, dispatch, schedule, enqueue, spawn do not exist
    illegal_methods = {"execute", "run", "submit", "dispatch", "schedule", "enqueue", "spawn"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.name not in illegal_methods, f"Composition boundary must not contain execution method {node.name}"
