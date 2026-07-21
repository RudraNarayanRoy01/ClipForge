from typing import List

from src.domain.models.render_draft import RenderDraft
from src.domain.models.validation import ValidationResult


class RenderValidator:
    """
    Validates a RenderDraft to ensure it is suitable for rendering execution.
    
    This component performs verification only. It does not mutate the RenderDraft,
    compose a RenderPlan, or interact with rendering or export backends.
    """
    
    def validate(self, draft: RenderDraft) -> ValidationResult:
        """
        Validates the cross-object consistency of a RenderDraft.
        
        Args:
            draft: The assembled inputs required for rendering.
            
        Returns:
            ValidationResult detailing success/failure and any specific issues.
        """
        errors: List[str] = []
        messages: List[str] = []
        
        # Validate TimelineState presence and content
        if not draft.timeline_state:
            errors.append("RenderDraft is missing a TimelineState.")
        else:
            timeline = draft.timeline_state
            
            # Ensure there is at least one track with items to render
            has_video = any(track.items for track in timeline.video_tracks)
            has_audio = any(track.items for track in timeline.audio_tracks)
            has_overlay = any(track.items for track in timeline.overlay_tracks)
            has_subtitle = any(track.items for track in timeline.subtitle_tracks)
            
            if not (has_video or has_audio or has_overlay or has_subtitle):
                errors.append("TimelineState contains no renderable content (no items in any tracks).")
                
            # Basic invariant validation (if duration < 0 is possible)
            if hasattr(timeline.total_duration, 'total_seconds') and timeline.total_duration.total_seconds() <= 0:
                errors.append("TimelineState has an invalid total duration (<= 0).")
                
        # Validate RenderProfile presence
        if not draft.render_profile:
            errors.append("RenderDraft is missing a RenderProfile.")
            
        if errors:
            messages.append("Validation failed for RenderDraft.")
            return ValidationResult.failure(
                errors=tuple(errors),
                messages=tuple(messages)
            )
            
        messages.append("RenderDraft successfully validated.")
        return ValidationResult.success(messages=tuple(messages))
