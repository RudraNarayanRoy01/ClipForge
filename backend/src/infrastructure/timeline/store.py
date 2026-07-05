from typing import List, Dict, Any, TypeVar, Type
from backend.src.intelligence.timeline.models import SemanticEvent

T = TypeVar('T', bound=SemanticEvent)

class TemporalStore:
    def __init__(self):
        # MVP: simple in-memory list instead of PostgreSQL
        self._events: List[SemanticEvent] = []

    def insert(self, event: SemanticEvent) -> None:
        self._events.append(event)
        # Sort by start time for easier temporal queries
        self._events.sort(key=lambda x: x.start_time_ms)

    def query_range(self, stream_id: str, start_time_ms: int, end_time_ms: int) -> List[SemanticEvent]:
        # Basic O(n) filter for overlapping events
        return [
            e for e in self._events
            if e.stream_id == stream_id and
               e.start_time_ms < end_time_ms and
               e.end_time_ms > start_time_ms
        ]

    def query_by_modality(self, stream_id: str, modality: str) -> List[SemanticEvent]:
        return [e for e in self._events if e.stream_id == stream_id and e.modality == modality]

# Singleton for MVP
temporal_store = TemporalStore()
