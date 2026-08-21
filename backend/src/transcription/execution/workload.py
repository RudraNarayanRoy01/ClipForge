from dataclasses import dataclass
from src.runtime.core.execution_workload import ExecutionWorkload
from src.transcription.dtos import TranscriptionRequest, Transcript
from typing import Optional

@dataclass
class TranscriptionCapabilityContext:
    request: TranscriptionRequest
    result: Optional[Transcript] = None
    exception: Optional[Exception] = None
@dataclass(frozen=True, init=False)
class TranscriptionWorkload(ExecutionWorkload):
    """
    Immutable, provider-neutral execution workload for transcription.

    Bridges the capability-specific TranscriptionRequest into the
    Runtime ExecutionWorkload contract.
    """
    context: TranscriptionCapabilityContext

    def __init__(self, context: Optional[TranscriptionCapabilityContext] = None, request: Optional[TranscriptionRequest] = None):
        if context is None and request is not None:
            context = TranscriptionCapabilityContext(request=request)
        object.__setattr__(self, 'context', context)

    @property
    def capability_id(self) -> str:
        return "AUDIO_TRANSCRIPTION"

    @property
    def request(self) -> TranscriptionRequest:
        return self.context.request
