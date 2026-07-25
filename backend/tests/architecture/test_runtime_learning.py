import ast
from pathlib import Path

def get_ast_for_file(filepath: str) -> ast.Module:
    with open(filepath, "r", encoding="utf-8") as f:
        return ast.parse(f.read(), filename=filepath)

def test_learning_model_immutability():
    """Certify that LearningResult, LearningPattern, and LearningSummary are frozen."""
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    model_path = base_dir / "learning_model.py"
    
    assert model_path.exists(), "learning_model.py must exist"
    
    tree = get_ast_for_file(str(model_path))
    
    frozen_classes = {"LearningResult", "LearningPattern", "LearningSummary"}
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

def test_learning_enums():
    """Certify that LearningCategory and LearningConfidence are Enums."""
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    model_path = base_dir / "learning_model.py"
    
    tree = get_ast_for_file(str(model_path))
    
    enum_classes = {"LearningCategory", "LearningConfidence"}
    found_enums = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name in enum_classes:
                found_enums.add(node.name)
                # Ensure it inherits from Enum
                bases = [getattr(b, "id", "") for b in node.bases]
                assert "Enum" in bases, f"{node.name} must inherit from Enum"
                
    assert enum_classes == found_enums, f"Missing enums: {enum_classes - found_enums}"

def test_runtime_learning_isolation():
    """
    Certify RuntimeLearning has:
    - No execution logic
    - No scheduling logic
    - No retry logic
    - No observation extraction logic (it just consumes it)
    - No optimization logic
    - No prediction logic
    - No recommendation logic
    - No analytics
    - No monitoring
    - No resource allocation
    """
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    learning_path = base_dir / "learning.py"
    
    assert learning_path.exists(), "learning.py must exist"
    
    tree = get_ast_for_file(str(learning_path))
    
    forbidden_imports = {
        "executor", "scheduler", "queue", "asyncio", "threading", "multiprocessing",
        "datadog", "prometheus_client", "opentelemetry", "logging", "pandas", "numpy", "sklearn",
        "runtime_optimization", "runtime_execution"
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_imports, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_imports, f"Forbidden import found: {node.module}"
                
    # No execution state (no self.state = ...)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RuntimeLearning":
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                            assert False, "RuntimeLearning must not own execution state or historical state"

def test_planning_learning_isolation():
    """
    Certify RuntimePlanning does not import learning or depend on LearningResult.
    """
    base_dir = Path(__file__).parent.parent.parent / "src" / "runtime" / "core"
    planning_path = base_dir / "runtime_planning.py"
    
    assert planning_path.exists(), "runtime_planning.py must exist"
    
    tree = get_ast_for_file(str(planning_path))
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "learning" not in alias.name, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert "learning" not in node.module, f"Forbidden import found: {node.module}"
