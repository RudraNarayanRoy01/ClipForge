import ast
import os
from pathlib import Path

def get_ast_for_file(filepath: str) -> ast.Module:
    with open(filepath, "r", encoding="utf-8") as f:
        return ast.parse(f.read(), filename=filepath)

def test_retry_model_immutability():
    """Certify that RetryResult, RetryPolicy, and RetrySummary are frozen."""
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    model_path = base_dir / "retry_model.py"
    
    assert model_path.exists(), "retry_model.py must exist"
    
    tree = get_ast_for_file(str(model_path))
    
    frozen_classes = {"RetryResult", "RetryPolicy", "RetrySummary"}
    found_classes = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name in frozen_classes:
                found_classes.add(node.name)
                # Check for @dataclass(frozen=True)
                is_frozen = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", "") == "dataclass":
                        for kw in decorator.keywords:
                            if kw.arg == "frozen" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                is_frozen = True
                assert is_frozen, f"{node.name} must be a frozen dataclass"
                
    assert frozen_classes == found_classes, f"Missing classes: {frozen_classes - found_classes}"

def test_retry_enums():
    """Certify that RetryDecision and RetryReason are Enums."""
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    model_path = base_dir / "retry_model.py"
    
    tree = get_ast_for_file(str(model_path))
    
    enum_classes = {"RetryDecision", "RetryReason"}
    found_enums = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name in enum_classes:
                found_enums.add(node.name)
                # Ensure it inherits from Enum
                bases = [getattr(b, "id", "") for b in node.bases]
                assert "Enum" in bases, f"{node.name} must inherit from Enum"
                
    assert enum_classes == found_enums, f"Missing enums: {enum_classes - found_enums}"

def test_runtime_retry_isolation():
    """
    Certify RuntimeRetry has:
    - No execution logic
    - No scheduling logic
    - No lifecycle ownership
    - No recovery implementation
    - No retry loops or backoff implementation
    - No queue management
    - No forbidden imports
    """
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    retry_path = base_dir / "retry.py"
    
    assert retry_path.exists(), "retry.py must exist"
    
    tree = get_ast_for_file(str(retry_path))
    
    # 1. No forbidden imports
    forbidden_imports = {"executor", "scheduler", "queue", "asyncio", "threading", "multiprocessing"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_imports, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden_imports, f"Forbidden import found: {node.module}"
            
    # 2. No retry loops (while loops, sleep calls)
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            assert False, "RuntimeRetry must not contain while loops (no polling or backoff delays)"
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "sleep":
                assert False, "RuntimeRetry must not contain time.sleep or asyncio.sleep calls"
            if isinstance(func, ast.Name) and func.id == "sleep":
                assert False, "RuntimeRetry must not contain sleep calls"
                
    # 3. No execution state (no self.state = ...)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RuntimeRetry":
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                            assert False, "RuntimeRetry must not own execution state"
