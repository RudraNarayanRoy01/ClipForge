import ast
from pathlib import Path

# Paths to the specific files established by Batch 6B.4.7
TARGET_FILES = [
    Path("backend/src/runtime/core/execution_target.py"),
    Path("backend/src/runtime/core/target_selector.py")
]

FORBIDDEN_IMPORT_SUBSTRINGS = [
    "ollama", "openai", "google.generativeai", "gemini", "llama_cpp",
    "cuda", "torch.cuda", "gputil", "pynvml",
    "scheduler", "scheduling", "queue", "worker", "dispatch", "executor", "execution_engine",
    "telemetry", "metrics", "monitoring", "benchmark", "adaptation",
    "fastapi", "pydantic", "subprocess"
]

FORBIDDEN_CALL_NAMES = [
    "OllamaClient", "OpenAI", "Scheduler", "Executor",
    "execute", "run", "invoke", "spawn", "allocate", "release", "load", "unload"
]


def test_target_selection_production_files_exist():
    """
    Ensure the exact production files established by this boundary exist.
    Do NOT use `if not file_path.exists(): continue` here.
    Missing files must fail the test.
    """
    for file_path in TARGET_FILES:
        assert file_path.exists(), f"Required production file is missing: {file_path}"


def test_no_forbidden_imports_in_target_selection():
    """
    Target selection must not import provider implementations, hardware APIs,
    or telemetry/adaptation systems.
    """
    for file_path in TARGET_FILES:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _check_forbidden_module(alias.name, file_path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    _check_forbidden_module(node.module, file_path)


def test_no_forbidden_execution_calls_in_target_selection():
    """
    Target selection must not invoke provider clients, schedulers, or executors.
    """
    for file_path in TARGET_FILES:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = None
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr
                    
                if call_name:
                    assert call_name not in FORBIDDEN_CALL_NAMES, (
                        f"Forbidden call '{call_name}' found in {file_path}. "
                        "Target selection must not execute or schedule."
                    )


def _check_forbidden_module(module_name: str, file_path: Path):
    module_name_lower = module_name.lower()
    for forbidden in FORBIDDEN_IMPORT_SUBSTRINGS:
        assert forbidden not in module_name_lower, (
            f"Forbidden import '{module_name}' found in {file_path}. "
            f"Matched forbidden substring: '{forbidden}'"
        )
