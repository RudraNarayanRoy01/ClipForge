import os
from typing import Callable, Optional
from uuid import UUID

from src.domain.services import IRenderingProvider
from src.domain.models.rendering import RenderSettings, RenderResult, RenderStatus
from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.items import Clip, Overlay, Subtitle
from src.editing.domain.enums.items import TimelineItemType
from src.editing.domain.value_objects.time import TimeRange

try:
    from moviepy.editor import (
        VideoFileClip,
        AudioFileClip,
        CompositeVideoClip,
        CompositeAudioClip,
        ColorClip,
        TextClip,
        ImageClip
    )
    import moviepy.video.fx.all as vfx
except ImportError:
    pass


class MoviePyRenderingProvider(IRenderingProvider):
    """
    First concrete implementation of IRenderingProvider using MoviePy.
    
    Responsible for translating a complete TimelineState and RenderSettings 
    into MoviePy rendering operations. Ensures complete isolation of MoviePy 
    constructs from the domain models.
    """

    def __init__(self, asset_path_resolver: Callable[[UUID], str]):
        """
        Initializes the MoviePyRenderingProvider.
        
        Args:
            asset_path_resolver: A synchronous callable that resolves an asset UUID 
                                 to a local file system path for rendering.
        """
        self._asset_path_resolver = asset_path_resolver

    def render(self, timeline_state: TimelineState, render_settings: RenderSettings) -> RenderResult:
        """
        Renders a TimelineState according to RenderSettings using MoviePy.
        
        Translates domain tracks and items into MoviePy clips, composites them, 
        and triggers the final rendering process.
        """
        visual_clips = []
        audio_clips = []

        # Process Video Tracks
        for track in timeline_state.video_tracks:
            for item in track.items:
                if item.item_type == TimelineItemType.CLIP and isinstance(item, Clip):
                    file_path = self._asset_path_resolver(item.asset_id)
                    video_clip = VideoFileClip(file_path)
                    
                    video_clip = self._apply_time_range(video_clip, item.source_time_range, item.timeline_time_range)
                    
                    if item.playback_speed != 1.0:
                        video_clip = video_clip.fx(vfx.speedx, item.playback_speed)
                        
                    visual_clips.append(video_clip)

        # Process Overlay Tracks
        for track in timeline_state.overlay_tracks:
            for item in track.items:
                if item.item_type == TimelineItemType.OVERLAY and isinstance(item, Overlay):
                    file_path = self._asset_path_resolver(item.asset_id)
                    overlay_clip = ImageClip(file_path)
                    
                    duration = item.timeline_time_range.end.value - item.timeline_time_range.start.value
                    overlay_clip = (overlay_clip
                                    .set_start(item.timeline_time_range.start.value)
                                    .set_duration(duration))
                    
                    overlay_clip = overlay_clip.set_position((item.bounding_box.x, item.bounding_box.y))
                    
                    if item.opacity < 1.0 and hasattr(overlay_clip, "set_opacity"):
                        overlay_clip = overlay_clip.set_opacity(item.opacity)
                        
                    visual_clips.append(overlay_clip)

        # Process Subtitle Tracks
        for track in timeline_state.subtitle_tracks:
            for item in track.items:
                if item.item_type == TimelineItemType.SUBTITLE and isinstance(item, Subtitle):
                    text_clip = TextClip(item.text)
                    duration = item.timeline_time_range.end.value - item.timeline_time_range.start.value
                    text_clip = (text_clip
                                 .set_start(item.timeline_time_range.start.value)
                                 .set_duration(duration))
                    
                    if item.position:
                        text_clip = text_clip.set_position((item.position.x, item.position.y))
                        
                    visual_clips.append(text_clip)

        # Process Audio Tracks
        for track in timeline_state.audio_tracks:
            for item in track.items:
                if item.item_type == TimelineItemType.CLIP and isinstance(item, Clip):
                    file_path = self._asset_path_resolver(item.asset_id)
                    audio_clip = AudioFileClip(file_path)
                    audio_clip = self._apply_time_range(audio_clip, item.source_time_range, item.timeline_time_range)
                    audio_clips.append(audio_clip)

        # Composite Visuals
        output_width = render_settings.output_resolution.width
        output_height = render_settings.output_resolution.height
        total_duration = timeline_state.total_duration.value

        base_clip = ColorClip(size=(output_width, output_height), color=(0, 0, 0), duration=total_duration)
        final_video = CompositeVideoClip([base_clip] + visual_clips, size=(output_width, output_height))

        # Composite Audio
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)

        # Render Output
        output_path = render_settings.render_output_location
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        final_video.write_videofile(
            output_path,
            fps=render_settings.frame_rate,
            codec=render_settings.video_codec,
            audio_codec=render_settings.audio_codec,
            bitrate=render_settings.bitrate
        )

        final_video.close()

        return RenderResult(
            status=RenderStatus.COMPLETED,
            rendered_output_location=output_path,
            rendered_duration=total_duration,
            rendering_metadata={"provider": "MoviePyRenderingProvider"}
        )

    def _apply_time_range(self, moviepy_clip, source_time_range: Optional[TimeRange], timeline_time_range: TimeRange):
        """
        Applies trimming and timeline positioning to a MoviePy clip based on domain models.
        """
        if source_time_range:
            moviepy_clip = moviepy_clip.subclip(
                source_time_range.start.value,
                source_time_range.end.value
            )
            
        moviepy_clip = moviepy_clip.set_start(timeline_time_range.start.value)
        return moviepy_clip
