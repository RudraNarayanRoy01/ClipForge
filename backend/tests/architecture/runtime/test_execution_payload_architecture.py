import ast
from pathlib import Path

def is_generic_type(node):
    if isinstance(node, ast.Name):
        return node.id in {"Any", "dict", "Dict", "object"}
    elif isinstance(node, ast.Subscript):
        # Check the base (e.g. Dict in Dict[str, Any] or Optional in Optional[Any])
        if isinstance(node.value, ast.Name):
            if node.value.id in {"dict", "Dict", "list", "List", "tuple", "Tuple", "Optional"}:
                # It's a container type, recursively check its elements
                if hasattr(node.slice, 'elts'): # Tuple case for multiple elements
                    return any(is_generic_type(e) for e in node.slice.elts)
                elif hasattr(node.slice, 'value'): # Python < 3.9
                    if isinstance(node.slice.value, ast.Tuple):
                        return any(is_generic_type(e) for e in node.slice.value.elts)
                    return is_generic_type(node.slice.value)
                else:
                    return is_generic_type(node.slice)
            elif node.value.id in {"Any", "object"}:
                return True
    elif isinstance(node, ast.Tuple):
        return any(is_generic_type(e) for e in node.elts)
    return False

def test_execution_result_remains_outcome_only():
    """
    Assertion A & B:
    Verify that ExecutionResult does not define generic payload fields,
    whether annotated or unannotated.
    """
    engine_file = Path("backend/src/runtime/execution/execution_result.py")
    assert engine_file.exists(), "execution_result.py must exist"
    
    with open(engine_file, "r") as f:
        content = f.read()
        
    tree = ast.parse(content)
    
    forbidden_fields = {"payload", "data", "artifact", "result_data"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ExecutionResult":
            for item in node.body:
                # Check annotated assignments (e.g. payload: Any)
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    assert item.target.id not in forbidden_fields, (
                        f"ExecutionResult must not define generic payload field: {item.target.id}"
                    )
                    assert not is_generic_type(item.annotation), (
                        f"ExecutionResult field '{item.target.id}' must not use generic type"
                    )
                # Check unannotated assignments (e.g. payload = ...)
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            assert target.id not in forbidden_fields, (
                                f"ExecutionResult must not define generic payload field: {target.id}"
                            )


def test_runtime_core_remains_capability_agnostic():
    """
    Assertion C & D:
    Verify that Runtime Core does not import capability-specific domain results,
    neither via symbol names nor via module paths.
    """
    runtime_dirs = [
        Path("backend/src/runtime/core"),
        Path("backend/src/runtime/execution"),
        Path("backend/src/runtime/invocation"),
    ]
    
    forbidden_symbols = {
        "Transcript", 
        "TranscriptSearchResult", 
        "VideoUnderstandingResult", 
        "RenderExecutionResult"
    }
    
    forbidden_module_substrings = {
        "src.transcription",
        "src.video_understanding",
        "src.application"
    }
    
    for d in runtime_dirs:
        if not d.exists():
            continue
            
        for py_file in d.glob("**/*.py"):
            with open(py_file, "r") as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name not in forbidden_symbols, (
                            f"Runtime core ({py_file.name}) must not import domain payload: {alias.name}"
                        )
                        for forbidden_mod in forbidden_module_substrings:
                            assert forbidden_mod not in alias.name, (
                                f"Runtime core ({py_file.name}) must not import capability module: {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for forbidden_mod in forbidden_module_substrings:
                            assert forbidden_mod not in node.module, (
                                f"Runtime core ({py_file.name}) must not import capability module: {node.module}"
                            )
                    for alias in node.names:
                        assert alias.name not in forbidden_symbols, (
                            f"Runtime core ({py_file.name}) must not import domain payload: {alias.name}"
                        )

def test_execution_mechanism_contract_remains_outcome_oriented():
    """
    Assertion E:
    Verify that AbstractExecutionMechanism.execute returns exactly Tuple[ExecutionOutcome, Optional[str]].
    """
    registry_file = Path("backend/src/runtime/execution/execution_mechanism_registry.py")
    assert registry_file.exists(), "execution_mechanism_registry.py must exist"
    
    with open(registry_file, "r") as f:
        content = f.read()
        
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AbstractExecutionMechanism":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "execute":
                    returns = item.returns
                    assert isinstance(returns, ast.Subscript), (
                        "execute() must return Tuple[ExecutionOutcome, Optional[str]]"
                    )
                    assert isinstance(returns.value, ast.Name) and returns.value.id == "Tuple", (
                        "execute() must return Tuple[ExecutionOutcome, Optional[str]]"
                    )
                    
                    if hasattr(returns.slice, 'elts'):
                        elts = returns.slice.elts
                    else:
                        elts = getattr(returns.slice, 'value', returns.slice).elts
                        
                    assert len(elts) == 2, "Tuple must have exactly 2 elements"
                    
                    # First element must be ExecutionOutcome
                    assert getattr(elts[0], "id", None) == "ExecutionOutcome", (
                        "execute() first return value must be ExecutionOutcome"
                    )
                    
                    # Second element must be Optional[str] or str
                    assert not is_generic_type(elts[1]), (
                        "execute() second return value must not be a generic payload type"
                    )
                    
                    # Check for Optional[str]
                    if isinstance(elts[1], ast.Subscript) and isinstance(elts[1].value, ast.Name):
                        assert elts[1].value.id == "Optional", "execute() second return value should be Optional[str]"
                        if hasattr(elts[1].slice, 'value'):
                            slice_val = elts[1].slice.value
                        else:
                            slice_val = elts[1].slice
                        assert getattr(slice_val, "id", None) == "str", "execute() second return value must be Optional[str]"


def test_execution_engine_does_not_own_payloads():
    """
    Assertion F:
    Verify that ExecutionEngine does not implement payload handling methods.
    """
    engine_file = Path("backend/src/runtime/execution/execution_engine.py")
    assert engine_file.exists(), "execution_engine.py must exist"
    
    with open(engine_file, "r") as f:
        content = f.read()
        
    tree = ast.parse(content)
    
    forbidden_method_keywords = [
        "persist", "save", "handle_payload", "store_result", 
        "emit_artifact", "transfer_payload", "extract_payload"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ExecutionEngine":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    for keyword in forbidden_method_keywords:
                        assert keyword not in item.name.lower(), (
                            f"ExecutionEngine must not implement payload handling method: {item.name}"
                        )
