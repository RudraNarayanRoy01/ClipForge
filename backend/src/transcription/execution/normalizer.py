from src.runtime.execution.workload_normalizer import WorkloadNormalizer, WorkloadNormalizationError
from src.runtime.core.intent import ExecutionIntent
from src.transcription.dtos import TranscriptionRequest
from src.transcription.execution.workload import TranscriptionWorkload

class TranscriptionNormalizer(WorkloadNormalizer[TranscriptionWorkload]):
    """
    Transforms opaque intent payload into a typed TranscriptionWorkload.
    """
    def normalize(self, intent: ExecutionIntent) -> TranscriptionWorkload:
        if intent.capability_id != "AUDIO_TRANSCRIPTION":
            raise WorkloadNormalizationError(f"Unsupported capability: {intent.capability_id}")

        if not isinstance(intent.payload, dict):
            raise WorkloadNormalizationError("Transcription payload must be a dictionary.")

        try:
            # Construct the immutable DTO from the opaque payload
            request = TranscriptionRequest(**intent.payload)
            # Wrap in the capability-owned execution workload
            return TranscriptionWorkload(request=request)
        except Exception as e:
            raise WorkloadNormalizationError(f"Failed to normalize transcription payload: {str(e)}") from e
