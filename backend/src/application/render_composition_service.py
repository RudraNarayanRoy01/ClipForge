import uuid
from typing import Optional, Tuple

from src.domain.models.render_draft import RenderDraft
from src.domain.render_plan import (
    RenderPlan, RenderMetadata, RenderResolution, FrameRate, AspectRatio,
    TimelinePosition, RenderSegment, RenderTrack, LayerCategory,
    RenderInstruction
)
from src.editing.domain.models.state import TimelineState, TimelineTrack
from src.editing.domain.models.items import TimelineItem, Clip, Subtitle, Overlay
from src.domain.models.render_profile import RenderProfile
from src.application.render_plan_builder import RenderPlanBuilder

class RenderCompositionService:
    """
    Stateless service responsible for extracting and normalizing editing outputs
    into the immutable RenderPlan, acting as the architectural bridge between 
    editing and rendering.
    
    Each composition request instantiates a fresh builder. No intermediate state
    is retained.
    """
    
    def compose(self, draft: RenderDraft) -> RenderPlan:
        """
        Extracts editing outputs from the RenderDraft and orchestrates the creation
        of the RenderPlan via the builder.
        
        Args:
            draft: The intermediate rendering specification from the planner.
            
        Returns:
            RenderPlan: The complete, normalized execution blueprint.
        """
        # Since RenderDraft doesn't include a project ID, we assign one for the final plan execution context
        project_id = uuid.uuid4()
        
        metadata = self._normalize_metadata(draft.timeline_state, draft.render_profile)
        builder = RenderPlanBuilder(project_id=project_id, metadata=metadata)
        
        self._compose_layer(builder, LayerCategory.VIDEO, "Video Layer", 0, draft.timeline_state.video_tracks)
        self._compose_layer(builder, LayerCategory.AUDIO, "Audio Layer", 1, draft.timeline_state.audio_tracks)
        self._compose_layer(builder, LayerCategory.OVERLAY, "Overlay Layer", 2, draft.timeline_state.overlay_tracks)
        self._compose_layer(builder, LayerCategory.SUBTITLE, "Subtitle Layer", 3, draft.timeline_state.subtitle_tracks)
        
        return builder.build()
        
    def _normalize_metadata(self, timeline_state: TimelineState, profile: RenderProfile) -> RenderMetadata:
        """Normalizes TimelineState and RenderProfile into RenderMetadata."""
        ratio_str = profile.aspect_ratio.value
        if ":" in ratio_str:
            w_str, h_str = ratio_str.split(":")
            w, h = int(w_str), int(h_str)
        else:
            w, h = 16, 9  # Fallback for custom or unknown

        return RenderMetadata(
            resolution=RenderResolution(width=profile.resolution.width, height=profile.resolution.height),
            frame_rate=FrameRate(fps=profile.frame_rate),
            duration_seconds=timeline_state.total_duration.value,
            aspect_ratio=AspectRatio(width_ratio=w, height_ratio=h)
        )
        
    def _compose_layer(
        self, 
        builder: RenderPlanBuilder, 
        category: LayerCategory, 
        name: str, 
        z_index: int, 
        editing_tracks: Tuple[TimelineTrack, ...]
    ) -> None:
        """Extracts and normalizes editing tracks into rendering tracks, adding them to the builder."""
        render_tracks = []
        for track in editing_tracks:
            segments = []
            for item in track.items:
                segment = self._normalize_item_to_segment(item)
                if segment:
                    segments.append(segment)
            
            # Deterministically sort segments by start time
            segments.sort(key=lambda s: s.timeline_start.time_seconds)
            
            render_tracks.append(RenderTrack(
                id=uuid.uuid4(),
                name=f"Track {track.id}",
                segments=segments
            ))
            
        builder.add_layer(category=category, name=name, z_index=z_index, tracks=render_tracks)

    def _normalize_item_to_segment(self, item: TimelineItem) -> Optional[RenderSegment]:
        """Normalizes a TimelineItem into a RenderSegment."""
        if isinstance(item, Clip):
            source_start = item.source_time_range.start.value if item.source_time_range else 0.0
            source_end = item.source_time_range.end.value if item.source_time_range else (item.timeline_time_range.end.value - item.timeline_time_range.start.value)
            
            return RenderSegment(
                id=uuid.uuid4(),
                source_reference=str(item.asset_id),
                timeline_start=TimelinePosition(time_seconds=item.timeline_time_range.start.value),
                timeline_end=TimelinePosition(time_seconds=item.timeline_time_range.end.value),
                source_start=TimelinePosition(time_seconds=source_start),
                source_end=TimelinePosition(time_seconds=source_end),
                instructions=[
                    RenderInstruction("playback_speed", {"speed": item.playback_speed}),
                    RenderInstruction("scaling", {"mode": item.scaling_mode.value})
                ]
            )
        elif isinstance(item, Overlay):
            return RenderSegment(
                id=uuid.uuid4(),
                source_reference=str(item.asset_id),
                timeline_start=TimelinePosition(time_seconds=item.timeline_time_range.start.value),
                timeline_end=TimelinePosition(time_seconds=item.timeline_time_range.end.value),
                source_start=TimelinePosition(time_seconds=0.0),
                source_end=TimelinePosition(time_seconds=item.timeline_time_range.end.value - item.timeline_time_range.start.value),
                instructions=[
                    RenderInstruction("opacity", {"value": item.opacity}),
                    RenderInstruction("position", {
                        "x": item.bounding_box.origin.x,
                        "y": item.bounding_box.origin.y,
                        "w": item.bounding_box.size.width,
                        "h": item.bounding_box.size.height
                    })
                ]
            )
        elif isinstance(item, Subtitle):
            return RenderSegment(
                id=uuid.uuid4(),
                source_reference="text",  # Special marker since subtitles use text, not asset_id
                timeline_start=TimelinePosition(time_seconds=item.timeline_time_range.start.value),
                timeline_end=TimelinePosition(time_seconds=item.timeline_time_range.end.value),
                source_start=TimelinePosition(time_seconds=0.0),
                source_end=TimelinePosition(time_seconds=item.timeline_time_range.end.value - item.timeline_time_range.start.value),
                instructions=[
                    RenderInstruction("text_content", {"text": item.text}),
                    RenderInstruction("text_style", {"style_id": item.style_reference_id})
                ]
            )
        
        return None
