import inspect
from dataclasses import is_dataclass
from src.runtime.domain.model_registry_model import ModelInfo, ModelType, ModelStatus, ModelRegistryResult
from src.runtime.core.model_registry import ModelRegistry
from src.runtime.core.context import RuntimeContext
from src.runtime.domain.provider_registry_model import ProviderInfo
from src.runtime.domain.provider_capability_model import ProviderCapability

def test_model_info_is_immutable_dataclass():
    """Verify ModelInfo is an immutable dataclass."""
    assert is_dataclass(ModelInfo), "ModelInfo must be a dataclass"
    assert ModelInfo.__dataclass_params__.frozen == True, "ModelInfo must be frozen (immutable)"

def test_model_registry_result_is_immutable_dataclass():
    """Verify ModelRegistryResult is an immutable dataclass."""
    assert is_dataclass(ModelRegistryResult), "ModelRegistryResult must be a dataclass"
    assert ModelRegistryResult.__dataclass_params__.frozen == True, "ModelRegistryResult must be frozen (immutable)"

def test_model_info_does_not_own_provider_info_or_capability():
    """Verify ModelInfo references provider_id but does not embed ProviderInfo or ProviderCapability."""
    annotations = ModelInfo.__annotations__
    assert "provider_id" in annotations, "ModelInfo must reference provider_id"
    assert annotations["provider_id"] == str or annotations["provider_id"] == "str", "provider_id must be a string identifier"
    
    for field_name, field_type in annotations.items():
        assert field_type is not ProviderInfo, f"ModelInfo must not embed ProviderInfo directly (found in {field_name})"
        assert field_type is not ProviderCapability, f"ModelInfo must not embed ProviderCapability directly (found in {field_name})"

def test_model_registry_has_no_execution_or_lifecycle_imports():
    """Verify ModelRegistry is purely a metadata manager and does not import execution/lifecycle components."""
    import src.runtime.core.model_registry as model_registry_module
    
    # We inspect the global namespace of the module
    module_dict = model_registry_module.__dict__
    
    forbidden_imports = [
        "RuntimeExecutor", "RuntimeScheduler", "RuntimeLifecycle",
        "ExecutionResult", "ExecutionRequest"
    ]
    
    for forbidden in forbidden_imports:
        assert forbidden not in module_dict, f"ModelRegistry module must not import {forbidden}"

def test_model_registry_methods():
    """Verify ModelRegistry only contains approved registry methods."""
    allowed_methods = {
        '__init__', 'register_model', 'update_model', 'remove_model',
        'get_model', 'list_models', 'model_exists', 
        'list_models_for_provider', 'list_models_by_type'
    }
    
    registry_methods = [
        name for name, method in inspect.getmembers(ModelRegistry, predicate=inspect.isfunction)
        if not name.startswith('_') or name == '__init__'
    ]
    
    for method in registry_methods:
        assert method in allowed_methods, f"ModelRegistry has unapproved method: {method}"

def test_runtime_context_remains_passive():
    """
    Verify RuntimeContext exposes ModelRegistry but does NOT 
    implement model registration methods itself.
    """
    assert hasattr(RuntimeContext, 'model_registry'), "RuntimeContext must expose model_registry property"
    
    # Ensure it doesn't wrap registry methods
    assert not hasattr(RuntimeContext, 'register_model'), "RuntimeContext must not implement register_model"
    assert not hasattr(RuntimeContext, 'list_models'), "RuntimeContext must not implement list_models"

def test_registry_dependency_direction():
    """
    Verify the dependency direction ProviderRegistry -> ProviderCapabilityRegistry -> ModelRegistry.
    ModelRegistry should not know about ProviderRegistry instances.
    """
    # This is partially verified by the lack of ProviderInfo/ProviderCapability in ModelInfo.
    # We can also verify ModelRegistry initialization takes no arguments.
    init_signature = inspect.signature(ModelRegistry.__init__)
    assert len(init_signature.parameters) == 1, "ModelRegistry.__init__ should only take 'self', it must not require ProviderRegistry"
