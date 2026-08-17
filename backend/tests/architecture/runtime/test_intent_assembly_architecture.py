import ast
from pathlib import Path

def test_intent_assembler_architecture():
    """
    Test 5, 6, 7, 8 - Provider Neutrality, Hardware Neutrality, 
    Execution Neutrality, Planning Neutrality.
    """
    
    # Get the path to intent_assembly.py
    backend_dir = Path(__file__).parent.parent.parent.parent
    assembler_path = backend_dir / "src" / "runtime" / "core" / "intent_assembly.py"
    
    assert assembler_path.exists(), f"Expected {assembler_path} to exist."
    
    with open(assembler_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    tree = ast.parse(source_code)
    
    forbidden_imports = [
        "ollama", "openai", "gemini",
        "ProviderFactory",
        "CUDA", "GPU", "hardware", "resource",
        "scheduler", "queue",
        "executor", "RuntimeExecutionResult", "RuntimeExecutor",
        "CampaignIntelligenceService", "ImportCampaignUseCase",
        "planning", "strategy", "policy", "retry",
        "pydantic"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden.lower() not in alias.name.lower(), \
                        f"Architecture violation: assembler imports '{alias.name}', " \
                        f"which violates neutrality rule '{forbidden}'"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in forbidden_imports:
                assert forbidden.lower() not in module.lower(), \
                    f"Architecture violation: assembler imports from '{module}', " \
                    f"which violates neutrality rule '{forbidden}'"
            
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden.lower() not in alias.name.lower(), \
                        f"Architecture violation: assembler imports '{alias.name}' from '{module}', " \
                        f"which violates neutrality rule '{forbidden}'"
