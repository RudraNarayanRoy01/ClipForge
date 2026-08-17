import ast
import os


def get_planning_result_ast() -> ast.Module:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
    target_file = os.path.join(backend_dir, "src", "runtime", "core", "planning_result.py")
    
    with open(target_file, "r", encoding="utf-8") as f:
        source = f.read()
    return ast.parse(source)


def extract_imports(tree: ast.Module) -> set[str]:
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # Handle relative imports by resolving them based on the file location.
            # In runtime/core/planning_result.py, we only expect `.intent` or similar.
            # We don't need a perfect absolute resolver, just catching the forbidden keywords.
            if node.level > 0:
                module = f"relative_import_{node.level}.{module}"
            imports.add(module)
    return imports


def test_provider_neutrality():
    """Test 10: Provider Neutrality"""
    tree = get_planning_result_ast()
    imports = extract_imports(tree)
    
    forbidden_provider_terms = [
        "ollama", "openai", "gemini", "provider", "model", "llama", "factory"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_provider_terms:
            assert forbidden not in imp_lower, f"Forbidden provider import found: {imp}"


def test_hardware_neutrality():
    """Test 11: Hardware Neutrality"""
    tree = get_planning_result_ast()
    imports = extract_imports(tree)
    
    forbidden_hardware_terms = [
        "gpu", "cuda", "vram", "hardware", "cpu", "device", "resource"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_hardware_terms:
            assert forbidden not in imp_lower, f"Forbidden hardware import found: {imp}"


def test_scheduling_execution_neutrality():
    """Test 12: Scheduling/Execution Neutrality"""
    tree = get_planning_result_ast()
    imports = extract_imports(tree)
    
    forbidden_terms = [
        "scheduler", "queue", "worker", "priority", "retry", "executor",
        "subprocess", "invocation", "dispatch"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_terms:
            assert forbidden not in imp_lower, f"Forbidden scheduling/execution import found: {imp}"


def test_application_neutrality():
    """Test 13: Application Neutrality"""
    tree = get_planning_result_ast()
    imports = extract_imports(tree)
    
    forbidden_terms = [
        "fastapi", "pydantic", "schema", "intelligence", "domain",
        "service", "campaign", "metrics", "telemetry"
    ]
    
    for imp in imports:
        imp_lower = imp.lower()
        for forbidden in forbidden_terms:
            assert forbidden not in imp_lower, f"Forbidden application import found: {imp}"

