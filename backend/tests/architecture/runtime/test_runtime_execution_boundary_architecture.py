import pytest
import inspect
import pathlib
import ast
from dataclasses import is_dataclass
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary

def test_execution_boundary_artifacts_exist():
    boundary_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "execution" / "runtime_execution_boundary.py"
    admission_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "execution" / "execution_admission.py"
    
    assert boundary_path.exists(), "runtime_execution_boundary.py must exist"
    assert admission_path.exists(), "execution_admission.py must exist"
    
    assert ExecutionAdmission is not None
    assert RuntimeExecutionBoundary is not None

def test_execution_admission_is_immutable():
    assert is_dataclass(ExecutionAdmission)
    import dataclasses
    assert ExecutionAdmission.__dataclass_params__.frozen is True

def test_execution_admission_contract():
    fields = inspect.signature(ExecutionAdmission).parameters
    assert "execution_target" in fields
    assert "outcome" not in fields, "Admission artifact must not fake an outcome"
    assert "is_success" not in fields, "Admission artifact must not fake a success outcome"
    assert "error_message" not in fields

def test_execution_boundary_contract():
    sig = inspect.signature(RuntimeExecutionBoundary.execute)
    assert sig.return_annotation == ExecutionAdmission
    assert sig.parameters["target"].annotation == "ExecutionTarget" or sig.parameters["target"].annotation.__name__ == "ExecutionTarget"

def test_execution_boundary_forbidden_imports():
    boundary_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "execution" / "runtime_execution_boundary.py"
    with open(boundary_path, "r") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                assert name not in ['asyncio', 'threading', 'multiprocessing', 'requests', 'aiohttp', 'httpx', 'torch', 'cuda', 'openai', 'gemini', 'ollama', 'celery']
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in ['asyncio', 'threading', 'multiprocessing', 'requests', 'aiohttp', 'httpx', 'torch', 'cuda', 'openai', 'gemini', 'ollama', 'celery']

def test_execution_boundary_does_not_instantiate_infrastructure():
    boundary_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "execution" / "runtime_execution_boundary.py"
    with open(boundary_path, "r") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id
                assert "queue" not in name.lower()
                assert "worker" not in name.lower()
                assert "thread" not in name.lower()
                assert "process" not in name.lower()
                assert "pool" not in name.lower()
                assert "engine" not in name.lower(), "Must not construct ExecutionEngine"

def test_execution_boundary_no_fake_success():
    """Verify the boundary does not claim successful execution in its AST."""
    boundary_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "execution" / "runtime_execution_boundary.py"
    with open(boundary_path, "r") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword):
            if node.arg == 'outcome':
                pytest.fail("RuntimeExecutionBoundary must not assert 'outcome' before actual execution")
            if node.arg == 'is_success':
                pytest.fail("RuntimeExecutionBoundary must not assert 'is_success' before actual execution")

def test_execution_boundary_no_upstream_modification():
    base_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "src" / "runtime" / "core"
    target_path = base_dir / "execution_target.py"
    with open(target_path, "r") as f:
        content = f.read()
        assert "execution_result" not in content.lower()
        assert "execution_admission" not in content.lower()
        assert "runtime_execution_boundary" not in content.lower()
