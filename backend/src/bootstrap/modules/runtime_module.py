from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry
from src.runtime.execution.workload_normalization_extension import WorkloadNormalizationExtensionPoint
from src.transcription.interfaces import ITranscriptionService
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.execution.normalizer import TranscriptionNormalizer
from src.transcription.execution.mechanism import WhisperExecutionMechanism

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

        # 2. Wire Transcription (AUDIO_TRANSCRIPTION)
        # Assumes ITranscriptionService is already registered by InfrastructureModule
        transcription_service = container.resolve(ITranscriptionService)
        whisper_mechanism = WhisperExecutionMechanism(transcription_service)

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

        # 3. Expose resulting runtime dependencies
        container.register_singleton(ExecutionMechanismRegistry, registry)
        container.register_singleton(WorkloadNormalizationExtensionPoint, extension_point)

        # 4. Expose Runtime Core Execution boundaries
        from src.runtime.execution.execution_engine import ExecutionEngine
        from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary

        container.register_singleton(ExecutionEngine, ExecutionEngine)
        container.register_singleton(RuntimeExecutionBoundary, RuntimeExecutionBoundary)

        # 5. Expose Runtime Invocation boundaries
        pipeline_context = RuntimePipelineFactory.create()
        pipeline = RuntimePipeline(pipeline_context)
        container.register_singleton(RuntimePipeline, pipeline)
        container.register_singleton(RuntimeInvocationFacade, RuntimeInvocationFacade)
