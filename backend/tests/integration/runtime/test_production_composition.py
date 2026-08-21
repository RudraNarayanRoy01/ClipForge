import pytest
from src.bootstrap.startup import initialize_container
from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.domain.ports import ILLMReasoningEngine
from src.transcription.interfaces import ITranscriptionService
from src.infrastructure.runtime_adapters.runtime_reasoning_adapter import RuntimeReasoningAdapter
from src.infrastructure.runtime_adapters.runtime_transcription_adapter import RuntimeTranscriptionAdapter
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry
from src.transcription.execution.mechanism import WhisperExecutionMechanism
from src.runtime.execution.mechanisms.llm_execution_mechanism import LLMExecutionMechanism
from src.runtime.core.providers import RuntimeProviderRegistry, ProviderIdentity

@pytest.fixture
def container():
    return initialize_container()

def test_runtime_invocation_facade_resolves(container):
    # Test 1 — RuntimeInvocationFacade resolves
    facade = container.resolve(RuntimeInvocationFacade)
    assert facade is not None
    assert isinstance(facade, RuntimeInvocationFacade)

def test_llm_reasoning_engine_resolves_to_runtime_adapter(container):
    # Test 2 — LLM application port uses Runtime adapter
    adapter = container.resolve(ILLMReasoningEngine)
    assert adapter is not None
    assert isinstance(adapter, RuntimeReasoningAdapter)

def test_transcription_service_resolves_to_runtime_adapter(container):
    # Test 3 — Transcription application port uses Runtime adapter
    adapter = container.resolve(ITranscriptionService)
    assert adapter is not None
    assert isinstance(adapter, RuntimeTranscriptionAdapter)

def test_execution_mechanism_registry_contains_llm(container):
    # Test 4 — Mechanism registry contains LLM
    registry = container.resolve(ExecutionMechanismRegistry)
    mechanism = registry.resolve("ollama", "LLM_REASONING").mechanism
    assert mechanism is not None
    assert isinstance(mechanism, LLMExecutionMechanism)

def test_execution_mechanism_registry_contains_whisper(container):
    # Test 5 — Mechanism registry contains Whisper
    registry = container.resolve(ExecutionMechanismRegistry)
    mechanism = registry.resolve("whisper", "AUDIO_TRANSCRIPTION").mechanism
    assert mechanism is not None
    assert isinstance(mechanism, WhisperExecutionMechanism)

def test_provider_registry_is_populated(container):
    # Test 6 — Provider registry is populated
    registry = container.resolve(RuntimeProviderRegistry)
    
    ollama_provider = registry.get_provider(ProviderIdentity("ollama"))
    assert ollama_provider is not None
    assert ollama_provider.descriptor.identity.identifier == "ollama"
    
    whisper_provider = registry.get_provider(ProviderIdentity("whisper"))
    assert whisper_provider is not None
    assert whisper_provider.descriptor.identity.identifier == "whisper"
