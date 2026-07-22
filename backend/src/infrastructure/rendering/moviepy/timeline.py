import uuid
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Dict

try:
    from moviepy.editor import CompositeVideoClip, CompositeAudioClip
except ImportError:
    CompositeVideoClip = None
    CompositeAudioClip = None

from src.domain.render_plan import RenderPlan, RenderSegment, LayerCategory
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool

@dataclass(frozen=True)
class MoviePyCompositionContext:
    """Encapsulates global composition settings for the timeline."""
    duration_seconds: float
    resolution_width: int
    resolution_height: int
    fps: float
    background_color: Tuple[int, int, int] = (0, 0, 0)


@dataclass(frozen=True)
class MoviePyTimeline:
    """
    Immutable representation of the composed MoviePy timeline.
    Owns the root composition graph but NOT the underlying file resources,
    which remain owned by the MoviePyResourcePool.
    """
    context: MoviePyCompositionContext
    _root_video: Any  # Hidden implementation detail (CompositeVideoClip)
    _root_audio: Any  # Hidden implementation detail (CompositeAudioClip)
    
    @property
    def has_video(self) -> bool:
        return self._root_video is not None
        
    @property
    def has_audio(self) -> bool:
        return self._root_audio is not None


class MoviePyPositionTranslator:
    """
    Translates backend-neutral positioning abstractions into MoviePy-specific
    positioning tuples or strings.
    """
    @staticmethod
    def translate(segment: RenderSegment, context: MoviePyCompositionContext) -> Any:
        for instruction in segment.instructions:
            if instruction.instruction_type in ("transform", "position"):
                params = instruction.parameters
                # Explicit pixel coordinates
                if "x" in params and "y" in params:
                    return (params["x"], params["y"])
                # Named positions or normalized strings
                if "position" in params:
                    return params["position"]
        
        # Default positioning if not specified
        return "center"


class MoviePyTimelineComposer:
    """
    Composes a MoviePy timeline via an operation pipeline:
    trim -> timing -> positioning -> layering -> composition
    """
    
    @classmethod
    def create_context(cls, plan: RenderPlan) -> MoviePyCompositionContext:
        return MoviePyCompositionContext(
            duration_seconds=plan.metadata.duration_seconds,
            resolution_width=plan.metadata.resolution.width,
            resolution_height=plan.metadata.resolution.height,
            fps=plan.metadata.frame_rate.fps
        )

    @classmethod
    def apply_trimming(cls, clip: Any, segment: RenderSegment) -> Any:
        """Pipeline Stage 1: Trimming (source_start to source_end)"""
        try:
            return clip.subclip(segment.source_start.time_seconds, segment.source_end.time_seconds)
        except AttributeError:
            # Some clips (like static ImageClip) might not require/support subclip directly in older versions
            return clip

    @classmethod
    def apply_timing(cls, clip: Any, segment: RenderSegment) -> Any:
        """Pipeline Stage 2: Timing (set_start and duration calculation)"""
        clip = clip.set_start(segment.timeline_start.time_seconds)
        duration = segment.timeline_end.time_seconds - segment.timeline_start.time_seconds
        return clip.set_duration(duration)

    @classmethod
    def apply_positioning(cls, clip: Any, segment: RenderSegment, context: MoviePyCompositionContext) -> Any:
        """Pipeline Stage 3: Positioning (placement on canvas)"""
        if hasattr(clip, 'set_position'):
            position = MoviePyPositionTranslator.translate(segment, context)
            return clip.set_position(position)
        return clip

    @classmethod
    def process_segment(
        cls, 
        segment: RenderSegment, 
        clip: Any, 
        context: MoviePyCompositionContext,
        category: LayerCategory
    ) -> Any:
        """Executes the operations pipeline for a single segment."""
        # 1. Trimming
        processed = cls.apply_trimming(clip, segment)
        
        # 2. Timing
        processed = cls.apply_timing(processed, segment)
        
        # 3. Positioning (only applicable for visual layers)
        if category in (LayerCategory.VIDEO, LayerCategory.OVERLAY):
            processed = cls.apply_positioning(processed, segment, context)
            
        return processed

    @classmethod
    def compose(cls, plan: RenderPlan, resources: MoviePyResourcePool) -> MoviePyTimeline:
        """
        Main composition orchestrator. Iterates the RenderPlan and assembles
        the final immutable MoviePyTimeline.
        """
        context = cls.create_context(plan)
        
        video_clips: List[Any] = []
        audio_clips: List[Any] = []
        
        # Pipeline Stage 4: Layering (Deterministic Z-Ordering)
        sorted_layers = sorted(plan.layers, key=lambda l: l.z_index)
        
        for layer in sorted_layers:
            for track in layer.tracks:
                for segment in track.segments:
                    # Retrieve read-only resource
                    clip = None
                    if layer.category == LayerCategory.VIDEO:
                        clip = resources.get_video_clip(segment.id)
                    elif layer.category == LayerCategory.AUDIO:
                        clip = resources.get_audio_clip(segment.id)
                    elif layer.category == LayerCategory.OVERLAY:
                        clip = resources.get_image_clip(segment.id)
                        
                    if clip is None:
                        continue
                        
                    # Process pipeline
                    processed_clip = cls.process_segment(segment, clip, context, layer.category)
                    
                    if layer.category in (LayerCategory.VIDEO, LayerCategory.OVERLAY):
                        video_clips.append(processed_clip)
                    elif layer.category == LayerCategory.AUDIO:
                        audio_clips.append(processed_clip)
                        
        # Pipeline Stage 5: Composition
        root_video = None
        if video_clips and CompositeVideoClip is not None:
            root_video = CompositeVideoClip(
                video_clips, 
                size=(context.resolution_width, context.resolution_height),
                bg_color=context.background_color
            )
            root_video = root_video.set_duration(context.duration_seconds)
            
        root_audio = None
        if audio_clips and CompositeAudioClip is not None:
            root_audio = CompositeAudioClip(audio_clips)
            root_audio = root_audio.set_duration(context.duration_seconds)
            
        return MoviePyTimeline(
            context=context,
            _root_video=root_video,
            _root_audio=root_audio
        )
