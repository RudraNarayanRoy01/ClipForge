from typing import Tuple

from src.reasoning.execution.models import ExecutionInput
from .interfaces import IExecutionPlanner
from .models import ExecutionPlanDraft, DraftSegment


class DefaultExecutionPlanner(IExecutionPlanner):
    """
    Default deterministic implementation of IExecutionPlanner.
    Transforms ExecutionInput into an ExecutionPlanDraft.
    """

    def create_execution_draft(self, execution_input: ExecutionInput) -> ExecutionPlanDraft:
        """
        Transforms ExecutionInput into a deterministic ExecutionPlanDraft.
        Selects candidate segments from the provided immutable input.
        """
        segments = self._select_candidate_segments(execution_input)
        
        return ExecutionPlanDraft(
            execution_input=execution_input,
            segments=segments
        )

    def _select_candidate_segments(self, execution_input: ExecutionInput) -> Tuple[DraftSegment, ...]:
        """
        Selects candidate segments from the execution input context.
        This must remain deterministic, without generating UUIDs,
        timestamps, or relying on external state.
        
        Currently acts as a structural implementation. As the subsystem matures,
        this will extract candidate segments from the TimelineContext and 
        Recommendation parameters of the ExecutionInput.
        """
        # A structural base implementation returning no segments initially.
        return ()
