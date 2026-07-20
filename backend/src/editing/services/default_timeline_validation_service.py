from typing import List, Set
from uuid import UUID

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.validation import ValidationResult
from src.editing.domain.services.timeline_validation_service import ITimelineValidationService


class DefaultTimelineValidationService(ITimelineValidationService):
    """
    Default implementation of ITimelineValidationService.
    Evaluates TimelineState against structural domain invariants.
    """

    def validate(self, timeline_state: TimelineState) -> ValidationResult:
        errors: List[str] = []

        self._validate_metadata(timeline_state, errors)
        self._validate_duration(timeline_state, errors)
        self._validate_tracks_and_items(timeline_state, errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors)
        )

    def _validate_metadata(self, state: TimelineState, errors: List[str]) -> None:
        if state.metadata.fps <= 0:
            errors.append(f"Invalid fps: {state.metadata.fps}. Must be > 0.")
        
        width, height = state.metadata.resolution
        if width <= 0 or height <= 0:
            errors.append(f"Invalid resolution: {state.metadata.resolution}. Dimensions must be > 0.")
            
        if state.metadata.sample_rate <= 0:
            errors.append(f"Invalid sample rate: {state.metadata.sample_rate}. Must be > 0.")

    def _validate_duration(self, state: TimelineState, errors: List[str]) -> None:
        if state.total_duration.value < 0:
            errors.append(f"Invalid total_duration: {state.total_duration.value}. Must be >= 0.")

    def _validate_tracks_and_items(self, state: TimelineState, errors: List[str]) -> None:
        seen_ids: Set[UUID] = set()

        all_tracks = (
            state.video_tracks
            + state.audio_tracks
            + state.overlay_tracks
            + state.subtitle_tracks
        )

        for track in all_tracks:
            # Check track ID uniqueness
            if track.id in seen_ids:
                errors.append(f"Duplicate track ID found: {track.id}")
            seen_ids.add(track.id)

            for item in track.items:
                # Check item ID uniqueness
                if item.id in seen_ids:
                    errors.append(f"Duplicate item ID found: {item.id}")
                seen_ids.add(item.id)

                # Validate timeline_time_range
                t_range = item.timeline_time_range
                if t_range.start.value < 0:
                    errors.append(f"Item {item.id} has negative start time: {t_range.start.value}.")
                if t_range.end.value < t_range.start.value:
                    errors.append(
                        f"Item {item.id} has end time ({t_range.end.value}) "
                        f"before start time ({t_range.start.value})."
                    )

                # Validate source_time_range if present
                if item.source_time_range:
                    s_range = item.source_time_range
                    if s_range.start.value < 0:
                        errors.append(f"Item {item.id} has negative source start time: {s_range.start.value}.")
                    if s_range.end.value < s_range.start.value:
                        errors.append(
                            f"Item {item.id} has source end time ({s_range.end.value}) "
                            f"before source start time ({s_range.start.value})."
                        )
