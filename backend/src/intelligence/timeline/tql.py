from typing import List, Optional, TypeVar, Type, Callable
from src.intelligence.timeline.models import SemanticEvent
from src.infrastructure.timeline.store import TemporalStore

T = TypeVar('T', bound=SemanticEvent)

class TemporalQueryBuilder:
    def __init__(self, store: TemporalStore, stream_id: str):
        self.store = store
        self.stream_id = stream_id
        self._filters: List[Callable[[SemanticEvent], bool]] = []

    def during(self, start_time_ms: int, end_time_ms: int) -> 'TemporalQueryBuilder':
        self._filters.append(lambda e: e.start_time_ms >= start_time_ms and e.end_time_ms <= end_time_ms)
        return self

    def of_type(self, event_type: Type[T]) -> 'TemporalQueryBuilder':
        self._filters.append(lambda e: isinstance(e, event_type))
        return self
    
    def overlapping(self, other_events: List[SemanticEvent]) -> 'TemporalQueryBuilder':
        def overlaps_any(e: SemanticEvent) -> bool:
            return any(
                max(e.start_time_ms, o.start_time_ms) < min(e.end_time_ms, o.end_time_ms)
                for o in other_events
            )
        self._filters.append(overlaps_any)
        return self

    def execute(self) -> List[SemanticEvent]:
        # Fetch all for the stream, then apply filters (inefficient but works for MVP)
        results = [e for e in self.store._events if e.stream_id == self.stream_id]
        for f in self._filters:
            results = [e for e in results if f(e)]
        return results
