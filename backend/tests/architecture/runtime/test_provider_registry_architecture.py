import pytest
from dataclasses import is_dataclass
from src.runtime.domain.provider_registry_model import (
    ProviderType,
    ProviderStatus,
    ProviderInfo,
    ProviderRegistryResult
)
from src.runtime.core.provider_registry import ProviderRegistry
from src.runtime.core.context import RuntimeContext

class TestProviderRegistryArchitecture:
    """
    Architectural certification tests for ProviderRegistry (Batch 6.6.1).
    """

    def test_provider_info_is_immutable(self):
        """Verify ProviderInfo is an immutable dataclass."""
        assert is_dataclass(ProviderInfo)
        assert ProviderInfo.__dataclass_params__.frozen == True

    def test_provider_registry_result_is_immutable(self):
        """Verify ProviderRegistryResult is an immutable dataclass."""
        assert is_dataclass(ProviderRegistryResult)
        assert ProviderRegistryResult.__dataclass_params__.frozen == True

    def test_provider_registry_single_responsibility(self):
        """
        Verify ProviderRegistry only exposes identity/metadata methods.
        It must not contain methods for execution, routing, or building.
        """
        registry = ProviderRegistry()
        methods = [m for m in dir(registry) if not m.startswith('_')]
        
        allowed_methods = {'register', 'unregister', 'get_provider', 'list_providers', 'provider_exists'}
        
        for method in methods:
            assert method in allowed_methods, f"ProviderRegistry exposes unapproved method: {method}"

    def test_provider_registry_dependency_integrity(self):
        """
        Verify ProviderRegistry does not depend on execution components.
        """
        import src.runtime.core.provider_registry as pr_module
        
        imported_names = dir(pr_module)
        forbidden_imports = [
            'RuntimeExecutor',
            'RuntimeScheduler',
            'RuntimeLifecycle',
            'RuntimeProviderSelection',
            'AdaptiveRuntime'
        ]
        
        for forbidden in forbidden_imports:
            assert forbidden not in imported_names, f"ProviderRegistry violates dependency rules by importing {forbidden}"

    def test_runtime_context_passive_composition(self):
        """
        Verify RuntimeContext passively composes ProviderRegistry 
        without absorbing registry behavior.
        """
        context = RuntimeContext()
        
        assert hasattr(context, 'ai_provider_registry')
        assert isinstance(context.ai_provider_registry, ProviderRegistry)
        
        # Verify Context doesn't expose proxy methods for registry behavior
        context_methods = [m for m in dir(context) if not m.startswith('_')]
        assert 'register_provider_info' not in context_methods
        assert 'list_ai_providers' not in context_methods

    def test_runtime_context_never_calls_registry_methods(self):
        """
        Verify RuntimeContext source code only wires the dependency and NEVER calls 
        registry behavior methods (register, unregister, provider_exists, etc.).
        """
        import inspect
        
        context_source = inspect.getsource(RuntimeContext)
        
        # It's permitted to instantiate it: ProviderRegistry()
        # It's permitted to expose it: def ai_provider_registry(...)
        
        # It is forbidden to call behavior methods on it or proxy them
        forbidden_calls = [
            '.register(',
            '.unregister(',
            '.provider_exists(',
            '.list_providers(',
            '.get_provider('
        ]
        
        for forbidden in forbidden_calls:
            assert forbidden not in context_source, f"RuntimeContext violates composition rule by calling {forbidden}"
