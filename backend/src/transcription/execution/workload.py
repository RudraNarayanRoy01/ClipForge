from dataclasses import dataclass
from src.runtime.core.execution_workload import ExecutionWorkload
from src.transcription.dtos import TranscriptionRequest

@dataclass(frozen=True)
class TranscriptionWorkload(ExecutionWorkload):
    """
    Immutable, provider-neutral execution workload for transcription.

    Bridges the capability-specific TranscriptionRequest into the
    Runtime ExecutionWorkload contract.
    """
    request: TranscriptionRequest

    @property
    def capability_id(self) -> str:
        return "AUDIO_TRANSCRIPTION"
