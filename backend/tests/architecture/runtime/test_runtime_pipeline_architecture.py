import ast
from pathlib import Path
import pytest


def test_runtime_pipeline_file_exists():
    """Verify that the production invocation boundary file exists."""
    path = Path("backend/src/runtime/invocation/runtime_pipeline.py")
    assert path.exists(), "RuntimePipeline file must exist"


def test_runtime_pipeline_import_boundary():
    """
    Verify the AST/import boundary for RuntimePipeline.
    Must not import providers, hardware, schedulers, telemetry, network, 
    subprocess, threads, or legacy runtime implementations.
    """
    path = Path("backend/src/runtime/invocation/runtime_pipeline.py")
    assert path.exists()

    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    forbidden_modules = {
        # Providers & Models
        "openai", "gemini", "anthropic", "ollama", "llama_cpp", "google.generativeai",
        "src.providers", "src.models", "boto3",
        
        # Hardware
        "torch", "tensorflow", "cuda", "pynvml", "src.hardware", "gpu",
        
        # Scheduling & concurrency
        "queue", "threading", "multiprocessing", "concurrent", "concurrent.futures",
        "asyncio", "celery", "src.scheduler", "src.execution",
        
        # Network & execution
        "requests", "httpx", "aiohttp", "urllib", "subprocess", "socket",
        
        # Telemetry & observability
        "logging", "metrics", "telemetry", "prometheus_client", "opentelemetry",
        "src.runtime.runtime_telemetry", "src.runtime.runtime_metrics",
        
        # Legacy Runtime
        "src.runtime.runtime_policy", "src.runtime.runtime_planning", 
        "src.runtime.context", "src.runtime.bootstrap"
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                assert alias.name not in forbidden_modules, f"Forbidden import: {alias.name}"
                assert base_module not in forbidden_modules, f"Forbidden import: {alias.name}"
                
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                assert node.module not in forbidden_modules, f"Forbidden from-import: {node.module}"
                assert base_module not in forbidden_modules, f"Forbidden from-import: {node.module}"


def test_runtime_pipeline_no_execution_calls():
    """
    Verify that RuntimePipeline does not execute work itself.
    No calls to execute(), run_job(), submit(), spawn(), etc.
    """
    path = Path("backend/src/runtime/invocation/runtime_pipeline.py")
    assert path.exists()

    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    forbidden_calls = {
        "execute", "run_job", "submit", "dispatch", "spawn", 
        "run", "start", "invoke", "call"
    }
    
    # Exceptions where these names might legitimately occur on our mocked artifacts or stdlib
    allowed_object_methods = {"plan", "evaluate", "select", "process"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls, f"Forbidden function call: {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                # Only explicitly allowed method invocations
                assert node.func.attr in allowed_object_methods, f"Forbidden method call: {node.func.attr}"


def test_runtime_pipeline_no_dependency_instantiation():
    """
    Verify that RuntimePipeline receives context and does not act as a composition root.
    It must not instantiate ExecutionPlanner, PolicyEngine, RoutingEngine, TargetSelector,
    or RuntimePipelineFactory.
    """
    path = Path("backend/src/runtime/invocation/runtime_pipeline.py")
    assert path.exists()

    tree = ast.parse(path.read_text(encoding="utf-8"))
    
    forbidden_instantiations = {
        "ExecutionPlanner", "PolicyEngine", "RoutingEngine", 
        "TargetSelector", "RuntimePipelineFactory", "RuntimePipelineContext"
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_instantiations, \
                    f"Pipeline must not instantiate its own dependencies: {node.func.id}"


def test_core_does_not_import_invocation():
    """
    Verify the architectural dependency direction: Core must not import Invocation.
    """
    core_dir = Path("backend/src/runtime/core")
    assert core_dir.exists() and core_dir.is_dir()

    for py_file in core_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "invocation" not in alias.name, f"Reverse dependency in {py_file.name}: imports {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "invocation" not in node.module, f"Reverse dependency in {py_file.name}: from {node.module}"
