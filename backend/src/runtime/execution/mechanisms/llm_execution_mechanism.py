from dataclasses import dataclass
from typing import Optional, Tuple

from src.runtime.core.intent import ExecutionIntent
from src.runtime.execution.workload_normalizer import WorkloadNormalizer, WorkloadNormalizationError

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.execution.execution_mechanism_registry import AbstractExecutionMechanism
from src.runtime.execution.execution_result import ExecutionOutcome
from src.intelligence.providers.capabilities import IAIProvider
from src.intelligence.schemas.ai_models import AIRequest, AIResponse
import asyncio

@dataclass
class LLMCapabilityContext:
    request: AIRequest
    response: Optional[AIResponse] = None
    exception: Optional[Exception] = None

@dataclass(frozen=True)
class LLMExecutionWorkload(ExecutionWorkload):
    context: LLMCapabilityContext

    @property
    def capability_id(self) -> str:
        return "LLM_REASONING"


class LLMExecutionMechanism(AbstractExecutionMechanism[LLMExecutionWorkload]):
    """
    Concrete execution mechanism for LLM reasoning capabilities.
    
    Delegates to the existing IAIProvider interface.
    Attaches the result back onto the LLMCapabilityContext to satisfy 
    the transient payload architectural requirement (6C.3.1).
    """
    def __init__(self, provider: IAIProvider) -> None:
        self._provider = provider

    def execute(self, target: ExecutionTarget, workload: LLMExecutionWorkload) -> Tuple[ExecutionOutcome, Optional[str]]:
        try:
            # We run the async generate call within a synchronous wrapper.
            # This aligns with the ExecutionEngine's synchronous dispatch.
            response = asyncio.run(self._provider.generate(workload.context.request))
            workload.context.response = response
            return ExecutionOutcome.SUCCESS, None
        except Exception as e:
            workload.context.exception = e
            return ExecutionOutcome.FAILED, str(e)


class LLMNormalizer(WorkloadNormalizer[LLMExecutionWorkload]):
    def normalize(self, intent: ExecutionIntent) -> LLMExecutionWorkload:
        if not isinstance(intent.payload, LLMExecutionWorkload):
            raise WorkloadNormalizationError(f"Expected LLMExecutionWorkload, got {type(intent.payload)}")
        return intent.payload
