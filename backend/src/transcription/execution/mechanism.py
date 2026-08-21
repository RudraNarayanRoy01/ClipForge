import asyncio
import threading
from typing import Optional, Tuple, Callable, AsyncContextManager

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.execution.execution_mechanism_registry import AbstractExecutionMechanism
from src.runtime.execution.execution_result import ExecutionOutcome
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.interfaces import ITranscriptionService, ITranscriptRepository
from src.transcription.exceptions import TranscriptionProcessingError, TranscriptionConfigurationError

class WhisperExecutionMechanism(AbstractExecutionMechanism[TranscriptionWorkload]):
    """
    Concrete execution mechanism for Whisper transcription.

    Bridges the asynchronous WhisperTranscriptionService into the synchronous
    Runtime execution boundary, executing fully decoupled from Runtime Core.
    """

    def __init__(
        self,
        service: ITranscriptionService,
        repo_factory: Optional[Callable[[], AsyncContextManager[ITranscriptRepository]]] = None
    ) -> None:
        self._service = service
        self._repo_factory = repo_factory

    def execute(self, target: ExecutionTarget, workload: TranscriptionWorkload) -> Tuple[ExecutionOutcome, Optional[str]]:
        # Target identity is preserved but dynamic model switching is bypassed
        # as WhisperTranscriptionService natively enforces configuration via TranscriptionSettings.

        result = None
        exception: Optional[Exception] = None

        def _runner() -> None:
            nonlocal result, exception
            try:
                # Bridge the async transcription call safely within a new thread
                async def transcribe_and_persist():
                    transcript = await self._service.transcribe(workload.context.request)
                    
                    # Optional persistence using mechanism-level domain sink
                    if getattr(workload.context.request, "video_asset_id", None) and self._repo_factory:
                        async with self._repo_factory() as repository:
                            await repository.save_transcript(workload.context.request.video_asset_id, transcript)
                            
                    return transcript

                result = asyncio.run(transcribe_and_persist())
                workload.context.result = result
            except Exception as e:
                exception = e
                workload.context.exception = e

        t = threading.Thread(target=_runner)
        t.start()
        t.join()

        if exception:
            if isinstance(exception, (TranscriptionProcessingError, TranscriptionConfigurationError)):
                return ExecutionOutcome.FAILED, str(exception)
            # Persistence errors or unexpected issues correctly translate to FAILED
            # to strictly prevent false SUCCESS reporting when artifacts are lost.
            return ExecutionOutcome.FAILED, str(exception)

        # Success guarantees genuine local inference and persistence occurred
        return ExecutionOutcome.SUCCESS, None
