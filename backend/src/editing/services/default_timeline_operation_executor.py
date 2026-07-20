from src.editing.domain.exceptions import UnsupportedTimelineOperationError
from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineOperation, TimelineOperationType
from src.editing.domain.services.executor import ITimelineOperationExecutor


class DefaultTimelineOperationExecutor(ITimelineOperationExecutor):
    """
    Default implementation of the timeline operation executor.
    Applies exactly one TimelineOperation to a TimelineState.
    Dispatches execution according to the operation type.
    """

    async def execute(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """
        Executes a single TimelineOperation and returns a new immutable TimelineState.
        Dispatches to operation-specific handlers.
        """
        if not state:
            raise ValueError("TimelineState cannot be None")
        if not operation:
            raise ValueError("TimelineOperation cannot be None")

        if operation.operation_type == TimelineOperationType.INSERT:
            return await self._handle_insert(state, operation)
        elif operation.operation_type == TimelineOperationType.REMOVE:
            return await self._handle_remove(state, operation)
        elif operation.operation_type == TimelineOperationType.MOVE:
            return await self._handle_move(state, operation)
        elif operation.operation_type == TimelineOperationType.TRIM:
            return await self._handle_trim(state, operation)
        elif operation.operation_type == TimelineOperationType.SPLIT:
            return await self._handle_split(state, operation)
        elif operation.operation_type == TimelineOperationType.MERGE:
            return await self._handle_merge(state, operation)
        elif operation.operation_type == TimelineOperationType.OVERLAY:
            return await self._handle_overlay(state, operation)
        elif operation.operation_type == TimelineOperationType.SUBTITLE:
            return await self._handle_subtitle(state, operation)
        elif operation.operation_type == TimelineOperationType.TRANSITION:
            return await self._handle_transition(state, operation)
        else:
            raise UnsupportedTimelineOperationError(f"Unsupported operation type: {operation.operation_type}")

    async def _handle_insert(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for insert execution algorithm."""
        return state

    async def _handle_remove(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for remove execution algorithm."""
        return state

    async def _handle_move(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for move execution algorithm."""
        return state

    async def _handle_trim(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for trim execution algorithm."""
        return state

    async def _handle_split(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for split execution algorithm."""
        return state
        
    async def _handle_merge(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for merge execution algorithm."""
        return state
        
    async def _handle_overlay(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for overlay execution algorithm."""
        return state
        
    async def _handle_subtitle(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for subtitle execution algorithm."""
        return state
        
    async def _handle_transition(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """Placeholder for transition execution algorithm."""
        return state
