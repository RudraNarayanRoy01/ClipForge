from src.transcription.interfaces import ITranscriptionService
from src.transcription.dtos import TranscriptionRequest, Transcript
from src.transcription.exceptions import TranscriptionProcessingError

from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.execution.execution_result import ExecutionOutcome
from src.transcription.execution.workload import (
    TranscriptionWorkload, TranscriptionCapabilityContext
)


class RuntimeTranscriptionAdapter(ITranscriptionService):
    """
    Adapter bridging the ITranscriptionService domain port with the new Runtime boundary.
    
    This replaces direct execution of WhisperTranscriptionService from the application layer.
    The Runtime mechanism executed behind this facade will continue to fulfill
    the 6C.2.3 requirement of persisting the transcript, while this adapter
    extracts the transient result from the CapabilityContext to return it synchronously
    to the orchestrator.
    """
    
    def __init__(self, facade: RuntimeInvocationFacade):
        self._facade = facade

    async def transcribe(self, request: TranscriptionRequest) -> Transcript:
        context = TranscriptionCapabilityContext(request=request)
        workload = TranscriptionWorkload(context=context)
        
        intent = ExecutionIntent(
            capability_id="AUDIO_TRANSCRIPTION",
            payload=workload
        )
        planning_context = PlanningContext()

        # The Facade is synchronous but the caller is async.
        # This aligns with the new architecture; the underlying mechanism
        # will run the transcription inside a thread or asyncio.run.
        result = self._facade.invoke(intent, planning_context)

        if result.outcome != ExecutionOutcome.SUCCESS:
            error_msg = result.error_message or "Unknown execution error"
            raise TranscriptionProcessingError(f"Runtime transcription failed: {error_msg}")
            
        if context.exception:
            raise context.exception
            
        if not context.result:
            raise TranscriptionProcessingError("Runtime succeeded but returned no transcript in context.")
            
        return context.result
