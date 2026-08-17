import ast
from pathlib import Path
from src.runtime.execution.execution_engine import ExecutionEngine, AbstractExecutionMechanism

def test_authoritative_execution_engine_exists():
    """1. execution_engine.py exists. 2. Exactly one authoritative ExecutionEngine exists."""
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists(), "execution_engine.py must exist"
    
    with open(engine_file, "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    # 2. Exactly one authoritative ExecutionEngine class exists.
    assert "ExecutionEngine" in classes, "ExecutionEngine class must exist"
    
    # 3. AbstractExecutionMechanism exists in the intended location.
    assert "AbstractExecutionMechanism" in classes, "AbstractExecutionMechanism must be defined in execution_engine.py"
    
    # No second execution orchestrator / Result abstraction
    assert len(classes) == 2, f"Only AbstractExecutionMechanism and ExecutionEngine are allowed in this file. Found: {classes}"

def test_provider_and_hardware_neutrality():
    """4-11, 16. No imports of specific providers, networking, hardware, telemetry, or schedulers."""
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists()
    
    with open(engine_file, "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    forbidden_modules = {
        # Providers
        "openai", "anthropic", "google.generativeai", "ollama",
        # Cloud/Network
        "requests", "aiohttp", "urllib", "httpx", "boto3", "google.cloud",
        # Subprocess/Threads/Workers
        "subprocess", "threading", "multiprocessing", "concurrent.futures", "asyncio", "celery",
        # Hardware
        "torch", "tensorflow", "pynvml", "psutil", "cuda",
        # Telemetry/Adaptation
        "opentelemetry", "prometheus_client", "logging", "tracing"
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                assert base_module not in forbidden_modules, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                assert base_module not in forbidden_modules, f"Forbidden import found: {node.module}"

def test_legacy_isolation_and_no_reverse_dependency():
    """12-15, 24. No RuntimeContext, SchedulingDecision, RuntimeExecutionResult, or core reverse dependencies."""
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists()
    
    with open(engine_file, "r") as f:
        content = f.read()
    
    forbidden_terms = [
        "RuntimeContext", 
        "SchedulingDecision", 
        "RuntimeExecutionResult", 
        "RuntimeExecutor"
    ]
    
    for term in forbidden_terms:
        assert term not in content, f"Legacy artifact {term} must not be referenced in execution_engine.py"

def test_no_catch_all_exception_swallowing():
    """21. No catch-all exception swallowing."""
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists()
    
    with open(engine_file, "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # If type is None, it's a bare 'except:'
            assert node.type is not None, "Bare except: is strictly prohibited"
            # If it's catching Exception
            if isinstance(node.type, ast.Name):
                assert node.type.id != "Exception", "'except Exception:' is strictly prohibited"

def test_no_internal_mechanism_construction():
    """23. No execution mechanism construction inside ExecutionEngine."""
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists()
    
    with open(engine_file, "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Check that in __init__, there are no Calls building objects, only assignments
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    if isinstance(stmt.value, ast.Call):
                        assert False, "ExecutionEngine must not instantiate its dependencies internally"
