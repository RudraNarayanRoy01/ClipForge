from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry
from src.runtime.execution.workload_normalization_extension import WorkloadNormalizationExtensionPoint
from src.transcription.interfaces import ITranscriptionService
from src.transcription.providers.whisper_provider import WhisperTranscriptionService
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.execution.normalizer import TranscriptionNormalizer
from src.transcription.execution.mechanism import WhisperExecutionMechanism
from src.runtime.core.providers import RuntimeProviderRegistry, ProviderDescriptor, ProviderIdentity, ProviderCategory
from src.intelligence.providers.capabilities import IAIProvider
from src.runtime.execution.mechanisms.llm_execution_mechanism import LLMExecutionMechanism, LLMExecutionWorkload, LLMNormalizer
class RuntimeModule(DIModule):
    """
    Bootstrap module for Runtime execution architecture.

    Provisions execution registries, normalizers, and wires existing infrastructure
    capabilities into the ExecutionEngine boundary without creating legacy side-effects.
    """
    def register(self, container: Container) -> None:
        from src.runtime.composition.runtime_pipeline_factory import RuntimePipelineFactory
        from src.runtime.invocation.runtime_pipeline import RuntimePipeline
        from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
        # 1. Provision Registries
        registry = ExecutionMechanismRegistry()
        extension_point = WorkloadNormalizationExtensionPoint()
        provider_registry = RuntimeProviderRegistry()

        from src.config.ai_settings import AISettings
        from src.config.transcription_settings import TranscriptionSettings
        
        ai_settings = container.resolve(AISettings)
        transcription_settings = container.resolve(TranscriptionSettings)

        provider_registry.register_provider(ProviderDescriptor(
            identity=ProviderIdentity("whisper"),
            display_name="Whisper Transcription",
            description="Local whisper model",
            supported_capability_ids=["AUDIO_TRANSCRIPTION"],
            category=ProviderCategory.AUDIO,
            metadata={
                "target_class": "local",
                "model": transcription_settings.transcription_model,
                "device": transcription_settings.transcription_device,
                "compute_class": transcription_settings.transcription_compute_type,
            }
        ))

        provider_registry.register_provider(ProviderDescriptor(
            identity=ProviderIdentity("ollama"),
            display_name="Ollama LLM",
            description="Local reasoning models",
            supported_capability_ids=["LLM_REASONING"],
            category=ProviderCategory.REASONING,
            metadata={
                "target_class": "local",
                "model": ai_settings.ollama_model,
                "timeout_seconds": ai_settings.ai_timeout_seconds,
            }
        ))

        # 2. Wire Transcription (AUDIO_TRANSCRIPTION)
        transcription_service = container.resolve(WhisperTranscriptionService)
        
        from contextlib import asynccontextmanager
        
        @asynccontextmanager
        async def transcript_repository_factory():
            from src.infrastructure.database import AsyncSessionLocal
            from src.repositories.transcript_repository import TranscriptRepository
            
            async with AsyncSessionLocal() as session:
                yield TranscriptRepository(session)
                
        whisper_mechanism = WhisperExecutionMechanism(transcription_service, repo_factory=transcript_repository_factory)

        registry.register(
            provider_id="whisper",
            capability_id="AUDIO_TRANSCRIPTION",
            expected_type=TranscriptionWorkload,
            mechanism=whisper_mechanism
        )

        extension_point.register_normalizer(
            capability_id="AUDIO_TRANSCRIPTION",
            normalizer=TranscriptionNormalizer()
        )
        
        # 3. Wire Reasoning (LLM_REASONING)
        llm_provider = container.resolve(IAIProvider)
        llm_mechanism = LLMExecutionMechanism(llm_provider)

        registry.register(
            provider_id="ollama",
            capability_id="LLM_REASONING",
            expected_type=LLMExecutionWorkload,
            mechanism=llm_mechanism
        )

        extension_point.register_normalizer(
            capability_id="LLM_REASONING",
            normalizer=LLMNormalizer()
        )

        # 4. Expose resulting runtime dependencies
        container.register_singleton(ExecutionMechanismRegistry, registry)
        container.register_singleton(WorkloadNormalizationExtensionPoint, extension_point)
        container.register_singleton(RuntimeProviderRegistry, provider_registry)

        # 5. Expose Runtime Core Execution boundaries
        from src.runtime.execution.execution_engine import ExecutionEngine
        from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary

        container.register_singleton(ExecutionEngine, ExecutionEngine)
        container.register_singleton(RuntimeExecutionBoundary, RuntimeExecutionBoundary)

        # 6. Expose Runtime Invocation boundaries
        pipeline_context = RuntimePipelineFactory.create()
        pipeline = RuntimePipeline(pipeline_context)
        container.register_singleton(RuntimePipeline, pipeline)
        container.register_singleton(RuntimeInvocationFacade, RuntimeInvocationFacade)
