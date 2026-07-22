import os
import uuid
from typing import Callable, Optional
from uuid import UUID

from src.domain.ports import IRenderBackend
from src.domain.render_plan import RenderPlan
from src.domain.models.render_result import RenderResult, RenderStatus
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


class MoviePyRenderingBackend(IRenderBackend):
    """
    Concrete implementation of IRenderBackend using MoviePy.
    
    Responsible for executing a RenderPlan using MoviePy constructs.
    Maintains complete isolation of MoviePy types from the application layer.
    """

    def __init__(self, asset_path_resolver: Callable[[UUID], str], output_dir: Optional[str] = None):
        """
        Initializes the MoviePyRenderingBackend.
        
        Args:
            asset_path_resolver: Resolves an asset UUID to a local file system path.
            output_dir: The directory where rendered outputs will be saved. Defaults to system temp.
        """
        self._asset_path_resolver = asset_path_resolver
        if output_dir is None:
            import tempfile
            self._output_dir = tempfile.gettempdir()
        else:
            self._output_dir = output_dir

    def execute(self, plan: RenderPlan) -> RenderResult:
        """
        Executes a rendering plan using MoviePy.
        
        Args:
            plan: The canonical RenderPlan containing timeline state and render profile.
            
        Returns:
            RenderResult containing status and output location on success, or error details on failure.
        """
        try:
            return self._execute_safe(plan)
        except Exception as e:
            return RenderResult(
                status=RenderStatus.FAILED,
                message=str(e),
                rendering_metadata={"provider": "MoviePyRenderingBackend", "error_type": type(e).__name__}
            )

    def _execute_safe(self, plan: RenderPlan) -> RenderResult:
        visual_clips = []
        audio_clips = []
        
        timeline_state = plan.timeline_state
        render_profile = plan.render_profile

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
        output_width = render_profile.resolution.width
        output_height = render_profile.resolution.height
        total_duration = timeline_state.total_duration.value

        base_clip = ColorClip(size=(output_width, output_height), color=(0, 0, 0), duration=total_duration)
        final_video = CompositeVideoClip([base_clip] + visual_clips, size=(output_width, output_height))

        # Composite Audio
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)

        # Generate unique output path
        os.makedirs(self._output_dir, exist_ok=True)
        filename = f"render_{uuid.uuid4().hex}.{render_profile.output_container.lstrip('.')}"
        output_path = os.path.join(self._output_dir, filename)
        
        # Determine bitrates (MoviePy expects strings like '5000k')
        video_bitrate = render_profile.video_bitrate if render_profile.video_bitrate else None
        audio_bitrate = render_profile.audio_bitrate if render_profile.audio_bitrate else None
        
        # Render Output
        final_video.write_videofile(
            output_path,
            fps=render_profile.frame_rate,
            codec=render_profile.video_codec,
            audio_codec=render_profile.audio_codec,
            bitrate=video_bitrate,
            audio_bitrate=audio_bitrate
        )

        final_video.close()

        return RenderResult(
            status=RenderStatus.COMPLETED,
            rendered_output_location=output_path,
            rendered_duration=total_duration,
            rendering_metadata={"provider": "MoviePyRenderingBackend"}
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
