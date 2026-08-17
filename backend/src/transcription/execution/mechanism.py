import asyncio
import threading
from typing import Optional, Tuple

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.execution.execution_mechanism_registry import AbstractExecutionMechanism
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.interfaces import ITranscriptionService
from src.transcription.exceptions import TranscriptionProcessingError, TranscriptionConfigurationError

class WhisperExecutionMechanism(AbstractExecutionMechanism[TranscriptionWorkload]):
    """
    Concrete execution mechanism for Whisper transcription.

    Bridges the asynchronous WhisperTranscriptionService into the synchronous
    Runtime execution boundary, executing fully decoupled from Runtime Core.
    """

    def __init__(self, service: ITranscriptionService) -> None:
        self._service = service

    def execute(self, target: ExecutionTarget, workload: TranscriptionWorkload) -> Tuple[bool, Optional[str]]:
        # Target identity is preserved but dynamic model switching is bypassed
        # as WhisperTranscriptionService natively enforces configuration via TranscriptionSettings.

        result = None
        exception: Optional[Exception] = None

        def _runner() -> None:
            nonlocal result, exception
            try:
                # Bridge the async transcription call safely within a new thread
                result = asyncio.run(self._service.transcribe(workload.request))
            except Exception as e:
                exception = e

        t = threading.Thread(target=_runner)
        t.start()
        t.join()

        if exception:
            if isinstance(exception, (TranscriptionProcessingError, TranscriptionConfigurationError)):
                return False, str(exception)
            # Unexpected errors propagate out of the mechanism
            raise exception

        # Success guarantees genuine local inference execution occurred
        return True, None
